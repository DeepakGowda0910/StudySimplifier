from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class ContentChunk(Base):
    __tablename__ = "content_chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    course = Column(String(100), nullable=False, index=True)
    stream = Column(String(100), nullable=True)
    subject = Column(String(200), nullable=False, index=True)
    topic = Column(String(200), nullable=True)
    chapter = Column(String(200), nullable=False, index=True)
    source = Column(String(50), nullable=False, default="NCERT")
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
