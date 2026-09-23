from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------------- USER ----------------

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None  # ADDED: Profile response fix


# ---------------- AUTH ----------------

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserOut] = None  # ADDED: Login response convenience


# ---------------- PASSWORD RESET ----------------

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=6)


# ---------------- UPLOAD ----------------

class UploadCreate(BaseModel):
    exam: Optional[str] = None
    subject: Optional[str] = None
    year: Optional[str] = None


class UploadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    exam: Optional[str] = None
    subject: Optional[str] = None
    year: Optional[str] = None
    created_at: datetime


# ---------------- QUESTIONS ----------------

class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    upload_id: int
    question_text: str
    explanation: Optional[str] = None
    answer: Optional[str] = None
    notes: Optional[str] = None
    topic: Optional[str] = None
    created_at: Optional[datetime] = None


class QuestionDetailOut(QuestionOut):
    exam: Optional[str] = None
    subject: Optional[str] = None
    year: Optional[str] = None


# ---------------- BOOKMARK ----------------

class BookmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    created_at: datetime


# ---------------- NOTES ----------------

class NoteCreate(BaseModel):
    question_id: Optional[int] = None
    title: Optional[str] = "Untitled Note"
    content: str


class NoteUpdate(BaseModel):  # ADDED: Note update fix
    title: Optional[str] = None
    content: Optional[str] = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: Optional[int] = None
    title: Optional[str] = None
    content: str
    created_at: datetime


# ---------------- PRACTICE ----------------

class PracticeAnswerCreate(BaseModel):
    question_id: int
    selected_option: Optional[str] = None
    is_correct: bool
    feedback: Optional[str] = None


class PracticeAnswerOut(PracticeAnswerCreate):  # ADDED: Detailed result view fix
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int


class MCQOption(BaseModel):
    label: str
    text: str


class PracticeQuizItem(BaseModel):
    question_id: int
    question_text: str
    options: List[MCQOption]
    correct_option: Optional[str] = None


class PracticeQuizRequest(BaseModel):
    question_id: Optional[int] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    count: int = Field(default=5, ge=1, le=50)


class PracticeSessionCreate(BaseModel):
    upload_id: Optional[int] = None
    score: int
    total_questions: int
    correct_count: int
    wrong_count: int
    answers: List[PracticeAnswerCreate]


class PracticeSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    upload_id: Optional[int] = None
    score: int
    total_questions: int
    correct_count: int
    wrong_count: int
    created_at: datetime
    answers: Optional[List[PracticeAnswerOut]] = []  # ADDED: Include answered items


# ---------------- DASHBOARD SUMMARY ----------------

class DashboardSummaryOut(BaseModel):  # ADDED: Dashboard API route fix
    uploads_count: int
    questions_count: int
    bookmarks_count: int
    notes_count: int
    recent_uploads: List[UploadOut] = []