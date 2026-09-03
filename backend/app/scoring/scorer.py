"""Deterministic confidence scoring and decision engine for PEEXH."""

from typing import Optional
from app.core.config import settings
from app.models.agent import (
    AgentAction,
    AgentDecision,
    ConfidenceLevel,
    InterpretationResult,
)


class ConfidenceScorer:
    """Calculates deterministic confidence outside the LLM and selects agent action."""

    def __init__(
        self,
        high_threshold: Optional[float] = None,
        low_threshold: Optional[float] = None,
        min_stt_confidence_for_high: Optional[float] = None,
    ) -> None:
        self.high_threshold = (
            high_threshold
            if high_threshold is not None
            else settings.PEEXH_HIGH_CONFIDENCE_THRESHOLD
        )
        self.low_threshold = (
            low_threshold
            if low_threshold is not None
            else settings.PEEXH_LOW_CONFIDENCE_THRESHOLD
        )
        self.min_stt_confidence_for_high = (
            min_stt_confidence_for_high
            if min_stt_confidence_for_high is not None
            else settings.PEEXH_MIN_STT_CONFIDENCE_FOR_HIGH
        )

    def score_and_decide(
        self,
        interpretation: InterpretationResult,
        has_memory_match: bool = False,
    ) -> AgentDecision:
        """Evaluate an interpretation result and produce an authoritative AgentDecision.

        Core rules:
        - HIGH (>= high_threshold) -> PROPOSE_PHRASE (one best interpretation)
        - MEDIUM (>= low_threshold) -> SHOW_CANDIDATES (2-3 candidates)
        - LOW (< low_threshold) -> REQUEST_REPEAT (do not guess; ask user to repeat)
        """
        raw_text = interpretation.raw_transcript.strip()
        candidates = interpretation.candidates

        # 1. Guard against empty transcript or empty candidates
        if not raw_text or not candidates:
            return AgentDecision(
                action=AgentAction.REQUEST_REPEAT,
                confidence_level=ConfidenceLevel.LOW,
                overall_confidence=0.0,
                primary_phrase=None,
                candidates=[],
                reason="No candidate interpretations available or empty speech transcript.",
            )

        # Sort candidates descending by confidence
        sorted_candidates = sorted(candidates, key=lambda c: c.confidence, reverse=True)
        top_cand = sorted_candidates[0]

        # Calculate candidate margin
        margin = (
            top_cand.confidence - sorted_candidates[1].confidence
            if len(sorted_candidates) > 1
            else top_cand.confidence
        )

        # 2. Compute composite confidence
        # Weigh: STT acoustic confidence (35%) + Model confidence (65%)
        stt_conf = max(0.0, min(1.0, interpretation.stt_confidence))
        model_conf = max(0.0, min(1.0, top_cand.confidence))

        composite = (0.35 * stt_conf) + (0.65 * model_conf)

        # Apply margin bonus if top candidate is distinct
        if margin >= 0.20:
            composite += 0.05

        # Apply personal memory bonus if previously confirmed pattern matches
        if has_memory_match:
            composite += 0.10

        composite_score = round(max(0.0, min(1.0, composite)), 2)

        # 3. Classify into deterministic tiers
        # A high-confidence proposal needs strong independent evidence from both
        # transcription and interpretation. A memory match may raise the composite
        # score, but it must not bypass either safeguard.
        if (
            composite_score >= self.high_threshold
            and model_conf >= self.high_threshold
            and stt_conf >= self.min_stt_confidence_for_high
        ):
            return AgentDecision(
                action=AgentAction.PROPOSE_PHRASE,
                confidence_level=ConfidenceLevel.HIGH,
                overall_confidence=composite_score,
                primary_phrase=top_cand.text,
                candidates=sorted_candidates[:3],
                reason=f"High confidence ({composite_score} >= {self.high_threshold}). Proposing best match.",
            )

        if composite_score >= self.low_threshold:
            return AgentDecision(
                action=AgentAction.SHOW_CANDIDATES,
                confidence_level=ConfidenceLevel.MEDIUM,
                overall_confidence=composite_score,
                primary_phrase=top_cand.text,
                candidates=sorted_candidates[:3],
                reason=f"Medium confidence ({composite_score}). Presenting top candidate phrases.",
            )

        # Low confidence: never pretend certainty or guess blindly
        return AgentDecision(
            action=AgentAction.REQUEST_REPEAT,
            confidence_level=ConfidenceLevel.LOW,
            overall_confidence=composite_score,
            primary_phrase=None,
            candidates=sorted_candidates[:2],
            reason=f"Low confidence ({composite_score} < {self.low_threshold}). Asking user to repeat.",
        )
