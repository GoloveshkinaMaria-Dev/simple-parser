from datetime import datetime, UTC

from fastapi import APIRouter

from src.jobs.domain.value_objects import JobStatus
from src.jobs.schemas import JobResponse, ParseRequest, ResumeResponse


router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post(
    "",
    response_model=JobResponse,
    status_code=202,
    summary="Create a parse job",
)
async def create_job(request: ParseRequest) -> JobResponse:
    return JobResponse(
        id=1,
        text=request.text,
        status=JobStatus.PENDING,
        items_count=0,
        created_at=datetime.now(UTC),
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=200,
    summary="Get a job status",
)
async def get_job(job_id: int) -> JobResponse:
    return JobResponse(
        id=job_id,
        text="python",
        status=JobStatus.RUNNING,
        items_count=0,
        created_at=datetime.now(UTC),
    )


@router.get(
    "/{job_id}/resumes",
    response_model=list[ResumeResponse],
    status_code=200,
    summary="Get parsed resumes for a job",
)
async def get_job_resumes(job_id: int) -> list[ResumeResponse]:
    return []
