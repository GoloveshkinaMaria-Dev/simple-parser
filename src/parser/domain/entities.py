"""Domain model representing a normalized resume."""

from dataclasses import dataclass


@dataclass
class Resume:
    external_id: str
    title: str
    first_name: str | None
    last_name: str | None
    area_name: str
    area_id: int | None
    salary_amount: int | None
    salary_currency: str | None
    url: str
    work_format: list[str]
    skills: list[str]
