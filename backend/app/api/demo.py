"""Demo simulation REST endpoint for RFC-008 microphone-free testing.

Accepts a raw distorted text string, runs it through the full PEEXH agent
pipeline (interpret → score → decide), and returns the agent decision.

This endpoint enables judges and evaluators to test the PEEXH interpretation
stack without requiring microphone access or live AssemblyAI credentials.
No audio is captured or stored.
"""

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

from app.agent.orchestrator import PeexhAgent
from app.core.config import settings

router = APIRouter(prefix="/demo", tags=["demo"])


class DemoSimulateRequest(BaseModel):
    """Payload for a demo speech simulation request."""

    text: str
    """Raw distorted utterance text (e.g. 'i ned wtr')."""

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("text must not be empty")
        if len(stripped) > 500:
            raise ValueError("text must not exceed 500 characters")
        return stripped


@router.post("/simulate")
async def demo_simulate(request: DemoSimulateRequest):
    """Run a raw text string through the PEEXH agent pipeline and return the decision.

    This endpoint is intended for demo and evaluation purposes only.
    No audio is recorded, transmitted, or stored.
    """
    agent = PeexhAgent(config=settings)
    decision = await agent.process_transcript(
        transcript=request.text,
        stt_confidence=0.72,  # Simulated mid-range STT acoustic confidence
    )
    return decision.model_dump()
