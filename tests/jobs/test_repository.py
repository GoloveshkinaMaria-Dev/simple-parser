import pytest
from sqlalchemy import delete

from src.database import SessionLocal
from src.jobs.domain.entities import ParseJob
from src.jobs.domain.value_objects import JobStatus


class TestSave:
    async def test_save_new_job_assigns_id(self, repo, session) -> None:
        job = ParseJob(id=None, text="python", area=1)

        await repo.save(job)
        await session.commit()

        assert job.id is not None
        assert job.id > 0

    async def test_save_persists_all_fields(self, repo, session) -> None:
        job = ParseJob(
            id=None,
            text="python",
            area=1,
            status=JobStatus.PENDING,
            items_count=0,
            per_page=20,
            max_pages=5,
            error=None,
        )
        await repo.save(job)
        await session.commit()

        loaded = await repo.get(job.id)
        assert loaded is not None
        assert loaded.text == "python"
        assert loaded.area == 1
        assert loaded.status == JobStatus.PENDING
        assert loaded.items_count == 0
        assert loaded.per_page == 20
        assert loaded.max_pages == 5
        assert loaded.error is None

    async def test_save_updates_existing(self, repo, session) -> None:
        job = ParseJob(id=None, text="python", area=1)
        await repo.save(job)
        await session.commit()

        job.start()
        job.complete(items_count=42)
        await repo.save(job)
        await session.commit()

        loaded = await repo.get(job.id)
        assert loaded is not None
        assert loaded.status == JobStatus.COMPLETED
        assert loaded.items_count == 42

        # убедиться, что не создался дубликат
        all_jobs = await repo.list_all()
        assert len(all_jobs) == 1

    async def test_save_with_error(self, repo, session) -> None:
        job = ParseJob(id=None, text="python", area=1)
        await repo.save(job)
        await session.commit()

        job.start()
        job.fail(reason="hh.ru unavailable")
        await repo.save(job)
        await session.commit()

        loaded = await repo.get(job.id)
        assert loaded is not None
        assert loaded.status == JobStatus.FAILED
        assert loaded.error == "hh.ru unavailable"


class TestGet:
    async def test_get_returns_saved_job(self, repo, session) -> None:
        job = ParseJob(id=None, text="python", area=1)
        await repo.save(job)
        await session.commit()

        loaded = await repo.get(job.id)

        assert loaded is not None
        assert loaded.id == job.id
        assert loaded.text == "python"
        assert loaded.area == 1

    async def test_get_returns_none_if_not_found(self, repo) -> None:
        loaded = await repo.get(999_999)
        assert loaded is None

    async def test_get_returns_none_area(self, repo, session) -> None:
        job = ParseJob(id=None, text="python", area=None)
        await repo.save(job)
        await session.commit()

        loaded = await repo.get(job.id)
        assert loaded is not None
        assert loaded.area is None


class TestListAll:
    async def test_list_all_empty(self, repo) -> None:
        jobs = await repo.list_all()
        assert jobs == []

    async def test_list_all_returns_all(self, repo, session) -> None:
        for i in range(3):
            job = ParseJob(id=None, text=f"python-{i}", area=1)
            await repo.save(job)
        await session.commit()

        jobs = await repo.list_all()

        assert len(jobs) == 3
        texts = sorted(j.text for j in jobs)
        assert texts == ["python-0", "python-1", "python-2"]
