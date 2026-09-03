"""Unit tests for agent domain models."""

import pytest
from app.models.agent import (
    AgentAction,
    AgentDecision,
    ConfidenceLevel,
    InterpretationResult,
    PhraseCandidate,
)


def test_phrase_candidate():
    """Verify PhraseCandidate validation and properties."""
    cand = PhraseCandidate(text="I need water", confidence=0.92, explanation="Phonetic match")
    assert cand.text == "I need water"
    assert cand.confidence == 0.92
    assert cand.explanation == "Phonetic match"


def test_interpretation_result():
    """Verify InterpretationResult contains raw transcript and candidate list."""
    cand = PhraseCandidate(text="I need water", confidence=0.85)
    result = InterpretationResult(
        raw_transcript="need wa-er",
        stt_confidence=0.70,
        candidates=[cand],
    )
    assert result.raw_transcript == "need wa-er"
    assert result.stt_confidence == 0.70
    assert len(result.candidates) == 1


def test_agent_decision_high_confidence():
    """Verify AgentDecision serialization for high confidence."""
    decision = AgentDecision(
        action=AgentAction.PROPOSE_PHRASE,
        confidence_level=ConfidenceLevel.HIGH,
        overall_confidence=0.88,
        primary_phrase="I need water",
        candidates=[PhraseCandidate(text="I need water", confidence=0.88)],
        reason="Candidate confidence exceeds high threshold",
    )
    data = decision.model_dump()
    assert data["type"] == "agent_decision"
    assert data["action"] == "PROPOSE_PHRASE"
    assert data["confidence_level"] == "HIGH"
    assert data["primary_phrase"] == "I need water"
