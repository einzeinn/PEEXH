"""Abstract base class for personal speech memory storage and retrieval."""

from abc import ABC, abstractmethod
from typing import List
from app.models.memory import MemoryMatch


class MemoryStore(ABC):
    """Abstract interface defining operations for speech memory retrieval and persistence."""

    @abstractmethod
    async def retrieve_matches(
        self,
        transcript: str,
        user_id: str = "default_user",
        limit: int = 3,
    ) -> List[MemoryMatch]:
        """Search memory for correction pairs matching or similar to the raw transcript."""
        pass

    @abstractmethod
    async def record_correction(
        self,
        raw_transcript: str,
        corrected_phrase: str,
        user_id: str = "default_user",
    ) -> None:
        """Persist or increment frequency for a user-verified correction pair."""
        pass

    @abstractmethod
    async def record_phrase_usage(
        self,
        phrase: str,
        user_id: str = "default_user",
    ) -> None:
        """Increment usage count and update last_used timestamp for a confirmed phrase."""
        pass

    @abstractmethod
    async def clear_memory(self, user_id: str = "default_user") -> None:
        """Erase stored speech memory for the specified user."""
        pass
