from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProfileUpdate(BaseModel):
    category: Optional[str] = None
    course: Optional[str] = None
    stream: Optional[str] = None
    board: Optional[str] = None
    preferred_language: Optional[str] = None
    theme: Optional[str] = None

class ProfileResponse(BaseModel):
    username: str
    category: Optional[str] = None
    course: Optional[str] = None
    stream: Optional[str] = None
    board: Optional[str] = None
    onboarded: bool = False
    preferred_language: str = "English"
    theme: str = "light"

class StatsResponse(BaseModel):
    total_xp: int
    level: int
    level_progress: int
    streak_days: int
    longest_streak: int
    total_minutes: int
    total_sessions: int
    flashcards_due: int
    badges_earned: int

class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    total_xp: int
    level: int
    streak_days: int
    total_minutes: int

class StudySessionCreate(BaseModel):
    subject: Optional[str] = None
    minutes: int
    session_type: str = "regular"

class AnalyticsResponse(BaseModel):
    daily_minutes: List[dict]
    xp_trend: List[dict]
    subject_distribution: List[dict]
    flashcard_performance: dict
    weekly_summary: dict
