from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from arq.connections import ArqRedis

from src.workers import tasks


@pytest.fixture
def fake_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.__getitem__.side_effect = lambda key: {
        "redis": AsyncMock(spec=ArqRedis),
    }[key]
    return ctx


@pytest.fixture
def fake_service() -> AsyncMock:
    service = AsyncMock()
    service.run = AsyncMock()
    return service


@pytest.fixture
def patch_build_service(fake_service: AsyncMock):
    @asynccontextmanager
    async def fake_build_service(ctx):
        yield fake_service

    with patch.object(tasks, "build_service", fake_build_service):
        yield fake_service


async def test_task_calls_service_run_with_job_id(fake_ctx, patch_build_service):
    await tasks.parse_job_task(fake_ctx, job_id=42)

    patch_build_service.run.assert_awaited_once_with(42)


async def test_task_returns_none_on_success(fake_ctx, patch_build_service):
    result = await tasks.parse_job_task(fake_ctx, job_id=42)

    assert result is None


async def test_task_propagates_unexpected_exception(fake_ctx, patch_build_service, caplog):
    patch_build_service.run.side_effect = RuntimeError("db is down")

    with pytest.raises(RuntimeError, match="db is down"):
        await tasks.parse_job_task(fake_ctx, job_id=42)


async def test_task_logs_exception(fake_ctx, patch_build_service, caplog):
    patch_build_service.run.side_effect = RuntimeError("db is down")

    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError):
            await tasks.parse_job_task(fake_ctx, job_id=42)

    assert any("42" in r.message for r in caplog.records)


async def test_task_logs_start_and_finish(fake_ctx, patch_build_service, caplog):
    with caplog.at_level("INFO"):
        await tasks.parse_job_task(fake_ctx, job_id=42)

    messages = [r.message for r in caplog.records]
    assert any("started" in m and "42" in m for m in messages)
    assert any("finished" in m and "42" in m for m in messages)
