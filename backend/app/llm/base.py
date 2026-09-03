"""Base abstract interface for speech interpretation providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.models.agent import InterpretationResult


class Interpreter(ABC):
    """Abstract base class for interpreting dysarthric speech transcripts into intended phrase candidates."""

    @abstractmethod
    async def interpret(
        self,
        transcript: str,
        stt_confidence: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> InterpretationResult:
        """Analyze a raw speech transcript and return candidate intended phrases with confidence."""
        pass
