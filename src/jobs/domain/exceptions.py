"""Domain exceptions for parse jobs."""

class DomainError(Exception):
    """Base domain error."""


class JobNotFound(DomainError):
    """Parse job not found."""


class InvalidJobState(DomainError):
    """Operation not allowed in the current job state."""
