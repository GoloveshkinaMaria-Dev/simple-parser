from pathlib import Path

import pytest
from src.parser.schemas import (
    HHArea,
    HHResume,
    HHResumeSearchResponse,
    HHSalary,
    HHWorkFormat,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


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
    """Полное резюме со всеми заполненными полями."""
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
def hh_resume_search_json_path() -> Path:
    return FIXTURES_DIR / "hh_resume_search.json"


@pytest.fixture
def hh_response(hh_resume_search_json_path: Path) -> HHResumeSearchResponse:
    """Ответ API hh.ru, прочитанный из JSON-мока."""
    import json

    data = json.loads(hh_resume_search_json_path.read_text(encoding="utf-8"))
    return HHResumeSearchResponse.model_validate(data)