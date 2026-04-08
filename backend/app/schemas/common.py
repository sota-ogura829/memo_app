from pydantic import BaseModel


class FieldError(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    detail: str | list[FieldError]


class PaginationResponse(BaseModel):
    page: int
    per_page: int
    total: int
