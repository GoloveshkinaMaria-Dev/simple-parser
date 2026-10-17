from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.parser.domain.entities import Resume
from src.resumes.mappers import orm_to_resume, resume_to_orm
from src.resumes.models import ResumeORM, ResumeSkillORM


class SqlResumeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_many(self, resumes: list[Resume], job_id: int) -> None:
        for resume in resumes:
            orm = resume_to_orm(resume, job_id=job_id)
            self.session.add(orm)
            await self.session.flush()
            for skill in dict.fromkeys(resume.skills or []):
                self.session.add(ResumeSkillORM(resume_id=orm.id, skill=skill))

    async def list_by_job(self, job_id: int) -> list[Resume]:
        stmt = select(ResumeORM).where(ResumeORM.job_id == job_id)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [orm_to_resume(orm) for orm in orms]

    async def average_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        stmt = (
            select(
                func.avg(ResumeORM.salary_amount),
                func.count(ResumeORM.id),
            )
            .where(ResumeORM.area_id == area_id)
            .where(ResumeORM.title.ilike(f"%{keyword}%"))
            .where(ResumeORM.salary_amount.is_not(None))
        )
        result = await self.session.execute(stmt)
        avg, count = result.one()
        return (float(avg) if avg is not None else None, count)

    async def median_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        stmt = (
            select(
                func.percentile_cont(0.5).within_group(ResumeORM.salary_amount.asc()),
                func.count(ResumeORM.id),
            )
            .where(ResumeORM.area_id == area_id)
            .where(ResumeORM.title.ilike(f"%{keyword}%"))
            .where(ResumeORM.salary_amount.is_not(None))
        )
        result = await self.session.execute(stmt)
        median, count = result.one()
        return (float(median) if median is not None else None, count)

    async def top_skills(
        self,
        area_id: int | None,
        keyword: str | None,
        limit: int,
    ) -> list[tuple[str, int]]:
        stmt = select(
            ResumeSkillORM.skill,
            func.count(ResumeSkillORM.resume_id).label("cnt"),
        ).join(ResumeORM, ResumeORM.id == ResumeSkillORM.resume_id)

        if area_id is not None:
            stmt = stmt.where(ResumeORM.area_id == area_id)
        if keyword is not None:
            stmt = stmt.where(ResumeORM.title.ilike(f"%{keyword}%"))

        stmt = (
            stmt.group_by(ResumeSkillORM.skill)
            .order_by(func.count(ResumeSkillORM.resume_id).desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return [(row.skill, row.cnt) for row in result.all()]
