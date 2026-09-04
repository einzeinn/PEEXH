"""Unit tests for PeexhAgent orchestrator and state transitions."""

import pytest
from app.agent.orchestrator import PeexhAgent
from app.agent.state import AgentState
from app.models.agent import AgentAction, ConfidenceLevel


@pytest.mark.anyio
async def test_agent_process_high_confidence_phrase():
    """Verify agent transitions through INTERPRETING, DECIDING to AWAITING_CONFIRMATION on clear match."""
    agent = PeexhAgent()
    assert agent.state == AgentState.IDLE

    decision = await agent.process_transcript(
        transcript="I need water",
        stt_confidence=0.88,
    )

    assert decision.action == AgentAction.PROPOSE_PHRASE
    assert decision.confidence_level == ConfidenceLevel.HIGH
    assert decision.primary_phrase == "I need water"
    assert agent.state == AgentState.AWAITING_CONFIRMATION


@pytest.mark.anyio
async def test_agent_process_low_confidence_phrase():
    """Verify agent transitions to IDLE and requests repeat on low-confidence noise."""
    agent = PeexhAgent()
    decision = await agent.process_transcript(
        transcript="uh",
        stt_confidence=0.1,
    )

    assert decision.action == AgentAction.REQUEST_REPEAT
    assert decision.confidence_level == ConfidenceLevel.LOW
    # RFC-004 invariant: all agent decisions → AWAITING_CONFIRMATION, never IDLE.
    # Only an explicit request_repeat user message returns agent to IDLE.
    assert agent.state == AgentState.AWAITING_CONFIRMATION


def test_agent_reset():
    """Verify agent reset returns to IDLE state."""
    agent = PeexhAgent()
    agent.set_state(AgentState.AWAITING_CONFIRMATION)
    agent.reset()
    assert agent.state == AgentState.IDLE
