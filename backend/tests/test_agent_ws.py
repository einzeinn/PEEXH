"""Integration test verifying WebSocket emits agent_decision upon speech stop."""

import json
from fastapi.testclient import TestClient
from app.main import app


def test_speech_websocket_agent_decision_flow():
    """Verify WebSocket emits agent_decision event after final transcript."""
    client = TestClient(app)

    with client.websocket_connect("/ws/speech") as websocket:
        # 1. Start session
        websocket.send_text(json.dumps({"type": "start", "sample_rate": 16000}))
        data = websocket.receive_json()
        assert data["type"] == "session_started"

        # 2. Stream audio chunks to trigger mock speech
        dummy_chunk = b"\x00" * 3200
        for _ in range(8):
            websocket.send_bytes(dummy_chunk)

        # 3. Stop speech
        websocket.send_text(json.dumps({"type": "stop"}))

        # Collect events until we find agent_decision
        received_types = []
        agent_decision = None

        while True:
            try:
                event = websocket.receive_json()
                msg_type = event.get("type")
                received_types.append(msg_type)

                if msg_type == "agent_decision":
                    agent_decision = event
                    break
            except Exception:
                break

        assert "speech_stopped" in received_types
        assert agent_decision is not None
        assert agent_decision["type"] == "agent_decision"
        assert agent_decision["action"] == "PROPOSE_PHRASE"
        assert agent_decision["confidence_level"] == "HIGH"
        assert "water" in agent_decision["primary_phrase"].lower()
        assert len(agent_decision["candidates"]) >= 1
