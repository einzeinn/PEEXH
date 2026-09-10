"""Pydantic domain models for evaluation results and summary reports."""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

from evaluation.metrics import LatencyBreakdown


class BaselineResult(BaseModel):
    """Result of running raw STT baseline against intended ground truth."""
    sample_id: str
    raw_transcript: str
    intended_phrase: str
    baseline_wer: float


class PeexhResult(BaseModel):
    """Result of evaluating the full PEEXH agent pipeline on an utterance."""
    sample_id: str
    raw_transcript: str
    intended_phrase: str
    agent_action: str
    primary_phrase: Optional[str] = None
    candidates: List[str] = Field(default_factory=list)
    peexh_wer: float
    intent_matched: bool
    has_memory_match: bool = False
    latency: LatencyBreakdown


class MemoryLoopResult(BaseModel):
    """Result of a two-pass memory learning evaluation."""
    sample_id: str
    raw_transcript: str
    intended_phrase: str
    pass1_wer: float
    pass2_wer: float
    memory_delta: float
    has_memory_match_pass2: bool


class EvaluationSummary(BaseModel):
    """Aggregated evaluation metrics across baseline, agent, and memory loop."""
    total_samples: int
    baseline_avg_wer: float
    peexh_avg_wer: float
    wer_improvement_pct: float
    intent_match_rate: float
    avg_total_latency_ms: float
    memory_loop_avg_delta: float
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
