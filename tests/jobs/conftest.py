"""Fixtures for jobs integration tests."""

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

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
from src.jobs.dependencies import get_arq_pool
from src.jobs.domain.entities import ParseJob
from src.jobs.infrastructure.repository import SqlJobRepository
from src.main import app


@pytest.fixture
def job() -> ParseJob:
    j = ParseJob(text="python", area=1)
    j.id = 1
    return j


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
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
async def fake_arq() -> AsyncMock:   
    pool = AsyncMock()
    pool.enqueue_job = AsyncMock(return_value=None)
    return pool


@pytest_asyncio.fixture
async def client(
    session: AsyncSession,
    fake_arq: AsyncMock,      
) -> AsyncIterator[AsyncClient]:

    async def override_get_session():
        yield session
        await session.commit()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_arq_pool] = lambda: fake_arq 

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()