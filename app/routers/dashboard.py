import io
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import get_current_active_user
from app.models import (
    Upload,
    Question,
    Bookmark,
    Note,
    PracticeSession,
    PracticeAnswer
)
from app.schemas import (
    BookmarkOut,
    NoteCreate,
    NoteOut,
    PracticeSessionCreate,
    PracticeSessionOut
)


router = APIRouter()



# Dashboard Summary
@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    uploads_count = (
        db.query(Upload)
        .filter(
            Upload.user_id == current_user.id
        )
        .count()
    )


    questions_count = (
        db.query(Question)
        .join(Upload)
        .filter(
            Upload.user_id == current_user.id
        )
        .count()
    )


    bookmarks_count = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == current_user.id
        )
        .count()
    )


    notes_count = (
        db.query(Note)
        .filter(
            Note.user_id == current_user.id
        )
        .count()
    )


    recent_uploads = (
        db.query(Upload)
        .filter(
            Upload.user_id == current_user.id
        )
        .order_by(
            Upload.created_at.desc()
        )
        .limit(5)
        .all()
    )


    return {
        "uploads_count": uploads_count,
        "questions_count": questions_count,
        "bookmarks_count": bookmarks_count,
        "notes_count": notes_count,

        "recent_uploads": [
            {
                "id": upload.id,
                "filename": upload.filename,
                "exam": upload.exam,
                "subject": upload.subject,
                "year": upload.year,
                "created_at": upload.created_at
            }

            for upload in recent_uploads
        ]
    }




# Get Bookmarks
@router.get(
    "/bookmarks",
    response_model=List[BookmarkOut]
)
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    return (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == current_user.id
        )
        .all()
    )




# Add Bookmark
@router.post(
    "/bookmarks/{question_id}",
    response_model=BookmarkOut
)
def add_bookmark(
    question_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    existing = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == current_user.id,
            Bookmark.question_id == question_id
        )
        .first()
    )


    if existing:
        raise HTTPException(
            status_code=400,
            detail="Question already bookmarked"
        )


    bookmark = Bookmark(
        user_id=current_user.id,
        question_id=question_id
    )


    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return bookmark




# Notes
@router.get(
    "/notes",
    response_model=List[NoteOut]
)
def get_notes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    return (
        db.query(Note)
        .filter(
            Note.user_id == current_user.id
        )
        .order_by(
            Note.created_at.desc()
        )
        .all()
    )




# Create Note
@router.post(
    "/notes",
    response_model=NoteOut
)
def create_note(
    note_create: NoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    note = Note(
        user_id=current_user.id,
        question_id=note_create.question_id,
        title=note_create.title,
        content=note_create.content
    )


    db.add(note)
    db.commit()
    db.refresh(note)

    return note




# Download Single Note
@router.get("/notes/{note_id}/download")
def download_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    note = (
        db.query(Note)
        .filter(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
        .first()
    )


    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )


    created_time = (
        note.created_at.isoformat()
        if note.created_at
        else ""
    )


    content = (
        f"Title: {note.title or 'Untitled'}\n"
        f"Question ID: {note.question_id or 'N/A'}\n"
        f"Created At: {created_time}\n\n"
        f"{note.content}"
    )


    file = io.BytesIO(
        content.encode("utf-8")
    )


    return StreamingResponse(
        file,
        media_type="text/plain",
        headers={
            "Content-Disposition":
            f"attachment; filename=note_{note.id}.txt"
        }
    )




# Download All Notes
@router.get("/notes/download-all")
def download_all_notes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    notes = (
        db.query(Note)
        .filter(
            Note.user_id == current_user.id
        )
        .order_by(
            Note.created_at.desc()
        )
        .all()
    )


    if not notes:
        raise HTTPException(
            status_code=404,
            detail="No notes available"
        )


    content = ""


    for note in notes:

        content += (
            f"Title: {note.title or 'Untitled'}\n"
            f"Question ID: {note.question_id or 'N/A'}\n"
            f"{note.content}\n"
            "\n-----------------\n\n"
        )


    file = io.BytesIO(
        content.encode("utf-8")
    )


    return StreamingResponse(
        file,
        media_type="text/plain",
        headers={
            "Content-Disposition":
            "attachment; filename=all_notes.txt"
        }
    )




# Practice Session
@router.post(
    "/practice",
    response_model=PracticeSessionOut
)
def create_practice_session(
    session_data: PracticeSessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    practice = PracticeSession(
        user_id=current_user.id,
        upload_id=session_data.upload_id,
        score=session_data.score,
        total_questions=session_data.total_questions,
        correct_count=session_data.correct_count,
        wrong_count=session_data.wrong_count
    )


    db.add(practice)
    db.commit()
    db.refresh(practice)



    for answer_data in session_data.answers:

        answer = PracticeAnswer(
            session_id=practice.id,
            question_id=answer_data.question_id,
            selected_option=answer_data.selected_option,
            is_correct=answer_data.is_correct,
            feedback=answer_data.feedback
        )

        db.add(answer)


    db.commit()

    return practice




# Practice History
@router.get(
    "/practice/history",
    response_model=List[PracticeSessionOut]
)
def get_practice_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    return (
        db.query(PracticeSession)
        .filter(
            PracticeSession.user_id == current_user.id
        )
        .order_by(
            PracticeSession.created_at.desc()
        )
        .all()
    )




# Progress Report
@router.get("/progress")
def get_progress_report(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    sessions = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.user_id == current_user.id
        )
        .all()
    )


    total_sessions = len(sessions)

    total_questions = sum(
        session.total_questions
        for session in sessions
    )


    correct_answers = sum(
        session.correct_count
        for session in sessions
    )


    accuracy = (
        correct_answers / total_questions * 100
        if total_questions
        else 0
    )


    return {
        "total_sessions": total_sessions,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "accuracy_percentage": round(
            accuracy,
            2
        ),
        "weak_topics": []
    }