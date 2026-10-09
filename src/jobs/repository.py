from typing import Protocol

from src.jobs.domain.entities import ParseJob


class JobRepository(Protocol):
    async def get(self, job_id: int) -> ParseJob | None: ...

    async def save(self, job: ParseJob) -> None: ...

    async def list_all(self) -> list[ParseJob]: ...
