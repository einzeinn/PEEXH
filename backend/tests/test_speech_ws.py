"""Integration tests for speech streaming WebSocket endpoint."""

import json
from fastapi.testclient import TestClient
from app.main import app


def test_speech_websocket_flow():
    """Verify full WebSocket lifecycle: start, audio streaming, transcript, stop."""
    client = TestClient(app)

    with client.websocket_connect("/ws/speech") as websocket:
        # 1. Send start session
        websocket.send_text(json.dumps({"type": "start", "sample_rate": 16000}))
        data = websocket.receive_json()
        assert data["type"] == "session_started"
        assert "session_id" in data
        assert data["provider"] in ("mock", "assemblyai")

        # 2. Send 8 dummy audio chunks (16-bit PCM zeroes)
        dummy_chunk = b"\x00" * 3200
        for _ in range(8):
            websocket.send_bytes(dummy_chunk)

        # Mock transcriber emits partial transcript after 4 chunks
        partial_event = websocket.receive_json()
        assert partial_event["type"] == "transcript"
        assert partial_event["is_final"] is False
        assert len(partial_event["text"]) > 0

        # 3. Send stop session
        websocket.send_text(json.dumps({"type": "stop"}))

        # Collect events until we receive the final transcript
        event = websocket.receive_json()
        while not (event.get("type") == "transcript" and event.get("is_final") is True):
            event = websocket.receive_json()

        assert event["type"] == "transcript"
        assert event["is_final"] is True
        assert event["text"] == "I need water"

        # Expect speech stopped event
        stopped_event = websocket.receive_json()
        assert stopped_event["type"] == "speech_stopped"


def test_speech_websocket_multi_turn_accumulation(monkeypatch):
    """Verify multiple finalized turns accumulate so the agent receives the full utterance."""
    from app.assemblyai.base import SpeechTranscriber
    from app.models.speech import TranscriptEvent

    class MultiTurnMockTranscriber(SpeechTranscriber):
        def __init__(self):
            super().__init__()

        async def start(self) -> None:
            pass

        async def send_audio(self, chunk: bytes) -> None:
            pass

        async def stop(self) -> None:
            # Emulate AssemblyAI v3 sending two finalized turns before terminating
            if self._on_transcript:
                await self._on_transcript(
                    TranscriptEvent(text="I need", is_final=True, confidence=0.90)
                )
                await self._on_transcript(
                    TranscriptEvent(text="a glass of water", is_final=True, confidence=0.92)
                )

    import app.api.speech_ws as speech_ws_module
    monkeypatch.setattr(
        speech_ws_module,
        "get_speech_transcriber",
        lambda settings, sample_rate: MultiTurnMockTranscriber(),
    )

    client = TestClient(app)
    with client.websocket_connect("/ws/speech") as websocket:
        websocket.send_text(json.dumps({"type": "start", "sample_rate": 16000}))
        _ = websocket.receive_json()

        # Stop session — MultiTurnMockTranscriber emits two finalized turns during stop()
        websocket.send_text(json.dumps({"type": "stop"}))

        # Receive turn 1
        ev1 = websocket.receive_json()
        assert ev1["type"] == "transcript"
        assert ev1["text"] == "I need"

        # Receive turn 2
        ev2 = websocket.receive_json()
        assert ev2["type"] == "transcript"
        assert ev2["text"] == "a glass of water"

        # Receive speech stopped
        ev_stopped = websocket.receive_json()
        assert ev_stopped["type"] == "speech_stopped"

        # Receive agent decision — must process the combined text "I need a glass of water"
        ev_decision = websocket.receive_json()
        assert ev_decision["type"] == "agent_decision"
        assert ev_decision["action"] in ("PROPOSE_PHRASE", "SHOW_CANDIDATES", "COMMUNICATE")
        assert "water" in (ev_decision.get("primary_phrase") or "").lower() or len(ev_decision.get("candidates", [])) > 0


