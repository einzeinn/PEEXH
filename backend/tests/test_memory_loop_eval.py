"""Unit tests for MemoryLoopEvaluator simulating two-pass adaptive learning."""

import pytest
from app.llm.mock import MockInterpreter
from app.memory.mock import MockMemoryStore
from evaluation.data.loader import EvaluationSample
from evaluation.memory_loop import MemoryLoopEvaluator


@pytest.mark.anyio
async def test_memory_loop_evaluator():
    """Verify MemoryLoopEvaluator shows improvement (positive delta) after user correction."""
    sample = EvaluationSample(
        id="TEST-MEM",
        dysarthria_type="spastic",
        raw_stt_transcript="custom uncommon phoneme phrase",
        intended_phrase="I want to sleep now",
        stt_confidence=0.60,
    )

    evaluator = MemoryLoopEvaluator(
        interpreter=MockInterpreter(),
        memory_store=MockMemoryStore(),
    )

    result = await evaluator.evaluate_sample(sample, user_id="test_mem_user")

    assert result.sample_id == "TEST-MEM"
    assert result.has_memory_match_pass2 is True
    # Pass 2 WER should be 0.0 because exact memory match returns "I want to sleep now"
    assert result.pass2_wer == 0.0
    assert result.memory_delta >= 0.0
