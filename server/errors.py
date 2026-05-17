"""Standardized error responses for Yefai API."""

from fastapi import HTTPException


class YefaiError(HTTPException):
    """Base exception for Yefai API."""


class NotFoundError(YefaiError):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=404, detail=detail)


class ForbiddenError(YefaiError):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class UnauthorizedError(YefaiError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ConflictError(YefaiError):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=409, detail=detail)


class ValidationError(YefaiError):
    def __init__(self, detail: str = "Validation Error"):
        super().__init__(status_code=422, detail=detail)
