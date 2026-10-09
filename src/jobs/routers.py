from fastapi import APIRouter, Depends

from src.jobs.dependencies import get_parse_job_service
from src.jobs.schemas import JobResponse, ParseRequest, ResumeResponse
from src.jobs.service import ParseJobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobResponse,
    status_code=202,
    summary="Create a parse job",
)
async def create_job(
    request: ParseRequest, service: ParseJobService = Depends(get_parse_job_service)
) -> JobResponse:
    job = await service.create(text=request.text, area=request.area)
    return JobResponse.from_domain(job)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=200,
    responses={
        404: {"description": "Job not found"},
        409: {"description": "Invalid job state"},
    },
    summary="Get a job status",
)
async def get_job(
    job_id: int, service: ParseJobService = Depends(get_parse_job_service)
) -> JobResponse:
    job = await service.get(job_id)
    return JobResponse.from_domain(job)


@router.get(
    "/{job_id}/resumes",
    response_model=list[ResumeResponse],
    status_code=200,
    responses={
        404: {"description": "Job not found"},
        409: {"description": "Invalid job state"},
    },
    summary="Get parsed resumes for a job",
)
async def get_job_resumes(
    job_id: int, service: ParseJobService = Depends(get_parse_job_service)
) -> list[ResumeResponse]:
    resumes = await service.get_products(job_id)
    return ResumeResponse.from_domain_list(resumes)
