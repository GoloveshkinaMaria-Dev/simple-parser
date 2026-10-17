"""Integration tests for SqlResumeRepository."""

import pytest

from src.parser.domain.entities import Resume
from src.resumes.infrastructure.repository import SqlResumeRepository


def make_resume(
    external_id: str,
    title: str = "Python developer",
    area_id: int | None = 1,
    area_name: str = "Москва",
    salary_amount: int | None = 200_000,
    salary_currency: str | None = "RUR",
    work_format: list[str] | None = None,
    skills: list[str] | None = None,
) -> Resume:
    return Resume(
        external_id=external_id,
        title=title,
        first_name=None,
        last_name=None,
        area_id=area_id,
        area_name=area_name,
        salary_amount=salary_amount,
        salary_currency=salary_currency,
        url=f"https://hh.ru/resume/{external_id}",
        work_format=work_format or ["REMOTE"],
        skills=skills or [],
    )


class TestSaveMany:
    async def test_inserts_resumes(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev"),
            make_resume("2", title="Java dev"),
        ]

        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        stored = await repo.list_by_job(job_id)
        assert len(stored) == 2
        assert {r.external_id for r in stored} == {"1", "2"}

    async def test_saves_all_fields(self, repo, session, job_id) -> None:
        resume = make_resume(
            "abc",
            title="Senior Python",
            area_id=1,
            area_name="Москва",
            salary_amount=300_000,
            salary_currency="RUR",
            work_format=["REMOTE", "OFFICE"],
        )

        await repo.save_many([resume], job_id=job_id)
        await session.commit()

        stored = (await repo.list_by_job(job_id))[0]
        assert stored.external_id == "abc"
        assert stored.title == "Senior Python"
        assert stored.area_id == 1
        assert stored.area_name == "Москва"
        assert stored.salary_amount == 300_000
        assert stored.salary_currency == "RUR"
        assert stored.work_format == ["REMOTE", "OFFICE"]

    async def test_saves_skills(self, repo, session, job_id) -> None:
        resume = make_resume("1", skills=["Python", "Django", "PostgreSQL"])

        await repo.save_many([resume], job_id=job_id)
        await session.commit()

        stored = (await repo.list_by_job(job_id))[0]
        assert sorted(stored.skills) == ["Django", "PostgreSQL", "Python"]

    async def test_no_skills(self, repo, session, job_id) -> None:
        resume = make_resume("1", skills=[])

        await repo.save_many([resume], job_id=job_id)
        await session.commit()

        stored = (await repo.list_by_job(job_id))[0]
        assert stored.skills == []

    async def test_none_salary(self, repo, session, job_id) -> None:
        resume = make_resume("1", salary_amount=None, salary_currency=None)

        await repo.save_many([resume], job_id=job_id)
        await session.commit()

        stored = (await repo.list_by_job(job_id))[0]
        assert stored.salary_amount is None
        assert stored.salary_currency is None

    async def test_none_area(self, repo, session, job_id) -> None:
        resume = make_resume("1", area_id=None, area_name="")

        await repo.save_many([resume], job_id=job_id)
        await session.commit()

        stored = (await repo.list_by_job(job_id))[0]
        assert stored.area_id is None
        assert stored.area_name == ""

    async def test_empty_list(self, repo, session, job_id) -> None:
        await repo.save_many([], job_id=job_id)
        await session.commit()

        assert await repo.list_by_job(job_id) == []

    async def test_three_resumes_from_hh_fixture(self, repo, session, job_id) -> None:
        resumes = [
            make_resume(
                "0123456789abcdef",
                title="Python-разработчик",
                area_id=1,
                area_name="Москва",
                salary_amount=200_000,
                salary_currency="RUR",
                work_format=["Удалённо", "Гибрид"],
            ),
            make_resume(
                "fedcba9876543210",
                title="Backend-разработчик",
                area_id=2,
                area_name="Санкт-Петербург",
                salary_amount=None,
                salary_currency=None,
                work_format=["Офис"],
            ),
            make_resume(
                "aaaabbbbccccdddd",
                title="QA Engineer",
                area_id=None,
                area_name="",
                salary_amount=None,
                salary_currency=None,
                work_format=[],
            ),
        ]

        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        stored = await repo.list_by_job(job_id)
        assert len(stored) == 3


class TestListByJob:
    async def test_returns_only_this_job(self, repo, session) -> None:
        from src.jobs.models import ParseJobORM

        job1 = ParseJobORM(text="a", area=1, status="pending", items_count=0,
                           per_page=20, max_pages=5)
        job2 = ParseJobORM(text="b", area=1, status="pending", items_count=0,
                           per_page=20, max_pages=5)
        session.add_all([job1, job2])
        await session.flush()

        await repo.save_many([make_resume("1")], job_id=job1.id)
        await repo.save_many([make_resume("2"), make_resume("3")], job_id=job2.id)
        await session.commit()

        only_job1 = await repo.list_by_job(job1.id)
        assert [r.external_id for r in only_job1] == ["1"]

        only_job2 = await repo.list_by_job(job2.id)
        assert {r.external_id for r in only_job2} == {"2", "3"}

    async def test_empty_for_missing_job(self, repo) -> None:
        assert await repo.list_by_job(999_999) == []

    async def test_includes_skills(self, repo, session, job_id) -> None:
        await repo.save_many(
            [make_resume("1", skills=["Python", "Django"])],
            job_id=job_id,
        )
        await session.commit()

        stored = (await repo.list_by_job(job_id))[0]
        assert sorted(stored.skills) == ["Django", "Python"]


