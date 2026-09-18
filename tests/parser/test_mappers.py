from src.parser.mappers import hh_response_to_domain_list, hh_resume_to_domain
from src.parser.schemas import (
    HHResume,
    HHResumeSearchResponse,
    HHSalary,
    HHWorkFormat,
)


class TestHhResumeToDomain:
    def test_full(self, hh_resume_full: HHResume) -> None:
        result = hh_resume_to_domain(hh_resume_full)

        assert result.id == "0123456789abcdef"
        assert result.title == "Python-разработчик"
        assert result.first_name == "Иван"
        assert result.last_name == "Иванов"
        assert result.area == "Москва"
        assert result.salary_amount == 200000
        assert result.salary_currency == "RUR"
        assert result.url == "https://hh.ru/resume/0123456789abcdef"
        assert result.work_format == ["Удалённо", "Гибрид"]

    def test_no_area(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.area = None
        result = hh_resume_to_domain(hh_resume_full)
        assert result.area == ""

    def test_no_salary(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.salary = None
        result = hh_resume_to_domain(hh_resume_full)
        assert result.salary_amount is None
        assert result.salary_currency is None

    def test_salary_no_amount(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.salary = HHSalary(amount=None, currency=None)
        result = hh_resume_to_domain(hh_resume_full)
        assert result.salary_amount is None
        assert result.salary_currency is None

    def test_salary_zero(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.salary = HHSalary(amount=0, currency="RUR")
        result = hh_resume_to_domain(hh_resume_full)
        assert result.salary_amount == 0
        assert result.salary_currency == "RUR"

    def test_no_work_format(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.work_format = None
        result = hh_resume_to_domain(hh_resume_full)
        assert result.work_format == []

    def test_empty_work_format(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.work_format = []
        result = hh_resume_to_domain(hh_resume_full)
        assert result.work_format == []

    def test_no_first_name(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.first_name = None
        result = hh_resume_to_domain(hh_resume_full)
        assert result.first_name is None

    def test_no_last_name(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.last_name = None
        result = hh_resume_to_domain(hh_resume_full)
        assert result.last_name is None

    def test_multiple_work_formats(self, hh_resume_full: HHResume) -> None:
        hh_resume_full.work_format = [
            HHWorkFormat(id="REMOTE", name="Удалённо"),
            HHWorkFormat(id="HYBRID", name="Гибрид"),
            HHWorkFormat(id="OFFICE", name="Офис"),
        ]
        result = hh_resume_to_domain(hh_resume_full)
        assert result.work_format == ["Удалённо", "Гибрид", "Офис"]


class TestHhResponseToDomainList:
    def test_empty(self) -> None:
        response = HHResumeSearchResponse(
            items=[], found=0, pages=0, per_page=20, page=0
        )
        result = hh_response_to_domain_list(response)
        assert result == []

    def test_one_item(self, hh_resume_full: HHResume) -> None:
        response = HHResumeSearchResponse(
            items=[hh_resume_full], found=1, pages=1, per_page=20, page=0
        )
        result = hh_response_to_domain_list(response)
        assert len(result) == 1
        assert result[0].id == "0123456789abcdef"

    def test_multiple_items(self, hh_resume_full: HHResume) -> None:
        r2 = hh_resume_full.model_copy(update={"id": "second"})
        r3 = hh_resume_full.model_copy(update={"id": "third"})
        response = HHResumeSearchResponse(
            items=[hh_resume_full, r2, r3],
            found=3,
            pages=1,
            per_page=20,
            page=0,
        )
        result = hh_response_to_domain_list(response)
        assert len(result) == 3
        assert [r.id for r in result] == [
            "0123456789abcdef",
            "second",
            "third",
        ]

    def test_preserves_order(self, hh_resume_full: HHResume) -> None:
        ids = ["1", "2", "3"]
        items = [hh_resume_full.model_copy(update={"id": i}) for i in ids]
        response = HHResumeSearchResponse(
            items=items, found=3, pages=1, per_page=20, page=0
        )
        result = hh_response_to_domain_list(response)
        assert [r.id for r in result] == ids


class TestFromFixture:
    def test_parse_fixture(self, hh_response: HHResumeSearchResponse) -> None:
        assert hh_response.found == 3
        assert hh_response.pages == 1
        assert len(hh_response.items) == 3

    def test_map_fixture(self, hh_response: HHResumeSearchResponse) -> None:
        resumes = hh_response_to_domain_list(hh_response)

        assert len(resumes) == 3

        first, second, third = resumes

        assert first.area == "Москва"
        assert first.salary_amount == 200000
        assert first.salary_currency == "RUR"
        assert first.work_format == ["Удалённо", "Гибрид"]

        assert second.area == "Санкт-Петербург"
        assert second.salary_amount is None
        assert second.salary_currency is None

        assert third.area == ""
        assert third.work_format == []
        assert third.first_name is None
        assert third.last_name is None


class TestTypes:
    def test_id_is_str(self, hh_resume_full: HHResume) -> None:
        result = hh_resume_to_domain(hh_resume_full)
        assert isinstance(result.id, str)

    def test_work_format_is_list(self, hh_resume_full: HHResume) -> None:
        result = hh_resume_to_domain(hh_resume_full)
        assert isinstance(result.work_format, list)

    def test_salary_amount_is_int_or_none(
        self, hh_resume_full: HHResume
    ) -> None:
        result = hh_resume_to_domain(hh_resume_full)
        assert result.salary_amount is None or isinstance(result.salary_amount, int)