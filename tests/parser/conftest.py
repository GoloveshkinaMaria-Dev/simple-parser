"""Fixtures for parser tests."""

import json
import shutil
from pathlib import Path

import pytest
from src.parser.schemas import (
    HHArea,
    HHResume,
    HHResumeSearchResponse,
    HHSalary,
    HHWorkFormat,
)
from src.parser.service import ParserService

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SEARCH_FIXTURES = FIXTURES_DIR / "search"
RESUME_FIXTURES = FIXTURES_DIR / "resume"


@pytest.fixture
def search_fixtures_dir() -> Path:
    """Path to HHResumeSearchResponse fixtures (wrappers with items)."""
    return SEARCH_FIXTURES


@pytest.fixture
def resume_fixtures_dir() -> Path:
    """Path to single HHResume fixtures (no wrapper)."""
    return RESUME_FIXTURES


@pytest.fixture
def resume_fixture() -> Path:
    """Path to a single HHResume JSON file."""
    return RESUME_FIXTURES / "hh_resume_one.json"


@pytest.fixture
def hh_area() -> HHArea:
    return HHArea(id="1", name="Москва")


@pytest.fixture
def hh_salary() -> HHSalary:
    return HHSalary(amount=200000, currency="RUR")


@pytest.fixture
def hh_work_format_remote() -> HHWorkFormat:
    return HHWorkFormat(id="REMOTE", name="Удалённо")


@pytest.fixture
def hh_work_format_hybrid() -> HHWorkFormat:
    return HHWorkFormat(id="HYBRID", name="Гибрид")


@pytest.fixture
def hh_resume_full(
    hh_area: HHArea,
    hh_salary: HHSalary,
    hh_work_format_remote: HHWorkFormat,
    hh_work_format_hybrid: HHWorkFormat,
) -> HHResume:
    """Full HHResume with all fields filled."""
    return HHResume(
        id="0123456789abcdef",
        title="Python-разработчик",
        first_name="Иван",
        last_name="Иванов",
        area=hh_area,
        salary=hh_salary,
        alternate_url="https://hh.ru/resume/0123456789abcdef",
        work_format=[hh_work_format_remote, hh_work_format_hybrid],
    )


@pytest.fixture
def hh_response() -> HHResumeSearchResponse:
    """HHResumeSearchResponse parsed from the real search-wrapper fixture."""
    path = SEARCH_FIXTURES / "hh_resume_search.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return HHResumeSearchResponse.model_validate(data)


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Copy only search wrappers into a tmp dir for isolated tests."""
    for src in SEARCH_FIXTURES.glob("*.json"):
        shutil.copy(src, tmp_path / src.name)
    return tmp_path


@pytest.fixture
def parser_service(tmp_data_dir: Path) -> ParserService:
    return ParserService(data_dir=tmp_data_dir)
