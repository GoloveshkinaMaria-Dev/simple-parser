from fastapi import Depends

from src.analytics.service import AnalyticsService
from src.jobs.dependencies import get_resume_repo
from src.resumes.repository import ResumeRepository


async def get_analytics_service(
    repo: ResumeRepository = Depends(get_resume_repo),
) -> AnalyticsService:
    return AnalyticsService(repo)
