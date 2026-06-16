from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models.user import User
from models.notes import Note
from schemas.flashcard import NoteCreate, NoteUpdate
from middleware.auth import get_current_user
from services.ai_service import enhance_note

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/")
async def get_notes(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.username == current_user.username))
    notes = result.scalars().all()
    return [{"id": n.id, "title": n.title, "content": n.content, "subject": n.subject,
             "chapter": n.chapter, "tags": n.tags, "is_pinned": n.is_pinned, "color": n.color,
             "word_count": n.word_count, "created_at": n.created_at.isoformat(),
             "updated_at": n.updated_at.isoformat() if n.updated_at else None} for n in notes]

@router.post("/")
async def create_note(data: NoteCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    word_count = len((data.content or "").split())
    note = Note(
        username=current_user.username,
        title=data.title,
        content=data.content,
        subject=data.subject,
        chapter=data.chapter,
        tags=data.tags,
        color=data.color,
        word_count=word_count
    )
    db.add(note)
    await db.commit()
    return {"message": "Note created", "id": note.id}

@router.put("/{note_id}")
async def update_note(note_id: int, data: NoteUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id, Note.username == current_user.username))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    for field, value in data.dict(exclude_none=True).items():
        setattr(note, field, value)
    if data.content is not None:
        note.word_count = len(data.content.split())
    await db.commit()
    return {"message": "Note updated"}

@router.delete("/{note_id}")
async def delete_note(note_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Note).where(Note.id == note_id, Note.username == current_user.username))
    await db.commit()
    return {"message": "Note deleted"}

@router.post("/{note_id}/enhance")
async def enhance_note_ai(note_id: int, action: str = "improve", current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id, Note.username == current_user.username))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    result = await enhance_note(note.content or "", action)
    return {"enhanced_content": result, "action": action}
