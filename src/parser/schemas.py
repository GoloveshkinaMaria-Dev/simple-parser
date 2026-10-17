"""Pydantic schemas for the hh.ru API responses."""

from pydantic import BaseModel


class HHSkill(BaseModel):
    name: str


class HHArea(BaseModel):
    """Вложенный объект региона."""

    id: str
    name: str


class HHSalary(BaseModel):
    "Вложенный объект зарплаты."

    amount: int | None
    currency: str | None


class HHWorkFormat(BaseModel):
    "Вложенный объект формата занятости."

    id: str
    name: str


class HHResume(BaseModel):
    """Вложенная единица резюме."""

    id: str
    title: str
    first_name: str | None
    last_name: str | None
    area: HHArea | None
    salary: HHSalary | None
    alternate_url: str
    work_format: list[HHWorkFormat] | None
    key_skills: list[HHSkill] | None = None


class HHResumeSearchResponse(BaseModel):
    """Получает ответ с хх."""

    items: list[HHResume]
    found: int
    pages: int
    per_page: int
    page: int
