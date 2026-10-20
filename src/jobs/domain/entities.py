"""Domain entities for parse jobs."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from .events import DomainEvent, JobCompleted, JobFailed
from .exceptions import InvalidJobState
from .value_objects import JobStatus


@dataclass
class DomainModel:
    """Base class for domain models that accumulate events."""

    _events: list[DomainEvent] = field(default_factory=list, init=False, compare=False, repr=False)


@dataclass
class ParseJob(DomainModel):
    """Parse job aggregate root: tracks parsing lifecycle and domain events."""

    id: int | None = None
    text: str = ""
    area: int | None = None
    status: JobStatus = JobStatus.PENDING
    items_count: int = 0
    per_page: int = 20
    max_pages: int = 5
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def pull_events(self) -> list[DomainEvent]:
        """Return accumulated events and clear the internal list."""
        events = list(self._events)
        self._events.clear()
        return events

    def start(self) -> None:
        """Transition PENDING → RUNNING. Raises InvalidJobState otherwise."""
        if self.status != JobStatus.PENDING:
            raise InvalidJobState()
        self.status = JobStatus.RUNNING
        self.error = None

    def complete(self, items_count: int) -> None:
        """Transition RUNNING → COMPLETED, reset error, emit JobCompleted."""
        if self.status != JobStatus.RUNNING:
            raise InvalidJobState()
        self.status = JobStatus.COMPLETED
        self.items_count = items_count
        self.error = None
        self._events.append(JobCompleted(job_id=self.id, count=items_count))

    def fail(self, reason: str) -> None:
        """Transition RUNNING → FAILED, store reason, emit JobFailed."""
        if self.status != JobStatus.RUNNING:
            raise InvalidJobState()
        self.status = JobStatus.FAILED
        self.error = reason
        self._events.append(JobFailed(job_id=self.id, reason=reason))
