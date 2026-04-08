from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.search import NoteInnerSearchResponse, SearchNotesResponse
from app.services.search_service import search_notes, search_within_note


router = APIRouter(tags=["search"])


@router.get("/search/notes", response_model=SearchNotesResponse)
def search_notes_route(
    q: str = Query(min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchNotesResponse:
    return search_notes(db, current_user, q, page=page, per_page=per_page)


@router.get("/notes/{note_id}/search", response_model=NoteInnerSearchResponse)
def search_within_note_route(
    note_id: int,
    q: str = Query(min_length=1, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteInnerSearchResponse:
    return search_within_note(db, current_user, note_id, q)
