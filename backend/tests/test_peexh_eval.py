"""Unit tests for PeexhEvaluator pipeline runner."""

import pytest
from app.llm.mock import MockInterpreter
from app.memory.mock import MockMemoryStore
from evaluation.data.loader import EvaluationSample
from evaluation.peexh_eval import PeexhEvaluator


@pytest.mark.anyio
async def test_peexh_evaluator_sample():
    """Verify PeexhEvaluator produces PeexhResult with timing and accuracy metrics."""
    sample = EvaluationSample(
        id="TEST-PEEXH",
        dysarthria_type="spastic",
        raw_stt_transcript="i ned wtr",
        intended_phrase="I need some water",
        stt_confidence=0.85,
    )

    evaluator = PeexhEvaluator(
        interpreter=MockInterpreter(),
        memory_store=MockMemoryStore(),
    )
    result = await evaluator.evaluate_sample(sample)

    assert result.sample_id == "TEST-PEEXH"
    assert result.agent_action in ("PROPOSE_PHRASE", "SHOW_CANDIDATES")
    assert result.primary_phrase is not None
    assert "water" in result.primary_phrase.lower()
    assert result.intent_matched is True
    assert result.peexh_wer < 0.50
    # Latency breakdown checks
    assert result.latency.total_pipeline_ms > 0.0
    assert result.latency.llm_interpret_ms >= 0.0
    assert result.latency.scorer_ms >= 0.0
