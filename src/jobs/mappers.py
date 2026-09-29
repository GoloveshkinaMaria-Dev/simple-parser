from src.jobs.domain.entities import ParseJob
from src.jobs.domain.value_objects import JobStatus
from src.jobs.models import ParseJobORM


def parse_job_to_orm(job: ParseJob) -> ParseJobORM:
    """Map domain ParseJob to ORM model."""
    return ParseJobORM(
        id=job.id,
        text=job.text,
        area=job.area,
        status=job.status.value,
        items_count=job.items_count,
        per_page=job.per_page,
        max_pages=job.max_pages,
        error=job.error,
        created_at=job.created_at,
    )


def orm_to_parse_job(job_orm: ParseJobORM) -> ParseJob:
    """Map ORM model to domain ParseJob."""
    return ParseJob(
        id=job_orm.id,
        text=job_orm.text,
        area=job_orm.area,
        status=JobStatus(job_orm.status),
        items_count=job_orm.items_count,
        per_page=job_orm.per_page,
        max_pages=job_orm.max_pages,
        error=job_orm.error,
        created_at=job_orm.created_at,
    )
