from typing import ClassVar

from arq.connections import RedisSettings

from src.config import settings
from src.workers.tasks import parse_job_task


class WorkerSettings:
    functions: ClassVar[list] = [parse_job_task]
    redis_settings = RedisSettings.from_dsn(str(settings.REDIS_URL))
    job_timeout = 300
    max_tries = 1
