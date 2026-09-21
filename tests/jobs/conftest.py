import pytest

from src.jobs.domain.entities import ParseJob


@pytest.fixture
def job() -> ParseJob:
    return ParseJob(id=1, text="python", area=1)
