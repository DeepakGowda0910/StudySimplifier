from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc
from database import get_db
from models.user import User
from models.school import ClassSection, StudentEnrollment
from models.curriculum import Lesson, LessonProgress, Assignment, AssignmentSubmission
from schemas.curriculum import AssignmentCreate, AssignmentOut
from schemas.school import StudentOut
from middleware.rbac import require_role
from typing import List

router = APIRouter(prefix="/school/teacher", tags=["school-teacher"])

RequireTeacher = Depends(require_role("school_teacher", "school_admin"))


@router.get("/dashboard")
async def teacher_dashboard(
    current_user: User = RequireTeacher,
    db: AsyncSession = Depends(get_db)
):
    # Classes this teacher is assigned to
    result = await db.execute(
        select(ClassSection)
        .where(ClassSection.teacher_id == current_user.id)
        .where(ClassSection.is_active == True)
    )
    classes = result.scalars().all()

    class_data = []
    for cls in classes:
        student_count_r = await db.execute(
            select(sqlfunc.count(StudentEnrollment.id))
            .where(StudentEnrollment.class_section_id == cls.id)
            .where(StudentEnrollment.status == "active")
        )
        student_count = student_count_r.scalar_one()
        class_data.append({
            "id": cls.id,
            "grade": cls.grade,
            "section_name": cls.section_name,
            "academic_year": cls.academic_year,
            "student_count": student_count,
        })

    # Recent assignments
    assign_r = await db.execute(
        select(Assignment)
        .where(Assignment.teacher_id == current_user.id)
        .order_by(Assignment.created_at.desc())
        .limit(5)
    )
    assignments = assign_r.scalars().all()

    return {
        "classes": class_data,
        "recent_assignments": [
            {"id": a.id, "lesson_id": a.lesson_id, "class_section_id": a.class_section_id,
             "due_date": a.due_date, "instructions": a.instructions}
            for a in assignments
        ]
    }


@router.get("/classes")
async def my_classes(
    current_user: User = RequireTeacher,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ClassSection)
        .where(ClassSection.teacher_id == current_user.id)
        .where(ClassSection.is_active == True)
        .order_by(ClassSection.grade, ClassSection.section_name)
    )
    classes = result.scalars().all()
    return [{"id": c.id, "grade": c.grade, "section_name": c.section_name, "academic_year": c.academic_year}
            for c in classes]


@router.get("/classes/{class_id}/students", response_model=List[StudentOut])
async def class_students(
    class_id: int,
    current_user: User = RequireTeacher,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User, StudentEnrollment.grade, StudentEnrollment.status)
        .join(StudentEnrollment, StudentEnrollment.student_id == User.id)
        .where(StudentEnrollment.class_section_id == class_id)
        .where(StudentEnrollment.status == "active")
    )
    rows = result.all()
    return [
        StudentOut(id=row[0].id, username=row[0].username, full_name=row[0].full_name,
                   email=row[0].email, grade=row[1], status=row[2])
        for row in rows
    ]


@router.get("/classes/{class_id}/progress")
async def class_progress(
    class_id: int,
    current_user: User = RequireTeacher,
    db: AsyncSession = Depends(get_db)
):
    """Heatmap data: student × lesson completion grid."""
    # Get all students in this class
    students_r = await db.execute(
        select(User, StudentEnrollment.grade)
        .join(StudentEnrollment, StudentEnrollment.student_id == User.id)
        .where(StudentEnrollment.class_section_id == class_id)
        .where(StudentEnrollment.status == "active")
    )
    students = students_r.all()
    if not students:
        return {"students": [], "lessons": [], "progress": []}

    grade = students[0][1]

    # Get lessons for this grade
    lessons_r = await db.execute(
        select(Lesson)
        .where(Lesson.grade == grade)
        .where(Lesson.is_global == True)
        .order_by(Lesson.order_index)
    )
    lessons = lessons_r.scalars().all()

    # Get all progress records for these students and lessons
    student_ids = [s[0].id for s in students]
    lesson_ids = [l.id for l in lessons]

    progress_r = await db.execute(
        select(LessonProgress)
        .where(LessonProgress.student_id.in_(student_ids))
        .where(LessonProgress.lesson_id.in_(lesson_ids))
    )
    progress_records = progress_r.scalars().all()

    progress_map = {(p.student_id, p.lesson_id): p.status for p in progress_records}

    return {
        "students": [{"id": s[0].id, "name": s[0].full_name or s[0].username} for s in students],
        "lessons": [{"id": l.id, "title": l.title, "order": l.order_index} for l in lessons],
        "progress": {
            str(sid): {str(lid): progress_map.get((sid, lid), "not_started") for lid in lesson_ids}
            for sid in student_ids
        }
    }


@router.post("/assignments", response_model=AssignmentOut)
async def create_assignment(
    payload: AssignmentCreate,
    current_user: User = RequireTeacher,
    db: AsyncSession = Depends(get_db)
):
    cls = await db.get(ClassSection, payload.class_section_id)
    if not cls or cls.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Class not found")

    assignment = Assignment(
        class_section_id=payload.class_section_id,
        lesson_id=payload.lesson_id,
        teacher_id=current_user.id,
        school_id=current_user.school_id,
        due_date=payload.due_date,
        instructions=payload.instructions,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.get("/students/{student_id}/progress")
async def student_progress_detail(
    student_id: int,
    current_user: User = RequireTeacher,
    db: AsyncSession = Depends(get_db)
):
    student = await db.get(User, student_id)
    if not student or student.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Student not found")

    progress_r = await db.execute(
        select(LessonProgress, Lesson.title, Lesson.grade, Lesson.order_index)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .where(LessonProgress.student_id == student_id)
        .order_by(Lesson.grade, Lesson.order_index)
    )
    rows = progress_r.all()

    return {
        "student": {"id": student.id, "name": student.full_name or student.username},
        "progress": [
            {
                "lesson_id": row[0].lesson_id,
                "lesson_title": row[1],
                "grade": row[2],
                "status": row[0].status,
                "score": row[0].score,
                "time_spent_mins": row[0].time_spent_mins,
                "completed_at": row[0].completed_at,
            }
            for row in rows
        ]
    }
