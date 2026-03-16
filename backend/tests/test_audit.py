"""Tests for Audit Readiness endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_score_empty(client: AsyncClient, auth_headers: dict):
    """Test fetching score when no scores exist yet."""
    response = await client.get("/api/v1/audit/score", headers=auth_headers)
    assert response.status_code == 200
    # No score yet — returns null
    assert response.json() is None


@pytest.mark.asyncio
async def test_recalculate_score(client: AsyncClient, auth_headers: dict):
    """Test triggering audit score recalculation."""
    response = await client.post("/api/v1/audit/score/recalculate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert data["score"]["overall_score"] >= 0
