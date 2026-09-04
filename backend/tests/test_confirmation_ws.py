"""Integration tests for WebSocket confirmation control loop (RFC-004)."""

import json
from fastapi.testclient import TestClient
from app.main import app


def _reach_agent_decision(websocket):
    """Helper to start session, send audio, stop, and consume up to agent_decision."""
    websocket.send_text(json.dumps({"type": "start", "sample_rate": 16000}))
    started = websocket.receive_json()
    assert started["type"] == "session_started"

    # Send dummy audio to trigger transcript
    dummy_chunk = b"\x00" * 3200
    for _ in range(8):
        websocket.send_bytes(dummy_chunk)

    # Stop session
    websocket.send_text(json.dumps({"type": "stop"}))

    agent_decision = None
    while True:
        event = websocket.receive_json()
        if event.get("type") == "agent_decision":
            agent_decision = event
            break

    return agent_decision


def test_ws_confirm_proposal_flow():
    """Verify confirm_proposal produces communication_ready event."""
    client = TestClient(app)

    with client.websocket_connect("/ws/speech") as websocket:
        decision = _reach_agent_decision(websocket)
        assert decision["action"] == "PROPOSE_PHRASE"

        # Send confirm_proposal
        websocket.send_text(json.dumps({"type": "confirm_proposal"}))
        response = websocket.receive_json()

        assert response["type"] == "communication_ready"
        assert response["phrase"] == decision["primary_phrase"]
        assert response["source"] == "proposal"


def test_ws_submit_correction_flow():
    """Verify submit_correction produces communication_ready with correction source."""
    client = TestClient(app)

    with client.websocket_connect("/ws/speech") as websocket:
        _ = _reach_agent_decision(websocket)

        # Send submit_correction
        websocket.send_text(json.dumps({
            "type": "submit_correction",
            "phrase": "  I would like some tea please  "
        }))
        response = websocket.receive_json()

        assert response["type"] == "communication_ready"
        assert response["phrase"] == "I would like some tea please"
        assert response["source"] == "correction"


def test_ws_request_repeat_flow():
    """Verify request_repeat produces repeat_requested event."""
    client = TestClient(app)

    with client.websocket_connect("/ws/speech") as websocket:
        _ = _reach_agent_decision(websocket)

        # Send request_repeat
        websocket.send_text(json.dumps({"type": "request_repeat"}))
        response = websocket.receive_json()

        assert response["type"] == "repeat_requested"


def test_ws_confirm_in_invalid_state_returns_error():
    """Sending confirm_proposal before stop/decision returns INVALID_AGENT_STATE error."""
    client = TestClient(app)

    with client.websocket_connect("/ws/speech") as websocket:
        websocket.send_text(json.dumps({"type": "start", "sample_rate": 16000}))
        _ = websocket.receive_json()

        # Send confirm_proposal while agent is still in IDLE/LISTENING
        websocket.send_text(json.dumps({"type": "confirm_proposal"}))
        response = websocket.receive_json()

        assert response["type"] == "error"
        assert response["code"] == "INVALID_AGENT_STATE"


def test_ws_submit_empty_correction_returns_error():
    """Submitting empty whitespace correction returns INVALID_CONTROL_MESSAGE error."""
    client = TestClient(app)

    with client.websocket_connect("/ws/speech") as websocket:
        _ = _reach_agent_decision(websocket)

        websocket.send_text(json.dumps({
            "type": "submit_correction",
            "phrase": "   "
        }))
        response = websocket.receive_json()

        assert response["type"] == "error"
        assert response["code"] == "INVALID_CONTROL_MESSAGE"
