from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.jobs.domain.entities import ParseJob
from src.jobs.mappers import orm_to_parse_job, parse_job_to_orm
from src.jobs.models import ParseJobORM


class SqlJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, job_id: int) -> ParseJob | None:
        orm = await self.session.get(ParseJobORM, job_id)
        if orm is None:
            return None
        return orm_to_parse_job(orm)

    async def save(self, job: ParseJob) -> None:
        orm = parse_job_to_orm(job)
        merged = await self.session.merge(orm)
        await self.session.flush()
        if job.id is None:
            job.id = merged.id

    async def list_all(self) -> list[ParseJob]:
        result = await self.session.execute(select(ParseJobORM))
        orms = result.scalars().all()
        return [orm_to_parse_job(orm) for orm in orms]
