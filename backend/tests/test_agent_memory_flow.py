"""Integration tests verifying the adaptive learning loop with Personal Speech Memory (RFC-005)."""

import asyncio
import pytest
from app.agent.orchestrator import PeexhAgent
from app.agent.state import AgentState
from app.llm.mock import MockInterpreter
from app.memory.mock import MockMemoryStore
from app.models.agent import AgentAction, ConfidenceLevel
from app.scoring.scorer import ConfidenceScorer


@pytest.mark.anyio
async def test_adaptive_learning_flow():
    """Verify that correcting a phrase improves subsequent interpretation from MEDIUM to HIGH."""
    memory_store = MockMemoryStore()
    interpreter = MockInterpreter()
    scorer = ConfidenceScorer()
    agent = PeexhAgent(
        interpreter=interpreter,
        scorer=scorer,
        memory_store=memory_store,
    )

    # 1. First Attempt: User says "pls hlp me" with moderate STT confidence
    # Without personal memory, this is interpreted generically
    decision_1 = await agent.process_transcript(
        transcript="pls hlp me",
        stt_confidence=0.55,
    )
    assert decision_1.has_memory_match is False
    assert agent.state == AgentState.AWAITING_CONFIRMATION

    # 2. User submits explicit manual correction: "Please help me now"
    await memory_store.record_correction("pls hlp me", "Please help me now")
    agent.submit_correction("Please help me now")
    assert agent.state == AgentState.CONFIRMED

    # 3. Second Attempt: User says the same "pls hlp me" again with identical STT confidence
    agent.reset()
    decision_2 = await agent.process_transcript(
        transcript="pls hlp me",
        stt_confidence=0.55,
    )

    # 4. Invariant checks:
    # Memory must be detected
    assert decision_2.has_memory_match is True
    # The primary proposed phrase must be the user's previously corrected message
    assert decision_2.primary_phrase == "Please help me now"
    # Action must be upgraded to PROPOSE_PHRASE (HIGH confidence) due to memory bonus
    assert decision_2.action == AgentAction.PROPOSE_PHRASE
    assert decision_2.confidence_level == ConfidenceLevel.HIGH
    assert decision_2.overall_confidence >= 0.80

    # 5. User confirms the proposal
    ready_event = agent.confirm_proposal()
    assert ready_event.phrase == "Please help me now"
    assert ready_event.source == "proposal"


@pytest.mark.anyio
async def test_memory_match_does_not_override_inaudible_noise():
    """Verify safety guard: even with a memory store, inaudible noise cannot produce high confidence."""
    memory_store = MockMemoryStore()
    # Save a past correction for 'uh'
    await memory_store.record_correction("uh", "Hello")

    agent = PeexhAgent(memory_store=memory_store)
    decision = await agent.process_transcript(
        transcript="uh",
        stt_confidence=0.1,  # Below min_stt_confidence_for_high (0.50)
    )

    # Scorer safeguard: low STT acoustic confidence must prevent HIGH confidence proposal
    assert decision.action != AgentAction.PROPOSE_PHRASE
    assert decision.confidence_level != ConfidenceLevel.HIGH
