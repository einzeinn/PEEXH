"""In-memory mock implementation of MemoryStore for testing and offline development."""

from difflib import SequenceMatcher
from typing import Any, Dict, List
from app.memory.base import MemoryStore
from app.models.memory import MemoryMatch


class MockMemoryStore(MemoryStore):
    """In-memory speech memory store with fuzzy matching support."""

    def __init__(self) -> None:
        # user_id -> { raw_clean: {"original": raw, "corrected": phrase, "frequency": int} }
        self._corrections: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # user_id -> { phrase: int }
        self._frequencies: Dict[str, Dict[str, int]] = {}

    def _normalize(self, text: str) -> str:
        """Normalize text for consistent lookup."""
        return " ".join(text.lower().strip().split())

    async def retrieve_matches(
        self,
        transcript: str,
        user_id: str = "default_user",
        limit: int = 3,
    ) -> List[MemoryMatch]:
        """Find matching or similar past corrections for the given transcript."""
        clean_query = self._normalize(transcript)
        if not clean_query:
            return []

        user_corrections = self._corrections.get(user_id, {})
        matches: List[MemoryMatch] = []

        for clean_raw, data in user_corrections.items():
            # Exact match gives 1.0 similarity
            if clean_query == clean_raw:
                similarity = 1.0
            else:
                # Fuzzy similarity via SequenceMatcher
                similarity = round(
                    SequenceMatcher(None, clean_query, clean_raw).ratio(), 2
                )

            if similarity >= 0.60:
                matches.append(
                    MemoryMatch(
                        matched_phrase=data["corrected"],
                        original_transcript=data["original"],
                        similarity_score=similarity,
                        frequency=data["frequency"],
                        source="correction",
                    )
                )

        # Sort primarily by similarity score, secondarily by frequency
        matches.sort(key=lambda m: (m.similarity_score, m.frequency), reverse=True)
        return matches[:limit]

    async def record_correction(
        self,
        raw_transcript: str,
        corrected_phrase: str,
        user_id: str = "default_user",
    ) -> None:
        """Store or increment frequency for a correction pair."""
        clean_raw = self._normalize(raw_transcript)
        clean_corrected = corrected_phrase.strip()

        if not clean_raw or not clean_corrected:
            return

        if user_id not in self._corrections:
            self._corrections[user_id] = {}

        user_dict = self._corrections[user_id]
        if clean_raw in user_dict:
            user_dict[clean_raw]["frequency"] += 1
            user_dict[clean_raw]["corrected"] = clean_corrected
        else:
            user_dict[clean_raw] = {
                "original": raw_transcript.strip(),
                "corrected": clean_corrected,
                "frequency": 1,
            }

        # Also record phrase usage
        await self.record_phrase_usage(clean_corrected, user_id=user_id)

    async def record_phrase_usage(
        self,
        phrase: str,
        user_id: str = "default_user",
    ) -> None:
        """Increment the usage frequency for a confirmed phrase."""
        clean_phrase = phrase.strip()
        if not clean_phrase:
            return

        if user_id not in self._frequencies:
            self._frequencies[user_id] = {}

        self._frequencies[user_id][clean_phrase] = (
            self._frequencies[user_id].get(clean_phrase, 0) + 1
        )

    async def clear_memory(self, user_id: str = "default_user") -> None:
        """Clear all stored data for user."""
        self._corrections.pop(user_id, None)
        self._frequencies.pop(user_id, None)
