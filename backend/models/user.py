from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, Date, ForeignKey
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    avatar_url = Column(String(500), nullable=True)
    # School module fields — null for StudySmart users
    role = Column(String(30), default="studysmart_user")  # studysmart_user | school_student | school_teacher | school_admin
    school_id = Column(Integer, nullable=True)  # FK resolved at app layer to avoid circular imports
    full_name = Column(String(200), nullable=True)  # required for school users

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), ForeignKey("users.username"), unique=True, index=True)
    category = Column(String(100), nullable=True)
    course = Column(String(100), nullable=True)
    stream = Column(String(100), nullable=True)
    board = Column(String(100), nullable=True)
    onboarded = Column(Boolean, default=False)
    preferred_language = Column(String(50), default="English")
    theme = Column(String(20), default="light")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), ForeignKey("users.username"), unique=True, index=True)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    level_progress = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_login = Column(String(20), nullable=True)
    total_minutes = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class DailyLogin(Base):
    __tablename__ = "daily_logins"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    login_date = Column(String(20), nullable=False)
    xp_awarded = Column(Integer, default=20)

class StudySession(Base):
    __tablename__ = "study_sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    subject = Column(String(200), nullable=True)
    minutes = Column(Integer, default=0)
    session_type = Column(String(50), default="regular")  # regular, pomodoro
    sess_date = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Streak(Base):
    __tablename__ = "streaks"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), ForeignKey("users.username"), unique=True, index=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_login_date = Column(String(20), nullable=True)
