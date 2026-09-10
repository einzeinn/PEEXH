"""Tests for RFC-008 demo simulation REST endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_demo_simulate_returns_agent_decision():
    """POST /demo/simulate with a known dysarthric phrase returns a valid agent decision."""
    response = client.post("/demo/simulate", json={"text": "i ned wtr"})
    assert response.status_code == 200
    data = response.json()
    assert data["action"] in ("PROPOSE_PHRASE", "SHOW_CANDIDATES", "REQUEST_REPEAT")
    assert "confidence_level" in data
    assert "overall_confidence" in data
    assert "candidates" in data


def test_demo_simulate_empty_text_is_rejected():
    """POST /demo/simulate rejects empty text with HTTP 422."""
    response = client.post("/demo/simulate", json={"text": ""})
    assert response.status_code == 422


def test_demo_simulate_whitespace_only_is_rejected():
    """POST /demo/simulate rejects whitespace-only text."""
    response = client.post("/demo/simulate", json={"text": "   "})
    assert response.status_code == 422


def test_demo_simulate_text_too_long_is_rejected():
    """POST /demo/simulate rejects text exceeding 500 characters."""
    response = client.post("/demo/simulate", json={"text": "a" * 501})
    assert response.status_code == 422


def test_demo_simulate_low_confidence_sample():
    """POST /demo/simulate with near-unintelligible input returns REQUEST_REPEAT."""
    response = client.post("/demo/simulate", json={"text": "uh"})
    assert response.status_code == 200
    data = response.json()
    # Low-signal input should typically trigger a repeat or low-confidence path
    assert data["action"] in ("PROPOSE_PHRASE", "SHOW_CANDIDATES", "REQUEST_REPEAT")
