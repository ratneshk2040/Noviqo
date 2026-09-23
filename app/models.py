from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


def current_time():
    return datetime.now(timezone.utc)


# ================= USER =================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=current_time)

    uploads = relationship("Upload", back_populates="owner", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="user", cascade="all, delete-orphan")


# ================= UPLOAD =================

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    exam = Column(String(100))
    subject = Column(String(100))
    year = Column(String(20))
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), default=current_time)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="uploads")
    questions = relationship("Question", back_populates="upload", cascade="all, delete-orphan")
    practice_sessions = relationship("PracticeSession", back_populates="upload")


# ================= QUESTION =================

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    explanation = Column(Text)
    answer = Column(Text)
    notes = Column(Text)
    topic = Column(String(120))
    created_at = Column(DateTime(timezone=True), default=current_time)

    upload = relationship("Upload", back_populates="questions")
    bookmarks = relationship("Bookmark", back_populates="question", cascade="all, delete-orphan")
    notes_entries = relationship("Note", back_populates="question")


# ================= BOOKMARK =================

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=current_time)

    user = relationship("User", back_populates="bookmarks")
    question = relationship("Question", back_populates="bookmarks")


# ================= NOTES =================

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), default="Untitled Note")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=current_time)

    user = relationship("User", back_populates="notes")
    question = relationship("Question", back_populates="notes_entries")


# ================= PRACTICE SESSION =================

class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="SET NULL"), nullable=True)

    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    wrong_count = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), default=current_time)

    user = relationship("User", back_populates="practice_sessions")
    upload = relationship("Upload", back_populates="practice_sessions")
    answers = relationship("PracticeAnswer", back_populates="session", cascade="all, delete-orphan")


# ================= PRACTICE ANSWER =================

class PracticeAnswer(Base):
    __tablename__ = "practice_answers"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)

    selected_option = Column(String(255))
    is_correct = Column(Boolean, default=False)
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), default=current_time)

    session = relationship("PracticeSession", back_populates="answers")
    question = relationship("Question")