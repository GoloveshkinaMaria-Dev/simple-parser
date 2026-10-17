import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from src.database import SessionLocal
from src.jobs.infrastructure.bus import RedisEventBus
from src.jobs.infrastructure.repository import SqlJobRepository
from src.jobs.service import ParseJobService, ParserService
from src.resumes.infrastructure.repository import SqlResumeRepository

logger = logging.getLogger(__name__)


@asynccontextmanager
async def build_service(ctx) -> AsyncIterator[ParseJobService]:
    async with SessionLocal() as session:
        repo = SqlJobRepository(session)
        resume_repo = SqlResumeRepository(session)
        parser = ParserService()
        event_bus = RedisEventBus(ctx["redis"])
        try:
            service = ParseJobService(
                repo=repo,
                resume_repo=resume_repo,
                parser=parser,
                event_bus=event_bus,
            )
            yield service
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def parse_job_task(ctx, job_id: int) -> None:
    logger.info("job %s started", job_id)
    try:
        async with build_service(ctx) as service:
            await service.run(job_id)
    except Exception:
        logger.exception("job %s failed", job_id)
        raise

    logger.info("job %s finished", job_id)
