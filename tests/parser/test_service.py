"""Unit tests for ParserService (using real hh.ru fixtures)."""

import json

import pytest
from src.parser.domain.entities import Resume
from src.parser.exceptions import EmptyDataError, InvalidResponse
from src.parser.service import ParserService


class TestRead:
    def test_read_valid_fixture(self, parser_service, search_fixtures_dir) -> None:
        path = search_fixtures_dir / "hh_resume_search.json"
        response = parser_service.read(path)

        assert response.found == 3
        assert len(response.items) == 3
        assert response.items[0].title == "Python-разработчик"

    def test_read_missing_file_raises(self, parser_service, tmp_path) -> None:
        with pytest.raises(FileNotFoundError):
            parser_service.read(tmp_path / "missing.json")

    def test_read_empty_file_raises(self, parser_service, tmp_path) -> None:
        path = tmp_path / "empty.json"
        path.write_text("", encoding="utf-8")
        with pytest.raises(EmptyDataError):
            parser_service.read(path)

    def test_read_whitespace_file_raises(self, parser_service, tmp_path) -> None:
        path = tmp_path / "ws.json"
        path.write_text("   \n  ", encoding="utf-8")
        with pytest.raises(EmptyDataError):
            parser_service.read(path)

    def test_read_invalid_json_raises(self, parser_service, tmp_path) -> None:
        path = tmp_path / "broken.json"
        path.write_text("{ not valid json", encoding="utf-8")
        with pytest.raises(InvalidResponse):
            parser_service.read(path)

    def test_read_wrong_schema_raises(self, parser_service, tmp_path) -> None:
        path = tmp_path / "wrong.json"
        path.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
        with pytest.raises(InvalidResponse):
            parser_service.read(path)


class TestReadAll:
    def test_read_all_two_fixtures(self, parser_service) -> None:
        responses = parser_service.read_all()
        assert len(responses) == 2

    def test_read_all_empty_dir(self, tmp_path) -> None:
        service = ParserService(data_dir=tmp_path)
        assert service.read_all() == []

    def test_read_all_skips_invalid_when_flag_false(
        self, tmp_path, search_fixtures_dir
    ) -> None:
        from src.parser.exceptions import InvalidResponse, ParseError

        print(
            f"DEBUG: InvalidResponse is subclass of ParseError: {issubclass(InvalidResponse, ParseError)}"
        )
        print(f"DEBUG: InvalidResponse.__mro__: {InvalidResponse.__mro__}")
        print(f"DEBUG: ParseError.__module__: {ParseError.__module__}")
        (tmp_path / "valid.json").write_bytes(
            (search_fixtures_dir / "hh_resume_search.json").read_bytes()
        )
        (tmp_path / "broken.json").write_text("{ broken", encoding="utf-8")

        service = ParserService(data_dir=tmp_path, fail_on_invalid=False)

        # отладка
        from src.parser.exceptions import ParseError as PE
        from src.parser.service import ParseError as SPE

        print(f"DEBUG: PE is SPE = {PE is SPE}")
        print(f"DEBUG: fail_on_invalid = {service.fail_on_invalid}")

        responses = service.read_all()
        print(f"DEBUG: len(responses) = {len(responses)}")

        assert len(responses) == 1


class TestSearchAll:
    def test_search_all_returns_resumes(self, parser_service) -> None:
        resumes = parser_service.search_all()
        assert len(resumes) == 3
        assert all(isinstance(r, Resume) for r in resumes)

    def test_search_all_empty_dir(self, tmp_path) -> None:
        service = ParserService(data_dir=tmp_path)
        assert service.search_all() == []

    def test_search_all_from_fixture_fields(
        self, tmp_path, search_fixtures_dir
    ) -> None:
        (tmp_path / "search.json").write_bytes(
            (search_fixtures_dir / "hh_resume_search.json").read_bytes()
        )
        service = ParserService(data_dir=tmp_path)

        resumes = service.search_all()
        assert len(resumes) == 3

        # первое резюме, полное
        first = resumes[0]
        assert first.id == "0123456789abcdef"
        assert first.title == "Python-разработчик"
        assert first.area == "Москва"
        assert first.salary_amount == 200000
        assert first.salary_currency == "RUR"
        assert first.work_format == ["Удалённо", "Гибрид"]

        # второе, без salary
        second = resumes[1]
        assert second.area == "Санкт-Петербург"
        assert second.salary_amount is None
        assert second.salary_currency is None

        # третье, без area / work_format
        third = resumes[2]
        assert third.area == ""
        assert third.work_format == []
        assert third.first_name is None
        assert third.last_name is None
