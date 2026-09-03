"""Unit tests for deterministic confidence scorer."""

import pytest
from app.models.agent import (
    AgentAction,
    ConfidenceLevel,
    InterpretationResult,
    PhraseCandidate,
)
from app.scoring.scorer import ConfidenceScorer


@pytest.fixture
def scorer():
    """Create ConfidenceScorer with standard thresholds (0.80 / 0.45)."""
    return ConfidenceScorer(high_threshold=0.80, low_threshold=0.45)


def test_high_confidence_proposes_phrase(scorer: ConfidenceScorer):
    """Verify strong candidate scores yield HIGH confidence and PROPOSE_PHRASE action."""
    interp = InterpretationResult(
        raw_transcript="I need water",
        stt_confidence=0.85,
        candidates=[
            PhraseCandidate(text="I need water", confidence=0.90),
            PhraseCandidate(text="I need a drink", confidence=0.40),
        ],
    )
    decision = scorer.score_and_decide(interp)

    assert decision.action == AgentAction.PROPOSE_PHRASE
    assert decision.confidence_level == ConfidenceLevel.HIGH
    assert decision.overall_confidence >= 0.80
    assert decision.primary_phrase == "I need water"


def test_medium_confidence_shows_candidates(scorer: ConfidenceScorer):
    """Verify medium candidate scores yield MEDIUM confidence and SHOW_CANDIDATES action."""
    interp = InterpretationResult(
        raw_transcript="need wa",
        stt_confidence=0.55,
        candidates=[
            PhraseCandidate(text="I need water", confidence=0.65),
            PhraseCandidate(text="I need to wait", confidence=0.60),
        ],
    )
    decision = scorer.score_and_decide(interp)

    assert decision.action == AgentAction.SHOW_CANDIDATES
    assert decision.confidence_level == ConfidenceLevel.MEDIUM
    assert 0.45 <= decision.overall_confidence < 0.80
    assert len(decision.candidates) == 2


def test_high_confidence_requires_strong_stt_evidence(scorer: ConfidenceScorer):
    """Verify a confident interpretation cannot bypass the minimum STT safeguard."""
    interp = InterpretationResult(
        raw_transcript="need water",
        stt_confidence=0.49,
        candidates=[
            PhraseCandidate(text="I need water", confidence=0.95),
            PhraseCandidate(text="I need to wait", confidence=0.30),
        ],
    )

    decision = scorer.score_and_decide(interp, has_memory_match=True)

    assert decision.action == AgentAction.SHOW_CANDIDATES
    assert decision.confidence_level == ConfidenceLevel.MEDIUM


def test_high_confidence_requires_top_candidate_threshold(scorer: ConfidenceScorer):
    """Verify a high composite score cannot elevate a weak top candidate."""
    interp = InterpretationResult(
        raw_transcript="need water",
        stt_confidence=1.0,
        candidates=[
            PhraseCandidate(text="I need water", confidence=0.79),
            PhraseCandidate(text="I need to wait", confidence=0.20),
        ],
    )

    decision = scorer.score_and_decide(interp, has_memory_match=True)

    assert decision.action == AgentAction.SHOW_CANDIDATES
    assert decision.confidence_level == ConfidenceLevel.MEDIUM


def test_low_confidence_requests_repeat(scorer: ConfidenceScorer):
    """Verify weak candidate scores yield LOW confidence and REQUEST_REPEAT action without guessing."""
    interp = InterpretationResult(
        raw_transcript="uh mmm",
        stt_confidence=0.20,
        candidates=[
            PhraseCandidate(text="unknown sound", confidence=0.30),
        ],
    )
    decision = scorer.score_and_decide(interp)

    assert decision.action == AgentAction.REQUEST_REPEAT
    assert decision.confidence_level == ConfidenceLevel.LOW
    assert decision.overall_confidence < 0.45
    assert decision.primary_phrase is None


def test_empty_candidates_requests_repeat(scorer: ConfidenceScorer):
    """Verify empty candidates immediately trigger REQUEST_REPEAT with zero confidence."""
    interp = InterpretationResult(
        raw_transcript="",
        stt_confidence=0.0,
        candidates=[],
    )
    decision = scorer.score_and_decide(interp)

    assert decision.action == AgentAction.REQUEST_REPEAT
    assert decision.confidence_level == ConfidenceLevel.LOW
    assert decision.overall_confidence == 0.0


def test_memory_match_bonus(scorer: ConfidenceScorer):
    """Verify personal memory match boosts composite confidence."""
    interp = InterpretationResult(
        raw_transcript="watah",
        stt_confidence=0.60,
        candidates=[
            PhraseCandidate(text="I need water", confidence=0.74),
        ],
    )
    without_memory = scorer.score_and_decide(interp, has_memory_match=False)
    with_memory = scorer.score_and_decide(interp, has_memory_match=True)

    assert with_memory.overall_confidence > without_memory.overall_confidence
