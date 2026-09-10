"""Domain models for personal speech memory and adaptive learning (RFC-005)."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CorrectionRecord(BaseModel):
    """A verified association between a raw STT transcript and the intended phrase."""

    id: Optional[str] = None
    user_id: str = "default_user"
    raw_transcript: str
    corrected_phrase: str
    frequency: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MemoryMatch(BaseModel):
    """A retrieved historical memory candidate relevant to the active utterance."""

    matched_phrase: str
    original_transcript: str
    similarity_score: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency: int = 1
    source: str = "correction"  # "correction" | "frequent_phrase"


class MemoryContext(BaseModel):
    """Container for memory matches passed into interpretation and scoring."""

    matches: List[MemoryMatch] = Field(default_factory=list)
    has_match: bool = False
