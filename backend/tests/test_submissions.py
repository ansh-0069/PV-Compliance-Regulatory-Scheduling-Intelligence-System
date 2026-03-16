"""Tests for Submission API endpoints."""

import uuid
from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


@pytest.mark.asyncio
async def test_create_and_list_submissions(client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
    """Test creating a submission and listing it back."""
    # First, create a product
    product = Product(
        name="TestDrug",
        active_substance="TestSubstance",
        mah="TestPharma",
        ibd=date(2020, 1, 1),
    )
    db_session.add(product)
    await db_session.flush()
    await db_session.refresh(product)

    # Create a submission
    response = await client.post(
        "/api/v1/submissions",
        json={
            "product_id": str(product.id),
            "type": "PSUR",
            "cycle": "PSUR-01",
            "data_lock_point": "2024-06-01",
            "submission_due": "2024-09-01",
            "authority": "EMA",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "PSUR"
    assert data["status"] == "Planned"

    # List submissions
    response = await client.get("/api/v1/submissions", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1


@pytest.mark.asyncio
async def test_generate_schedule(client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
    """Test auto-generating a submission schedule from IBD."""
    product = Product(
        name="ScheduleTestDrug",
        active_substance="TestMolecule",
        mah="TestMAH",
        ibd=date(2022, 3, 15),
    )
    db_session.add(product)
    await db_session.flush()
    await db_session.refresh(product)

    response = await client.post(
        "/api/v1/submissions/generate-schedule",
        json={
            "product_id": str(product.id),
            "type": "PSUR",
            "num_cycles": 3,
            "authority": "EMA",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 3
    assert data[0]["cycle"] == "PSUR-01"
