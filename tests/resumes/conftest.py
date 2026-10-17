"""Fixtures for resumes repository tests."""

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config import settings
from src.parser.domain.entities import Resume
from src.resumes.infrastructure.repository import SqlResumeRepository


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

    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE resume_skill RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE resume RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE parse_job RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> SqlResumeRepository:
    return SqlResumeRepository(session)

@pytest_asyncio.fixture
async def job_id(session: AsyncSession) -> int:
    from src.jobs.models import ParseJobORM

    orm = ParseJobORM(
        text="python",
        area=1,
        status="pending",
        items_count=0,
        per_page=20,
        max_pages=5,
    )
    session.add(orm)
    await session.flush()
    return orm.id