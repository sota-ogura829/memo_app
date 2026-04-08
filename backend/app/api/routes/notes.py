from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.note import NoteCreate, NoteDetailResponse, NoteListResponse, NoteUpdate
from app.services.note_service import create_note, delete_note, get_note_detail, list_notes, update_note


router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=NoteListResponse)
def get_notes(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    title: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteListResponse:
    return list_notes(db, current_user, page=page, per_page=per_page, title=title)


@router.get("/{note_id}", response_model=NoteDetailResponse)
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> NoteDetailResponse:
    return get_note_detail(db, note_id, current_user)


@router.post("", response_model=NoteDetailResponse, status_code=status.HTTP_201_CREATED)
def create_note_route(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteDetailResponse:
    return create_note(db, payload, current_user)


@router.put("/{note_id}", response_model=NoteDetailResponse)
def update_note_route(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteDetailResponse:
    return update_note(db, note_id, payload, current_user)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_route(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    delete_note(db, note_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
