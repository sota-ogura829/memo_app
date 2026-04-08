from datetime import datetime

from pydantic import BaseModel, Field


class SearchMatchPosition(BaseModel):
    start: int
    end: int


class SearchNoteItem(BaseModel):
    id: int
    title: str
    matched_in: list[str]
    snippet: str | None
    updated_at: datetime


class SearchNotesResponse(BaseModel):
    query: str
    items: list[SearchNoteItem]
    total: int


class NoteInnerSearchResponse(BaseModel):
    note_id: int
    title: str
    query: str
    matched: bool
    positions: list[SearchMatchPosition] = Field(default_factory=list)
