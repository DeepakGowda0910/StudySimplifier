from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=True)
    board = Column(String(100), nullable=True)  # CBSE, ICSE, State Board, etc.
    subscription_plan = Column(String(50), default="free")  # free, basic, premium
    max_students = Column(Integer, default=500)
    ai_provider = Column(String(20), default="groq")  # gemini | groq
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class SchoolInvite(Base):
    __tablename__ = "school_invites"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    invite_code = Column(String(20), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # school_teacher | school_student
    grade = Column(Integer, nullable=True)  # for student invites — which grade
    expires_at = Column(DateTime, nullable=True)
    is_used = Column(Boolean, default=False)
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class ClassSection(Base):
    __tablename__ = "class_sections"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    grade = Column(Integer, nullable=False)  # 6-12
    section_name = Column(String(10), default="A")  # A, B, C, etc.
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    academic_year = Column(String(10), default="2025-26")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class StudentEnrollment(Base):
    __tablename__ = "student_enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_section_id = Column(Integer, ForeignKey("class_sections.id"), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    grade = Column(Integer, nullable=False)
    status = Column(String(20), default="active")  # active | promoted | inactive
    promoted_from_grade = Column(Integer, nullable=True)
    enrolled_at = Column(DateTime, server_default=func.now())
    promoted_at = Column(DateTime, nullable=True)
