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

