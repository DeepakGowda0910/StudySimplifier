from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

# --- Lesson ---
class LessonOut(BaseModel):
    id: int
    grade: int
    title: str
    description: Optional[str]
    content_type: str
    content_json: Optional[Any]
    subject: str
    estimated_mins: int
    order_index: int
    is_global: bool

    class Config:
        from_attributes = True

class LessonWithProgress(LessonOut):
    progress_status: str = "not_started"  # not_started | in_progress | completed
    score: Optional[float] = None
    time_spent_mins: int = 0

# --- Progress ---
class LessonProgressUpdate(BaseModel):
    lesson_id: int
    status: str  # not_started | in_progress | completed
    score: Optional[float] = None
    time_spent_mins: Optional[int] = 0

class LessonProgressOut(BaseModel):
    id: int
    student_id: int
    lesson_id: int
    status: str
    score: Optional[float]
    time_spent_mins: int
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# --- Assignment ---
class AssignmentCreate(BaseModel):
    lesson_id: int
    class_section_id: int
    due_date: Optional[datetime] = None
    instructions: Optional[str] = None

class AssignmentOut(BaseModel):
    id: int
    class_section_id: int
    lesson_id: int
    teacher_id: int
    due_date: Optional[datetime]
    instructions: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Submission ---
class SubmissionCreate(BaseModel):
    assignment_id: int
    score: Optional[float] = None

class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    score: Optional[float]
    feedback: Optional[str]
    status: str

    class Config:
        from_attributes = True

# --- AI Tutor ---
class TutorAskRequest(BaseModel):
    question: str
    lesson_id: Optional[int] = None
    lesson_title: Optional[str] = None

class TutorAskResponse(BaseModel):
    answer: str
    model_used: str

# --- Student Dashboard ---
class StudentDashboard(BaseModel):
    grade: int
    school_name: str
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    completion_pct: float
    next_lesson: Optional[LessonOut]
    recent_lessons: List[LessonWithProgress]
