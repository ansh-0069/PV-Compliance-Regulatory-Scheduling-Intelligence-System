"""Tests for CAPA lifecycle endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_capa_lifecycle(client: AsyncClient, auth_headers: dict):
    """Test full CAPA lifecycle: create → investigate → corrective → verify → close."""
    # Create CAPA
    response = await client.post(
        "/api/v1/capas",
        json={
            "title": "Test CAPA",
            "description": "Quality incident for testing",
            "priority": "High",
            "owner": "Test Admin",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    capa = response.json()
    capa_id = capa["id"]
    assert capa["status"] == "Open"

    # Transition: Open → Investigation
    response = await client.patch(
        f"/api/v1/capas/{capa_id}/transition",
        json={"to_status": "Investigation", "changed_by": "Test Admin", "comment": "Starting RCA"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Investigation"

    # Transition: Investigation → Corrective Action
    response = await client.patch(
        f"/api/v1/capas/{capa_id}/transition",
        json={"to_status": "Corrective Action", "changed_by": "Test Admin", "comment": "Root cause found"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Corrective Action"

    # Add action
    response = await client.post(
        f"/api/v1/capas/{capa_id}/actions",
        json={
            "action_type": "Corrective",
            "description": "Fix the process",
            "assignee": "Test Admin",
            "due_date": "2025-12-31",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201

    # Transition: Corrective Action → Verification
    response = await client.patch(
        f"/api/v1/capas/{capa_id}/transition",
        json={"to_status": "Verification", "changed_by": "Test Admin"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Transition: Verification → Closed
    response = await client.patch(
        f"/api/v1/capas/{capa_id}/transition",
        json={"to_status": "Closed", "changed_by": "Test Admin", "comment": "Effectiveness confirmed"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Closed"

    # Check audit trail
    response = await client.get(f"/api/v1/capas/{capa_id}/history", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 5  # initial + 4 transitions


@pytest.mark.asyncio
async def test_invalid_capa_transition(client: AsyncClient, auth_headers: dict):
    """Test that invalid state transitions are rejected."""
    response = await client.post(
        "/api/v1/capas",
        json={"title": "Invalid CAPA", "description": "test", "priority": "Low", "owner": "Test"},
        headers=auth_headers,
    )
    capa_id = response.json()["id"]

    # Try invalid: Open → Closed (must go through full lifecycle)
    response = await client.patch(
        f"/api/v1/capas/{capa_id}/transition",
        json={"to_status": "Closed", "changed_by": "Test"},
        headers=auth_headers,
    )
    assert response.status_code == 422
