"""Tests for health and root endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check_endpoint(async_client: AsyncClient):
    """Test that the /health endpoint returns 200 and expected status."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "peexh"
    assert "environment" in data


@pytest.mark.anyio
async def test_root_endpoint(async_client: AsyncClient):
    """Test that the root / endpoint returns 200 and service information."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "peexh"
    assert data["docs_url"] == "/docs"
