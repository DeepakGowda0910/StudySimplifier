import streamlit as st
import sqlite3
import hashlib
import datetime
import time
import json
import os
# import google.generativeai as genai  # Uncomment and configure your Gemini API here

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS STYLING (Add your custom CSS here)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .sf-header { text-align: center; padding: 20px; }
    .sf-header-title { font-size: 2.5rem; font-weight: bold; color: #2563eb; }
    .sf-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    /* Add the rest of your custom CSS here */
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
def _ensure_column(cursor, table_name, column_name, column_def):
    """Safely add columns if they don't exist"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if column_name not in existing_cols:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    # User Profile
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            username TEXT PRIMARY KEY,
            category TEXT DEFAULT '',
            course TEXT DEFAULT '',
            stream TEXT DEFAULT '',
            board TEXT DEFAULT '',
            onboarded INTEGER DEFAULT 0,
            created_at TEXT DEFAULT ''
        )
    """)

    # User Stats
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            username TEXT PRIMARY KEY,
            total_xp INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_login TEXT DEFAULT '',
            total_minutes INTEGER DEFAULT 0,
            total_study_minutes INTEGER DEFAULT 0,
            weekly_minutes TEXT DEFAULT '{}',
            xp_points INTEGER DEFAULT 0
        )
    """)

    # Badges & Achievements
    c.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            username TEXT,
            badge_id TEXT,
            earned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username, badge_id)
        )
    """)

    # Flashcards
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            front_text TEXT DEFAULT '',
            back_text TEXT DEFAULT '',
            front TEXT DEFAULT '',
            back TEXT DEFAULT '',
            subject TEXT DEFAULT '',
            chapter TEXT DEFAULT '',
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            next_review_date TEXT DEFAULT '',
            review_count INTEGER DEFAULT 0,
            created_date TEXT DEFAULT ''
        )
    """)

    # Activity Log
    c.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            tool TEXT,
            chapter TEXT,
            subject TEXT,
            preview TEXT,
            log_time TEXT
        )
    """)

    # Migrations
    _ensure_column(c, "user_profile", "onboarded", "INTEGER DEFAULT 0")
    _ensure_column(c, "user_stats", "streak_days", "INTEGER DEFAULT 0")
    _ensure_column(c, "flashcards", "front_text", "TEXT DEFAULT ''")
    _ensure_column(c, "flashcards", "back_text", "TEXT DEFAULT ''")
    
    conn.commit()
    conn.close()
    # ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION & WHITELIST
# ─────────────────────────────────────────────────────────────────────────────
def hash_p(password):
    return hashlib.sha256(password.encode()).hexdigest()

WHITELISTED_USERS = {
    "admin": "admin123",
    "student1": "pass123",
    "demo": "demo123",
    "Deepak": "deepak123" # Add your exact username here
}

