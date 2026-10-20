"""Pydantic schemas for the hh.ru API responses."""

from pydantic import BaseModel


class HHSkill(BaseModel):
    """Single skill entry from an hh.ru resume."""

    name: str


class HHArea(BaseModel):
    """Nested area (region) object."""

    id: str
    name: str


class HHSalary(BaseModel):
    """Nested salary object."""

    amount: int | None
    currency: str | None


class HHWorkFormat(BaseModel):
    """Nested work-format entry (remote, office, hybrid)."""

    id: str
    name: str


class HHResume(BaseModel):
    """Single resume item from the hh.ru search response."""

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
    """Pydantic wrapper for the hh.ru resume search response."""

    items: list[HHResume]
    found: int
    pages: int
    per_page: int
    page: int
