from datetime import datetime

from pydantic import BaseModel, Field

from src.jobs.domain.entities import ParseJob
from src.parser.domain.entities import Resume

from .domain.value_objects import JobStatus


class ResumeResponse(BaseModel):
    """Resume data returned by the API."""

    external_id: str
    title: str
    area_name: str
    area_id: int | None
    salary_amount: int | None
    salary_currency: str | None
    url: str
    work_format: list[str]
    skills: list[str]

    @classmethod
    def from_domain(cls, r: Resume) -> "ResumeResponse":
        """Build a response DTO from a domain Resume."""
        return cls(
            external_id=r.external_id,
            title=r.title,
            area_name=r.area_name,
            area_id=r.area_id,
            salary_amount=r.salary_amount,
            salary_currency=r.salary_currency,
            url=r.url,
            work_format=r.work_format,
            skills=r.skills,
        )

    @classmethod
    def from_domain_list(cls, rs: list[Resume]) -> list["ResumeResponse"]:
        """Build a list of response DTOs from a list of domain resumes."""
        return [cls.from_domain(r) for r in rs]


class JobResponse(BaseModel):
    """Status and results of a parse job."""

    status: JobStatus
    id: int
    text: str
    area: int | None
    items_count: int
    created_at: datetime

    @classmethod
    def from_domain(cls, job: ParseJob) -> "JobResponse":
        """Build a response DTO from a domain ParseJob."""
        return cls(
            id=job.id,
            text=job.text,
            area=job.area,
            status=job.status.value,
            items_count=job.items_count,
            created_at=job.created_at,
        )

    @classmethod
    def from_domain_list(cls, jobs: list[ParseJob]) -> list["JobResponse"]:
        """Build a list of response DTOs from a list of domain jobs."""
        return [cls.from_domain(j) for j in jobs]


class ParseRequest(BaseModel):
    """Parameters for starting a parse job."""

    text: str = Field(min_length=1)
    area: int | None = None
    per_page: int = Field(20, ge=1, le=100)
    max_pages: int = Field(5, ge=1, le=50)
