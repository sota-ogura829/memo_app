from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.user import User
from app.schemas.search import NoteInnerSearchResponse, SearchMatchPosition, SearchNoteItem, SearchNotesResponse
from app.services.note_service import _extract_content, get_owned_note


def _build_snippet(text: str, query: str, radius: int = 24) -> str:
    lower_text = text.lower()
    lower_query = query.lower()
    index = lower_text.find(lower_query)
    if index < 0:
        return text[: radius * 2]
    start = max(index - radius, 0)
    end = min(index + len(query) + radius, len(text))
    return text[start:end]


def search_notes(db: Session, user: User, query: str, page: int = 1, per_page: int = 20) -> SearchNotesResponse:
    normalized_query = query.strip()
    lowered_query = normalized_query.lower()
    notes = db.scalars(select(Note).where(Note.user_id == user.id).order_by(Note.updated_at.desc())).all()

    matched_items: list[SearchNoteItem] = []
    for note in notes:
        matched_in: list[str] = []
        snippet = None
        if lowered_query in note.title.lower():
            matched_in.append("title")

        text, _ = _extract_content(note)
        if text and lowered_query in text.lower():
            matched_in.append("text")
            snippet = _build_snippet(text, normalized_query)

        if matched_in:
            matched_items.append(
                SearchNoteItem(
                    id=note.id,
                    title=note.title,
                    matched_in=matched_in,
                    snippet=snippet,
                    updated_at=note.updated_at,
                )
            )

    total = len(matched_items)
    start = (page - 1) * per_page
    end = start + per_page
    return SearchNotesResponse(query=normalized_query, items=matched_items[start:end], total=total)


def search_within_note(db: Session, user: User, note_id: int, query: str) -> NoteInnerSearchResponse:
    note = get_owned_note(db, note_id, user)
    normalized_query = query.strip()
    text, _ = _extract_content(note)
    if not text or not normalized_query:
        return NoteInnerSearchResponse(note_id=note.id, title=note.title, query=normalized_query, matched=False)

    positions: list[SearchMatchPosition] = []
    lowered_text = text.lower()
    lowered_query = normalized_query.lower()
    start_index = 0
    while True:
        index = lowered_text.find(lowered_query, start_index)
        if index == -1:
            break
        positions.append(SearchMatchPosition(start=index, end=index + len(normalized_query)))
        start_index = index + len(normalized_query)

    return NoteInnerSearchResponse(
        note_id=note.id,
        title=note.title,
        query=normalized_query,
        matched=bool(positions),
        positions=positions,
    )
