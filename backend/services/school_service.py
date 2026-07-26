import random
import string
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc
from models.school import School, SchoolInvite, ClassSection, StudentEnrollment
from models.user import User
from models.curriculum import LessonProgress

def generate_invite_code(length: int = 8) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))

async def create_invite_codes(
    db: AsyncSession,
    school_id: int,
    role: str,
    grade: Optional[int],
    count: int,
    expires_days: int = 30,
) -> List[SchoolInvite]:
    expires_at = datetime.utcnow() + timedelta(days=expires_days)
    invites = []
    for _ in range(count):
        code = generate_invite_code()
        # Ensure uniqueness
        while True:
            existing = await db.execute(
                select(SchoolInvite).where(SchoolInvite.invite_code == code)
            )
            if not existing.scalar_one_or_none():
                break
            code = generate_invite_code()
        invite = SchoolInvite(
            school_id=school_id,
            invite_code=code,
            role=role,
            grade=grade,
            expires_at=expires_at,
        )
        db.add(invite)
        invites.append(invite)
    await db.commit()
    for inv in invites:
        await db.refresh(inv)
    return invites

async def get_school_overview(db: AsyncSession, school_id: int) -> dict:
    school = await db.get(School, school_id)

    total_students = (await db.execute(
        select(sqlfunc.count(StudentEnrollment.id))
        .where(StudentEnrollment.school_id == school_id)
        .where(StudentEnrollment.status == "active")
    )).scalar_one()

    total_teachers = (await db.execute(
        select(sqlfunc.count(User.id))
        .where(User.school_id == school_id)
        .where(User.role == "school_teacher")
    )).scalar_one()

    total_classes = (await db.execute(
        select(sqlfunc.count(ClassSection.id))
        .where(ClassSection.school_id == school_id)
        .where(ClassSection.is_active == True)
    )).scalar_one()

    completed = (await db.execute(
        select(sqlfunc.count(LessonProgress.id))
        .join(StudentEnrollment, StudentEnrollment.student_id == LessonProgress.student_id)
        .where(LessonProgress.school_id == school_id)
        .where(LessonProgress.status == "completed")
    )).scalar_one()

    total_progress = (await db.execute(
        select(sqlfunc.count(LessonProgress.id))
        .where(LessonProgress.school_id == school_id)
    )).scalar_one()

    avg_completion = round((completed / total_progress * 100) if total_progress else 0, 1)

    return {
        "school_name": school.name if school else "",
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_classes": total_classes,
        "active_lessons": total_progress,
        "avg_completion_rate": avg_completion,
    }

async def get_student_grade(db: AsyncSession, student_id: int, school_id: int) -> Optional[int]:
    result = await db.execute(
        select(StudentEnrollment)
        .where(StudentEnrollment.student_id == student_id)
        .where(StudentEnrollment.school_id == school_id)
        .where(StudentEnrollment.status == "active")
    )
    enrollment = result.scalar_one_or_none()
    return enrollment.grade if enrollment else None

async def promote_student(
    db: AsyncSession, student_id: int, school_id: int, new_grade: int
) -> StudentEnrollment:
    result = await db.execute(
        select(StudentEnrollment)
        .where(StudentEnrollment.student_id == student_id)
        .where(StudentEnrollment.school_id == school_id)
        .where(StudentEnrollment.status == "active")
    )
    old_enrollment = result.scalar_one_or_none()
    if old_enrollment:
        old_enrollment.status = "promoted"
        old_enrollment.promoted_at = datetime.utcnow()

    new_enrollment = StudentEnrollment(
        student_id=student_id,
        school_id=school_id,
        grade=new_grade,
        promoted_from_grade=old_enrollment.grade if old_enrollment else None,
        status="active",
    )
    db.add(new_enrollment)
    await db.commit()
    await db.refresh(new_enrollment)
    return new_enrollment
