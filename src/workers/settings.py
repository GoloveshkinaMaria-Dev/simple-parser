from typing import ClassVar

from arq.connections import RedisSettings

from src.config import settings
from src.logging_config import configure_logging
from src.workers.tasks import parse_job_task


async def on_startup(ctx) -> None:
    configure_logging()


class WorkerSettings:
    functions: ClassVar[list] = [parse_job_task]
    redis_settings = RedisSettings.from_dsn(str(settings.REDIS_URL))
    job_timeout = 300
    max_tries = 1
