from datetime import UTC, datetime

import pytest

from src.jobs.domain.entities import ParseJob
from src.jobs.domain.value_objects import JobStatus
from src.jobs.mappers import orm_to_parse_job, parse_job_to_orm
from src.jobs.models import ParseJobORM


class TestParseJobToOrm:
    def test_full(self) -> None:
        job = ParseJob(
            id=1,
            text="python",
            area=1,
            status=JobStatus.RUNNING,
            items_count=42,
            per_page=20,
            max_pages=5,
            error=None,
        )
        orm = parse_job_to_orm(job)

        assert orm.id == 1
        assert orm.text == "python"
        assert orm.area == 1
        assert orm.status == "running"
        assert orm.items_count == 42
        assert orm.per_page == 20
        assert orm.max_pages == 5
        assert orm.error is None
        assert orm.created_at == job.created_at

    def test_status_is_str(self) -> None:
        job = ParseJob(
            id=1,
            text="python",
            area=1,
            status=JobStatus.RUNNING,
        )
        orm = parse_job_to_orm(job)

        assert orm.status == "running"
        assert isinstance(orm.status, str)

    def test_all_statuses(self) -> None:
        for status in JobStatus:
            job = ParseJob(id=1, text="python", area=1, status=status)
            orm = parse_job_to_orm(job)
            assert orm.status == status.value
            assert isinstance(orm.status, str)

    def test_none_id(self) -> None:
        job = ParseJob(id=None, text="python", area=1)
        orm = parse_job_to_orm(job)
        assert orm.id is None

    def test_none_area(self) -> None:
        job = ParseJob(id=1, text="python", area=None)
        orm = parse_job_to_orm(job)
        assert orm.area is None

    def test_error_set(self) -> None:
        job = ParseJob(id=1, text="python", area=1)
        job.start()
        job.fail(reason="hh.ru unavailable")
        orm = parse_job_to_orm(job)

        assert orm.status == "failed"
        assert orm.error == "hh.ru unavailable"


class TestOrmToParseJob:
    def test_full(self) -> None:
        ts = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)
        orm = ParseJobORM(
            id=1,
            text="python",
            area=1,
            status="running",
            items_count=42,
            per_page=20,
            max_pages=5,
            error=None,
            created_at=ts,
        )
        job = orm_to_parse_job(orm)

        assert job.id == 1
        assert job.text == "python"
        assert job.area == 1
        assert job.status == JobStatus.RUNNING
        assert job.items_count == 42
        assert job.per_page == 20
        assert job.max_pages == 5
        assert job.error is None
        assert job.created_at == ts

    def test_status_is_enum(self) -> None:
        orm = ParseJobORM(
            id=1,
            text="python",
            area=1,
            status="running",
            created_at=datetime.now(UTC),
        )
        job = orm_to_parse_job(orm)

        assert job.status == JobStatus.RUNNING
        assert isinstance(job.status, JobStatus)

    def test_all_statuses(self) -> None:
        for status in JobStatus:
            orm = ParseJobORM(
                id=1,
                text="python",
                area=1,
                status=status.value,
                created_at=datetime.now(UTC),
            )
            job = orm_to_parse_job(orm)
            assert job.status == status
            assert isinstance(job.status, JobStatus)

    def test_events_empty(self) -> None:
        orm = ParseJobORM(
            id=1,
            text="python",
            area=1,
            status="pending",
            created_at=datetime.now(UTC),
        )
        job = orm_to_parse_job(orm)
        assert job._events == []

    def test_error_set(self) -> None:
        orm = ParseJobORM(
            id=1,
            text="python",
            area=1,
            status="failed",
            error="hh.ru unavailable",
            created_at=datetime.now(UTC),
        )
        job = orm_to_parse_job(orm)
        assert job.status == JobStatus.FAILED
        assert job.error == "hh.ru unavailable"


class TestRoundtrip:
    def test_full(self) -> None:
        original = ParseJob(
            id=1,
            text="python",
            area=1,
            status=JobStatus.PENDING,
            items_count=0,
            per_page=20,
            max_pages=5,
            error=None,
        )
        restored = orm_to_parse_job(parse_job_to_orm(original))

        assert restored.id == original.id
        assert restored.text == original.text
        assert restored.area == original.area
        assert restored.status == original.status
        assert restored.items_count == original.items_count
        assert restored.per_page == original.per_page
        assert restored.max_pages == original.max_pages
        assert restored.error == original.error
        assert restored.created_at == original.created_at

    def test_with_error(self) -> None:
        original = ParseJob(id=1, text="python", area=1)
        original.start()
        original.fail(reason="hh.ru unavailable")

        restored = orm_to_parse_job(parse_job_to_orm(original))

        assert restored.status == JobStatus.FAILED
        assert restored.error == "hh.ru unavailable"

    def test_none_values(self) -> None:
        original = ParseJob(id=None, text="python", area=None)

        restored = orm_to_parse_job(parse_job_to_orm(original))

        assert restored.id is None
        assert restored.area is None

    def test_with_completed(self) -> None:
        original = ParseJob(id=1, text="python", area=1)
        original.start()
        original.complete(items_count=42)

        restored = orm_to_parse_job(parse_job_to_orm(original))

        assert restored.status == JobStatus.COMPLETED
        assert restored.items_count == 42

    def test_events_not_preserved(self) -> None:
        original = ParseJob(id=1, text="python", area=1)
        original.start()
        original.complete(items_count=42)
        assert len(original._events) == 1

        restored = orm_to_parse_job(parse_job_to_orm(original))
        assert restored._events == []