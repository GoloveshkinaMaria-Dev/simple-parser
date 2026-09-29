"""Fixtures for jobs integration tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.jobs.domain.entities import ParseJob
from src.jobs.infrastructure.repository import SqlJobRepository
from src.jobs.models import ParseJobORM


@pytest.fixture
def job() -> ParseJob:
    """Fresh ParseJob in PENDING status."""
    return ParseJob(id=1, text="python", area=1)


@pytest.fixture
async def engine():
    """Fresh engine with NullPool per test."""
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        poolclass=NullPool,   # ← отключает пул
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncSession:
    """Async session with cleanup."""
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
        await session.rollback()
        from sqlalchemy import delete
        await session.execute(delete(ParseJobORM))
        await session.commit()


@pytest.fixture
async def repo(session):
    from src.jobs.infrastructure.repository import SqlJobRepository
    return SqlJobRepository(session)