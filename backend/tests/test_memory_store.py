"""Unit tests for personal speech memory store implementations (RFC-005)."""

import pytest
from app.memory.mock import MockMemoryStore
from app.memory.factory import get_memory_store
from app.core.config import Settings


@pytest.fixture
def store():
    """Create a fresh MockMemoryStore for testing."""
    return MockMemoryStore()


@pytest.mark.anyio
async def test_record_and_retrieve_exact_correction(store):
    """Verify that recording a correction pair allows exact retrieval."""
    await store.record_correction(
        raw_transcript="i ned wtr",
        corrected_phrase="I need water",
        user_id="user_123",
    )

    matches = await store.retrieve_matches("i ned wtr", user_id="user_123")
    assert len(matches) == 1
    assert matches[0].matched_phrase == "I need water"
    assert matches[0].original_transcript == "i ned wtr"
    assert matches[0].similarity_score == 1.0
    assert matches[0].frequency == 1


@pytest.mark.anyio
async def test_correction_frequency_increment(store):
    """Verify that recording the same correction repeatedly increments its frequency."""
    await store.record_correction("i ned wtr", "I need water", user_id="user_123")
    await store.record_correction("i ned wtr", "I need water", user_id="user_123")
    await store.record_correction("i ned wtr", "I need water", user_id="user_123")

    matches = await store.retrieve_matches("i ned wtr", user_id="user_123")
    assert len(matches) == 1
    assert matches[0].frequency == 3


@pytest.mark.anyio
async def test_fuzzy_retrieval(store):
    """Verify that slight variations in raw speech still match via fuzzy similarity."""
    await store.record_correction(
        raw_transcript="i need water please",
        corrected_phrase="I need water",
        user_id="user_123",
    )

    # Similar but not identical transcript
    matches = await store.retrieve_matches("i need water", user_id="user_123")
    assert len(matches) == 1
    assert matches[0].matched_phrase == "I need water"
    assert matches[0].similarity_score >= 0.70


@pytest.mark.anyio
async def test_user_isolation(store):
    """Verify that speech memory is strictly partitioned by user_id."""
    await store.record_correction("meds", "Take my medicine", user_id="user_A")

    matches_a = await store.retrieve_matches("meds", user_id="user_A")
    assert len(matches_a) == 1

    matches_b = await store.retrieve_matches("meds", user_id="user_B")
    assert len(matches_b) == 0


@pytest.mark.anyio
async def test_phrase_usage_recording(store):
    """Verify that confirming phrases tracks usage frequency."""
    await store.record_phrase_usage("Good morning", user_id="user_123")
    await store.record_phrase_usage("Good morning", user_id="user_123")

    assert store._frequencies["user_123"]["Good morning"] == 2


@pytest.mark.anyio
async def test_clear_memory(store):
    """Verify that clear_memory erases stored data for that user."""
    await store.record_correction("help", "Please help me", user_id="user_123")
    await store.record_phrase_usage("Please help me", user_id="user_123")

    await store.clear_memory(user_id="user_123")

    matches = await store.retrieve_matches("help", user_id="user_123")
    assert len(matches) == 0
    assert "user_123" not in store._frequencies


def test_factory_returns_mock_when_supabase_unconfigured():
    """Verify factory returns MockMemoryStore when credentials are not configured."""
    cfg = Settings(
        ENABLE_PERSONAL_MEMORY=True,
        SUPABASE_URL=None,
        SUPABASE_KEY=None,
    )
    store = get_memory_store(cfg)
    assert isinstance(store, MockMemoryStore)
