# ═══════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — daily_engagement.py
# Handles: Daily logins, XP/Streaks, Study sessions, Badges, User stats
# ═══════════════════════════════════════════════════════════════════════════

import sqlite3
import datetime

# ─────────────────────────────────────────────────────────────────────────
# DATABASE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────
def init_enhanced_db():
    """Create all engagement-related tables."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Daily logins & streaks
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            login_date TEXT NOT NULL UNIQUE,
            xp_awarded INTEGER DEFAULT 20,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)

    # XP and levels
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_xp (
            username TEXT PRIMARY KEY,
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            level_progress INTEGER DEFAULT 0,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)

    # Study sessions (for timer tracking)
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            subject TEXT NOT NULL,
            session_type TEXT DEFAULT 'study',
            duration_minutes INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)

    # Streaks tracking
    c.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            username TEXT PRIMARY KEY,
            current_streak_days INTEGER DEFAULT 0,
            longest_streak_days INTEGER DEFAULT 0,
            last_login_date TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)

    # Badges earned
    c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            badge_id TEXT NOT NULL,
            badge_name TEXT NOT NULL,
            earned_date TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username),
            UNIQUE(username, badge_id)
        )
    """)

    # Flashcards table
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            front_text TEXT NOT NULL,
            back_text TEXT NOT NULL,
            subject TEXT,
            chapter TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            next_review_date TEXT DEFAULT CURRENT_DATE,
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            review_count INTEGER DEFAULT 0,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────
# DAILY LOGIN & STREAK MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────
def check_daily_login(username):
    """
    Check if user logged in today.
    If yes: return message.
    If no: record login, update streak, award XP.
    """
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Check if already logged in today
    c.execute("SELECT id FROM daily_logins WHERE username=? AND login_date=?",
              (username, today))
    existing = c.fetchone()

    if existing:
        conn.close()
        return {"message": "Already checked in today! ✅", "new_login": False}

    # Record new login
    c.execute("INSERT INTO daily_logins (username, login_date, xp_awarded) VALUES (?,?,?)",
              (username, today, 20))

    # Update streak
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    c.execute("SELECT current_streak_days FROM streaks WHERE username=?", (username,))
    row = c.fetchone()

    if row:
        streak_days = row[0]
        c.execute("SELECT login_date FROM daily_logins WHERE username=? AND login_date=?",
                  (username, yesterday))
        if c.fetchone():
            # Consecutive login — increment
            new_streak = streak_days + 1
        else:
            # Broken streak — reset
            new_streak = 1
        c.execute("""
            UPDATE streaks
            SET current_streak_days=?, last_login_date=?
            WHERE username=?
        """, (new_streak, today, username))
    else:
        # First login ever
        c.execute("""
            INSERT INTO streaks (username, current_streak_days, longest_streak_days, last_login_date)
            VALUES (?, 1, 1, ?)
        """, (username, today))
        new_streak = 1

    # Award XP
    award_xp(username, 20)

    conn.commit()
    conn.close()

    return {"message": f"Daily check-in awarded! 🔥 {new_streak} day streak", "new_login": True}

# ─────────────────────────────────────────────────────────────────────────
# XP & LEVELS
# ─────────────────────────────────────────────────────────────────────────
def award_xp(username, xp_amount):
    """Add XP to user, auto-level if needed."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT total_xp, level FROM user_xp WHERE username=?", (username,))
    row = c.fetchone()

    if row:
        total_xp, level = row
    else:
        c.execute("INSERT INTO user_xp (username, total_xp, level, level_progress) VALUES (?,?,?,?)",
                  (username, 0, 1, 0))
        conn.commit()
        total_xp, level = 0, 1

    # Calculate new XP
    new_total_xp = total_xp + xp_amount
    xp_per_level = 500

    # Level up logic
    new_level = 1 + (new_total_xp // xp_per_level)
    level_progress = new_total_xp % xp_per_level

    c.execute("""
        UPDATE user_xp
        SET total_xp=?, level=?, level_progress=?
        WHERE username=?
    """, (new_total_xp, new_level, level_progress, username))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────
# STUDY SESSIONS
# ─────────────────────────────────────────────────────────────────────────
def record_study_session(username, subject, session_type, duration_minutes):
    """Record a study session (for timer)."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO study_sessions
        (username, subject, session_type, duration_minutes, session_date)
        VALUES (?, ?, ?, ?, ?)
    """, (username, subject, session_type, duration_minutes, today))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────
# BADGES / ACHIEVEMENTS
# ─────────────────────────────────────────────────────────────────────────
def award_badge(username, badge_id, badge_name):
    """Award a badge if not already earned."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Check if already earned
    c.execute("SELECT id FROM achievements WHERE username=? AND badge_id=?",
              (username, badge_id))
    if c.fetchone():
        conn.close()
        return False  # Already earned

    # Award it
    c.execute("""
        INSERT INTO achievements (username, badge_id, badge_name, earned_date)
        VALUES (?, ?, ?, ?)
    """, (username, badge_id, badge_name, today))

    conn.commit()
    conn.close()
    return True

# ─────────────────────────────────────────────────────────────────────────
# USER STATS
# ─────────────────────────────────────────────────────────────────────────
def get_user_stats(username):
    """Get all user statistics for dashboard display."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # XP & Level
    c.execute("SELECT total_xp, level, level_progress FROM user_xp WHERE username=?",
              (username,))
    xp_row = c.fetchone()
    if xp_row:
        total_xp, level, level_progress = xp_row
    else:
        total_xp, level, level_progress = 0, 1, 0

    # Streak
    c.execute("SELECT current_streak_days, longest_streak_days FROM streaks WHERE username=?",
              (username,))
    streak_row = c.fetchone()
    if streak_row:
        streak_days, longest_streak = streak_row
    else:
        streak_days, longest_streak = 0, 0

    # Study sessions this week
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    c.execute("""
        SELECT SUM(duration_minutes) FROM study_sessions
        WHERE username=? AND session_date >= ?
    """, (username, week_ago))
    week_minutes = c.fetchone()[0] or 0

    # Total study time
    c.execute("""
        SELECT SUM(duration_minutes) FROM study_sessions
        WHERE username=?
    """, (username,))
    total_minutes = c.fetchone()[0] or 0

    # Flashcards due today
    today = datetime.date.today().isoformat()
    c.execute("""
        SELECT COUNT(*) FROM flashcards
        WHERE username=? AND next_review_date <= ?
    """, (username, today))
    flashcards_due = c.fetchone()[0] or 0

    conn.close()

    return {
        "total_xp": total_xp,
        "level": level,
        "level_progress": level_progress,
        "streak_days": streak_days,
        "longest_streak": longest_streak,
        "weekly_study_minutes": week_minutes,
        "total_study_minutes": total_minutes,
        "flashcards_due": flashcards_due,
    }

# ─────────────────────────────────────────────────────────────────────────
# MAINTENANCE
# ─────────────────────────────────────────────────────────────────────────
def reset_daily_engagement():
    """
    Reset daily engagement (call if you want to reset streaks, etc).
    Use with caution!
    """
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE streaks SET current_streak_days = 0")
    conn.commit()
    conn.close()
