"""Supabase PostgreSQL adapter for personal speech memory persistence."""

import logging
from typing import List, Optional
import httpx

from app.memory.base import MemoryStore
from app.memory.mock import MockMemoryStore
from app.models.memory import MemoryMatch

logger = logging.getLogger(__name__)


class SupabaseMemoryStore(MemoryStore):
    """Production memory store persisting to Supabase via PostgREST with in-memory fallback."""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        timeout: float = 3.0,
    ) -> None:
        self.supabase_url = supabase_url.rstrip("/") if supabase_url else ""
        self.supabase_key = supabase_key or ""
        self.timeout = timeout
        self._fallback_store = MockMemoryStore()

    def _headers(self) -> dict:
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def retrieve_matches(
        self,
        transcript: str,
        user_id: str = "default_user",
        limit: int = 3,
    ) -> List[MemoryMatch]:
        """Search Supabase for matching speech corrections with fallback to mock."""
        if not self.supabase_url or not self.supabase_key:
            return await self._fallback_store.retrieve_matches(
                transcript, user_id=user_id, limit=limit
            )

        clean_transcript = transcript.strip()
        if not clean_transcript:
            return []

        try:
            url = f"{self.supabase_url}/rest/v1/speech_corrections"
            # Query by user_id and matching raw_transcript
            params = {
                "user_id": f"eq.{user_id}",
                "raw_transcript": f"ilike.*{clean_transcript}*",
                "order": "frequency.desc",
                "limit": str(limit),
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self._headers(), params=params)
                if resp.status_code == 200:
                    rows = resp.json()
                    matches: List[MemoryMatch] = []
                    for row in rows:
                        matches.append(
                            MemoryMatch(
                                matched_phrase=row.get("corrected_phrase", ""),
                                original_transcript=row.get("raw_transcript", ""),
                                similarity_score=0.90,
                                frequency=row.get("frequency", 1),
                                source="correction",
                            )
                        )
                    if matches:
                        return matches
        except Exception as exc:
            logger.warning(
                f"Supabase memory search failed ({exc}), falling back to local memory"
            )

        return await self._fallback_store.retrieve_matches(
            transcript, user_id=user_id, limit=limit
        )

    async def record_correction(
        self,
        raw_transcript: str,
        corrected_phrase: str,
        user_id: str = "default_user",
    ) -> None:
        """Persist or increment a correction pair in Supabase and local fallback."""
        # Always update fallback store so local session reflects it immediately
        await self._fallback_store.record_correction(
            raw_transcript, corrected_phrase, user_id=user_id
        )

        if not self.supabase_url or not self.supabase_key:
            return

        clean_raw = raw_transcript.strip()
        clean_corrected = corrected_phrase.strip()
        if not clean_raw or not clean_corrected:
            return

        try:
            url = f"{self.supabase_url}/rest/v1/speech_corrections"
            payload = {
                "user_id": user_id,
                "raw_transcript": clean_raw,
                "corrected_phrase": clean_corrected,
                "frequency": 1,
            }
            headers = self._headers()
            headers["Prefer"] = "resolution=merge-duplicates"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await client.post(url, headers=headers, json=payload)
        except Exception as exc:
            logger.warning(f"Failed to persist correction to Supabase: {exc}")

    async def record_phrase_usage(
        self,
        phrase: str,
        user_id: str = "default_user",
    ) -> None:
        """Track confirmed phrase usage in Supabase."""
        await self._fallback_store.record_phrase_usage(phrase, user_id=user_id)

        if not self.supabase_url or not self.supabase_key:
            return

        clean_phrase = phrase.strip()
        if not clean_phrase:
            return

        try:
            url = f"{self.supabase_url}/rest/v1/phrase_frequencies"
            payload = {
                "user_id": user_id,
                "phrase": clean_phrase,
                "use_count": 1,
            }
            headers = self._headers()
            headers["Prefer"] = "resolution=merge-duplicates"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await client.post(url, headers=headers, json=payload)
        except Exception as exc:
            logger.warning(f"Failed to record phrase usage in Supabase: {exc}")

    async def clear_memory(self, user_id: str = "default_user") -> None:
        """Clear memory in Supabase and fallback."""
        await self._fallback_store.clear_memory(user_id=user_id)

        if not self.supabase_url or not self.supabase_key:
            return

        try:
            headers = self._headers()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                await client.delete(
                    f"{self.supabase_url}/rest/v1/speech_corrections?user_id=eq.{user_id}",
                    headers=headers,
                )
                await client.delete(
                    f"{self.supabase_url}/rest/v1/phrase_frequencies?user_id=eq.{user_id}",
                    headers=headers,
                )
        except Exception as exc:
            logger.warning(f"Failed to clear memory in Supabase: {exc}")
