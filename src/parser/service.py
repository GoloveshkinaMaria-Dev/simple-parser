import logging
from pathlib import Path

from pydantic import ValidationError

from src.parser.config import parser_settings
from src.parser.domain.entities import Resume
from src.parser.exceptions import EmptyDataError, InvalidResponse, ParseError
from src.parser.mappers import hh_response_to_domain_list
from src.parser.schemas import HHResumeSearchResponse

logger = logging.getLogger(__name__)


class ParserService:
    """Service for reading and parsing hh.ru JSON files."""

    def __init__(
        self,
        data_dir: Path | None = None,
        fail_on_invalid: bool | None = None,
    ) -> None:
        self.data_dir = data_dir or parser_settings.data_dir
        self.fail_on_invalid = (
            fail_on_invalid if fail_on_invalid is not None else parser_settings.fail_on_invalid
        )

    def read(self, path: Path) -> HHResumeSearchResponse:
        """Read and validate a single JSON file into a search response."""
        with open(path, encoding=parser_settings.encoding) as file:
            content = file.read()
            if not content.strip():
                raise EmptyDataError(f"Empty file: {path}")
            try:
                response = HHResumeSearchResponse.model_validate_json(content)
            except ValidationError as e:
                logger.warning("Invalid JSON in %s: %s", path, e)
                raise InvalidResponse(f"Invalid JSON in {path}") from e

            return response

    def read_all(self) -> list[HHResumeSearchResponse]:
        """Read all JSON files from the configured data directory."""
        files = sorted(self.data_dir.glob(parser_settings.file_glob))
        results = []
        for path in files:
            if self.fail_on_invalid:
                results.append(self.read(path))
            else:
                try:
                    results.append(self.read(path))
                except ParseError as e:
                    logger.warning("Skipping %s: %s", path, e)
        logger.info("Read %d responses from %s", len(results), self.data_dir)
        return results

    def search_all(self) -> list[Resume]:
        """Parse all JSON files and return a flat list of domain resumes."""
        files = self.read_all()
        results = []
        for response in files:
            results.extend(hh_response_to_domain_list(response))
        logger.info("Parsed %d resumes", len(results))
        return results
