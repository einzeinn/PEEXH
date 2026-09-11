"""Unit tests for AssemblyAI v3 streaming transcriber adapter."""

import asyncio
import json
from unittest.mock import AsyncMock, patch
import pytest

from app.assemblyai.adapter import AssemblyAITranscriber
from app.models.speech import ErrorEvent, TranscriptEvent


class FakeAssemblyAIWebSocket:
    """Simulates AssemblyAI v3 Streaming WebSocket for testing."""

    def __init__(self, flush_on_terminate: bool = True):
        self.inbound_queue: asyncio.Queue = asyncio.Queue()
        self.sent_messages: list = []
        self.closed: bool = False
        self.flush_on_terminate: bool = flush_on_terminate

    async def recv(self) -> str:
        msg = await self.inbound_queue.get()
        return msg

    async def send(self, data) -> None:
        self.sent_messages.append(data)
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if parsed.get("type") == "Terminate" and self.flush_on_terminate:
                    # AssemblyAI v3 flushes remaining turn then sends Termination
                    await self.inbound_queue.put(
                        json.dumps({
                            "type": "Turn",
                            "transcript": "final flushed sentence",
                            "end_of_turn": True,
                            "confidence": 0.95,
                            "words": [{"text": "final"}, {"text": "flushed"}, {"text": "sentence"}],
                        })
                    )
                    await self.inbound_queue.put(
                        json.dumps({"type": "Termination"})
                    )
            except json.JSONDecodeError:
                pass

    async def close(self) -> None:
        self.closed = True


@pytest.mark.anyio
async def test_assemblyai_v3_lifecycle_with_graceful_flush():
    """Verify AssemblyAI v3 adapter receives Begin, Turns, and flushes final Turn on Terminate."""
    fake_ws = FakeAssemblyAIWebSocket(flush_on_terminate=True)
    transcripts: list[TranscriptEvent] = []
    errors: list[ErrorEvent] = []

    async def on_transcript(event: TranscriptEvent):
        transcripts.append(event)

    async def on_error(event: ErrorEvent):
        errors.append(event)

    adapter = AssemblyAITranscriber(api_key="test-api-key", sample_rate=16000)
    adapter.on_transcript(on_transcript)
    adapter.on_error(on_error)

    with patch("websockets.connect", new_callable=lambda: AsyncMock(return_value=fake_ws)):
        await adapter.start()

        # 1. Simulate Session Begin
        await fake_ws.inbound_queue.put(
            json.dumps({"type": "Begin", "id": "session-123"})
        )

        # 2. Simulate First Turn (partial then final)
        await fake_ws.inbound_queue.put(
            json.dumps({"type": "Turn", "transcript": "hello", "end_of_turn": False})
        )
        await fake_ws.inbound_queue.put(
            json.dumps({"type": "Turn", "transcript": "hello world", "end_of_turn": True, "confidence": 0.92})
        )

        # Give event loop a moment to process inbound queue
        await asyncio.sleep(0.05)

        # 3. Send audio chunk (raw PCM bytes)
        dummy_audio = b"\x00" * 3200
        await adapter.send_audio(dummy_audio)
        assert dummy_audio in fake_ws.sent_messages

        # 4. Stop session gracefully (triggers Terminate -> flush final Turn -> Termination)
        await adapter.stop()

    assert len(errors) == 0
    assert len(transcripts) == 3
    # Turn 1 partial
    assert transcripts[0].text == "hello"
    assert transcripts[0].is_final is False
    # Turn 1 final
    assert transcripts[1].text == "hello world"
    assert transcripts[1].is_final is True
    # Turn 2 final (flushed on Terminate)
    assert transcripts[2].text == "final flushed sentence"
    assert transcripts[2].is_final is True
    assert fake_ws.closed is True


@pytest.mark.anyio
async def test_assemblyai_v3_upstream_error_event():
    """Verify AssemblyAI upstream error is captured with ASSEMBLYAI_UPSTREAM_ERROR code."""
    fake_ws = FakeAssemblyAIWebSocket(flush_on_terminate=False)
    errors: list[ErrorEvent] = []

    async def on_error(event: ErrorEvent):
        errors.append(event)

    adapter = AssemblyAITranscriber(api_key="test-api-key", sample_rate=16000)
    adapter.on_error(on_error)

    with patch("websockets.connect", new_callable=lambda: AsyncMock(return_value=fake_ws)):
        await adapter.start()

        await fake_ws.inbound_queue.put(
            json.dumps({"type": "Error", "error": "Invalid audio encoding"})
        )
        await asyncio.sleep(0.05)

        await adapter.stop()

    assert len(errors) == 1
    assert errors[0].code == "ASSEMBLYAI_UPSTREAM_ERROR"
    assert "Invalid audio encoding" in errors[0].message


@pytest.mark.anyio
async def test_assemblyai_v3_stop_idempotent():
    """Verify multiple calls to stop() do not raise errors."""
    fake_ws = FakeAssemblyAIWebSocket(flush_on_terminate=False)
    adapter = AssemblyAITranscriber(api_key="test-api-key", sample_rate=16000)

    with patch("websockets.connect", new_callable=lambda: AsyncMock(return_value=fake_ws)):
        await adapter.start()
        await adapter.stop()
        # Second call should return immediately without error
        await adapter.stop()

    assert fake_ws.closed is True
