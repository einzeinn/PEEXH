"""Tests for speech transcriber factory."""

from app.assemblyai.adapter import AssemblyAITranscriber
from app.assemblyai.factory import get_speech_transcriber
from app.assemblyai.mock import MockSpeechTranscriber
from app.core.config import Settings


def test_factory_returns_mock_when_no_api_key():
    """Verify factory falls back to MockSpeechTranscriber when key is absent."""
    test_settings = Settings(ASSEMBLYAI_API_KEY="")
    transcriber = get_speech_transcriber(test_settings)
    assert isinstance(transcriber, MockSpeechTranscriber)


def test_factory_returns_adapter_when_key_present():
    """Verify factory instantiates AssemblyAITranscriber when key is provided."""
    test_settings = Settings(ASSEMBLYAI_API_KEY="dummy-assemblyai-key")
    transcriber = get_speech_transcriber(test_settings)
    assert isinstance(transcriber, AssemblyAITranscriber)
    assert transcriber.api_key == "dummy-assemblyai-key"
