from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    status,
    Query,
    Form
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Upload, Question
from app.schemas import QuestionOut, QuestionDetailOut
from app.routers.auth import get_current_active_user
from app.services.file_processing import (
    save_upload_file,
    extract_text_from_pdf,
    extract_text_from_image,
    detect_questions
)
from app.services.ai_service import explain_question

router = APIRouter(prefix="/api/upload", tags=["Uploads"])

print("UPLOAD ROUTER LOADED")


# --- 1. SEARCH ROUTE (Placed before dynamic routes to prevent path conflicts) ---
@router.get(
    "/search",
    response_model=List[QuestionOut]
)
def search_questions(
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = (
        db.query(Question)
        .join(Upload)
        .filter(Upload.user_id == current_user.id)
    )

    if subject:
        query = query.filter(Upload.subject.ilike(f"%{subject}%"))

    if topic:
        query = query.filter(Question.topic.ilike(f"%{topic}%"))

    if keyword:
        query = query.filter(Question.question_text.ilike(f"%{keyword}%"))

    return query.order_by(Question.created_at.desc()).all()


# --- 2. UPLOAD FILE ROUTE ---
@router.post(
    "/upload",
    response_model=List[QuestionOut]
)
def upload_file(
    category: str = Form(...),
    subject: str = Form(...),
    year: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    print("UPLOAD FUNCTION STARTED")

    allowed_types = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and image files are allowed"
        )

    try:
        file_path = save_upload_file(file)

        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_image(file_path)

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text found in file"
            )

        upload = Upload(
            filename=file.filename,
            content_type=file.content_type,
            exam=category,
            subject=subject,
            year=year,
            text=text,
            user_id=current_user.id
        )

        db.add(upload)
        db.commit()
        db.refresh(upload)

        question_texts = detect_questions(text)
        print("========== EXTRACTED TEXT ==========")
        print(text[:1000])
        print("========== QUESTIONS FOUND ==========")
        print(f"TOTAL QUESTIONS: {len(question_texts)}")
        
        if not question_texts:
            raise HTTPException(
                status_code=400,
                detail="No questions detected from uploaded file"
            )

        questions_to_create = []

        print("ENTERING QUESTION LOOP")

        for q_text in question_texts:
            print("GENERATING AI:", q_text[:100])
            ai_data = explain_question(q_text)

            question = Question(
                upload_id=upload.id,
                question_text=q_text,
                explanation=ai_data.get("explanation", ""),
                answer=ai_data.get("answer", ""),
                notes=ai_data.get("short_notes", "")
            )
            questions_to_create.append(question)

        # Batch insert all questions in a single transaction
        db.add_all(questions_to_create)
        db.commit()

        for q in questions_to_create:
            db.refresh(q)

        print("QUESTIONS SAVED SUCCESSFULLY")
        return questions_to_create

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print("UPLOAD ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --- 3. DYNAMIC PARAMETER ROUTES ---
@router.get(
    "/{upload_id}/questions",
    response_model=List[QuestionOut]
)
def get_upload_questions(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    upload = (
        db.query(Upload)
        .filter(
            Upload.id == upload_id,
            Upload.user_id == current_user.id
        )
        .first()
    )

    if not upload:
        raise HTTPException(
            status_code=404,
            detail="Upload not found"
        )

    return upload.questions


@router.get(
    "/question/{question_id}",
    response_model=QuestionDetailOut
)
def get_question_detail(
    question_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    question = (
        db.query(Question)
        .join(Upload)
        .filter(
            Question.id == question_id,
            Upload.user_id == current_user.id
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    return QuestionDetailOut(
        id=question.id,
        upload_id=question.upload_id,
        question_text=question.question_text,
        explanation=question.explanation,
        answer=question.answer,
        notes=question.notes,
        topic=question.topic,
        exam=question.upload.exam,
        subject=question.upload.subject,
        year=question.upload.year
    )