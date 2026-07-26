from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- School ---
class SchoolCreate(BaseModel):
    name: str
    city: Optional[str] = None
    board: Optional[str] = None  # CBSE, ICSE, State Board
    admin_username: str
    admin_email: str
    admin_password: str
    admin_full_name: str

class SchoolOut(BaseModel):
    id: int
    name: str
    city: Optional[str]
    board: Optional[str]
    subscription_plan: str
    max_students: int
    ai_provider: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Auth ---
class SchoolLoginRequest(BaseModel):
    username: str
    password: str

class SchoolJoinRequest(BaseModel):
    invite_code: str
    username: str
    password: str
    full_name: str
    email: Optional[str] = None

class SchoolAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    school_id: int
    school_name: str
    username: str
    full_name: Optional[str] = None

# --- Invite ---
class InviteCreate(BaseModel):
    role: str  # school_teacher | school_student
    grade: Optional[int] = None  # required for student invites
    count: int = 1  # how many invite codes to generate

class InviteOut(BaseModel):
    id: int
    invite_code: str
    role: str
    grade: Optional[int]
    expires_at: Optional[datetime]
    is_used: bool

    class Config:
        from_attributes = True

# --- ClassSection ---
class ClassSectionCreate(BaseModel):
    grade: int  # 6-12
    section_name: str = "A"
    teacher_id: Optional[int] = None
    academic_year: str = "2025-26"

class ClassSectionOut(BaseModel):
    id: int
    school_id: int
    grade: int
    section_name: str
    teacher_id: Optional[int]
    academic_year: str
    is_active: bool

    class Config:
        from_attributes = True

# --- Student Enrollment ---
class PromoteRequest(BaseModel):
    class_section_id: int
    new_grade: int

class StudentOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: Optional[str]
    grade: int
    status: str

    class Config:
        from_attributes = True

# --- Teacher ---
class TeacherOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True

# --- Admin Overview ---
class AdminOverview(BaseModel):
    school_name: str
    total_students: int
    total_teachers: int
    total_classes: int
    active_lessons: int
    avg_completion_rate: float
