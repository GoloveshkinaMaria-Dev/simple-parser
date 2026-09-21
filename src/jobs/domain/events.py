"""Domain events for parse jobs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DomainEvent:
    pass


@dataclass(frozen=True)
class JobCompleted(DomainEvent):
    job_id: int | None
    count: int


@dataclass(frozen=True)
class JobFailed(DomainEvent):
    job_id: int | None
    reason: str
