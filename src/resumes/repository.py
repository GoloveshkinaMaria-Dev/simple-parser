from typing import Protocol

from src.parser.domain.entities import Resume


class ResumeRepository(Protocol):
    """Persistence and analytics contract for parsed resumes."""

    async def save_many(self, resumes: list[Resume], job_id: int) -> None:
        """Save resumes and their skills for the given job."""
        ...

    async def list_by_job(self, job_id: int) -> list[Resume]:
        """Return all resumes for the given job."""
        ...

    async def average_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        """Return average salary and count for matching resumes (null salaries excluded)."""
        ...

    async def median_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        """Return median salary and count for matching resumes (null salaries excluded)."""
        ...

    async def top_skills(
        self,
        area_id: int | None,
        keyword: str | None,
        limit: int,
    ) -> list[tuple[str, int]]:
        """Return top N skills as (skill, count) pairs, sorted by count descending."""
        ...
