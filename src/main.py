from fastapi import FastAPI
from src.config import settings


app_configs = {"title": "Parser Service"}
# if settings.ENVIRONMENT not in ("local", "staging"):
    # app_configs["openapi_url"] = None

app = FastAPI(**app_configs)
@app.get("/health")
async def health():
    return {"status": "ok"}
