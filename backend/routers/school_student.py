from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc
from database import get_db
from models.user import User
from models.school import School, StudentEnrollment
from models.curriculum import Lesson, LessonProgress
from schemas.curriculum import (
    LessonOut, LessonWithProgress, LessonProgressUpdate,
    TutorAskRequest, TutorAskResponse, StudentDashboard
)
from middleware.rbac import require_role
from services.school_service import get_student_grade
from services.ai_service import generate_content, build_school_tutor_prompt
from datetime import datetime

router = APIRouter(prefix="/school/student", tags=["school-student"])

RequireStudent = Depends(require_role("school_student", "school_teacher", "school_admin"))


@router.get("/dashboard", response_model=StudentDashboard)
async def student_dashboard(
    current_user: User = RequireStudent,
    db: AsyncSession = Depends(get_db)
):
    grade = await get_student_grade(db, current_user.id, current_user.school_id)
    if not grade:
        raise HTTPException(status_code=404, detail="No active enrollment found")

    school = await db.get(School, current_user.school_id)

    # All lessons for this grade
    lessons_r = await db.execute(
        select(Lesson)
        .where(Lesson.grade == grade)
        .where(Lesson.is_global == True)
        .order_by(Lesson.order_index)
    )
    lessons = lessons_r.scalars().all()

    # Progress records for this student
    progress_r = await db.execute(
        select(LessonProgress)
        .where(LessonProgress.student_id == current_user.id)
        .where(LessonProgress.lesson_id.in_([l.id for l in lessons]))
    )
    progress_map = {p.lesson_id: p for p in progress_r.scalars().all()}

    completed = sum(1 for l in lessons if progress_map.get(l.id) and progress_map[l.id].status == "completed")
    in_progress = sum(1 for l in lessons if progress_map.get(l.id) and progress_map[l.id].status == "in_progress")
    total = len(lessons)

    # Next lesson = first not completed
    next_lesson = next(
        (l for l in lessons if not progress_map.get(l.id) or progress_map[l.id].status != "completed"),
        None
    )

    # Recent 5 with progress
    recent = []
    for l in lessons[:5]:
        p = progress_map.get(l.id)
        recent.append(LessonWithProgress(
            **LessonOut.model_validate(l).model_dump(),
            progress_status=p.status if p else "not_started",
            score=p.score if p else None,
            time_spent_mins=p.time_spent_mins if p else 0,
        ))

    return StudentDashboard(
        grade=grade,
        school_name=school.name if school else "",
        total_lessons=total,
        completed_lessons=completed,
        in_progress_lessons=in_progress,
        completion_pct=round(completed / total * 100, 1) if total else 0,
        next_lesson=LessonOut.model_validate(next_lesson) if next_lesson else None,
        recent_lessons=recent,
    )


@router.get("/curriculum")
async def get_curriculum(
    current_user: User = RequireStudent,
    db: AsyncSession = Depends(get_db)
):
    """Return all lessons for student's current grade with progress."""
    grade = await get_student_grade(db, current_user.id, current_user.school_id)
    if not grade:
        raise HTTPException(status_code=404, detail="No active enrollment found")

    lessons_r = await db.execute(
        select(Lesson)
        .where(Lesson.grade == grade)
        .where(Lesson.is_global == True)
        .order_by(Lesson.order_index)
    )
    lessons = lessons_r.scalars().all()

    progress_r = await db.execute(
        select(LessonProgress)
        .where(LessonProgress.student_id == current_user.id)
        .where(LessonProgress.lesson_id.in_([l.id for l in lessons]))
    )
    progress_map = {p.lesson_id: p for p in progress_r.scalars().all()}

    result = []
    for l in lessons:
        p = progress_map.get(l.id)
        lesson_dict = {
            "id": l.id,
            "grade": l.grade,
            "title": l.title,
            "description": l.description,
            "content_type": l.content_type,
            "subject": l.subject,
            "estimated_mins": l.estimated_mins,
            "order_index": l.order_index,
            "progress_status": p.status if p else "not_started",
            "score": p.score if p else None,
            "time_spent_mins": p.time_spent_mins if p else 0,
        }
        result.append(lesson_dict)

    return {"grade": grade, "lessons": result}


