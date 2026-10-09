from fastapi import FastAPI

from src.config import settings
from src.jobs.models import ParseJobORM  # noqa: F401
from src.jobs.routers import router as jobs_router
from src.exceptions import *

app = FastAPI(
    title="Parser Service",
    openapi_url=(
        None if settings.ENVIRONMENT not in ("local", "staging") else "/openapi.json"
    ),
)

app.include_router(jobs_router)
app.add_exception_handler(JobNotFound, job_not_found_handler)  # type: ignore[arg-type]
app.add_exception_handler(JobNotCompleted, job_not_completed_handler)  # type: ignore[arg-type]
app.add_exception_handler(InvalidJobState, invalid_job_state_handler)  # type: ignore[arg-type]


@app.get("/health")
async def health():
    return {"status": "ok"}
