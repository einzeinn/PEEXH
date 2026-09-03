"""Unit tests for speech transcriber interface and mock implementation."""

import pytest
from app.assemblyai.mock import MockSpeechTranscriber
from app.models.speech import TranscriptEvent


@pytest.mark.anyio
async def test_mock_transcriber_lifecycle():
    """Test MockSpeechTranscriber emits partial and final events properly."""
    transcripts = []

    async def on_transcript(event: TranscriptEvent):
        transcripts.append(event)

    transcriber = MockSpeechTranscriber(simulated_text="Hello world", confidence=0.9)
    transcriber.on_transcript(on_transcript)

    await transcriber.start()

    # Send 8 audio chunks to trigger 2 partial transcripts
    dummy_chunk = b"\x00" * 3200
    for _ in range(8):
        await transcriber.send_audio(dummy_chunk)

    assert len(transcripts) >= 1
    assert transcripts[0].is_final is False

    # Stop transcriber to trigger final transcript
    await transcriber.stop()

    assert len(transcripts) >= 2
    final_event = transcripts[-1]
    assert final_event.is_final is True
    assert final_event.text == "Hello world"
    assert final_event.confidence == 0.9