@router.get("/lessons/{lesson_id}")
async def get_lesson(
    lesson_id: int,
    current_user: User = RequireStudent,
    db: AsyncSession = Depends(get_db)
):
    """Get full lesson content including content_json."""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get or create progress record
    progress_r = await db.execute(
        select(LessonProgress)
        .where(LessonProgress.student_id == current_user.id)
        .where(LessonProgress.lesson_id == lesson_id)
    )
    progress = progress_r.scalar_one_or_none()

    if not progress:
        progress = LessonProgress(
            student_id=current_user.id,
            lesson_id=lesson_id,
            school_id=current_user.school_id,
            status="in_progress",
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
    elif progress.status == "not_started":
        progress.status = "in_progress"
        await db.commit()

    return {
        "id": lesson.id,
        "grade": lesson.grade,
        "title": lesson.title,
        "description": lesson.description,
        "content_type": lesson.content_type,
        "content_json": lesson.content_json,
        "subject": lesson.subject,
        "estimated_mins": lesson.estimated_mins,
        "order_index": lesson.order_index,
        "progress": {
            "status": progress.status,
            "score": progress.score,
            "time_spent_mins": progress.time_spent_mins,
            "completed_at": progress.completed_at,
        }
    }


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    payload: LessonProgressUpdate,
    current_user: User = RequireStudent,
    db: AsyncSession = Depends(get_db)
):
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress_r = await db.execute(
        select(LessonProgress)
        .where(LessonProgress.student_id == current_user.id)
        .where(LessonProgress.lesson_id == lesson_id)
    )
    progress = progress_r.scalar_one_or_none()

    if not progress:
        progress = LessonProgress(
            student_id=current_user.id,
            lesson_id=lesson_id,
            school_id=current_user.school_id,
        )
        db.add(progress)

    progress.status = payload.status
    if payload.score is not None:
        progress.score = payload.score
    if payload.time_spent_mins is not None:
        progress.time_spent_mins = (progress.time_spent_mins or 0) + payload.time_spent_mins
    if payload.status == "completed":
        progress.completed_at = datetime.utcnow()

    await db.commit()
    return {"message": "Progress updated", "status": progress.status}


@router.get("/progress")
async def my_progress(
    current_user: User = RequireStudent,
    db: AsyncSession = Depends(get_db)
):
    """All completed lessons across all grades (for history after promotion)."""
    progress_r = await db.execute(
        select(LessonProgress, Lesson.title, Lesson.grade, Lesson.content_type, Lesson.estimated_mins)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .where(LessonProgress.student_id == current_user.id)
        .order_by(Lesson.grade, Lesson.order_index)
    )
    rows = progress_r.all()

    total_completed = sum(1 for r in rows if r[0].status == "completed")
    total_time = sum(r[0].time_spent_mins or 0 for r in rows)

    return {
        "total_completed": total_completed,
        "total_time_mins": total_time,
        "lessons": [
            {
                "lesson_id": r[0].lesson_id,
                "title": r[1],
                "grade": r[2],
                "content_type": r[3],
                "status": r[0].status,
                "score": r[0].score,
                "time_spent_mins": r[0].time_spent_mins,
                "completed_at": r[0].completed_at,
            }
            for r in rows
        ]
    }


@router.post("/ask", response_model=TutorAskResponse)
async def ask_ai_tutor(
    payload: TutorAskRequest,
    current_user: User = RequireStudent,
    db: AsyncSession = Depends(get_db)
):
    """Grade-aware Socratic AI tutor for AI/coding questions."""
    grade = await get_student_grade(db, current_user.id, current_user.school_id)
    if not grade:
        grade = 6  # default fallback

    lesson_title = payload.lesson_title
    if not lesson_title and payload.lesson_id:
        lesson = await db.get(Lesson, payload.lesson_id)
        if lesson:
            lesson_title = lesson.title

    # Use school's preferred AI provider
    school = await db.get(School, current_user.school_id)
    provider = school.ai_provider if school else None

    prompt = build_school_tutor_prompt(payload.question, grade, lesson_title)
    answer, model_used = await generate_content(prompt, provider=provider)

    return TutorAskResponse(answer=answer, model_used=model_used)
