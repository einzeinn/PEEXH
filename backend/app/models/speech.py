"""Domain and protocol models for realtime speech streaming."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# --- Client to Server Control Messages ---

class StartSessionMessage(BaseModel):
    """Client request to initialize a speech transcription session."""
    type: Literal["start"] = "start"
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")


class StopSessionMessage(BaseModel):
    """Client notification that user stopped speaking."""
    type: Literal["stop"] = "stop"


# --- Server to Client Event Messages ---

class SessionStartedEvent(BaseModel):
    """Notification that transcription session has been established."""
    type: Literal["session_started"] = "session_started"
    session_id: str
    provider: str


class TranscriptWord(BaseModel):
    """Individual word timing and confidence within a transcript."""
    text: str
    start: Optional[int] = None
    end: Optional[int] = None
    confidence: Optional[float] = None


class TranscriptEvent(BaseModel):
    """Realtime speech transcription event (partial or final)."""
    type: Literal["transcript"] = "transcript"
    text: str
    is_final: bool = False
    confidence: float = 0.0
    words: List[TranscriptWord] = Field(default_factory=list)


class SpeechStoppedEvent(BaseModel):
    """Notification confirming speech session has ended."""
    type: Literal["speech_stopped"] = "speech_stopped"


class ErrorEvent(BaseModel):
    """Error notification sent to client."""
    type: Literal["error"] = "error"
    message: str
    code: str = "STREAMING_ERROR"
