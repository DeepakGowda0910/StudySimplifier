# daily_engagement.py
import sqlite3
import datetime
import json
from typing import List, Dict, Tuple

def check_daily_login(username: str) -> Dict:
    """Check and update daily streak. Returns streak info."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    today = datetime.date.today().isoformat()
    
    # Get user progress
    c.execute("SELECT streak_days, last_active_date FROM user_progress WHERE username=?", (username,))
    row = c.fetchone()
    
    if not row:
        # First time user
        c.execute("""
            INSERT INTO user_progress (username, streak_days, last_active_date, total_xp, level)
            VALUES (?, 1, ?, 100, 1)
        """, (username, today))
        conn.commit()
        conn.close()
        return {"streak": 1, "is_new_streak": True, "message": "🎉 First day streak started!"}
    
    streak_days, last_active = row
    
    if last_active == today:
        # Already checked in today
        conn.close()
        return {"streak": streak_days, "is_new_streak": False, "message": "✅ Already checked in today"}
    
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    
    if last_active == yesterday:
        # Consecutive day
        new_streak = streak_days + 1
        c.execute("UPDATE user_progress SET streak_days=?, last_active_date=? WHERE username=?", 
                 (new_streak, today, username))
        
        # Check for milestone rewards
        reward = check_streak_milestone(new_streak, username)
        
        conn.commit()
        conn.close()
        return {"streak": new_streak, "is_new_streak": True, "reward": reward, 
                "message": f"🔥 Day {new_streak} streak! {reward.get('message', '')}"}
    else:
        # Broken streak
        c.execute("UPDATE user_progress SET streak_days=1, last_active_date=? WHERE username=?", 
                 (today, username))
        conn.commit()
        conn.close()
        return {"streak": 1, "is_new_streak": True, "message": "🔄 Streak reset. New day 1!"}

def check_streak_milestone(streak: int, username: str) -> Dict:
    """Check if streak hits a milestone and award XP."""
    milestones = {
        3: {"xp": 50, "badge": "early_bird", "message": "🏅 3-day streak! +50 XP"},
        7: {"xp": 150, "badge": "weekly_warrior", "message": "🎖️ 7-day streak! +150 XP"},
        14: {"xp": 300, "badge": "fortnight_champ", "message": "🏆 14-day streak! +300 XP"},
        30: {"xp": 1000, "badge": "monthly_master", "message": "👑 30-day streak! +1000 XP"}
    }
    
    if streak in milestones:
        milestone = milestones[streak]
        award_xp(username, milestone["xp"])
        award_badge(username, milestone["badge"], f"{streak}-day streak")
        return milestone
    
    return {"xp": 10, "message": f"+10 XP for day {streak}"}

def award_xp(username: str, xp: int):
    """Award XP to user and check level up."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    c.execute("UPDATE user_progress SET total_xp = total_xp + ? WHERE username=?", (xp, username))
    
    # Check level up (simplified: 1000 XP per level)
    c.execute("SELECT total_xp, level FROM user_progress WHERE username=?", (username,))
    current_xp, current_level = c.fetchone()
    
    new_level = current_xp // 1000 + 1
    if new_level > current_level:
        c.execute("UPDATE user_progress SET level=? WHERE username=?", (new_level, username))
        conn.commit()
        conn.close()
        return {"level_up": True, "new_level": new_level, "message": f"🎯 Level up! Now level {new_level}"}
    
    conn.commit()
    conn.close()
    return {"level_up": False}

def award_badge(username: str, badge_id: str, badge_name: str):
    """Award a badge to user."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    today = datetime.date.today().isoformat()
    
    # Check if already has badge
    c.execute("SELECT id FROM achievements WHERE username=? AND badge_id=?", (username, badge_id))
    if not c.fetchone():
        c.execute("INSERT INTO achievements (username, badge_id, badge_name, earned_date) VALUES (?, ?, ?, ?)",
                 (username, badge_id, badge_name, today))
    
    conn.commit()
    conn.close()

def get_user_stats(username: str) -> Dict:
    """Get comprehensive user statistics."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    # Basic progress
    c.execute("""
        SELECT streak_days, total_xp, level, total_study_minutes 
        FROM user_progress WHERE username=?
    """, (username,))
    row = c.fetchone()
    
    if not row:
        return {}
    
    streak_days, total_xp, level, total_study_minutes = row
    
    # Flashcards due today
    today = datetime.date.today().isoformat()
    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=? AND next_review_date <= ?", 
             (username, today))
    flashcards_due = c.fetchone()[0] or 0
    
    # Study sessions this week
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    c.execute("""
        SELECT SUM(duration_minutes), COUNT(*) 
        FROM study_sessions 
        WHERE username=? AND start_time >= ?
    """, (username, week_ago))
    weekly_study_minutes, weekly_sessions = c.fetchone()
    
    # Achievements count
    c.execute("SELECT COUNT(*) FROM achievements WHERE username=?", (username,))
    achievements_count = c.fetchone()[0]
    
    conn.close()
    
    return {
        "streak_days": streak_days,
        "total_xp": total_xp,
        "level": level,
        "total_study_minutes": total_study_minutes or 0,
        "flashcards_due": flashcards_due,
        "weekly_study_minutes": weekly_study_minutes or 0,
        "weekly_sessions": weekly_sessions or 0,
        "achievements_count": achievements_count,
        "next_level_xp": (level * 1000) - total_xp,
        "level_progress": total_xp % 1000
    }

def record_study_session(username: str, subject: str, activity_type: str, duration_minutes: int):
    """Record a study session."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    start_time = datetime.datetime.now().isoformat()
    end_time = (datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)).isoformat()
    
    c.execute("""
        INSERT INTO study_sessions (username, start_time, end_time, duration_minutes, subject, activity_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, start_time, end_time, duration_minutes, subject, activity_type))
    
    # Update total study minutes
    c.execute("""
        UPDATE user_progress 
        SET total_study_minutes = total_study_minutes + ? 
        WHERE username=?
    """, (duration_minutes, username))
    
    # Award XP for studying (10 XP per 10 minutes)
    xp_earned = (duration_minutes // 10) * 10
    if xp_earned > 0:
        award_xp(username, xp_earned)
    
    conn.commit()
    conn.close()
    
    return {"xp_earned": xp_earned, "duration": duration_minutes}
