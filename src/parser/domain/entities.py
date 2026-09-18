"""Domain model representing a normalized resume."""

from dataclasses import dataclass


@dataclass
class Resume:
    id: str
    title: str
    first_name: str | None
    last_name: str | None
    area: str
    salary_amount: int | None
    salary_currency: str | None
    url: str
    work_format: list[str]
