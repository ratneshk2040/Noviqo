from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
import io

from app.database import get_db
from app.models import Note  # Aapka SQLAlchemy Note Model
from app.schemas import NoteCreate, NoteOut
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/api/notes", tags=["Notes"])


# 1. GET ALL NOTES
@router.get("", response_model=List[NoteOut])
def get_user_notes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    return db.query(Note).filter(Note.user_id == current_user.id).order_by(Note.created_at.desc()).all()


# 2. CREATE NOTE
@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    new_note = Note(
        user_id=current_user.id,
        question_id=note_data.question_id,
        title=note_data.title or "Untitled Note",
        content=note_data.content
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


# 3. DOWNLOAD SINGLE NOTE
@router.get("/{note_id}/download")
def download_single_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    file_content = f"Title: {note.title}\nDate: {note.created_at}\n\n{note.content}"
    return Response(
        content=file_content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={note.title or 'note'}.txt"}
    )


# 4. DOWNLOAD ALL NOTES
@router.get("/download-all")
def download_all_notes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    if not notes:
        raise HTTPException(status_code=404, detail="No notes available to download")

    combined_text = ""
    for idx, note in enumerate(notes, 1):
        combined_text += f"--- NOTE #{idx}: {note.title} ---\nDate: {note.created_at}\n\n{note.content}\n\n\n"

    return Response(
        content=combined_text,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=all_notes.txt"}
    )