class TestAverageSalary:
    async def test_basic(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", area_id=1, salary_amount=100_000),
            make_resume("2", title="Python dev", area_id=1, salary_amount=200_000),
            make_resume("3", title="Python dev", area_id=1, salary_amount=300_000),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        avg, count = await repo.average_salary(area_id=1, keyword="python")
        assert avg == 200_000.0
        assert count == 3

    async def test_ignores_null_salary(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", salary_amount=100_000),
            make_resume("2", title="Python dev", salary_amount=200_000),
            make_resume("3", title="Python dev", salary_amount=None),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        avg, count = await repo.average_salary(area_id=1, keyword="python")
        assert avg == 150_000.0
        assert count == 2

    async def test_filters_by_area(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", area_id=1, salary_amount=100_000),
            make_resume("2", title="Python dev", area_id=2, salary_amount=900_000),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        avg, count = await repo.average_salary(area_id=1, keyword="python")
        assert avg == 100_000.0
        assert count == 1

    async def test_filters_by_keyword(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", salary_amount=100_000),
            make_resume("2", title="Python dev", salary_amount=200_000),
            make_resume("3", title="Java dev", salary_amount=900_000),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        avg, count = await repo.average_salary(area_id=1, keyword="python")
        assert avg == 150_000.0
        assert count == 2

    async def test_keyword_case_insensitive(self, repo, session, job_id) -> None:
        await repo.save_many(
            [make_resume("1", title="Python dev", salary_amount=100_000)],
            job_id=job_id,
        )
        await session.commit()

        avg, count = await repo.average_salary(area_id=1, keyword="PYTHON")
        assert avg == 100_000.0
        assert count == 1

    async def test_empty_result(self, repo, session, job_id) -> None:
        await repo.save_many(
            [make_resume("1", title="Python dev", salary_amount=100_000)],
            job_id=job_id,
        )
        await session.commit()

        avg, count = await repo.average_salary(area_id=1, keyword="povar")
        assert avg is None
        assert count == 0


class TestMedianSalary:
    async def test_odd_count(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", salary_amount=100_000),
            make_resume("2", title="Python dev", salary_amount=200_000),
            make_resume("3", title="Python dev", salary_amount=300_000),
            make_resume("4", title="Python dev", salary_amount=400_000),
            make_resume("5", title="Python dev", salary_amount=500_000),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        median, count = await repo.median_salary(area_id=1, keyword="python")
        assert median == 300_000.0
        assert count == 5

    async def test_even_count(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", salary_amount=100_000),
            make_resume("2", title="Python dev", salary_amount=200_000),
            make_resume("3", title="Python dev", salary_amount=300_000),
            make_resume("4", title="Python dev", salary_amount=400_000),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        median, count = await repo.median_salary(area_id=1, keyword="python")
        assert median == 250_000.0
        assert count == 4

    async def test_ignores_null(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", salary_amount=100_000),
            make_resume("2", title="Python dev", salary_amount=None),
            make_resume("3", title="Python dev", salary_amount=300_000),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        median, count = await repo.median_salary(area_id=1, keyword="python")
        assert median == 200_000.0
        assert count == 2

    async def test_empty_result(self, repo, session, job_id) -> None:
        median, count = await repo.median_salary(area_id=1, keyword="povar")
        assert median is None
        assert count == 0


class TestTopSkills:
    async def test_basic(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", skills=["Python", "Django"]),
            make_resume("2", title="Python dev", skills=["Python", "FastAPI"]),
            make_resume("3", title="Python dev", skills=["Python", "Django", "PostgreSQL"]),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        result = await repo.top_skills(area_id=1, keyword="python", limit=10)
        assert result[0] == ("Python", 3)
        assert result[1] == ("Django", 2)
        assert set(result[2:]) == {("FastAPI", 1), ("PostgreSQL", 1)}

    async def test_respects_limit(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", skills=["Python", "Django"]),
            make_resume("2", title="Python dev", skills=["Python", "FastAPI"]),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        result = await repo.top_skills(area_id=1, keyword="python", limit=1)
        assert result == [("Python", 2)]

    async def test_filters_by_area(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", area_id=1, skills=["Python"]),
            make_resume("2", area_id=2, skills=["Python", "Java"]),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        result = await repo.top_skills(area_id=1, keyword="python", limit=10)
        assert result == [("Python", 1)]

    async def test_filters_by_keyword(self, repo, session, job_id) -> None:
        resumes = [
            make_resume("1", title="Python dev", skills=["Python"]),
            make_resume("2", title="Java dev", skills=["Python", "Java"]),
        ]
        await repo.save_many(resumes, job_id=job_id)
        await session.commit()

        result = await repo.top_skills(area_id=1, keyword="java", limit=10)
        assert result == [("Java", 1), ("Python", 1)]

    async def test_empty(self, repo, session, job_id) -> None:
        result = await repo.top_skills(area_id=1, keyword="python", limit=10)
        assert result == []