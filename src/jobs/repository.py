from typing import Protocol

from src.jobs.domain.entities import ParseJob


class JobRepository(Protocol):
    """Persistence contract for ParseJob aggregates."""

    async def get(self, job_id: int) -> ParseJob | None:
        """Return the job by id, or None if not found."""
        ...

    async def save(self, job: ParseJob) -> None:
        """Persist the job: INSERT if new, UPDATE if it already has an id."""
        ...

    async def list_all(self) -> list[ParseJob]:
        """Return all jobs."""
        ...
