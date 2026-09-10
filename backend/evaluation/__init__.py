"""PEEXH Evaluation Framework (Phase 5 - RFC-006)."""

from evaluation.baseline import BaselineCapture
from evaluation.data.loader import EvaluationSample, load_samples
from evaluation.memory_loop import MemoryLoopEvaluator
from evaluation.metrics import LatencyBreakdown, calculate_imr, calculate_wer
from evaluation.models import (
    BaselineResult,
    EvaluationSummary,
    MemoryLoopResult,
    PeexhResult,
)
from evaluation.peexh_eval import PeexhEvaluator
from evaluation.report import ReportGenerator
from evaluation.runner import EvaluationRunner

__all__ = [
    "EvaluationSample",
    "load_samples",
    "calculate_wer",
    "calculate_imr",
    "LatencyBreakdown",
    "BaselineResult",
    "PeexhResult",
    "MemoryLoopResult",
    "EvaluationSummary",
    "BaselineCapture",
    "PeexhEvaluator",
    "MemoryLoopEvaluator",
    "ReportGenerator",
    "EvaluationRunner",
]
