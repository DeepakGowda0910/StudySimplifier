from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.user import UserStats, DailyLogin, StudySession, Streak
from models.achievement import Achievement
from models.flashcard import Flashcard

BADGES = [
    {"id": "first_login", "name": "Welcome Scholar", "desc": "Logged in for the first time", "icon": "🎓", "xp": 50, "category": "milestones"},
    {"id": "streak_3", "name": "3-Day Warrior", "desc": "3-day study streak", "icon": "🔥", "xp": 100, "category": "streaks"},
    {"id": "streak_7", "name": "Week Champion", "desc": "7-day study streak", "icon": "⚡", "xp": 200, "category": "streaks"},
    {"id": "streak_30", "name": "Monthly Legend", "desc": "30-day study streak", "icon": "🏆", "xp": 500, "category": "streaks"},
    {"id": "level_5", "name": "Rising Star", "desc": "Reached Level 5", "icon": "⭐", "xp": 150, "category": "levels"},
    {"id": "level_10", "name": "Knowledge Seeker", "desc": "Reached Level 10", "icon": "🌟", "xp": 300, "category": "levels"},
    {"id": "level_25", "name": "Study Master", "desc": "Reached Level 25", "icon": "💫", "xp": 750, "category": "levels"},
    {"id": "fc_10", "name": "Flashcard Novice", "desc": "Created 10 flashcards", "icon": "🃏", "xp": 100, "category": "flashcards"},
    {"id": "fc_50", "name": "Card Collector", "desc": "Created 50 flashcards", "icon": "📚", "xp": 200, "category": "flashcards"},
    {"id": "fc_100", "name": "Flashcard Master", "desc": "Created 100 flashcards", "icon": "🎴", "xp": 400, "category": "flashcards"},
    {"id": "study_60", "name": "Hour Scholar", "desc": "Studied for 60 minutes total", "icon": "⏰", "xp": 100, "category": "study"},
    {"id": "study_600", "name": "Dedicated Learner", "desc": "Studied for 10 hours total", "icon": "📖", "xp": 250, "category": "study"},
    {"id": "study_3000", "name": "Study Marathon", "desc": "Studied for 50 hours total", "icon": "🏃", "xp": 600, "category": "study"},
    {"id": "gen_10", "name": "Content Creator", "desc": "Generated 10 study materials", "icon": "✨", "xp": 150, "category": "content"},
    {"id": "gen_50", "name": "Knowledge Factory", "desc": "Generated 50 study materials", "icon": "🏭", "xp": 350, "category": "content"},
    {"id": "pomodoro_10", "name": "Focus Master", "desc": "Completed 10 Pomodoro sessions", "icon": "🍅", "xp": 200, "category": "focus"},
    {"id": "notes_5", "name": "Note Taker", "desc": "Created 5 notes", "icon": "📝", "xp": 100, "category": "notes"},
]

BADGE_MAP = {b["id"]: b for b in BADGES}

async def award_xp(db: AsyncSession, username: str, amount: int) -> dict:
    result = await db.execute(select(UserStats).where(UserStats.username == username))
    stats = result.scalar_one_or_none()
    if not stats:
        stats = UserStats(username=username, total_xp=0, level=1, level_progress=0)
        db.add(stats)

    stats.total_xp += amount
    stats.level = stats.total_xp // 500 + 1
    stats.level_progress = stats.total_xp % 500
    await db.commit()
    return {"total_xp": stats.total_xp, "level": stats.level, "level_progress": stats.level_progress}

async def check_daily_login(db: AsyncSession, username: str) -> dict:
    today = date.today().isoformat()
    result = await db.execute(
        select(DailyLogin).where(DailyLogin.username == username, DailyLogin.login_date == today)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {"already_claimed": True, "xp": 0}

    login = DailyLogin(username=username, login_date=today, xp_awarded=20)
    db.add(login)
    await update_streak(db, username)
    await award_xp(db, username, 20)
    await db.commit()
    return {"already_claimed": False, "xp": 20}

async def update_streak(db: AsyncSession, username: str):
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    result = await db.execute(select(Streak).where(Streak.username == username))
    streak = result.scalar_one_or_none()

    if not streak:
        streak = Streak(username=username, current_streak=1, longest_streak=1, last_login_date=today)
        db.add(streak)
    else:
        if streak.last_login_date == yesterday:
            streak.current_streak += 1
        elif streak.last_login_date != today:
            streak.current_streak = 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_login_date = today

    result2 = await db.execute(select(UserStats).where(UserStats.username == username))
    stats = result2.scalar_one_or_none()
    if stats:
        stats.streak_days = streak.current_streak
        stats.longest_streak = streak.longest_streak
    await db.commit()

async def award_badge(db: AsyncSession, username: str, badge_id: str) -> bool:
    result = await db.execute(
        select(Achievement).where(Achievement.username == username, Achievement.badge_id == badge_id)
    )
    if result.scalar_one_or_none():
        return False

    badge = BADGE_MAP.get(badge_id)
    if not badge:
        return False

    achievement = Achievement(
        username=username,
        badge_id=badge_id,
        badge_name=badge["name"],
        badge_description=badge["desc"],
        badge_icon=badge["icon"],
        category=badge["category"],
        xp_reward=badge["xp"]
    )
    db.add(achievement)
    await award_xp(db, username, badge["xp"])
    await db.commit()
    return True

async def auto_check_badges(db: AsyncSession, username: str) -> list:
    awarded = []

    result = await db.execute(select(Achievement.badge_id).where(Achievement.username == username))
    earned_ids = {row[0] for row in result.fetchall()}

    result = await db.execute(select(UserStats).where(UserStats.username == username))
    stats = result.scalar_one_or_none()

    result2 = await db.execute(select(func.count()).select_from(Flashcard).where(Flashcard.username == username))
    fc_count = result2.scalar()

    checks = [
        ("first_login", True),
        ("streak_3", stats and stats.streak_days >= 3),
        ("streak_7", stats and stats.streak_days >= 7),
        ("streak_30", stats and stats.streak_days >= 30),
        ("level_5", stats and stats.level >= 5),
        ("level_10", stats and stats.level >= 10),
        ("level_25", stats and stats.level >= 25),
        ("fc_10", fc_count >= 10),
        ("fc_50", fc_count >= 50),
        ("fc_100", fc_count >= 100),
        ("study_60", stats and stats.total_minutes >= 60),
        ("study_600", stats and stats.total_minutes >= 600),
        ("study_3000", stats and stats.total_minutes >= 3000),
    ]

    for badge_id, condition in checks:
        if condition and badge_id not in earned_ids:
            if await award_badge(db, username, badge_id):
                awarded.append(badge_id)

    return awarded
