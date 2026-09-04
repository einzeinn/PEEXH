"""Pytest fixtures for PEEXH backend tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch

from app.main import app


@pytest.fixture(scope="session", autouse=True)
def use_mock_transcriber():
    """Force MockTranscriber for all tests by clearing the AssemblyAI API key.

    This prevents tests from attempting real network connections to AssemblyAI
    regardless of what is set in the local .env file.
    """
    with patch("app.core.config.settings.ASSEMBLYAI_API_KEY", ""):
        yield


@pytest.fixture
async def async_client():
    """Fixture providing an async HTTP client connected to the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
