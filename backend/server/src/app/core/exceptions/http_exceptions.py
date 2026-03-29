from fastapi import HTTPException


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=403, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(status_code=404, detail=detail)


class DuplicateValueException(HTTPException):
    def __init__(self, detail: str = "Duplicate value") -> None:
        super().__init__(status_code=409, detail=detail)


class RateLimitException(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(status_code=429, detail=detail)
