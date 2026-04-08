from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import PaginationResponse


class ContentFormat(str, Enum):
    PLAIN = "plain"
    MARKDOWN = "markdown"


class NotePayloadBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    text: str | None = None
    content_format: ContentFormat | None = ContentFormat.PLAIN

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("title must not be empty")
        return normalized

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.strip() == "":
            return None
        return value

    @model_validator(mode="after")
    def align_content_fields(self) -> "NotePayloadBase":
        if self.text is None:
            self.content_format = None
        elif self.content_format is None:
            self.content_format = ContentFormat.PLAIN
        return self


class NoteCreate(NotePayloadBase):
    pass


class NoteUpdate(NotePayloadBase):
    pass


class NoteListItem(BaseModel):
    id: int
    title: str
    has_content: bool
    content_format: ContentFormat | None
    created_at: datetime
    updated_at: datetime


class NoteDetailResponse(BaseModel):
    id: int
    title: str
    text: str | None
    content_format: ContentFormat | None
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    items: list[NoteListItem]
    pagination: PaginationResponse
