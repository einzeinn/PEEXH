"""Unit tests for speech domain models."""

from app.models.speech import (
    ErrorEvent,
    SessionStartedEvent,
    SpeechStoppedEvent,
    StartSessionMessage,
    StopSessionMessage,
    TranscriptEvent,
    TranscriptWord,
)


def test_start_session_message_defaults():
    """Test StartSessionMessage default values and serialization."""
    msg = StartSessionMessage()
    assert msg.type == "start"
    assert msg.sample_rate == 16000
    assert msg.model_dump() == {"type": "start", "sample_rate": 16000}


def test_stop_session_message():
    """Test StopSessionMessage serialization."""
    msg = StopSessionMessage()
    assert msg.type == "stop"
    assert msg.model_dump() == {"type": "stop"}


def test_session_started_event():
    """Test SessionStartedEvent serialization."""
    event = SessionStartedEvent(session_id="test-123", provider="assemblyai")
    assert event.type == "session_started"
    assert event.session_id == "test-123"
    assert event.provider == "assemblyai"


def test_transcript_event():
    """Test TranscriptEvent with word confidence."""
    word = TranscriptWord(text="hello", start=100, end=450, confidence=0.92)
    event = TranscriptEvent(
        text="hello",
        is_final=True,
        confidence=0.92,
        words=[word],
    )
    data = event.model_dump()
    assert data["type"] == "transcript"
    assert data["text"] == "hello"
    assert data["is_final"] is True
    assert data["confidence"] == 0.92
    assert len(data["words"]) == 1
    assert data["words"][0]["text"] == "hello"


def test_error_event():
    """Test ErrorEvent serialization."""
    err = ErrorEvent(message="Connection failed", code="ERR_TIMEOUT")
    assert err.type == "error"
    assert err.message == "Connection failed"
    assert err.code == "ERR_TIMEOUT"
