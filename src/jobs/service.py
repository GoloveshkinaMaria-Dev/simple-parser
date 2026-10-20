import logging

from src.jobs.domain.entities import ParseJob
from src.jobs.domain.exceptions import JobNotCompleted, JobNotFound
from src.jobs.domain.value_objects import JobStatus
from src.jobs.repository import JobRepository
from src.parser.domain.entities import Resume
from src.parser.exceptions import ParseError
from src.parser.service import ParserService
from src.resumes.repository import ResumeRepository

logger = logging.getLogger(__name__)


class ParseJobService:
    """Application service for parse job use cases: create, run, retrieve."""

    def __init__(
        self,
        repo: JobRepository,
        resume_repo: ResumeRepository,
        parser: ParserService,
        event_bus=None,
    ) -> None:
        self.repo = repo
        self.resume_repo = resume_repo
        self.parser = parser
        self.event_bus = event_bus

    async def create(self, text: str, area: int | None = None) -> ParseJob:
        """Create a new parse job in PENDING state and persist it."""
        job = ParseJob(text=text, area=area)
        await self.repo.save(job)
        return job

    async def get(self, job_id: int) -> ParseJob:
        """Return the job by id, or raise JobNotFound if it does not exist."""
        job = await self.repo.get(job_id)
        if job is None:
            raise JobNotFound(f"Job {job_id} not found")
        return job

    async def run(self, job_id: int) -> None:
        """Execute the parsing flow: start → parse → save → complete/fail.

        Idempotent: skips if the job is not in PENDING state.
        Publishes accumulated domain events after saving the final state.
        """
        job = await self.get(job_id)
        if job.status is not JobStatus.PENDING:
            logger.info(
                "job %s is in %s, skipping run",
                job_id,
                job.status,
            )
            return
        job.start()
        await self.repo.save(job)
        try:
            resumes = self.parser.search_all()
            await self.resume_repo.save_many(resumes, job_id=job_id)
            job.complete(items_count=len(resumes))
        except ParseError as e:
            logger.warning("Job %s failed during parsing: %s", job_id, e)
            job.fail(reason=str(e))

        await self.repo.save(job)
        events = job.pull_events()
        if self.event_bus is None:
            logger.warning(
                "event_bus is not set, %d events for job %s will be dropped",
                len(events),
                job_id,
            )
        else:
            for event in events:
                try:
                    await self.event_bus.publish(event)
                except Exception as e:
                    logger.warning(
                        "Failed to publish %s for job %s: %s",
                        type(event).__name__,
                        job_id,
                        e,
                    )

    async def get_products(self, job_id: int) -> list[Resume]:
        """Return parsed resumes for a completed job; raise JobNotCompleted otherwise."""
        job = await self.get(job_id)
        if job.status != JobStatus.COMPLETED:
            raise JobNotCompleted(f"Job {job_id} is not completed yet")
        return await self.resume_repo.list_by_job(job_id)
