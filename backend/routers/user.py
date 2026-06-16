from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from models.user import User, UserProfile, UserStats, StudySession, DailyLogin
from models.flashcard import Flashcard
from models.achievement import Achievement
from schemas.user import ProfileUpdate, ProfileResponse, StatsResponse, StudySessionCreate
from middleware.auth import get_current_user
from services.gamification import auto_check_badges, award_xp, BADGES
from datetime import date, timedelta

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).where(UserProfile.username == current_user.username))
    profile = result.scalar_one_or_none()
    if not profile:
        return ProfileResponse(username=current_user.username)
    return ProfileResponse(
        username=current_user.username,
        category=profile.category,
        course=profile.course,
        stream=profile.stream,
        board=profile.board,
        onboarded=profile.onboarded,
        preferred_language=profile.preferred_language or "English",
        theme=profile.theme or "light"
    )

@router.put("/profile")
async def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserProfile).where(UserProfile.username == current_user.username))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(username=current_user.username)
        db.add(profile)

    for field, value in data.dict(exclude_none=True).items():
        setattr(profile, field, value)

    if data.category and data.course:
        profile.onboarded = True

    await db.commit()
    return {"message": "Profile updated"}

@router.get("/stats", response_model=StatsResponse)
async def get_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStats).where(UserStats.username == current_user.username))
    stats = result.scalar_one_or_none()

    today = date.today().isoformat()
    result2 = await db.execute(
        select(func.count()).select_from(Flashcard).where(
            Flashcard.username == current_user.username,
            Flashcard.next_review_date <= today
        )
    )
    due_count = result2.scalar()

    result3 = await db.execute(
        select(func.count()).select_from(Achievement).where(Achievement.username == current_user.username)
    )
    badge_count = result3.scalar()

    new_badges = await auto_check_badges(db, current_user.username)

    return StatsResponse(
        total_xp=stats.total_xp if stats else 0,
        level=stats.level if stats else 1,
        level_progress=stats.level_progress if stats else 0,
        streak_days=stats.streak_days if stats else 0,
        longest_streak=stats.longest_streak if stats else 0,
        total_minutes=stats.total_minutes if stats else 0,
        total_sessions=stats.total_sessions if stats else 0,
        flashcards_due=due_count,
        badges_earned=badge_count
    )

@router.post("/study-session")
async def record_session(data: StudySessionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    session = StudySession(
        username=current_user.username,
        subject=data.subject,
        minutes=data.minutes,
        session_type=data.session_type,
        sess_date=date.today().isoformat()
    )
    db.add(session)

    result = await db.execute(select(UserStats).where(UserStats.username == current_user.username))
    stats = result.scalar_one_or_none()
    if stats:
        stats.total_minutes += data.minutes
        stats.total_sessions += 1

    xp = min(data.minutes * 2, 100)
    await award_xp(db, current_user.username, xp)
    await db.commit()
    await auto_check_badges(db, current_user.username)
    return {"message": "Session recorded", "xp_awarded": xp}

@router.get("/analytics")
async def get_analytics(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()

    result = await db.execute(
        select(StudySession.sess_date, func.sum(StudySession.minutes))
        .where(StudySession.username == current_user.username, StudySession.sess_date >= thirty_days_ago)
        .group_by(StudySession.sess_date)
        .order_by(StudySession.sess_date)
    )
    daily_minutes = [{"date": row[0], "minutes": row[1]} for row in result.fetchall()]

    result2 = await db.execute(
        select(StudySession.subject, func.sum(StudySession.minutes))
        .where(StudySession.username == current_user.username)
        .group_by(StudySession.subject)
        .order_by(desc(func.sum(StudySession.minutes)))
        .limit(10)
    )
    subject_dist = [{"subject": row[0] or "General", "minutes": row[1]} for row in result2.fetchall()]

    result3 = await db.execute(select(UserStats).where(UserStats.username == current_user.username))
    stats = result3.scalar_one_or_none()

    result4 = await db.execute(
        select(func.sum(StudySession.minutes))
        .where(StudySession.username == current_user.username, StudySession.sess_date >= (date.today() - timedelta(days=7)).isoformat())
    )
    weekly_mins = result4.scalar() or 0

    return {
        "daily_minutes": daily_minutes,
        "subject_distribution": subject_dist,
        "weekly_summary": {
            "total_minutes": weekly_mins,
            "total_xp": stats.total_xp if stats else 0,
            "level": stats.level if stats else 1,
            "streak": stats.streak_days if stats else 0
        }
    }

@router.get("/leaderboard")
async def get_leaderboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(UserStats.username, UserStats.total_xp, UserStats.level, UserStats.streak_days, UserStats.total_minutes)
        .order_by(desc(UserStats.total_xp))
        .limit(50)
    )
    rows = result.fetchall()
    leaderboard = []
    for i, row in enumerate(rows):
        leaderboard.append({
            "rank": i + 1,
            "username": row[0],
            "total_xp": row[1],
            "level": row[2],
            "streak_days": row[3],
            "total_minutes": row[4],
            "is_current_user": row[0] == current_user.username
        })
    return leaderboard

@router.get("/achievements")
async def get_achievements(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Achievement).where(Achievement.username == current_user.username)
    )
    earned = result.scalars().all()
    earned_ids = {a.badge_id for a in earned}

    all_badges = []
    for badge in BADGES:
        all_badges.append({
            **badge,
            "earned": badge["id"] in earned_ids,
            "earned_at": next((a.earned_at.isoformat() for a in earned if a.badge_id == badge["id"]), None)
        })
    return all_badges