def seed_whitelisted_users():
    """Insert or update whitelisted users with hashed passwords."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    for uname, raw_pwd in WHITELISTED_USERS.items():
        hashed_pwd = hash_p(raw_pwd)
        c.execute("SELECT username FROM users WHERE username=?", (uname,))
        if c.fetchone():
            c.execute("UPDATE users SET password=? WHERE username=?", (hashed_pwd, uname))
        else:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (uname, hashed_pwd))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE & ROUTING
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "logged_in": False,
        "username": "",
        "page": "login",
        "active_page": "dashboard",
        "history": [],
        "daily_checkin_done": False,
        "study_timer_active": False,
        "study_timer_start": None,
        "current_subject_for_timer": "General"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.get("logged_in", False) and st.session_state.get("page") == "login":
        st.session_state.page = "dashboard"

    if st.session_state.get("page") == "study_tools":
        st.session_state.active_page = "study"
    elif st.session_state.get("page") in ["dashboard", "study", "flashcards", "achievements", "settings"]:
        st.session_state.active_page = st.session_state.page

def go_to(page):
    page_alias = {"study_tools": "study", "study": "study", "dashboard": "dashboard", 
                  "flashcards": "flashcards", "achievements": "achievements", "login": "login"}
    st.session_state.page = page
    if page in page_alias and page != "login":
        st.session_state.active_page = page_alias[page]
    st.rerun()

def do_logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page = "login"
    st.session_state.active_page = "dashboard"
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE & STATS HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_user_profile(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_profile (username) VALUES (?)", (username,))
    conn.commit()
    c.execute("SELECT category, course, stream, board, onboarded FROM user_profile WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"category": row[0] or "", "course": row[1] or "", "stream": row[2] or "", "board": row[3] or "", "onboarded": int(row[4] or 0)}
    return None

def reset_profile(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE user_profile SET onboarded=0, category='', course='', stream='', board='' WHERE username=?", (username,))
    conn.commit()
    conn.close()

def get_user_stats(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT streak_days, total_minutes FROM user_stats WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return {"streak_days": row[0] if row else 0, "total_minutes": row[1] if row else 0}
# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARDS DB HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def add_flashcard(username, front, back, subject="", chapter=""):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        INSERT INTO flashcards (username, front_text, back_text, front, back, subject, chapter, next_review_date, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, front, back, front, back, subject, chapter, today, today))
    conn.commit()
    conn.close()

def get_due_flashcards(username):
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, COALESCE(NULLIF(front_text, ''), front), COALESCE(NULLIF(back_text, ''), back), subject, chapter, next_review_date, review_count
        FROM flashcards WHERE username=? AND next_review_date <= ? ORDER BY next_review_date ASC
    """, (username, today))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, COALESCE(NULLIF(front_text, ''), front), COALESCE(NULLIF(back_text, ''), back), subject, chapter, next_review_date, review_count
        FROM flashcards WHERE username=? ORDER BY id DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_flashcard_review(card_id, quality):
    interval_map = {1: 7, 2: 3, 3: 1} # 1: Easy, 2: Medium, 3: Hard
    days = interval_map.get(quality, 1)
    next_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE flashcards SET next_review_date=?, interval_days=?, review_count=review_count + 1 WHERE id=?", (next_date, days, card_id))
    conn.commit()
    conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        st.markdown("<div class='sf-header'><div class='sf-header-title'>StudySmart AI</div></div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                u = st.text_input("👤 Username", key="login_u")
                p = st.text_input("🔑 Password", type="password", key="login_p")
                submit = st.form_submit_button("Sign In 🚀", use_container_width=True)
            
            if submit:
                if u.strip() and p.strip():
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u.strip(), hash_p(p)))
                    user_row = c.fetchone()
                    
                    if user_row:
                        c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (u.strip(),))
                        conn.commit()
                        st.session_state.logged_in = True
                        st.session_state.username = u.strip()
                        st.session_state.page = "dashboard"
                        st.success("✅ Login successful!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
                    conn.close()
                else:
                    st.warning("⚠️ Enter username and password.")
                    
        with tab2:
            st.info("📝 Registration is currently closed. Contact admin for access.")

def render_sidebar(username):
    stats = get_user_stats(username)
    with st.sidebar:
        st.markdown(f"### 🎓 StudySmart AI\nHi, **{username}** 👋")
        st.success(f"🔥 Streak: {stats['streak_days']} Days")
        
        st.divider()
        st.markdown("**🧭 Navigate**")
        cur = st.session_state.active_page
        
        for key, label in [("dashboard", "📊 Dashboard"), ("study", "📚 Study Tools"), ("flashcards", "🗂️ Flashcards"), ("achievements", "🏅 Achievements")]:
            btn_type = "primary" if cur == key else "secondary"
            if st.button(label, use_container_width=True, key=f"nav_{key}", type=btn_type):
                go_to(key)

        st.divider()
        if st.button("🔄 Reset Profile"):
            reset_profile(username)
            st.rerun()
            
        if st.button("🚪 Logout", type="primary", use_container_width=True):
            do_logout()
# ─────────────────────────────────────────────────────────────────────────────
# VIEWS
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard(username):
    st.title("📊 Dashboard")
    st.write("Welcome to your dashboard!")
    # Add your dashboard graphs/activity UI back here

def show_study_tools(username):
    st.title("📚 Study Tools")
    st.write("Select a subject and generate notes/quizzes.")
    # Add your Gemini generation logic UI back here

def show_achievements(username):
    st.title("🏅 Achievements")
    st.write("Here are your unlocked badges.")
    # Add your badges UI here

def show_flashcards(username):
    st.title("🗂️ Flashcards")
    tab1, tab2, tab3 = st.tabs(["📖 Review Due", "➕ Create", "📋 My Library"])

    with tab1:
        due = get_due_flashcards(username)
        if not due:
            st.success("🎉 No flashcards due today — great job!")
        else:
            for row in due:
                c_id, front, back, subj, chap, nrd, rc = row
                with st.expander(f"📌 {front[:60]}"):
                    st.markdown(f"**Q:** {front}\n\n**A:** {back}")
                    c1, c2, c3 = st.columns(3)
                    if c1.button("😊 Easy", key=f"e_{c_id}"): update_flashcard_review(c_id, 1); st.rerun()
                    if c2.button("😐 Med", key=f"m_{c_id}"): update_flashcard_review(c_id, 2); st.rerun()
                    if c3.button("😓 Hard", key=f"h_{c_id}"): update_flashcard_review(c_id, 3); st.rerun()

    with tab2:
        front = st.text_area("Question")
        back = st.text_area("Answer")
        subj = st.text_input("Subject")
        chap = st.text_input("Chapter")
        if st.button("Save Flashcard"):
            add_flashcard(username, front, back, subj, chap)
            st.success("Saved!")
            st.rerun()

    with tab3:
        all_cards = get_all_flashcards(username)
        for row in all_cards:
            c_id, front, back, subj, chap, nrd, rc = row
            with st.expander(f"📌 {front[:60]}"):
                st.markdown(f"**Q:** {front}\n\n**A:** {back}")
                if st.button("🗑️ Delete", key=f"del_{c_id}"):
                    delete_flashcard(c_id)
                    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main_app():
    render_sidebar(st.session_state.username)
    page = st.session_state.active_page

    if page == "dashboard":    show_dashboard(st.session_state.username)
    elif page == "study":      show_study_tools(st.session_state.username)
    elif page == "flashcards": show_flashcards(st.session_state.username)
    elif page == "achievements": show_achievements(st.session_state.username)
    else:                      show_dashboard(st.session_state.username)

def main():
    init_db()
    init_session_state()
    
    # Ensures whitelist database is ready
    seed_whitelisted_users()

    if not st.session_state.logged_in:
        auth_ui()
    else:
        # Check maintenance mode (Optional: set to False to disable)
        MAINTENANCE_MODE = False
        ALLOWED_MAINTENANCE = ["Deepak"]
        
        if MAINTENANCE_MODE and st.session_state.username not in ALLOWED_MAINTENANCE:
            st.error("🛠️ App is under maintenance. Be back soon!")
        else:
            main_app()

if __name__ == "__main__":
    main()
