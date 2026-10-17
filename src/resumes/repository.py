from typing import Protocol

from src.parser.domain.entities import Resume


class ResumeRepository(Protocol):
    """Интерфейс репозитория резюме.

    Реализация — SqlResumeRepository в infrastructure.
    Сервисы зависят от этого протокола, а не от SQL-версии,
    чтобы в тестах подменять фейком без БД.
    """

    async def save_many(self, resumes: list[Resume], job_id: int) -> None:
        """Сохранить резюме, привязав их к указанному job_id.

        Сохраняет и resume, и resume_skill (навыки — отдельной таблицей).
        """
        ...

    async def list_by_job(self, job_id: int) -> list[Resume]:
        """Вернуть все резюме, привязанные к job'у. Пустой список, если нет."""
        ...

    async def average_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        """Средняя зарплата по area + keyword.

        Возвращает (average, count):
          average — None, если нет данных;
          count — количество резюме С зарплатой (не всех подходящих).
        """
        ...

    async def median_salary(self, area_id: int, keyword: str) -> tuple[float | None, int]:
        """Медиана зарплат по area + keyword. (median, count)."""
        ...

    async def top_skills(
        self,
        area_id: int | None,
        keyword: str | None,
        limit: int,
    ) -> list[tuple[str, int]]:
        """Топ-N навыков по частоте. [(skill, count), ...] убыв.

        area_id=None — без фильтра по городу.
        keyword=None — без фильтра по названию.
        """
        ...
