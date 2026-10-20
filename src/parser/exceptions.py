class ParseError(Exception):
    """Base exception for all parser errors."""


class Unavailable(ParseError):
    """Raised when the parser source is unavailable (network, 5xx)."""


class RateLimited(ParseError):
    """Raised when the parser source rate-limits requests (429)."""


class InvalidResponse(ParseError):
    """Raised when the response cannot be parsed or fails schema validation."""


class EmptyDataError(ParseError):
    """Raised when the response body or file is empty."""
