"""Fixtures for jobs integration tests."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config import settings
from src.database import get_session
from src.jobs.domain.entities import ParseJob
from src.jobs.infrastructure.repository import SqlJobRepository
from src.main import app


@pytest.fixture
def job() -> ParseJob:
    """Fresh ParseJob in PENDING status."""
    j = ParseJob(text="python", area=1)
    j.id = 1
    return j


@pytest_asyncio.fixture
async def engine():
    """Fresh engine with NullPool per test."""
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    """Async session with cleanup (TRUNCATE + RESTART IDENTITY)."""
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
        await s.rollback()

    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE parse_job RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> SqlJobRepository:
    return SqlJobRepository(session)


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """HTTP client с подменённой get_session."""

    async def override_get_session():
        yield session
        await session.commit()

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
