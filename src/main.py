import logging
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from src.config import settings
from src.exceptions import *
from src.jobs.models import ParseJobORM  # noqa: F401
from src.jobs.routers import router as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.arq = await create_pool(RedisSettings.from_dsn(str(settings.REDIS_URL)))
    yield
    await app.state.arq.close()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(
    lifespan=lifespan,
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
