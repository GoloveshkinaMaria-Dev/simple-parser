from pydantic import BaseModel


class AverageSalaryResponse(BaseModel):
    """Average salary aggregation result for a given area and keyword."""

    area_id: int
    keyword: str
    average: float | None
    count: int


class MedianSalaryResponse(BaseModel):
    """Median salary aggregation result for a given area and keyword."""

    area_id: int
    keyword: str
    median: float | None
    count: int


class SkillCountResponse(BaseModel):
    """Single skill with its occurrence count across resumes."""

    skill: str
    count: int
