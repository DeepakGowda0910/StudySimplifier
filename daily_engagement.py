# ═══════════════════════════════════════════════════════════════════════════════
# daily_engagement.py
# StudySmart AI — Daily Engagement Engine
#
# Handles:
#   - Database table creation for all engagement features
#   - Daily login streak tracking
#   - XP awarding and level calculation
#   - Badge / achievement awarding
#   - Study session logging
#   - User stats retrieval for Dashboard and Sidebar
#
# Used by: app.py
# No Streamlit imports here — pure Python logic only
# ═══════════════════════════════════════════════════════════════════════════════

import sqlite3
import datetime

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE — always connects to the same users.db as app.py
# ─────────────────────────────────────────────────────────────────────────────

DB_PATH = "users.db"


def _get_conn():
    """Return a connection to the shared users.db database."""
    return sqlite3.connect(DB_PATH)


# ─────────────────────────────────────────────────────────────────────────────
# INIT — creates all new tables without touching the existing users table
# Call this once at startup from app.py: init_enhanced_db()
# ─────────────────────────────────────────────────────────────────────────────

def init_enhanced_db():
    """
    Creates all engagement-related tables if they do not already exist.
    Safe to call every time the app starts — does NOT overwrite existing data.
    """

    conn = _get_conn()
    c = conn.cursor()

    # ── User progress: streak, XP, level, total study time ──────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            username         TEXT PRIMARY KEY,
            streak_days      INTEGER DEFAULT 0,
            last_active_date TEXT    DEFAULT NULL,
            total_xp         INTEGER DEFAULT 0,
            level            INTEGER DEFAULT 1,
            total_study_min  INTEGER DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # ── Achievements / badges ────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL,
            badge_id    TEXT    NOT NULL,
            badge_name  TEXT    NOT NULL,
            earned_date TEXT    NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # ── Study sessions: timer log ────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT    NOT NULL,
            subject          TEXT    DEFAULT 'General',
            activity_type    TEXT    DEFAULT 'study',
            duration_minutes INTEGER DEFAULT 0,
            session_date     TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # ── Flashcards: spaced repetition ───────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT    NOT NULL,
            front_text       TEXT    NOT NULL,
            back_text        TEXT    NOT NULL,
            subject          TEXT    DEFAULT '',
            chapter          TEXT    DEFAULT '',
            ease_factor      REAL    DEFAULT 2.5,
            interval_days    INTEGER DEFAULT 1,
            next_review_date TEXT    DEFAULT CURRENT_DATE,
            review_count     INTEGER DEFAULT 0,
            created_date     TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPER — ensure user_progress row exists
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_progress_row(username, cursor):
    """
    Inserts a default user_progress row if one does not already exist.
    Must be called inside an open cursor context.
    """
    cursor.execute(
        "SELECT username FROM user_progress WHERE username = ?",
        (username,)
    )
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO user_progress
            (username, streak_days, last_active_date, total_xp, level, total_study_min)
            VALUES (?, 0, NULL, 0, 1, 0)
        """, (username,))


# ─────────────────────────────────────────────────────────────────────────────
# BADGE AWARDING
# ─────────────────────────────────────────────────────────────────────────────

def award_badge(username, badge_id, badge_name=""):
    """
    Awards a badge to a user. Silently skips if already earned.

    Parameters:
        username  (str): The logged-in user.
        badge_id  (str): Unique badge identifier e.g. 'streak_7'
        badge_name(str): Human-readable name e.g. 'Weekly Warrior' (optional)

    Returns:
        True  — badge was newly awarded
        False — user already had this badge
    """
    conn = _get_conn()
    c = conn.cursor()

    # Check if already awarded
    c.execute(
        "SELECT id FROM achievements WHERE username = ? AND badge_id = ?",
        (username, badge_id)
    )
    if c.fetchone():
        conn.close()
        return False

    today = datetime.date.today().isoformat()

    # Use badge_id as name fallback if name not provided
    display_name = badge_name if badge_name else badge_id.replace("_", " ").title()

    c.execute("""
        INSERT INTO achievements (username, badge_id, badge_name, earned_date)
        VALUES (?, ?, ?, ?)
    """, (username, badge_id, display_name, today))

    conn.commit()
    conn.close()
    return True


# ─────────────────────────────────────────────────────────────────────────────
# XP AWARDING + LEVEL CALCULATION
# ─────────────────────────────────────────────────────────────────────────────

def award_xp(username, xp_amount):
    """
    Adds XP to the user and recalculates their level.
    Level formula: 1 level per 500 XP (level 1 at 0–499, level 2 at 500–999, etc.)

    Parameters:
        username   (str): The logged-in user.
        xp_amount  (int): How much XP to add.

    Returns:
        dict with keys:
            total_xp  (int)  — new total XP
            level     (int)  — new level
            leveled_up(bool) — whether user crossed a level threshold
    """
    if xp_amount <= 0:
        return {"total_xp": 0, "level": 1, "leveled_up": False}

    conn = _get_conn()
    c = conn.cursor()

    _ensure_progress_row(username, c)

    c.execute(
        "SELECT total_xp, level FROM user_progress WHERE username = ?",
        (username,)
    )
    row = c.fetchone()
    old_level = row[1] if row else 1

    c.execute("""
        UPDATE user_progress
        SET total_xp = total_xp + ?
        WHERE username = ?
    """, (xp_amount, username))

    # Recalculate level
    c.execute(
        "SELECT total_xp FROM user_progress WHERE username = ?",
        (username,)
    )
    new_xp = c.fetchone()[0]
    new_level = max(1, (new_xp // 500) + 1)

    c.execute(
        "UPDATE user_progress SET level = ? WHERE username = ?",
        (new_level, username)
    )

    conn.commit()
    conn.close()

    return {
        "total_xp": new_xp,
        "level": new_level,
        "leveled_up": new_level > old_level
    }


# ─────────────────────────────────────────────────────────────────────────────
# DAILY CHECK-IN / STREAK
# ─────────────────────────────────────────────────────────────────────────────

def check_daily_login(username):
    """
    Runs when a user logs in or clicks Daily Check-in.

    Logic:
        - If no record exists → create one, start streak at 1
        - If already checked in today → return current streak, no change
        - If last active was yesterday → increment streak
        - If last active was 2+ days ago → reset streak to 1

    Awards:
        - 20 XP per check-in
        - Bonus badges at 3, 7, 14, 30 day milestones

    Returns:
        dict with keys:
            streak  (int) — current streak days
            message (str) — human-readable status message
            xp_earned(int) — XP awarded this check-in (0 if already checked in)
    """
    conn = _get_conn()
    c = conn.cursor()

    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    _ensure_progress_row(username, c)
    conn.commit()

    c.execute("""
        SELECT streak_days, last_active_date
        FROM user_progress
        WHERE username = ?
    """, (username,))
    row = c.fetchone()
    conn.close()

    streak_days, last_active_date = row

    # ── Already checked in today ─────────────────────────────────────────────
    if last_active_date == today:
        return {
            "streak": streak_days,
            "message": f"✅ Already checked in today! 🔥 {streak_days} day streak",
            "xp_earned": 0
        }

    # ── Calculate new streak ─────────────────────────────────────────────────
    if last_active_date == yesterday:
        new_streak = streak_days + 1
    else:
        new_streak = 1  # Reset — missed a day

    # ── Update DB ────────────────────────────────────────────────────────────
    conn2 = _get_conn()
    c2 = conn2.cursor()
    c2.execute("""
        UPDATE user_progress
        SET streak_days = ?, last_active_date = ?
        WHERE username = ?
    """, (new_streak, today, username))
    conn2.commit()
    conn2.close()

    # ── Award daily XP ───────────────────────────────────────────────────────
    xp_earned = 20
    award_xp(username, xp_earned)

    # ── Award first login badge ──────────────────────────────────────────────
    award_badge(username, "first_login", "First Step")

    # ── Award streak milestone badges ─────────────────────────────────────────
    if new_streak == 3:
        award_badge(username, "streak_3", "Heatwave")
    elif new_streak == 7:
        award_badge(username, "streak_7", "Weekly Warrior")
    elif new_streak == 14:
        award_badge(username, "streak_14", "Fortnight Champ")
    elif new_streak == 30:
        award_badge(username, "streak_30", "Monthly Master")

    # ── Build message ─────────────────────────────────────────────────────────
    if new_streak == 1 and last_active_date is not None:
        message = f"🔄 Streak reset. Day 1 starts now! +{xp_earned} XP"
    elif new_streak == 1:
        message = f"🎉 Welcome to StudySmart! Your streak has begun! +{xp_earned} XP"
    else:
        message = f"🔥 Day {new_streak} streak! Great work! +{xp_earned} XP"

    return {
        "streak": new_streak,
        "message": message,
        "xp_earned": xp_earned
    }


# ─────────────────────────────────────────────────────────────────────────────
# USER STATS — used by Dashboard and Sidebar in app.py
# ─────────────────────────────────────────────────────────────────────────────

def get_user_stats(username):
    """
    Returns a comprehensive stats dictionary for a user.
    Called by app.py for the Dashboard, Sidebar metrics, and XP bar.

    Returns:
        dict with keys:
            streak_days         (int)
            total_xp            (int)
            level               (int)
            level_progress      (int) — XP earned within current level (0–499)
            next_level_xp       (int) — XP remaining to reach next level
            total_study_minutes (int)
            flashcards_due      (int) — cards with next_review_date <= today
            flashcards_total    (int) — all flashcards for the user
            weekly_study_minutes(int) — sum of study minutes in last 7 days
            weekly_sessions     (int) — count of sessions in last 7 days
            badge_count         (int) — total badges earned
        Returns {} if user has no progress record yet.
    """
    conn = _get_conn()
    c = conn.cursor()

    today = datetime.date.today().isoformat()
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()

    # ── Base progress row ────────────────────────────────────────────────────
    c.execute("""
        SELECT streak_days, total_xp, level, total_study_min
        FROM user_progress
        WHERE username = ?
    """, (username,))
    row = c.fetchone()

    if not row:
        conn.close()
        return {}

    streak_days, total_xp, level, total_study_min = row

    # ── XP within current level ──────────────────────────────────────────────
    # Each level requires 500 XP
    level_progress = total_xp % 500
    next_level_xp = 500 - level_progress

    # ── Flashcards due today ─────────────────────────────────────────────────
    c.execute("""
        SELECT COUNT(*)
        FROM flashcards
        WHERE username = ? AND next_review_date <= ?
    """, (username, today))
    flashcards_due = c.fetchone()[0] or 0

    # ── Total flashcards ─────────────────────────────────────────────────────
    c.execute("""
        SELECT COUNT(*)
        FROM flashcards
        WHERE username = ?
    """, (username,))
    flashcards_total = c.fetchone()[0] or 0

    # ── Weekly study stats ───────────────────────────────────────────────────
    c.execute("""
        SELECT
            COALESCE(SUM(duration_minutes), 0),
            COUNT(*)
        FROM study_sessions
        WHERE username = ? AND session_date >= ?
    """, (username, week_ago))
    weekly_row = c.fetchone()
    weekly_study_minutes = weekly_row[0] if weekly_row else 0
    weekly_sessions = weekly_row[1] if weekly_row else 0

    # ── Badge count ──────────────────────────────────────────────────────────
    c.execute("""
        SELECT COUNT(*)
        FROM achievements
        WHERE username = ?
    """, (username,))
    badge_count = c.fetchone()[0] or 0

    conn.close()

    return {
        "streak_days":          streak_days,
        "total_xp":             total_xp,
        "level":                level,
        "level_progress":       level_progress,
        "next_level_xp":        next_level_xp,
        "total_study_minutes":  total_study_min or 0,
        "flashcards_due":       flashcards_due,
        "flashcards_total":     flashcards_total,
        "weekly_study_minutes": weekly_study_minutes,
        "weekly_sessions":      weekly_sessions,
        "badge_count":          badge_count,
    }


# ─────────────────────────────────────────────────────────────────────────────
# RECORD STUDY SESSION — called by app.py when study timer is stopped
# ─────────────────────────────────────────────────────────────────────────────

def record_study_session(username, subject, activity_type, duration_minutes):
    """
    Logs a completed study session to the study_sessions table
    and adds study time to the user's total.

    Also awards XP: 10 XP per 10 minutes studied (minimum 5 XP).

    Parameters:
        username        (str): Logged-in user.
        subject         (str): Subject being studied e.g. 'Physics'
        activity_type   (str): Type of activity e.g. 'study', 'flashcard', 'quiz'
        duration_minutes(int): How long the session was in minutes.

    Returns:
        dict with keys:
            xp_earned       (int)
            duration_minutes(int)
            total_study_min (int) — updated cumulative total
    """
    if duration_minutes <= 0:
        return {"xp_earned": 0, "duration_minutes": 0, "total_study_min": 0}

    conn = _get_conn()
    c = conn.cursor()

    _ensure_progress_row(username, c)

    # Insert session record
    c.execute("""
        INSERT INTO study_sessions
        (username, subject, activity_type, duration_minutes, session_date)
        VALUES (?, ?, ?, ?, ?)
    """, (username, subject, activity_type, duration_minutes,
          datetime.datetime.now().isoformat()))

    # Update total study minutes
    c.execute("""
        UPDATE user_progress
        SET total_study_min = total_study_min + ?
        WHERE username = ?
    """, (duration_minutes, username))

    # Get updated total
    c.execute(
        "SELECT total_study_min FROM user_progress WHERE username = ?",
        (username,)
    )
    total = c.fetchone()[0] or 0

    conn.commit()
    conn.close()

    # Award XP: 10 XP per 10 minutes, minimum 5 XP for any session
    xp_earned = max(5, (duration_minutes // 10) * 10)
    award_xp(username, xp_earned)

    return {
        "xp_earned": xp_earned,
        "duration_minutes": duration_minutes,
        "total_study_min": total
    }
