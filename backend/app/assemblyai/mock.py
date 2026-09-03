"""Mock speech transcriber for local testing, offline development, and CI."""

import asyncio
from typing import List, Optional

from app.assemblyai.base import SpeechTranscriber
from app.models.speech import TranscriptEvent, TranscriptWord


class MockSpeechTranscriber(SpeechTranscriber):
    """Simulated transcriber emitting realistic transcripts without external API."""

    def __init__(
        self,
        simulated_text: str = "I need water",
        confidence: float = 0.88,
    ) -> None:
        super().__init__()
        self.simulated_text = simulated_text
        self.confidence = confidence
        self._is_active = False
        self._audio_chunk_count = 0
        self._words: List[str] = simulated_text.split()
        self._current_word_idx = 0

    async def start(self) -> None:
        """Start the mock transcription session."""
        self._is_active = True
        self._audio_chunk_count = 0
        self._current_word_idx = 0

    async def send_audio(self, chunk: bytes) -> None:
        """Receive audio chunk and emit partial transcript periodically."""
        if not self._is_active:
            return

        self._audio_chunk_count += 1

        # Emit progressive partial transcript every 4 audio chunks
        if self._audio_chunk_count % 4 == 0 and self._current_word_idx < len(self._words):
            self._current_word_idx += 1
            partial_text = " ".join(self._words[: self._current_word_idx])
            if self._on_transcript:
                words = [
                    TranscriptWord(text=w, confidence=self.confidence)
                    for w in self._words[: self._current_word_idx]
                ]
                await self._on_transcript(
                    TranscriptEvent(
                        text=partial_text,
                        is_final=False,
                        confidence=self.confidence,
                        words=words,
                    )
                )

    async def stop(self) -> None:
        """Finalize the transcription and emit the final transcript event."""
        if not self._is_active:
            return

        self._is_active = False

        # Emit final transcript
        if self._on_transcript:
            words = [
                TranscriptWord(text=w, confidence=self.confidence)
                for w in self._words
            ]
            await self._on_transcript(
                TranscriptEvent(
                    text=self.simulated_text,
                    is_final=True,
                    confidence=self.confidence,
                    words=words,
                )
            )
