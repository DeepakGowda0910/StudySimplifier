from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models.user import User
from models.planner import ExamCountdown, StudyPlan, PomodoroSession
from schemas.flashcard import ExamCreate, StudyPlanCreate
from middleware.auth import get_current_user
from services.ai_service import generate_content, build_study_plan_prompt
from services.gamification import award_xp
from datetime import date

router = APIRouter(prefix="/planner", tags=["planner"])

@router.get("/exams")
async def get_exams(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExamCountdown).where(ExamCountdown.username == current_user.username))
    exams = result.scalars().all()
    today = date.today()
    result_list = []
    for e in exams:
        exam_date = date.fromisoformat(e.exam_date)
        days_left = (exam_date - today).days
        result_list.append({
            "id": e.id, "exam_name": e.exam_name, "subject": e.subject,
            "exam_date": e.exam_date, "days_left": days_left, "notes": e.notes, "color": e.color,
            "created_at": e.created_at.isoformat()
        })
    return sorted(result_list, key=lambda x: x["days_left"])

@router.post("/exams")
async def create_exam(data: ExamCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    exam = ExamCountdown(
        username=current_user.username,
        exam_name=data.exam_name,
        subject=data.subject,
        exam_date=data.exam_date,
        notes=data.notes,
        color=data.color
    )
    db.add(exam)
    await db.commit()
    return {"message": "Exam added", "id": exam.id}

@router.delete("/exams/{exam_id}")
async def delete_exam(exam_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ExamCountdown).where(ExamCountdown.id == exam_id, ExamCountdown.username == current_user.username))
    await db.commit()
    return {"message": "Exam deleted"}

@router.post("/generate-plan")
async def generate_study_plan(data: StudyPlanCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    start_date = data.start_date or date.today().isoformat()
    prompt = build_study_plan_prompt(data.exam_name, data.exam_date, data.subjects, data.daily_hours, start_date)
    content, model = await generate_content(prompt)

    plan = StudyPlan(
        username=current_user.username,
        title=f"Study Plan: {data.exam_name}",
        content=content,
        start_date=start_date,
        end_date=data.exam_date,
        exam_name=data.exam_name
    )
    db.add(plan)
    await award_xp(db, current_user.username, 20)
    await db.commit()
    return {"content": content, "model": model, "plan_id": plan.id, "xp_awarded": 20}

@router.get("/plans")
async def get_plans(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudyPlan).where(StudyPlan.username == current_user.username))
    plans = result.scalars().all()
    return [{"id": p.id, "title": p.title, "exam_name": p.exam_name, "start_date": p.start_date,
             "end_date": p.end_date, "content": p.content, "created_at": p.created_at.isoformat()} for p in plans]

@router.post("/pomodoro")
async def record_pomodoro(subject: str = None, duration: int = 25, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = PomodoroSession(
        username=current_user.username,
        subject=subject,
        duration_minutes=duration,
        completed=True,
        sess_date=date.today().isoformat()
    )
    db.add(session)
    await award_xp(db, current_user.username, duration // 5)
    await db.commit()
    return {"message": "Pomodoro session recorded", "xp_awarded": duration // 5}

@router.get("/pomodoro/stats")
async def get_pomodoro_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PomodoroSession).where(PomodoroSession.username == current_user.username))
    sessions = result.scalars().all()
    total_sessions = len(sessions)
    total_minutes = sum(s.duration_minutes for s in sessions)
    return {"total_sessions": total_sessions, "total_minutes": total_minutes, "sessions": [
        {"date": s.sess_date, "subject": s.subject, "duration": s.duration_minutes} for s in sessions[-20:]
    ]}
