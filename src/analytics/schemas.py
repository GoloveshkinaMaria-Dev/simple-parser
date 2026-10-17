from pydantic import BaseModel


class AverageSalaryResponse(BaseModel):
    area_id: int
    keyword: str
    average: float | None
    count: int


class MedianSalaryResponse(BaseModel):
    area_id: int
    keyword: str
    median: float | None
    count: int


class SkillCountResponse(BaseModel):
    skill: str
    count: int
