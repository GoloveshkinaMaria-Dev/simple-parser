from datetime import datetime

from pydantic import BaseModel, Field

from .domain.value_objects import JobStatus


class ResumeResponse(BaseModel):
    """Resume data returned by the API."""
    id: str
    title: str
    area: str
    salary_amount: int | None
    salary_currency: str | None
    url: str
    work_format: list[str]


class JobResponse(BaseModel):
    """Status and results of a parse job."""
    status: JobStatus
    id: int
    text: str
    items_count: int
    created_at: datetime


class ParseRequest(BaseModel):
    """Parameters for starting a parse job."""
    text: str
    area: int | None = None
    per_page: int = Field(20, ge=1, le=100)
    max_pages: int = Field(5, ge=1, le=50)
