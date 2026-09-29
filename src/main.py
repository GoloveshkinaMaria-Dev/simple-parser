from fastapi import FastAPI

from src.jobs.router import router as jobs_router
from src.jobs.models import ParseJobORM  # noqa: F401

app_configs = {"title": "Parser Service"}
# if settings.ENVIRONMENT not in ("local", "staging"):
    # app_configs["openapi_url"] = None

app = FastAPI(**app_configs)
@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(jobs_router)
