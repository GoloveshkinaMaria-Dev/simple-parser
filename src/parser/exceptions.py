class ParseError(Exception):
    pass


class Unavailable(Exception):
    pass


class RateLimited(Exception):
    pass


class InvalidResponse(ParseError):
    pass


class EmptyDataError(ParseError):
    pass
