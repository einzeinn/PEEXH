"""Factory for instantiating appropriate speech transcriber based on settings."""

import logging
from app.assemblyai.adapter import AssemblyAITranscriber
from app.assemblyai.base import SpeechTranscriber
from app.assemblyai.mock import MockSpeechTranscriber
from app.core.config import Settings

logger = logging.getLogger(__name__)


def get_speech_transcriber(
    settings: Settings, sample_rate: int = 16000
) -> SpeechTranscriber:
    """Instantiate and return configured speech transcriber.

    If ASSEMBLYAI_API_KEY is configured, returns AssemblyAITranscriber.
    Otherwise, returns MockSpeechTranscriber for local development and testing.
    """
    if settings.ASSEMBLYAI_API_KEY and settings.ASSEMBLYAI_API_KEY.strip():
        logger.info("Initializing AssemblyAITranscriber with live credentials")
        return AssemblyAITranscriber(
            api_key=settings.ASSEMBLYAI_API_KEY.strip(),
            sample_rate=sample_rate,
        )

    logger.info("Initializing MockSpeechTranscriber (no AssemblyAI key found)")
    return MockSpeechTranscriber()
