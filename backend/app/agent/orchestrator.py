"""PEEXH agent orchestrator connecting transcription, interpretation, and scoring."""

import logging
from typing import Any, Dict, Optional

from app.agent.state import AgentState
from app.llm.base import Interpreter
from app.llm.factory import get_interpreter
from app.models.agent import AgentDecision, ConfidenceLevel
from app.scoring.scorer import ConfidenceScorer
from app.core.config import Settings, settings as default_settings

logger = logging.getLogger(__name__)


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
        )
        self._state: AgentState = AgentState.IDLE

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

        # 3. Transition based on outcome
        if decision.confidence_level in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM):
            self.set_state(AgentState.AWAITING_CONFIRMATION)
        else:
            self.set_state(AgentState.IDLE)

        return decision
