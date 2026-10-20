from arq.connections import ArqRedis
from fastapi import Depends, Request

from src.database import AsyncSession, get_session
from src.jobs.infrastructure.repository import SqlJobRepository
from src.jobs.repository import JobRepository
from src.jobs.service import ParseJobService
from src.parser.service import ParserService
from src.resumes.infrastructure.repository import SqlResumeRepository
from src.resumes.repository import ResumeRepository


async def get_arq_pool(request: Request) -> ArqRedis:
    """Return the arq connection pool from application state."""
    return request.app.state.arq


async def get_job_repo(session: AsyncSession = Depends(get_session)) -> JobRepository:
    """Build a SqlJobRepository for the current request."""
    return SqlJobRepository(session)


async def get_parser_service() -> ParserService:
    """Provide a ParserService instance."""
    return ParserService()


async def get_resume_repo(
    session: AsyncSession = Depends(get_session),
) -> ResumeRepository:
    """Build a SqlResumeRepository for the current request."""
    return SqlResumeRepository(session)


async def get_parse_job_service(
    repo: JobRepository = Depends(get_job_repo),
    resume_repo: ResumeRepository = Depends(get_resume_repo),
    parser: ParserService = Depends(get_parser_service),
) -> ParseJobService:
    """Build a ParseJobService with all its dependencies."""
    return ParseJobService(repo, resume_repo, parser, event_bus=None)
