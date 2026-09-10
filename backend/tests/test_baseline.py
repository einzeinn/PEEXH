"""Unit tests for BaselineCapture runner."""

from evaluation.baseline import BaselineCapture
from evaluation.data.loader import EvaluationSample


def test_baseline_capture_single_sample():
    """Verify BaselineCapture computes WER between raw transcript and intended phrase."""
    sample = EvaluationSample(
        id="TEST-001",
        dysarthria_type="spastic",
        raw_stt_transcript="i ned wtr",
        intended_phrase="I need water",
        stt_confidence=0.60,
    )
    runner = BaselineCapture()
    res = runner.evaluate_sample(sample)

    assert res.sample_id == "TEST-001"
    assert res.raw_transcript == "i ned wtr"
    assert res.intended_phrase == "I need water"
    assert res.baseline_wer > 0.0  # Phonetically distorted, so WER must be > 0


def test_baseline_capture_evaluate_all():
    """Verify evaluating a list of samples produces corresponding BaselineResult objects."""
    samples = [
        EvaluationSample(
            id="T1",
            dysarthria_type="ataxic",
            raw_stt_transcript="hel me",
            intended_phrase="help me",
            stt_confidence=0.50,
        ),
        EvaluationSample(
            id="T2",
            dysarthria_type="flaccid",
            raw_stt_transcript="thank you",
            intended_phrase="thank you",
            stt_confidence=0.90,
        ),
    ]
    runner = BaselineCapture()
    results = runner.evaluate_all(samples)

    assert len(results) == 2
    assert results[0].sample_id == "T1"
    assert results[1].baseline_wer == 0.0  # Identical
