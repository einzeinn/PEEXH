"""Unit tests for speech interpreters and factory."""

import pytest
from app.core.config import Settings
from app.llm.adapter import CloudLLMInterpreter
from app.llm.factory import get_interpreter
from app.llm.mock import MockInterpreter


@pytest.mark.anyio
async def test_mock_interpreter_known_pattern():
    """Verify MockInterpreter correctly identifies known dysarthric keywords."""
    interp = MockInterpreter()
    result = await interp.interpret(transcript="need water", stt_confidence=0.8)

    assert result.raw_transcript == "need water"
    assert len(result.candidates) >= 1
    assert "water" in result.candidates[0].text.lower()
    assert result.candidates[0].confidence >= 0.85


@pytest.mark.anyio
async def test_mock_interpreter_low_confidence_fallback():
    """Verify MockInterpreter produces low confidence for incomprehensible noise."""
    interp = MockInterpreter()
    result = await interp.interpret(transcript="uh", stt_confidence=0.2)

    assert len(result.candidates) == 1
    assert result.candidates[0].confidence <= 0.35


def test_interpreter_factory_selection():
    """Verify get_interpreter selects CloudLLMInterpreter only when API key is set."""
    no_key_settings = Settings(LLM_API_KEY="")
    assert isinstance(get_interpreter(no_key_settings), MockInterpreter)

    with_key_settings = Settings(LLM_API_KEY="sk-test-12345")
    interpreter = get_interpreter(with_key_settings)
    assert isinstance(interpreter, CloudLLMInterpreter)
    assert interpreter.api_key == "sk-test-12345"
