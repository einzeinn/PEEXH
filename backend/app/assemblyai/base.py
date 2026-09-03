"""Base abstract interface for speech transcribers."""

from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Optional

from app.models.speech import ErrorEvent, TranscriptEvent

TranscriptCallback = Callable[[TranscriptEvent], Awaitable[None]]
ErrorCallback = Callable[[ErrorEvent], Awaitable[None]]


class SpeechTranscriber(ABC):
    """Abstract base class for streaming speech-to-text transcribers."""

    def __init__(self) -> None:
        self._on_transcript: Optional[TranscriptCallback] = None
        self._on_error: Optional[ErrorCallback] = None

    def on_transcript(self, callback: TranscriptCallback) -> None:
        """Register callback invoked when a transcript event arrives."""
        self._on_transcript = callback

    def on_error(self, callback: ErrorCallback) -> None:
        """Register callback invoked when an error occurs."""
        self._on_error = callback

    @abstractmethod
    async def start(self) -> None:
        """Establish connection and start transcription session."""
        pass

    @abstractmethod
    async def send_audio(self, chunk: bytes) -> None:
        """Send a binary chunk of 16-bit PCM audio to the transcriber."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Signal that speech has ended and close session."""
        pass
