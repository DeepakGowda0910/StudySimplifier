from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from database import Base

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), ForeignKey("users.username"), index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    subject = Column(String(200), nullable=True)
    chapter = Column(String(200), nullable=True)
    tags = Column(String(500), nullable=True)
    is_pinned = Column(Boolean, default=False)
    color = Column(String(20), default="blue")
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
