from fastapi import Request
from fastapi.responses import JSONResponse

from src.jobs.domain.exceptions import InvalidJobState, JobNotCompleted, JobNotFound


async def job_not_found_handler(request: Request, exc: JobNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def job_not_completed_handler(
    request: Request, exc: JobNotCompleted
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def invalid_job_state_handler(
    request: Request, exc: InvalidJobState
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
