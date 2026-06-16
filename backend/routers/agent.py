from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from models.user import User, UserProfile, UserStats, StudySession
from models.quiz import StudentELO, MistakeEntry, DailyAgenda
from models.flashcard import Flashcard
from models.planner import ExamCountdown
from middleware.auth import get_current_user
from services.ai_service import generate_content, build_daily_agenda_prompt, build_knowledge_graph_prompt
from datetime import date, timedelta
import json
import re

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/daily-agenda")
async def get_daily_agenda(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today().isoformat()

    # Return cached agenda if already generated today
    result = await db.execute(
        select(DailyAgenda).where(
            DailyAgenda.username == current_user.username,
            DailyAgenda.agenda_date == today
        )
    )
    cached = result.scalar_one_or_none()
    if cached and cached.agenda_json:
        return {"agenda": json.loads(cached.agenda_json), "cached": True, "date": today}

    # Gather data
    profile_result = await db.execute(select(UserProfile).where(UserProfile.username == current_user.username))
    profile = profile_result.scalar_one_or_none()
    profile_dict = {
        "course": profile.course if profile else "General",
        "board": profile.board if profile else "",
        "category": profile.category if profile else ""
    }

    # Weak subjects (low ELO)
    elo_result = await db.execute(
        select(StudentELO)
        .where(StudentELO.username == current_user.username)
        .order_by(StudentELO.elo_rating)
        .limit(5)
    )
    weak_subjects = [
        {"subject": r.subject, "chapter": r.chapter, "accuracy": r.accuracy, "elo": r.elo_rating}
        for r in elo_result.scalars().all()
    ]

    # Due flashcards
    fc_result = await db.execute(
        select(func.count()).select_from(Flashcard).where(
            Flashcard.username == current_user.username,
            Flashcard.next_review_date <= today
        )
    )
    due_flashcards = fc_result.scalar() or 0

    # Upcoming exams
    exams_result = await db.execute(
        select(ExamCountdown)
        .where(ExamCountdown.username == current_user.username)
        .order_by(ExamCountdown.exam_date)
        .limit(3)
    )
    exams = []
    for e in exams_result.scalars().all():
        days_left = (date.fromisoformat(e.exam_date) - date.today()).days
        if days_left >= 0:
            exams.append({"exam_name": e.exam_name, "days_left": days_left})

    # Study minutes today
    sess_result = await db.execute(
        select(func.sum(StudySession.minutes)).where(
            StudySession.username == current_user.username,
            StudySession.sess_date == today
        )
    )
    study_minutes_today = sess_result.scalar() or 0

    # Recurring mistakes
    mistake_result = await db.execute(
        select(MistakeEntry)
        .where(MistakeEntry.username == current_user.username)
        .order_by(desc(MistakeEntry.times_wrong))
        .limit(5)
    )
    mistake_patterns = [
        {"concept_tag": m.concept_tag or m.chapter, "times": m.times_wrong}
        for m in mistake_result.scalars().all()
    ]

    prompt = build_daily_agenda_prompt(
        current_user.username, profile_dict, weak_subjects,
        due_flashcards, exams, study_minutes_today, mistake_patterns
    )

    raw, _ = await generate_content(prompt)

    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        agenda_data = json.loads(json_match.group() if json_match else raw)
    except Exception:
        agenda_data = {
            "greeting": "Ready to study today?",
            "priority_alert": "Review your flashcards",
            "predicted_score": "Keep studying to improve your score",
            "blocks": [
                {"time": "Now", "type": "flashcards", "subject": "General",
                 "topic": "Due cards", "action": "Review due flashcards",
                 "why": "Spaced repetition keeps knowledge fresh", "xp": 20, "minutes": 20}
            ],
            "daily_goal": "Study for at least 30 minutes today",
            "insight": "Consistent daily study outperforms long cramming sessions"
        }

    # Cache it
    agenda_record = DailyAgenda(
        username=current_user.username,
        agenda_date=today,
        agenda_json=json.dumps(agenda_data),
        total_minutes=sum(b.get("minutes", 0) for b in agenda_data.get("blocks", []))
    )
    db.add(agenda_record)
    await db.commit()

    return {"agenda": agenda_data, "cached": False, "date": today}


@router.post("/regenerate-agenda")
async def regenerate_agenda(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today().isoformat()
    result = await db.execute(
        select(DailyAgenda).where(
            DailyAgenda.username == current_user.username,
            DailyAgenda.agenda_date == today
        )
    )
    cached = result.scalar_one_or_none()
    if cached:
        await db.delete(cached)
        await db.commit()
    return await get_daily_agenda.__wrapped__(current_user, db) if hasattr(get_daily_agenda, '__wrapped__') else {"message": "Refresh to get new agenda"}


@router.get("/weak-spots")
async def get_weak_spots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(StudentELO)
        .where(
            StudentELO.username == current_user.username,
            StudentELO.total_questions > 0
        )
        .order_by(StudentELO.elo_rating)
        .limit(10)
    )
    weak = result.scalars().all()

    strong_result = await db.execute(
        select(StudentELO)
        .where(
            StudentELO.username == current_user.username,
            StudentELO.total_questions > 0
        )
        .order_by(desc(StudentELO.elo_rating))
        .limit(5)
    )
    strong = strong_result.scalars().all()

    return {
        "weak": [{"subject": r.subject, "chapter": r.chapter, "elo": r.elo_rating, "accuracy": r.accuracy, "questions": r.total_questions} for r in weak],
        "strong": [{"subject": r.subject, "chapter": r.chapter, "elo": r.elo_rating, "accuracy": r.accuracy, "questions": r.total_questions} for r in strong]
    }


@router.get("/performance-summary")
async def get_performance_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    total_q = await db.execute(select(func.count()).select_from(StudentELO).where(StudentELO.username == current_user.username, StudentELO.total_questions > 0))
    subjects_studied = total_q.scalar() or 0

    avg_elo = await db.execute(select(func.avg(StudentELO.elo_rating)).where(StudentELO.username == current_user.username, StudentELO.total_questions > 0))
    average_elo = round(avg_elo.scalar() or 1000, 1)

    total_mistakes = await db.execute(select(func.count()).select_from(MistakeEntry).where(MistakeEntry.username == current_user.username))
    mistake_count = total_mistakes.scalar() or 0

    return {
        "subjects_studied": subjects_studied,
        "average_elo": average_elo,
        "mistake_count": mistake_count,
        "elo_label": "Beginner" if average_elo < 900 else "Intermediate" if average_elo < 1100 else "Advanced" if average_elo < 1300 else "Expert"
    }


@router.post("/knowledge-graph")
async def generate_knowledge_graph(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    subject = payload.get("subject", "")
    course = payload.get("course", "")
    chapters = payload.get("chapters", [])

    if not chapters:
        return {"nodes": []}

    # Get mastery data
    elo_result = await db.execute(
        select(StudentELO).where(
            StudentELO.username == current_user.username,
            StudentELO.subject == subject
        )
    )
    elo_map = {r.chapter: {"elo": r.elo_rating, "accuracy": r.accuracy} for r in elo_result.scalars().all()}

    prompt = build_knowledge_graph_prompt(subject, course, chapters)
    raw, _ = await generate_content(prompt)

    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        graph_data = json.loads(json_match.group() if json_match else raw)
    except Exception:
        graph_data = {"nodes": [{"id": c, "label": c, "difficulty": 3, "prerequisites": [], "category": "core", "estimated_hours": 2} for c in chapters]}

    # Enrich nodes with mastery data
    for node in graph_data.get("nodes", []):
        chapter_elo = elo_map.get(node["id"], {})
        node["elo"] = chapter_elo.get("elo", None)
        node["accuracy"] = chapter_elo.get("accuracy", None)
        node["mastery"] = (
            "untouched" if not chapter_elo else
            "weak" if chapter_elo.get("elo", 1000) < 900 else
            "learning" if chapter_elo.get("elo", 1000) < 1100 else
            "strong" if chapter_elo.get("elo", 1000) < 1300 else
            "expert"
        )

    return graph_data
