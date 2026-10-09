import logging

from src.jobs.domain.entities import ParseJob
from src.jobs.domain.exceptions import JobNotCompleted, JobNotFound
from src.jobs.domain.value_objects import JobStatus
from src.jobs.repository import JobRepository
from src.parser.domain.entities import Resume
from src.parser.exceptions import ParseError
from src.parser.service import ParserService

logger = logging.getLogger(__name__)  # TODO: do basicConfig in main in future


class ParseJobService:
    def __init__(
        self, repo: JobRepository, parser: ParserService, event_bus=None
    ) -> None:
        self.repo = repo
        self.parser = parser
        self.event_bus = event_bus

    async def create(self, text: str, area: int | None = None) -> ParseJob:
        job = ParseJob(text=text, area=area)
        await self.repo.save(job)
        return job

    async def get(self, job_id: int) -> ParseJob:
        job = await self.repo.get(job_id)
        if job is None:
            raise JobNotFound(f"Job {job_id} not found")
        return job

    async def run(self, job_id: int) -> None:
        job = await self.get(job_id)
        job.start()
        await self.repo.save(job)
        try:
            resumes = self.parser.search_all()
            job.complete(items_count=len(resumes))
        except ParseError as e:
            logger.warning("Job %s failed during parsing: %s", job_id, e)
            job.fail(reason=str(e))

        await self.repo.save(job)
        events = job.pull_events()
        if self.event_bus is None:
            logger.warning(
                "event_bus is not set, %d events for job %s will be dropped",
                len(job._events),
                job_id,
            )
        else:
            for event in events:
                try:
                    await self.event_bus.publish(event)
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        "Failed to publish %s for job %s: %s",
                        type(event).__name__,
                        job_id,
                        e,
                    )

    async def get_products(self, job_id: int) -> list[Resume]:
        job = await self.get(job_id)
        if job.status != JobStatus.COMPLETED:
            raise JobNotCompleted(f"Job {job_id} is not completed yet")
        return []  # resume table
