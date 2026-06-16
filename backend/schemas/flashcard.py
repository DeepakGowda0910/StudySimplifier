from pydantic import BaseModel
from typing import Optional, List

class FlashcardCreate(BaseModel):
    front_text: str
    back_text: str
    subject: Optional[str] = None
    chapter: Optional[str] = None
    topic: Optional[str] = None
    tags: Optional[str] = None

class FlashcardResponse(BaseModel):
    id: int
    front_text: str
    back_text: str
    subject: Optional[str] = None
    chapter: Optional[str] = None
    next_review_date: str
    ease_factor: float
    interval_days: int
    review_count: int
    tags: Optional[str] = None

class FlashcardReview(BaseModel):
    performance: int  # 1=again, 2=hard, 3=good, 4=easy

class FlashcardGenerateRequest(BaseModel):
    subject: str
    chapter: str
    topic: Optional[str] = None
    count: int = 10

class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    tags: Optional[str] = None
    color: str = "blue"

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject: Optional[str] = None
    chapter: Optional[str] = None
    tags: Optional[str] = None
    color: Optional[str] = None
    is_pinned: Optional[bool] = None

class ExamCreate(BaseModel):
    exam_name: str
    subject: Optional[str] = None
    exam_date: str
    notes: Optional[str] = None
    color: str = "blue"

class StudyPlanCreate(BaseModel):
    exam_name: str
    exam_date: str
    subjects: List[str]
    daily_hours: int = 3
    start_date: Optional[str] = None
