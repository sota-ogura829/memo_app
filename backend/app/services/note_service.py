from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.user import User
from app.schemas.common import PaginationResponse
from app.schemas.note import ContentFormat, NoteCreate, NoteDetailResponse, NoteListItem, NoteListResponse, NoteUpdate
from app.security.encryption import decrypt_note_payload, encrypt_note_payload


def _extract_content(note: Note) -> tuple[str | None, ContentFormat | None]:
    if note.contents_encrypted is None:
        return None, None

    payload = decrypt_note_payload(note.contents_encrypted)
    raw_format = payload.get("format") or note.content_format
    content_format = ContentFormat(raw_format) if raw_format else None
    return payload.get("text"), content_format


def _to_list_item(note: Note) -> NoteListItem:
    return NoteListItem(
        id=note.id,
        title=note.title,
        has_content=note.contents_encrypted is not None,
        content_format=ContentFormat(note.content_format) if note.content_format else None,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def _to_detail(note: Note) -> NoteDetailResponse:
    text, content_format = _extract_content(note)
    return NoteDetailResponse(
        id=note.id,
        title=note.title,
        text=text,
        content_format=content_format,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def get_owned_note(db: Session, note_id: int, user: User) -> Note:
    note = db.scalar(select(Note).where(Note.id == note_id, Note.user_id == user.id))
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="note not found")
    return note


def list_notes(db: Session, user: User, page: int = 1, per_page: int = 20, title: str | None = None) -> NoteListResponse:
    base_query = select(Note).where(Note.user_id == user.id)
    if title:
        base_query = base_query.where(Note.title.ilike(f"%{title.strip()}%"))

    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    notes = db.scalars(
        base_query.order_by(Note.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
    ).all()

    return NoteListResponse(
        items=[_to_list_item(note) for note in notes],
        pagination=PaginationResponse(page=page, per_page=per_page, total=total),
    )


def get_note_detail(db: Session, note_id: int, user: User) -> NoteDetailResponse:
    note = get_owned_note(db, note_id, user)
    return _to_detail(note)


def create_note(db: Session, payload: NoteCreate, user: User) -> NoteDetailResponse:
    encrypted = None
    content_format = None
    if payload.text is not None:
        content_format = payload.content_format.value if payload.content_format else ContentFormat.PLAIN.value
        encrypted = encrypt_note_payload({"format": content_format, "text": payload.text})

    note = Note(
        user_id=user.id,
        title=payload.title,
        contents_encrypted=encrypted,
        content_format=content_format,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return _to_detail(note)


def update_note(db: Session, note_id: int, payload: NoteUpdate, user: User) -> NoteDetailResponse:
    note = get_owned_note(db, note_id, user)
    note.title = payload.title

    if payload.text is None:
        note.contents_encrypted = None
        note.content_format = None
    else:
        note.content_format = payload.content_format.value if payload.content_format else ContentFormat.PLAIN.value
        note.contents_encrypted = encrypt_note_payload({"format": note.content_format, "text": payload.text})

    db.add(note)
    db.commit()
    db.refresh(note)
    return _to_detail(note)


def delete_note(db: Session, note_id: int, user: User) -> None:
    note = get_owned_note(db, note_id, user)
    db.delete(note)
    db.commit()
