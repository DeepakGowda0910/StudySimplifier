from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    front_text = Column(Text, nullable=False)
    back_text = Column(Text, nullable=False)
    subject = Column(String(200), nullable=True)
    chapter = Column(String(200), nullable=True)
    topic = Column(String(200), nullable=True)
    created_date = Column(String(20), nullable=False)
    next_review_date = Column(String(20), nullable=False)
    ease_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=1)
    review_count = Column(Integer, default=0)
    tags = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
