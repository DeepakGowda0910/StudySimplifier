from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from database import Base

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    subject = Column(String(200), nullable=True)
    chapter = Column(String(200), nullable=True)
    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    difficulty = Column(Float, default=1000.0)
    time_taken_secs = Column(Integer, default=0)
    elo_before = Column(Float, default=1000.0)
    elo_after = Column(Float, default=1000.0)
    created_at = Column(DateTime, server_default=func.now())

class StudentELO(Base):
    __tablename__ = "student_elo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    subject = Column(String(200), nullable=False)
    chapter = Column(String(200), nullable=True)
    elo_rating = Column(Float, default=1000.0)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

class MistakeEntry(Base):
    __tablename__ = "mistake_journal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    subject = Column(String(200), nullable=True)
    chapter = Column(String(200), nullable=True)
    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    concept_tag = Column(String(500), nullable=True)
    times_wrong = Column(Integer, default=1)
    last_seen = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

class DailyAgenda(Base):
    __tablename__ = "daily_agendas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    agenda_date = Column(String(20), nullable=False)
    ai_analysis = Column(Text, nullable=True)
    agenda_json = Column(Text, nullable=True)
    total_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
