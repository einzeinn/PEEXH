"""Unit tests for PEEXH agent confirmation state transitions and validation (RFC-004)."""

import pytest
from app.agent.orchestrator import InvalidStateError, PeexhAgent
from app.agent.state import AgentState
from app.llm.mock import MockInterpreter
from app.models.agent import (
    AgentAction,
    AgentDecision,
    ConfidenceLevel,
    ConfirmedPhraseSource,
    PhraseCandidate,
)
from app.scoring.scorer import ConfidenceScorer


@pytest.fixture
def agent():
    """Create a PeexhAgent with deterministic mock interpreter and scorer."""
    interpreter = MockInterpreter()
    scorer = ConfidenceScorer()
    return PeexhAgent(interpreter=interpreter, scorer=scorer)


@pytest.mark.anyio
async def test_confirm_proposal_success(agent):
    """confirm_proposal succeeds for high-confidence PROPOSE_PHRASE decision."""
    decision = await agent.process_transcript(
        transcript="I need water",
        stt_confidence=0.9,
    )
    assert decision.action == AgentAction.PROPOSE_PHRASE
    assert agent.state == AgentState.AWAITING_CONFIRMATION

    event = agent.confirm_proposal()
    assert event.type == "communication_ready"
    assert event.phrase == decision.primary_phrase
    assert event.source == ConfirmedPhraseSource.PROPOSAL
    assert agent.state == AgentState.CONFIRMED
    assert agent.active_decision is None


def test_confirm_proposal_invalid_state_idle(agent):
    """confirm_proposal fails when agent is in IDLE state."""
    assert agent.state == AgentState.IDLE
    with pytest.raises(InvalidStateError, match="not in AWAITING_CONFIRMATION"):
        agent.confirm_proposal()


def test_confirm_proposal_invalid_for_non_proposal_action(agent):
    """confirm_proposal fails if active decision is SHOW_CANDIDATES or REQUEST_REPEAT."""
    # Set up a synthetic SHOW_CANDIDATES decision
    agent.active_decision = AgentDecision(
        action=AgentAction.SHOW_CANDIDATES,
        confidence_level=ConfidenceLevel.MEDIUM,
        overall_confidence=0.6,
        candidates=[PhraseCandidate(text="Option A", confidence=0.6)],
    )
    agent.set_state(AgentState.AWAITING_CONFIRMATION)

    with pytest.raises(InvalidStateError, match="active decision action is"):
        agent.confirm_proposal()


def test_select_candidate_success(agent):
    """select_candidate succeeds when selected phrase matches candidate list."""
    agent.active_decision = AgentDecision(
        action=AgentAction.SHOW_CANDIDATES,
        confidence_level=ConfidenceLevel.MEDIUM,
        overall_confidence=0.65,
        candidates=[
            PhraseCandidate(text="I need water", confidence=0.65),
            PhraseCandidate(text="I need medicine", confidence=0.55),
        ],
    )
    agent.set_state(AgentState.AWAITING_CONFIRMATION)

    event = agent.select_candidate("I need medicine")
    assert event.type == "communication_ready"
    assert event.phrase == "I need medicine"
    assert event.source == ConfirmedPhraseSource.CANDIDATE
    assert agent.state == AgentState.CONFIRMED
    assert agent.active_decision is None


def test_select_candidate_mismatch_raises_value_error(agent):
    """select_candidate rejects phrases not in candidate list."""
    agent.active_decision = AgentDecision(
        action=AgentAction.SHOW_CANDIDATES,
        confidence_level=ConfidenceLevel.MEDIUM,
        overall_confidence=0.65,
        candidates=[
            PhraseCandidate(text="I need water", confidence=0.65),
        ],
    )
    agent.set_state(AgentState.AWAITING_CONFIRMATION)

    with pytest.raises(ValueError, match="does not match any candidate"):
        agent.select_candidate("Unrelated phrase")


@pytest.mark.anyio
async def test_select_candidate_invalid_state_and_action(agent):
    """select_candidate fails when not in AWAITING_CONFIRMATION or wrong action."""
    with pytest.raises(InvalidStateError):
        agent.select_candidate("Test")

    # High confidence PROPOSE_PHRASE
    await agent.process_transcript("i ned wtr", stt_confidence=0.9)
    with pytest.raises(InvalidStateError, match="active decision action is"):
        agent.select_candidate("I need water")


def test_submit_correction_success_all_actions(agent):
    """submit_correction succeeds for PROPOSE_PHRASE, SHOW_CANDIDATES, and REQUEST_REPEAT."""
    for action in [AgentAction.PROPOSE_PHRASE, AgentAction.SHOW_CANDIDATES, AgentAction.REQUEST_REPEAT]:
        agent.active_decision = AgentDecision(
            action=action,
            confidence_level=ConfidenceLevel.LOW,
            overall_confidence=0.2,
        )
        agent.set_state(AgentState.AWAITING_CONFIRMATION)

        event = agent.submit_correction("  I want to go outside  ")
        assert event.type == "communication_ready"
        assert event.phrase == "I want to go outside"  # Trimmed
        assert event.source == ConfirmedPhraseSource.CORRECTION
        assert agent.state == AgentState.CONFIRMED
        assert agent.active_decision is None


def test_submit_correction_validation(agent):
    """submit_correction rejects empty, whitespace-only, and overlong text."""
    agent.active_decision = AgentDecision(
        action=AgentAction.REQUEST_REPEAT,
        confidence_level=ConfidenceLevel.LOW,
        overall_confidence=0.2,
    )
    agent.set_state(AgentState.AWAITING_CONFIRMATION)

    with pytest.raises(ValueError, match="cannot be empty"):
        agent.submit_correction("   ")

    with pytest.raises(ValueError, match="exceed 500 characters"):
        agent.submit_correction("a" * 501)


@pytest.mark.anyio
async def test_request_repeat_transitions_to_idle(agent):
    """request_repeat clears active decision and returns agent to IDLE."""
    # Process low confidence
    decision = await agent.process_transcript("uh", stt_confidence=0.1)
    assert decision.action == AgentAction.REQUEST_REPEAT
    assert agent.state == AgentState.AWAITING_CONFIRMATION
    assert agent.active_decision is not None

    event = agent.request_repeat()
    assert event.type == "repeat_requested"
    assert agent.state == AgentState.IDLE
    assert agent.active_decision is None


def test_request_repeat_invalid_state(agent):
    """request_repeat raises InvalidStateError if agent is in IDLE."""
    assert agent.state == AgentState.IDLE
    with pytest.raises(InvalidStateError):
        agent.request_repeat()
