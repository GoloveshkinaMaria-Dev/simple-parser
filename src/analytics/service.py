from src.resumes.repository import ResumeRepository


class AnalyticsService:
    def __init__(self, repo: ResumeRepository) -> None:
        self.repo = repo

    async def average_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        return await self.repo.average_salary(area_id, keyword)

    async def median_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        return await self.repo.median_salary(area_id, keyword)

    async def top_skills(
        self, area_id: int | None, keyword: str | None, limit: int
    ) -> list[tuple[str, int]]:
        return await self.repo.top_skills(area_id, keyword, limit)
