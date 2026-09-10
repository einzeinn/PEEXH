"""Data models and loader for dysarthric speech evaluation dataset."""

import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


class EvaluationSample(BaseModel):
    """Represents a single evaluated dysarthric speech utterance sample."""
    id: str
    dysarthria_type: str = Field(description="spastic | flaccid | ataxic | mixed")
    raw_stt_transcript: str
    intended_phrase: str
    stt_confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""


def get_default_dataset_path() -> Path:
    """Return default absolute path to samples.json."""
    return Path(__file__).resolve().parent / "samples.json"


def load_samples(filepath: str | Path | None = None) -> List[EvaluationSample]:
    """Load and validate evaluation samples from a JSON file."""
    target_path = Path(filepath) if filepath else get_default_dataset_path()
    if not target_path.is_file():
        raise FileNotFoundError(f"Evaluation dataset file not found: {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Dataset JSON root must be a list of sample objects.")

    return [EvaluationSample(**item) for item in data]
