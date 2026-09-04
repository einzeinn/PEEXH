"""PEEXH agent orchestrator connecting transcription, interpretation, and scoring."""

import logging
from typing import Any, Dict, Optional

from app.agent.state import AgentState
from app.llm.base import Interpreter
from app.llm.factory import get_interpreter
from app.models.agent import (
    AgentAction,
    AgentDecision,
    ConfidenceLevel,
    CommunicationReadyEvent,
    ConfirmedPhraseSource,
    RepeatRequestedEvent,
)
from app.scoring.scorer import ConfidenceScorer
from app.core.config import Settings, settings as default_settings

logger = logging.getLogger(__name__)


class InvalidStateError(Exception):
    """Raised when an action is attempted in an invalid agent state."""
    pass


class PeexhAgent:
    """Core agent orchestrator executing the Observe -> Interpret -> Score -> Decide loop."""

    def __init__(
        self,
        interpreter: Optional[Interpreter] = None,
        scorer: Optional[ConfidenceScorer] = None,
        config: Optional[Settings] = None,
    ) -> None:
        cfg = config or default_settings
        self.interpreter = interpreter or get_interpreter(cfg)
        self.scorer = scorer or ConfidenceScorer(
            high_threshold=cfg.PEEXH_HIGH_CONFIDENCE_THRESHOLD,
            low_threshold=cfg.PEEXH_LOW_CONFIDENCE_THRESHOLD,
            min_stt_confidence_for_high=cfg.PEEXH_MIN_STT_CONFIDENCE_FOR_HIGH,
        )
        self._state: AgentState = AgentState.IDLE
        self.active_decision: Optional[AgentDecision] = None

    @property
    def state(self) -> AgentState:
        """Return the current agent lifecycle state."""
        return self._state

    def set_state(self, new_state: AgentState) -> None:
        """Explicitly transition agent state."""
        logger.debug(f"PeexhAgent state transition: {self._state} -> {new_state}")
        self._state = new_state

    def reset(self) -> None:
        """Reset agent back to IDLE state."""
        self._state = AgentState.IDLE
        self.active_decision = None

    async def process_transcript(
        self,
        transcript: str,
        stt_confidence: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
        has_memory_match: bool = False,
    ) -> AgentDecision:
        """Execute interpretation and scoring on a final speech transcript."""
        # 1. Transition to INTERPRETING
        self.set_state(AgentState.INTERPRETING)
        interpretation = await self.interpreter.interpret(
            transcript=transcript,
            stt_confidence=stt_confidence,
            context=context,
        )

        # 2. Transition to DECIDING
        self.set_state(AgentState.DECIDING)
        decision = self.scorer.score_and_decide(
            interpretation=interpretation,
            has_memory_match=has_memory_match,
        )

        # 3. RFC-004 invariant: every agent_decision (HIGH, MEDIUM, or LOW) enters
        #    AWAITING_CONFIRMATION. Only the user's request_repeat WebSocket message
        #    may return the agent to IDLE from this state.
        self.active_decision = decision
        self.set_state(AgentState.AWAITING_CONFIRMATION)

        return decision

    def confirm_proposal(self) -> CommunicationReadyEvent:
        """Confirm the high-confidence primary proposed phrase."""
        if self._state != AgentState.AWAITING_CONFIRMATION:
            raise InvalidStateError("Cannot confirm proposal: agent is not in AWAITING_CONFIRMATION state")
        if not self.active_decision:
            raise InvalidStateError("No active decision available to confirm")
        if self.active_decision.action != AgentAction.PROPOSE_PHRASE:
            raise InvalidStateError(
                f"Cannot confirm proposal: active decision action is {self.active_decision.action}"
            )
        phrase = self.active_decision.primary_phrase or ""
        if not phrase:
            raise InvalidStateError("Active decision does not have a primary phrase to confirm")

        self.set_state(AgentState.CONFIRMED)
        self.active_decision = None
        return CommunicationReadyEvent(
            phrase=phrase,
            source=ConfirmedPhraseSource.PROPOSAL,
        )

    def select_candidate(self, phrase: str) -> CommunicationReadyEvent:
        """Select one candidate phrase from a candidate list decision."""
        if self._state != AgentState.AWAITING_CONFIRMATION:
            raise InvalidStateError("Cannot select candidate: agent is not in AWAITING_CONFIRMATION state")
        if not self.active_decision:
            raise InvalidStateError("No active decision available for candidate selection")
        if self.active_decision.action != AgentAction.SHOW_CANDIDATES:
            raise InvalidStateError(
                f"Cannot select candidate: active decision action is {self.active_decision.action}"
            )

        valid_candidate_texts = [c.text for c in self.active_decision.candidates]
        if phrase not in valid_candidate_texts:
            raise ValueError(
                f"Selected phrase '{phrase}' does not match any candidate: {valid_candidate_texts}"
            )

        self.set_state(AgentState.CONFIRMED)
        self.active_decision = None
        return CommunicationReadyEvent(
            phrase=phrase,
            source=ConfirmedPhraseSource.CANDIDATE,
        )

    def submit_correction(self, phrase: str) -> CommunicationReadyEvent:
        """Submit a user-provided correction for any active decision in AWAITING_CONFIRMATION."""
        if self._state != AgentState.AWAITING_CONFIRMATION:
            raise InvalidStateError("Cannot submit correction: agent is not in AWAITING_CONFIRMATION state")
        if not self.active_decision:
            raise InvalidStateError("No active decision available for correction")

        trimmed = phrase.strip()
        if not trimmed:
            raise ValueError("Correction phrase cannot be empty or whitespace only")
        if len(trimmed) > 500:
            raise ValueError("Correction phrase must not exceed 500 characters")

        self.set_state(AgentState.CONFIRMED)
        self.active_decision = None
        return CommunicationReadyEvent(
            phrase=trimmed,
            source=ConfirmedPhraseSource.CORRECTION,
        )

    def request_repeat(self) -> RepeatRequestedEvent:
        """Discard active decision and return agent to IDLE to allow the user to speak again."""
        if self._state != AgentState.AWAITING_CONFIRMATION:
            raise InvalidStateError("Cannot request repeat: agent is not in AWAITING_CONFIRMATION state")

        self.active_decision = None
        self.set_state(AgentState.IDLE)
        return RepeatRequestedEvent()
