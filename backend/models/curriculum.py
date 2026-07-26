from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Integer, nullable=False, index=True)  # 6-12
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(String(30), default="text")  # text | quiz | coding | project | video
    content_json = Column(JSON, nullable=True)  # structured lesson content
    subject = Column(String(100), default="AI Fundamentals")
    estimated_mins = Column(Integer, default=30)
    order_index = Column(Integer, default=0)  # sort order within grade
    is_global = Column(Boolean, default=True)  # True = system lesson, False = school-custom
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)  # null = global
    created_at = Column(DateTime, server_default=func.now())

class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    status = Column(String(20), default="not_started")  # not_started | in_progress | completed
    score = Column(Float, nullable=True)  # 0-100 for quiz lessons
    time_spent_mins = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    class_section_id = Column(Integer, ForeignKey("class_sections.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    due_date = Column(DateTime, nullable=True)
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, server_default=func.now())
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(String(20), default="submitted")  # submitted | graded | returned
