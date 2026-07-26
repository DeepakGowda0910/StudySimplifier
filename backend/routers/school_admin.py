from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc
from database import get_db
from models.user import User
from models.school import School, SchoolInvite, ClassSection, StudentEnrollment
from models.curriculum import LessonProgress
from schemas.school import (
    InviteCreate, InviteOut, ClassSectionCreate, ClassSectionOut,
    StudentOut, TeacherOut, AdminOverview, PromoteRequest
)
from middleware.rbac import require_role
from services.school_service import create_invite_codes, get_school_overview, promote_student
from typing import List

router = APIRouter(prefix="/school/admin", tags=["school-admin"])

RequireAdmin = Depends(require_role("school_admin"))


@router.get("/overview", response_model=AdminOverview)
async def admin_overview(
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    return await get_school_overview(db, current_user.school_id)


@router.post("/invites", response_model=List[InviteOut])
async def generate_invites(
    payload: InviteCreate,
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    if payload.role == "school_student" and not payload.grade:
        raise HTTPException(status_code=400, detail="Grade is required for student invites")
    if payload.role not in ("school_teacher", "school_student"):
        raise HTTPException(status_code=400, detail="Role must be school_teacher or school_student")

    invites = await create_invite_codes(
        db=db,
        school_id=current_user.school_id,
        role=payload.role,
        grade=payload.grade,
        count=min(payload.count, 50),  # cap at 50 per request
    )
    return invites


@router.get("/invites", response_model=List[InviteOut])
async def list_invites(
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SchoolInvite)
        .where(SchoolInvite.school_id == current_user.school_id)
        .order_by(SchoolInvite.created_at.desc())
        .limit(100)
    )
    return result.scalars().all()


@router.get("/teachers", response_model=List[TeacherOut])
async def list_teachers(
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
        .where(User.school_id == current_user.school_id)
        .where(User.role == "school_teacher")
        .where(User.is_active == True)
    )
    return result.scalars().all()


@router.delete("/teachers/{teacher_id}")
async def remove_teacher(
    teacher_id: int,
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    teacher = await db.get(User, teacher_id)
    if not teacher or teacher.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Teacher not found")
    teacher.is_active = False
    await db.commit()
    return {"message": "Teacher removed"}


@router.get("/students", response_model=List[StudentOut])
async def list_students(
    grade: int = None,
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(User, StudentEnrollment.grade, StudentEnrollment.status)
        .join(StudentEnrollment, StudentEnrollment.student_id == User.id)
        .where(User.school_id == current_user.school_id)
        .where(User.role == "school_student")
        .where(StudentEnrollment.status == "active")
    )
    if grade:
        query = query.where(StudentEnrollment.grade == grade)

    result = await db.execute(query)
    rows = result.all()
    return [
        StudentOut(id=row[0].id, username=row[0].username, full_name=row[0].full_name,
                   email=row[0].email, grade=row[1], status=row[2])
        for row in rows
    ]


@router.post("/classes", response_model=ClassSectionOut)
async def create_class(
    payload: ClassSectionCreate,
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    cls = ClassSection(
        school_id=current_user.school_id,
        grade=payload.grade,
        section_name=payload.section_name,
        teacher_id=payload.teacher_id,
        academic_year=payload.academic_year,
    )
    db.add(cls)
    await db.flush()

    # Backfill: link any already-enrolled, unassigned students of this grade to the new class
    unassigned_r = await db.execute(
        select(StudentEnrollment)
        .where(StudentEnrollment.school_id == current_user.school_id)
        .where(StudentEnrollment.grade == payload.grade)
        .where(StudentEnrollment.status == "active")
        .where(StudentEnrollment.class_section_id.is_(None))
    )
    for enrollment in unassigned_r.scalars().all():
        enrollment.class_section_id = cls.id

    await db.commit()
    await db.refresh(cls)
    return cls


@router.get("/classes", response_model=List[ClassSectionOut])
async def list_classes(
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ClassSection)
        .where(ClassSection.school_id == current_user.school_id)
        .where(ClassSection.is_active == True)
        .order_by(ClassSection.grade, ClassSection.section_name)
    )
    return result.scalars().all()


@router.post("/promote")
async def promote_grade(
    payload: PromoteRequest,
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    """Promote all active students in a class section to the next grade."""
    if payload.new_grade < 7 or payload.new_grade > 12:
        raise HTTPException(status_code=400, detail="New grade must be between 7 and 12")

    result = await db.execute(
        select(StudentEnrollment)
        .where(StudentEnrollment.class_section_id == payload.class_section_id)
        .where(StudentEnrollment.school_id == current_user.school_id)
        .where(StudentEnrollment.status == "active")
    )
    enrollments = result.scalars().all()

    promoted_count = 0
    for enrollment in enrollments:
        await promote_student(db, enrollment.student_id, current_user.school_id, payload.new_grade)
        promoted_count += 1

    return {"promoted": promoted_count, "new_grade": payload.new_grade}


@router.get("/reports")
async def school_reports(
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    """Completion rates by grade."""
    grades_data = []
    for grade in range(6, 13):
        student_count_r = await db.execute(
            select(sqlfunc.count(StudentEnrollment.id))
            .where(StudentEnrollment.school_id == current_user.school_id)
            .where(StudentEnrollment.grade == grade)
            .where(StudentEnrollment.status == "active")
        )
        student_count = student_count_r.scalar_one()
        if student_count == 0:
            continue

        completed_r = await db.execute(
            select(sqlfunc.count(LessonProgress.id))
            .join(StudentEnrollment, StudentEnrollment.student_id == LessonProgress.student_id)
            .where(StudentEnrollment.school_id == current_user.school_id)
            .where(StudentEnrollment.grade == grade)
            .where(LessonProgress.status == "completed")
        )
        completed = completed_r.scalar_one()

        total_r = await db.execute(
            select(sqlfunc.count(LessonProgress.id))
            .join(StudentEnrollment, StudentEnrollment.student_id == LessonProgress.student_id)
            .where(StudentEnrollment.school_id == current_user.school_id)
            .where(StudentEnrollment.grade == grade)
        )
        total = total_r.scalar_one()

        grades_data.append({
            "grade": grade,
            "students": student_count,
            "lessons_completed": completed,
            "total_lesson_attempts": total,
            "completion_rate": round(completed / total * 100, 1) if total else 0,
        })

    return {"by_grade": grades_data}


@router.put("/school/ai-provider")
async def update_ai_provider(
    provider: str,
    current_user: User = RequireAdmin,
    db: AsyncSession = Depends(get_db)
):
    if provider not in ("gemini", "groq"):
        raise HTTPException(status_code=400, detail="Provider must be gemini or groq")
    school = await db.get(School, current_user.school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    school.ai_provider = provider
    await db.commit()
    return {"ai_provider": provider}
