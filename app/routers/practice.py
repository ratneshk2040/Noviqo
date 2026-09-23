from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Upload,
    Question,
    PracticeSession,
    PracticeAnswer
)

from app.schemas import (
    PracticeQuizRequest,
    PracticeQuizItem,
    MCQOption,
    PracticeSessionCreate,
    PracticeSessionOut
)

from app.routers.auth import get_current_active_user

# Added prefix="/api/practice" to fix the 404 URL route error
router = APIRouter(prefix="/api/practice", tags=["Practice"])


# Generate Practice Quiz
@router.post(
    "/quiz",
    response_model=List[PracticeQuizItem]
)
def generate_quiz(
    request: PracticeQuizRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    query = (
        db.query(Question)
        .join(Upload)
        .filter(
            Upload.user_id == current_user.id
        )
    )

    if request.subject:
        query = query.filter(
            Upload.subject.ilike(
                f"%{request.subject}%"
            )
        )

    if request.topic:
        query = query.filter(
            Question.topic.ilike(
                f"%{request.topic}%"
            )
        )

    if request.question_id:
        query = query.filter(
            Question.id == request.question_id
        )

    count = request.count if request.count > 0 else 5

    questions = (
        query
        .order_by(
            Question.created_at.desc()
        )
        .limit(count)
        .all()
    )

    if not questions:
        raise HTTPException(
            status_code=404,
            detail="No questions found for this topic/subject"
        )

    from app.services.ai_service import generate_mcq

    quiz = []

    for question in questions:

        mcq_data = generate_mcq(
            question.question_text,
            question.answer or "Answer not available"
        )

        options = [
            MCQOption(
                label=item["label"],
                text=item["text"]
            )
            for item in mcq_data["options"]
        ]

        quiz.append(
            PracticeQuizItem(
                question_id=question.id,
                question_text=mcq_data["question_text"],
                options=options,
                correct_option=mcq_data["correct_option"]
            )
        )

    return quiz


# Save Practice Session
@router.post(
    "/session",
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
    db.refresh(practice)

    return practice


# Get Practice History
@router.get(
    "/history",
    response_model=List[PracticeSessionOut]
)
def get_practice_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):

    sessions = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.user_id == current_user.id
        )
        .order_by(
            PracticeSession.created_at.desc()
        )
        .all()
    )

    return sessions