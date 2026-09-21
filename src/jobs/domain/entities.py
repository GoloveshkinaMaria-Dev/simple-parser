"""Domain entities for parse jobs."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from .events import DomainEvent, JobCompleted, JobFailed
from .exceptions import InvalidJobState
from .value_objects import JobStatus


@dataclass
class DomainModel:
    _events: list[DomainEvent] = field(
        default_factory=list, init=False, compare=False, repr=False
    )


@dataclass
class ParseJob(DomainModel):
    id: int | None
    text: str
    area: int | None
    status: JobStatus = JobStatus.PENDING
    items_count: int = 0
    per_page: int = 20
    max_pages: int = 5
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now(UTC)

    def start(self) -> None:
        if self.status != JobStatus.PENDING:
            raise InvalidJobState
        self.status = JobStatus.RUNNING

    def complete(self, items_count) -> None:
        if self.status != JobStatus.RUNNING:
            raise InvalidJobState
        self.status = JobStatus.COMPLETED
        self.items_count = items_count
        self._events.append(JobCompleted(job_id=self.id, count=items_count))

    def fail(self, reason) -> None:
        if self.status != JobStatus.RUNNING:
            raise InvalidJobState
        self.status = JobStatus.FAILED
        self._events.append(JobFailed(job_id=self.id, reason=reason))
