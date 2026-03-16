"""Tests for QC check endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_qc_checks_empty(client: AsyncClient, auth_headers: dict):
    """Test listing QC checks when none exist."""
    response = await client.get("/api/v1/qc/results", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_qc_check_not_found(client: AsyncClient, auth_headers: dict):
    """Test fetching a non-existent QC check."""
    import uuid
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/qc/results/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
