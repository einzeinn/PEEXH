"""Baseline capture runner evaluating raw speech-to-text accuracy without agent assistance."""

from typing import List
from evaluation.data.loader import EvaluationSample
from evaluation.metrics import calculate_wer
from evaluation.models import BaselineResult


class BaselineCapture:
    """Evaluates raw Speech-To-Text transcripts directly against intended ground truth."""

    def evaluate_sample(self, sample: EvaluationSample) -> BaselineResult:
        """Compute baseline WER for an individual sample."""
        wer = calculate_wer(
            reference=sample.intended_phrase,
            hypothesis=sample.raw_stt_transcript,
        )
        return BaselineResult(
            sample_id=sample.id,
            raw_transcript=sample.raw_stt_transcript,
            intended_phrase=sample.intended_phrase,
            baseline_wer=round(wer, 4),
        )

    def evaluate_all(self, samples: List[EvaluationSample]) -> List[BaselineResult]:
        """Compute baseline WER across all provided samples."""
        return [self.evaluate_sample(s) for s in samples]
