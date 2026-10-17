from fastapi import APIRouter, Depends, Query

from src.analytics.dependencies import get_analytics_service
from src.analytics.schemas import (
    AverageSalaryResponse,
    MedianSalaryResponse,
    SkillCountResponse,
)
from src.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/salary/average",
    response_model=AverageSalaryResponse,
    summary="Average salary by area and keyword",
)
async def average_salary(
    area_id: int,
    keyword: str,
    service: AnalyticsService = Depends(get_analytics_service),
) -> AverageSalaryResponse:
    avg, count = await service.average_salary(area_id, keyword)
    return AverageSalaryResponse(
        area_id=area_id,
        keyword=keyword,
        average=avg,
        count=count,
    )


@router.get(
    "/salary/median",
    response_model=MedianSalaryResponse,
    summary="Median salary by area and keyword",
)
async def median_salary(
    area_id: int,
    keyword: str,
    service: AnalyticsService = Depends(get_analytics_service),
) -> MedianSalaryResponse:
    median, count = await service.median_salary(area_id, keyword)
    return MedianSalaryResponse(
        area_id=area_id,
        keyword=keyword,
        median=median,
        count=count,
    )


@router.get(
    "/skills/top",
    response_model=list[SkillCountResponse],
    summary="Top N skills by area and keyword",
)
async def top_skills(
    area_id: int | None = None,
    keyword: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    service: AnalyticsService = Depends(get_analytics_service),
) -> list[SkillCountResponse]:
    rows = await service.top_skills(area_id, keyword, limit)
    return [SkillCountResponse(skill=s, count=c) for s, c in rows]
