from fastapi import FastAPI

from src.config import settings
from src.jobs.models import ParseJobORM  # noqa: F401
from src.jobs.router import router as jobs_router


app = FastAPI(
    title="Parser Service",
    openapi_url=(
        None
        if settings.ENVIRONMENT not in ("local", "staging")
        else "/openapi.json"

    ),
)

app.include_router(jobs_router)

@app.get("/health")
async def health():
    return {"status": "ok"}