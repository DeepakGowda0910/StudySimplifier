from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.sql import func
from database import Base

class ExamCountdown(Base):
    __tablename__ = "exam_countdowns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    exam_name = Column(String(300), nullable=False)
    subject = Column(String(200), nullable=True)
    exam_date = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    color = Column(String(20), default="blue")
    created_at = Column(DateTime, server_default=func.now())

class StudyPlan(Base):
    __tablename__ = "study_plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=True)
    start_date = Column(String(20), nullable=True)
    end_date = Column(String(20), nullable=True)
    exam_name = Column(String(300), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    subject = Column(String(200), nullable=True)
    duration_minutes = Column(Integer, default=25)
    completed = Column(Boolean, default=False)
    sess_date = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
