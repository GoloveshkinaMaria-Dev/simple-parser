from datetime import UTC, datetime

import pytest

from src.jobs.domain.entities import ParseJob
from src.jobs.domain.events import JobCompleted
from src.jobs.domain.exceptions import InvalidJobState
from src.jobs.domain.value_objects import JobStatus


class TestParseJobStart:
    def test_start_from_pending(self, job: ParseJob) -> None:
        job.start()
        assert job.status == JobStatus.RUNNING

    def test_start_from_running_raises(self, job: ParseJob) -> None:
        job.start()
        with pytest.raises(InvalidJobState):
            job.start()


class TestParseJobComplete:
    def test_complete_from_running(self, job: ParseJob) -> None:
        job.start()
        job.complete(items_count=42)
        assert job.status == JobStatus.COMPLETED
        assert job.items_count == 42
        assert len(job._events) == 1
        assert job._events[0].count == 42

    def test_complete_from_pending_raises(self, job: ParseJob) -> None:
        with pytest.raises(InvalidJobState):
            job.complete(items_count=42)

    def test_complete_from_failed_raises(self, job: ParseJob) -> None:
        job.start()
        job.fail(reason="boom")
        with pytest.raises(InvalidJobState):
            job.complete(items_count=42)


class TestParseJobFail:
    def test_fail_from_running(self, job: ParseJob) -> None:
        job.start()
        job.fail(reason="hh.ru unavailable")
        assert job.status == JobStatus.FAILED
        assert len(job._events) == 1
        assert job._events[0].reason == "hh.ru unavailable"

    def test_fail_from_pending_raises(self, job: ParseJob) -> None:
        with pytest.raises(InvalidJobState):
            job.fail(reason="x")

    def test_fail_from_completed_raises(self, job: ParseJob) -> None:
        job.start()
        job.complete(items_count=42)
        with pytest.raises(InvalidJobState):
            job.fail(reason="x")


class TestParseJobCreatedAt:
    def test_created_at_set_on_creation(self, job: ParseJob) -> None:
        assert job.created_at is not None

    def test_created_at_preserved_if_provided(self) -> None:
        from datetime import UTC, datetime

        ts = datetime(2024, 1, 1, tzinfo=UTC)
        job = ParseJob(id=1, text="python", area=1, created_at=ts)
        assert job.created_at == ts


class TestParseJobDefaults:
    def test_default_status_is_pending(self, job: ParseJob) -> None:
        assert job.status == JobStatus.PENDING

    def test_default_items_count_is_zero(self, job: ParseJob) -> None:
        assert job.items_count == 0

    def test_default_per_page(self, job: ParseJob) -> None:
        assert job.per_page == 20

    def test_default_max_pages(self, job: ParseJob) -> None:
        assert job.max_pages == 5


class TestParseJobEvents:
    def test_events_empty_on_creation(self, job: ParseJob) -> None:
        assert job._events == []

    def test_events_accumulate_on_complete(self, job: ParseJob) -> None:
        job.start()
        job.complete(items_count=10)
        assert len(job._events) == 1

    def test_events_do_not_affect_equality(self) -> None:
        ts = datetime(2024, 1, 1, tzinfo=UTC)
        job1 = ParseJob(id=1, text="python", area=1, created_at=ts)
        job2 = ParseJob(id=1, text="python", area=1, created_at=ts)
        job1._events.append(JobCompleted(job_id=1, count=42))
        assert job1 == job2

    def test_events_do_not_appear_in_repr(self, job: ParseJob) -> None:
        job.start()
        job.complete(items_count=42)
        assert "_events" not in repr(job)
