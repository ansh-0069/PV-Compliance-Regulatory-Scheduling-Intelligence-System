"""Pytest fixtures and test configuration."""

import asyncio
import uuid
from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.security import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.user import User

# Use a separate test database or in-memory SQLite
TEST_DB_URL = settings.DATABASE_URL

test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Provide a transactional test database session."""
    async with test_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    """Provide an async HTTP test client with DB override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create and return a test user with Admin role."""
    user = User(
        id=uuid.uuid4(),
        email="test@pvcompli.com",
        full_name="Test Admin",
        role="Admin",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Return Authorization headers for the test user."""
    from app.core.security import create_access_token
    token = create_access_token(str(test_user.id), {"role": test_user.role})
    return {"Authorization": f"Bearer {token}"}
