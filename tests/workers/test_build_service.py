from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from arq.connections import ArqRedis
from sqlalchemy.ext.asyncio import AsyncSession

from src.workers import tasks


@pytest.fixture
def fake_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def fake_redis() -> AsyncMock:
    return AsyncMock(spec=ArqRedis)


@pytest.fixture
def fake_ctx(fake_redis) -> MagicMock:
    ctx = MagicMock()
    ctx.__getitem__.side_effect = lambda key: {"redis": fake_redis}[key]
    return ctx


@pytest.fixture
def patch_session_local(fake_session):
    class FakeSessionLocal:
        def __call__(self):
            return self

        async def __aenter__(self):
            return fake_session

        async def __aexit__(self, *args):
            return False

    with patch.object(tasks, "SessionLocal", FakeSessionLocal()):
        yield fake_session


async def test_build_service_commits_on_success(fake_ctx, patch_session_local, fake_session):
    async with tasks.build_service(fake_ctx) as service:
        assert service is not None

    fake_session.commit.assert_awaited_once()
    fake_session.rollback.assert_not_awaited()


async def test_build_service_rollbacks_on_exception(fake_ctx, patch_session_local, fake_session):
    with pytest.raises(RuntimeError, match="boom"):
        async with tasks.build_service(fake_ctx):
            raise RuntimeError("boom")

    fake_session.rollback.assert_awaited_once()
    fake_session.commit.assert_not_awaited()


async def test_build_service_creates_redis_event_bus(fake_ctx, patch_session_local, fake_redis):
    with patch.object(tasks, "RedisEventBus") as mock_bus_cls:
        async with tasks.build_service(fake_ctx) as service:
            assert service is not None

    mock_bus_cls.assert_called_once_with(fake_redis)
