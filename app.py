import streamlit as st
import sqlite3
import json
import google.generativeai as genai
from datetime import datetime, timedelta
import os
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_KEY = os.getenv("GEMINI_API_KEY", "")
if API_KEY:
    genai.configure(api_key=API_KEY)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "ob_step" not in st.session_state:
    st.session_state.ob_step = 1
if "ob_category" not in st.session_state:
    st.session_state.ob_category = ""
if "ob_course" not in st.session_state:
    st.session_state.ob_course = ""
if "ob_stream" not in st.session_state:
    st.session_state.ob_stream = ""
if "ob_board" not in st.session_state:
    st.session_state.ob_board = ""
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_seconds" not in st.session_state:
    st.session_state.timer_seconds = 0
if "study_mode" not in st.session_state:
    st.session_state.study_mode = "timer"

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
CATEGORY_META = {
    "K-12": {"icon": "🎒", "desc": "Primary & Secondary School", "color": "#3b82f6"},
    "JEE": {"icon": "🎯", "desc": "Engineering Entrance", "color": "#f59e0b"},
    "NEET": {"icon": "🏥", "desc": "Medical Entrance", "color": "#ef4444"},
    "State Boards": {"icon": "📚", "desc": "State Board Exams", "color": "#8b5cf6"},
    "UPSC": {"icon": "🏛️", "desc": "Civil Services", "color": "#10b981"},
    "University": {"icon": "🎓", "desc": "General University", "color": "#06b6d4"},
}

ALL_BADGES = [
    {"id": "streak_3", "name": "🔥 3-Day Streak", "desc": "Log in for 3 consecutive days"},
    {"id": "streak_7", "name": "🔥 7-Day Streak", "desc": "Log in for 7 consecutive days"},
    {"id": "streak_14", "name": "🔥 14-Day Streak", "desc": "Log in for 14 consecutive days"},
    {"id": "streak_30", "name": "🔥 30-Day Legend", "desc": "Log in for 30 consecutive days"},
    {"id": "study_60", "name": "⏱️ 60-Min Scholar", "desc": "Study for 60 minutes total"},
    {"id": "study_300", "name": "⏱️ 300-Min Master", "desc": "Study for 300 minutes total"},
    {"id": "fc_10", "name": "🗂️ Flashcard Maker", "desc": "Create 10 flashcards"},
]

def load_study_data():
    """Load study data from JSON file."""
    try:
        if Path("study_data.json").exists():
            with open("study_data.json", "r") as f:
                return json.load(f)
    except:
        pass
    return {}

STUDY_DATA = load_study_data()
BOARDS = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge"]

# Category metadata — icons & descriptions shown on onboarding screen
CATEGORY_META = {
    "K-12th": {
        "icon": "🏫",
        "desc": "Class 1 to 12 · School Curriculum",
        "color": "#3b82f6"
    },
    "Undergraduate": {
        "icon": "🎓",
        "desc": "Bachelor's Degree Programs",
        "color": "#8b5cf6"
    },
    "Postgraduate": {
        "icon": "🔬",
        "desc": "Master's & PhD Programs",
        "color": "#10b981"
    },
    "Competitive Exams": {
        "icon": "🏆",
        "desc": "JEE · NEET · UPSC · CAT & more",
        "color": "#f59e0b"
    },
    "Professional": {
        "icon": "💼",
        "desc": "CA · CS · CMA · Law & more",
        "color": "#ef4444"
    },
    "Skill & Certification": {
        "icon": "📜",
        "desc": "Tech · Design · Language Courses",
        "color": "#06b6d4"
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Part 2 CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* ── Hide ALL Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton,
[data-testid="baseButton-header"],
div[class*="viewerBadge"],
.st-emotion-cache-zq5wmm,
.st-emotion-cache-1dp5vir,
[data-testid="manage-app-button"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}

.block-container {
    max-width: 1180px !important;
    padding-top: 0.6rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

.stApp {
    background: linear-gradient(160deg,#f8fbff 0%,#eef3fb 60%,#e8f0fa 100%) !important;
    color: #0f172a !important;
}

.stApp p,.stApp span,.stApp li,.stApp label,
.stApp div,.stApp strong,.stApp small,
.stApp h1,.stApp h2,.stApp h3,.stApp h4 { color: #0f172a; }

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * { color: #0f172a !important; }

/* ── Hero ── */
.sf-hero { text-align:center; padding:14px 0 8px 0; }
.sf-hero-title {
    font-size:2.6rem; font-weight:800;
    background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; line-height:1.1; margin:0;
}
.sf-hero-sub { color:#475569 !important; font-size:.94rem; font-weight:500; margin-top:4px; }
.sf-powered {
    display:inline-block; margin-top:7px; padding:3px 14px;
    border-radius:999px; background:rgba(37,99,235,0.09);
    color:#2563eb !important; font-size:.69rem;
    font-weight:800; letter-spacing:.12em; text-transform:uppercase;
}

/* ── Cards ── */
.sf-card {
    position:relative !important; z-index:10 !important;
    background:#ffffff !important; border:1px solid #dde5f0 !important;
    border-radius:16px !important; padding:20px 22px !important;
    margin-bottom:14px !important;
    box-shadow:0 4px 18px rgba(15,23,42,.05) !important;
    overflow:visible !important;
}
.sf-card *,.sf-card p,.sf-card span,.sf-card li,
.sf-card strong,.sf-card small { color:#0f172a !important; }

.sf-soft-card {
    background:linear-gradient(160deg,#f8fbff,#f1f5f9) !important;
    border:1px solid #dde5f0 !important; border-radius:14px !important;
    padding:14px !important; color:#0f172a !important;
}
.sf-soft-card *,.sf-soft-card p,
.sf-soft-card span,.sf-soft-card strong { color:#0f172a !important; }

/* ── Metric cards ── */
.mc {
    border-radius:14px; padding:14px 10px;
    color:white !important; text-align:center;
    box-shadow:0 8px 20px rgba(0,0,0,.09); margin-bottom:10px;
}
.mc * { color:white !important; }
.mc-blue { background:linear-gradient(135deg,#3b82f6,#1d4ed8); }
.mc-green { background:linear-gradient(135deg,#10b981,#059669); }
.mc-purple { background:linear-gradient(135deg,#8b5cf6,#7c3aed); }
.mc-amber { background:linear-gradient(135deg,#f59e0b,#d97706); }
.mc .icon { font-size:1.25rem; }
.mc .val { font-size:1.45rem; font-weight:800; margin:3px 0; }
.mc .lbl { font-size:.75rem; opacity:.93; }

/* ── XP bar ── */
.xp-wrap { background:#e2e8f0; border-radius:999px; height:10px; overflow:hidden; }
.xp-fill { height:100%; background:linear-gradient(90deg,#3b82f6,#2563eb); border-radius:999px; }

/* ── Onboarding steps ── */
.ob-step {
    width:40px; height:40px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-weight:800; font-size:.95rem;
}
.ob-step-done { background:#10b981; color:white; }
.ob-step-active { background:#2563eb; color:white; }
.ob-step-lock { background:#e2e8f0; color:#94a3b8; }

.ob-line { height:3px; background:#e2e8f0; }
.ob-line-done { background:#10b981; }

/* ── BUTTONS — z-index fix ── */
.stButton > button,.stFormSubmitButton > button {
    position:relative !important; z-index:200 !important;
    border:none !important; border-radius:11px !important;
    background:linear-gradient(135deg,#3b82f6,#2563eb) !important;
    color:#ffffff !important; font-weight:700 !important;
    padding:.58rem 1rem !important;
    box-shadow:0 5px 14px rgba(37,99,235,.18) !important;
    transition:all .15s ease !important; width:100% !important;
    pointer-events:auto !important; cursor:pointer !important;
}
.stButton > button:hover {
    transform:translateY(-1px) !important;
    box-shadow:0 9px 20px rgba(37,99,235,.28) !important;
}
.stDownloadButton > button {
    position:relative !important; z-index:200 !important;
    border:none !important; border-radius:11px !important;
    background:linear-gradient(135deg,#10b981,#059669) !important;
    color:white !important; font-weight:700 !important;
    box-shadow:0 5px 14px rgba(16,185,129,.18) !important;
    width:100% !important; pointer-events:auto !important; cursor:pointer !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background:#ffffff !important; border-right:1px solid #dde5f0 !important;
}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,
[data-testid="stSidebar"] li,[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,[data-testid="stSidebar"] strong { color:#0f172a !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { border-bottom:2px solid #e2e8f0 !important; background:transparent !important; }
.stTabs [data-baseweb="tab"] { color:#64748b !important; font-weight:600 !important; background:transparent !important; }
.stTabs [aria-selected="true"] { color:#0f172a !important; border-bottom:3px solid #3b82f6 !important; }

/* ── Alerts ── */
div[data-testid="stSuccessMessage"],div[data-testid="stSuccessMessage"] *,
div[data-testid="stSuccessMessage"] p { color:#065f46 !important; }
div[data-testid="stWarningMessage"],div[data-testid="stWarningMessage"] *,
div[data-testid="stWarningMessage"] p { color:#78350f !important; }
div[data-testid="stErrorMessage"],div[data-testid="stErrorMessage"] *,
div[data-testid="stErrorMessage"] p { color:#7f1d1d !important; }
div[data-testid="stInfoMessage"],div[data-testid="stInfoMessage"] *,
div[data-testid="stInfoMessage"] p { color:#1e3a5f !important; }
div[data-testid="stSuccessMessage"],div[data-testid="stWarningMessage"],
div[data-testid="stErrorMessage"],div[data-testid="stInfoMessage"] { border-radius:11px !important; }

/* ── Radio ── */
.stRadio [data-testid="stMarkdownContainer"] p { color:#0f172a !important; }
.stRadio > div > div > label > div { color:#0f172a !important; }

/* ── Expander ── */
.streamlit-expanderHeader,.streamlit-expanderHeader p,
.streamlit-expanderHeader span { color:#0f172a !important; font-weight:600 !important; }
.streamlit-expanderContent,.streamlit-expanderContent * { color:#0f172a !important; }

/* ── Labels ── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stTextInput label,.stSelectbox label,
.stRadio label,.stTextArea label {
    color:#0f172a !important; font-weight:700 !important; font-size:.87rem !important;
}
input[type="text"],input[type="password"],textarea {
    color:#0f172a !important; background:#ffffff !important; border-radius:10px !important;
}

/* ── Dark Mode ── */
[data-theme="dark"] .stApp { background:linear-gradient(160deg,#1a2235 0%,#1e2a3a 55%,#1c2840 100%) !important; }
[data-theme="dark"] .sf-card { background:#243045 !important; border-color:#2e3f58 !important; }
[data-theme="dark"] .sf-card *,[data-theme="dark"] .sf-card p { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-soft-card { background:#1f2e42 !important; }
[data-theme="dark"] .sf-soft-card * { color:#e2e8f0 !important; }

[data-theme="dark"] input[type="text"],
[data-theme="dark"] input[type="password"],
[data-theme="dark"] textarea { color:#e2e8f0 !important; background:#243045 !important; }
[data-theme="dark"] [data-testid="stWidgetLabel"] p,
[data-theme="dark"] [data-testid="stWidgetLabel"] label,
[data-theme="dark"] .stTextInput label,
[data-theme="dark"] .stSelectbox label,
[data-theme="dark"] .stRadio label,
[data-theme="dark"] .stTextArea label { color:#e2e8f0 !important; }
[data-theme="dark"] .stRadio [data-testid="stMarkdownContainer"] p { color:#e2e8f0 !important; }
[data-theme="dark"] .stTabs [data-baseweb="tab"] { color:#94a3b8 !important; }
[data-theme="dark"] .stTabs [aria-selected="true"] { color:#f1f5f9 !important; border-bottom-color:#3b82f6 !important; }
[data-theme="dark"] .streamlit-expanderHeader,[data-theme="dark"] .streamlit-expanderHeader p,
[data-theme="dark"] .streamlit-expanderHeader span { color:#e2e8f0 !important; }
[data-theme="dark"] .streamlit-expanderContent,[data-theme="dark"] .streamlit-expanderContent * { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-hero-sub { color:#94a3b8 !important; }
[data-theme="dark"] .sf-powered { background:rgba(59,130,246,.15) !important; color:#93c5fd !important; }
[data-theme="dark"] .xp-wrap { background:#2e3f58 !important; }

</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# Part 3 DATABASE SETUP
# ─────────────────────────────────────────────────────────────────────────────
def generate_ai_content(tool, subject, chapter, prompt, username):
    """Generate AI content using Gemini."""
    model = get_gemini_model()
    if not model:
        return f"Generated {tool} content for {subject} - {chapter}.\n\n{prompt}"
    
    try:
        system_prompt = f"""
You are an expert study assistant for {subject}.
        
Tool: {tool}
Chapter: {chapter}
        
User request: {prompt}
        
Generate helpful, structured content appropriate for the tool type.
"""
        response = model.generate_content(system_prompt)
        return response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        return f"AI generation failed: {str(e)}"

def get_weekly_progress(username):
    """Get weekly study progress."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    # Get current week's minutes
    week_key = datetime.now().strftime("%Y-W%W")
    c.execute("SELECT weekly_minutes FROM user_stats WHERE username=?", (username,))
    row = c.fetchone()
    
    weekly_data = {}
    if row and row[0]:
        try:
            weekly_data = json.loads(row[0])
        except:
            weekly_data = {}
    
    current_week = weekly_data.get(week_key, 0)
    
    # Get last 4 weeks for chart
    weeks = []
    for i in range(4):
        week_num = int(week_key.split("-W")[1]) - i
        year = int(week_key.split("-W")[0])
        if week_num < 1:
            week_num += 52
            year -= 1
        week_key_i = f"{year}-W{week_num:02d}"
        weeks.append({
            "week": week_key_i,
            "minutes": weekly_data.get(week_key_i, 0)
        })
    
    weeks.reverse()
    conn.close()
    
    return {
        "current_week": current_week,
        "weekly_trend": weeks,
        "goal": 300,  # 5 hours per week goal
        "progress": min(100, (current_week / 300) * 100) if 300 > 0 else 0
    }

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User profiles table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            username TEXT PRIMARY KEY,
            category TEXT DEFAULT '',
            course TEXT DEFAULT '',
            stream TEXT DEFAULT '',
            board TEXT DEFAULT '',
            onboarded INTEGER DEFAULT 0
        )
    """)

    # User stats table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            username TEXT PRIMARY KEY,
            streak_days INTEGER DEFAULT 0,
            last_login TEXT DEFAULT '',
            total_study_minutes INTEGER DEFAULT 0,
            weekly_minutes TEXT DEFAULT '{}',
            xp_points INTEGER DEFAULT 0
        )
    """)

    # Badges table
    c.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            username TEXT,
            badge_id TEXT,
            earned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username, badge_id)
        )
    """)

    # Flashcards table
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            front TEXT,
            back TEXT,
            subject TEXT DEFAULT '',
            chapter TEXT DEFAULT '',
            next_review_date TEXT DEFAULT CURRENT_DATE,
            review_count INTEGER DEFAULT 0
        )
    """)

    # Study history table
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            tool TEXT,
            subject TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────────────────────────────────────────
# WHITELISTED USERS (add usernames here — registration is disabled)
# ─────────────────────────────────────────────────────────────────────────────
WHITELISTED_USERS = {
    "admin": "admin123",
    "student1": "pass123",
    "demo": "demo123",
}

def seed_whitelisted_users():
    """Insert whitelisted users into DB if they don't exist."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    for uname, pwd in WHITELISTED_USERS.items():
        c.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            (uname, pwd)
        )
    conn.commit()
    conn.close()

seed_whitelisted_users()

# ─────────────────────────────────────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def verify_user(username, password):
    """Check if username/password match DB record."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "SELECT username FROM users WHERE username=? AND password=?",
        (username, password)
    )
    result = c.fetchone()
    conn.close()
    return result is not None

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_user_profile(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "SELECT category, course, stream, board, onboarded FROM user_profiles WHERE username=?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "category":  row[0],
            "course":    row[1],
            "stream":    row[2],
            "board":     row[3],
            "onboarded": row[4],
        }
    return None

def save_user_profile(username, category, course, stream, board):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_profiles (username, category, course, stream, board, onboarded)
        VALUES (?, ?, ?, ?, ?, 1)
        ON CONFLICT(username) DO UPDATE SET
            category=excluded.category,
            course=excluded.course,
            stream=excluded.stream,
            board=excluded.board,
            onboarded=1
    """, (username, category, course, stream, board))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STATS HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_user_stats(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "SELECT streak_days, last_login, total_study_minutes, weekly_minutes, xp_points FROM user_stats WHERE username=?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    if row:
        try:
            weekly = json.loads(row[3]) if row[3] else {}
        except:
            weekly = {}
        return {
            "streak_days":          row[0],
            "last_login":           row[1],
            "total_study_minutes":  row[2],
            "weekly_minutes":       weekly,
            "xp_points":            row[4],
        }
    return {
        "streak_days": 0,
        "last_login": "",
        "total_study_minutes": 0,
        "weekly_minutes": {},
        "xp_points": 0,
    }

def update_streak(username):
    """Update login streak and XP on each login."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        "SELECT streak_days, last_login, xp_points FROM user_stats WHERE username=?",
        (username,)
    )
    row = c.fetchone()

    if row is None:
        c.execute(
            "INSERT INTO user_stats (username, streak_days, last_login, xp_points) VALUES (?, 1, ?, 10)",
            (username, today)
        )
    else:
        streak, last_login, xp = row
        if last_login == today:
            conn.close()
            return
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if last_login == yesterday:
            streak += 1
        else:
            streak = 1
        xp = (xp or 0) + 10
        c.execute(
            "UPDATE user_stats SET streak_days=?, last_login=?, xp_points=? WHERE username=?",
            (streak, today, xp, username)
        )

    conn.commit()
    conn.close()

def add_study_minutes(username, minutes):
    """Add study minutes and XP after a timer session."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    week_key = datetime.now().strftime("%Y-W%W")

    c.execute(
        "SELECT total_study_minutes, weekly_minutes, xp_points FROM user_stats WHERE username=?",
        (username,)
    )
    row = c.fetchone()

    if row is None:
        weekly = {week_key: minutes}
        c.execute(
            "INSERT INTO user_stats (username, total_study_minutes, weekly_minutes, xp_points) VALUES (?, ?, ?, ?)",
            (username, minutes, json.dumps(weekly), minutes * 2)
        )
    else:
        total, weekly_json, xp = row
        try:
            weekly = json.loads(weekly_json) if weekly_json else {}
        except:
            weekly = {}
        weekly[week_key] = weekly.get(week_key, 0) + minutes
        total = (total or 0) + minutes
        xp = (xp or 0) + minutes * 2
        c.execute(
            "UPDATE user_stats SET total_study_minutes=?, weekly_minutes=?, xp_points=? WHERE username=?",
            (total, json.dumps(weekly), xp, username)
        )

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# BADGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_earned_badges(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT badge_id FROM badges WHERE username=?", (username,))
    rows = c.fetchall()
    conn.close()
    return {r[0] for r in rows}

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO badges (username, badge_id) VALUES (?, ?)",
        (username, badge_id)
    )
    conn.commit()
    conn.close()

def auto_check_badges(username):
    """Automatically unlock badges based on user stats."""
    stats = get_user_stats(username)
    earned = get_earned_badges(username)

    streak = stats.get("streak_days", 0)
    total_min = stats.get("total_study_minutes", 0)

    if streak >= 3  and "streak_3"  not in earned: award_badge(username, "streak_3")
    if streak >= 7  and "streak_7"  not in earned: award_badge(username, "streak_7")
    if streak >= 14 and "streak_14" not in earned: award_badge(username, "streak_14")
    if streak >= 30 and "streak_30" not in earned: award_badge(username, "streak_30")
    if total_min >= 60  and "study_60"  not in earned: award_badge(username, "study_60")
    if total_min >= 300 and "study_300" not in earned: award_badge(username, "study_300")

    # Flashcard badge
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
    fc_count = c.fetchone()[0]
    conn.close()
    if fc_count >= 10 and "fc_10" not in earned:
        award_badge(username, "fc_10")

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_due_flashcards(username):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, front, back, subject, chapter, next_review_date, review_count
        FROM flashcards
        WHERE username=? AND next_review_date <= ?
        ORDER BY next_review_date ASC
    """, (username, today))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT id, front, back, subject, chapter, next_review_date, review_count
        FROM flashcards WHERE username=?
        ORDER BY id DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_flashcard(username, front, back, subject="", chapter=""):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO flashcards (username, front, back, subject, chapter)
        VALUES (?, ?, ?, ?, ?)
    """, (username, front, back, subject, chapter))
    conn.commit()
    conn.close()

def update_flashcard_review(card_id, quality):
    """
    Spaced repetition: quality 1=Easy, 2=Medium, 3=Hard
    """
    intervals = {1: 7, 2: 3, 3: 1}
    days = intervals.get(quality, 1)
    next_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        UPDATE flashcards
        SET next_review_date=?, review_count=review_count+1
        WHERE id=?
    """, (next_date, card_id))
    conn.commit()
    conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STUDY DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_courses(category):
    if not STUDY_DATA:
        return []
    cat_data = STUDY_DATA.get(category, {})
    if isinstance(cat_data, dict):
        return list(cat_data.keys())
    return []

def get_streams(category, course):
    if not STUDY_DATA:
        return []
    cat_data = STUDY_DATA.get(category, {})
    if isinstance(cat_data, dict):
        course_data = cat_data.get(course, {})
        if isinstance(course_data, dict):
            return list(course_data.keys())
    return []

def get_subjects(category, course, stream):
    if not STUDY_DATA:
        return []
    try:
        data = STUDY_DATA[category][course][stream]
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return list(data.keys())
    except:
        pass
    return []

def _safe_state_key(text):
    """Convert any string to a safe session_state key."""
    return "".join(c if c.isalnum() else "_" for c in str(text))

def category_skips_course(selected_category):
    """Returns True when the category should skip the course step."""
    text = selected_category.strip().lower()
    skip_markers = ["jee", "neet", "upsc", "cat ", "gate", "gre", "gmat"]
    return any(m in text for m in skip_markers)

def needs_board_selection(selected_category, selected_course=""):
    """Returns True when the school-board picker should be shown."""
    text = f"{selected_category} {selected_course}".strip().lower()
    school_markers = [
        "k-12", "school", "class ", "grade ", "standard",
        "cbse", "icse", "state board", "isc", "ib", "cambridge"
    ]
    return any(m in text for m in school_markers)

# ─────────────────────────────────────────────────────────────────────────────
# GEMINI AI HELPER
# ─────────────────────────────────────────────────────────────────────────────
def get_gemini_model():
    """Dynamically detect and return the best available Gemini model."""
    try:
        models = [m.name for m in genai.list_models()
                  if "generateContent" in m.supported_generation_methods]
        preferred = [
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-pro",
        ]
        for p in preferred:
            if p in models:
                return genai.GenerativeModel(p)
        if models:
            return genai.GenerativeModel(models[0])
    except:
        pass
    return None

def log_study_history(username, tool, subject):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO study_history (username, tool, subject) VALUES (?, ?, ?)",
        (username, tool, subject)
    )
    conn.commit()
    conn.close()

def go_to(page):
    """Navigate to a page."""
    st.session_state.page = page
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATION HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(content, filename="study_material.pdf"):
    """Generate a downloadable PDF from study content."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1d4ed8"),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        name="CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#374151"),
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        name="CustomNormal",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=8
    )
    
    story = []
    
    # Title
    story.append(Paragraph("StudySmart AI - Generated Material", title_style))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d1d5db")))
    story.append(Spacer(1, 20))
    
    # Content
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('# '):
            story.append(Paragraph(line[2:], heading_style))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles["Heading3"]))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles["Heading4"]))
        else:
            story.append(Paragraph(line, normal_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def get_question_paper_template(board, course):
    """Return question paper template based on board and course."""
    b = board.upper()
    if "CBSE" in b:
        if any(x in course for x in ["10", "X", "Class 10"]):
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "BOARD EXAMINATION",
                "class_label": "CLASS X",
                "total_marks": 80,
                "time": "3 Hours",
                "instructions": [
                    "This paper contains Sections A, B, C, D and E.",
                    "All questions are compulsory.",
                    "Section A — MCQ (1 mark each).",
                    "Section B — Very Short Answer (2 marks each).",
                    "Section C — Short Answer (3 marks each).",
                    "Section D — Long Answer (5 marks each).",
                    "Section E — Case / Source Based (4 marks each)."
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ", "q_count": 20, "marks_each": 1, "total": 20},
                    {"name": "SECTION B", "type": "Very Short Answer", "q_count": 5, "marks_each": 2, "total": 10},
                    {"name": "SECTION C", "type": "Short Answer", "q_count": 6, "marks_each": 3, "total": 18},
                    {"name": "SECTION D", "type": "Long Answer", "q_count": 4, "marks_each": 5, "total": 20},
                    {"name": "SECTION E", "type": "Case Based", "q_count": 3, "marks_each": 4, "total": 12}
                ]
            }
        # More templates for other classes...
    return None

# ─────────────────────────────────────────────────────────────────────────────
# Part 4 CHECKBOX & SINGLE-SELECT LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def clear_checkbox_group(prefix):
    """Uncheck every checkbox whose key starts with prefix_chk_"""
    for key in list(st.session_state.keys()):
        if key.startswith(f"{prefix}_chk_"):
            st.session_state[key] = False

def sync_checkbox_group(group_prefix, all_options, target_key):
    """
    Keep checkboxes in sync with the current session_state value.
    Called at the TOP of each step so the UI reflects the stored selection.
    """
    selected_value = st.session_state.get(target_key, "")
    for opt in all_options:
        opt_key = f"{group_prefix}_chk_{_safe_state_key(opt)}"
        st.session_state[opt_key] = (selected_value == opt)

def handle_single_select_checkbox(group_prefix, option_value, all_options,
                                  target_key, clear_keys=None, clear_groups=None):
    """
    on_change handler for every selection checkbox.
    Ensures only ONE option is ever ticked at a time.
    """
    current_key = f"{group_prefix}_chk_{_safe_state_key(option_value)}"
    checked = st.session_state.get(current_key, False)

    if checked:
        # Uncheck all siblings
        for opt in all_options:
            opt_key = f"{group_prefix}_chk_{_safe_state_key(opt)}"
            st.session_state[opt_key] = (opt == option_value)
        # Save the selection
        st.session_state[target_key] = option_value
        # Clear downstream state
        for key in (clear_keys or []):
            st.session_state[key] = ""
        for grp in (clear_groups or []):
            clear_checkbox_group(grp)
    else:
        # User unticked — deselect
        if st.session_state.get(target_key) == option_value:
            st.session_state[target_key] = ""

# ─────────────────────────────────────────────────────────────────────────────
# RENDER CHECKBOX CARD (FIXED INDENTATION)
# ─────────────────────────────────────────────────────────────────────────────
def render_checkbox_card(title, subtitle, icon, is_selected):
    """Renders a styled info card. The actual interaction is a checkbox below it."""
    border = "3px solid #2563eb" if is_selected else "2px solid #e2e8f0"
    bg = "linear-gradient(135deg,#eff6ff,#dbeafe)" if is_selected else "white"
    shadow = "0 4px 18px rgba(37,99,235,.18)" if is_selected else "0 2px 12px rgba(15,23,42,.06)"
    tick = "<div style='font-size:.72rem;color:#2563eb;font-weight:700;margin-top:7px;'>✓ Selected</div>" if is_selected else ""

    card_html = f"""
    <div style="
        background:{bg}; border:{border}; border-radius:16px;
        padding:16px 10px; text-align:center; box-shadow:{shadow};
        margin-bottom:4px; min-height:130px;
        display:flex; flex-direction:column;
        justify-content:center; align-items:center;">
        <div style="font-size:2.1rem;">{icon}</div>
        <div style="font-weight:800; font-size:.9rem; color:#0f172a; margin-top:7px;">{title}</div>
        <div style="font-size:.74rem; color:#64748b; margin-top:3px;">{subtitle}</div>
        {tick}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def render_header(title, subtitle):
    st.markdown(f"""
        <div class="sf-hero">
            <div class="sf-hero-title">{title}</div>
            <div class="sf-hero-sub">{subtitle}</div>
            <div class="sf-powered">✦ POWERED BY AI ✦</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

def render_back_button():
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("← Back to Dashboard", key="back_to_dash", use_container_width=True):
            go_to("dashboard")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

def render_step_indicator(current_step):
    labels = ["Category", "Course", "Stream", "Confirm"]
    cols = st.columns(len(labels) * 2 - 1)
    col_idx = 0
    for i, label in enumerate(labels, start=1):
        with cols[col_idx]:
            if i < current_step:
                cls = "ob-step-done"
                icon = "✓"
            elif i == current_step:
                cls = "ob-step-active"
                icon = str(i)
            else:
                cls = "ob-step-lock"
                icon = str(i)
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;
                align-items:center;gap:4px;">
                <div class="ob-step {cls}">{icon}</div>
                <div style="font-size:.68rem;font-weight:600;
                    color:{'#2563eb' if i==current_step else
                           '#10b981' if i<current_step else '#94a3b8'};">
                    {label}
                </div>
            </div>
            """, unsafe_allow_html=True)
        col_idx += 1
        if col_idx < len(cols):
            with cols[col_idx]:
                line_cls = "ob-line-done" if i < current_step else "ob-line"
                st.markdown(
                    f'<div class="ob-line {line_cls}" style="margin-top:18px;"></div>',
                    unsafe_allow_html=True
                )
            col_idx += 1

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(username):
    stats = get_user_stats(username) or {}
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:12px 0 10px 0;">
                <div style="font-size:2rem;">🎓</div>
                <div style="font-size:1.02rem;font-weight:800;color:#2563eb;">StudySmart AI</div>
                <div style="font-size:.77rem;margin-top:3px;">Hi, {username} 👋</div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#ff6b6b,#feca57);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                🔥 {stats.get('streak_days', 0)}<br>
                <span style="font-size:.62rem;font-weight:500;color:white;">day streak</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            weekly = stats.get("weekly_minutes", {})
            week_key = datetime.now().strftime("%Y-W%W")
            week_mins = weekly.get(week_key, 0)
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#3b82f6,#2563eb);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                ⏱️ {week_mins}m<br>
                <span style="font-size:.62rem;font-weight:500;color:white;">this week</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("### 📚 Quick Actions")
        if st.button("🎓 Dashboard", use_container_width=True, key="nav_dash"):
            go_to("dashboard")
        if st.button("🛠️ Study Tools", use_container_width=True, key="nav_study"):
            go_to("study_tools")
        if st.button("🗂️ Flashcards", use_container_width=True, key="nav_fc"):
            go_to("flashcards")
        if st.button("⭐ Achievements", use_container_width=True, key="nav_badges"):
            go_to("achievements")
        if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
            go_to("settings")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.page = "login"
            st.session_state.username = ""
            st.rerun()
# ─────────────────────────────────────────────────────────────────────────────
# Part 5 LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
        <div style="text-align:center;padding:30px 0 10px 0;">
            <div style="font-size:3.2rem;">🎓</div>
            <div style="font-size:2.8rem;font-weight:800;background:linear-gradient(135deg,#2563eb,#1d4ed8);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                StudySmart AI
            </div>
            <div style="font-size:.95rem;color:#64748b;margin-top:8px;">
                AI-powered exam preparation for students
            </div>
        </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Login to Continue")

        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")

        if st.button("🚀 Login", use_container_width=True, key="login_btn"):
            if not username or not password:
                st.error("Please enter both username and password.")
            elif verify_user(username, password):
                st.session_state.username = username
                st.session_state.page = "dashboard"
                update_streak(username)
                st.rerun()
            else:
                st.error("Invalid username or password.")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("""
            <div style="font-size:.82rem;color:#64748b;text-align:center;">
                <b>Demo Accounts:</b><br>
                👤 <b>admin</b> / admin123 &nbsp;|&nbsp;
                👤 <b>student1</b> / pass123 &nbsp;|&nbsp;
                👤 <b>demo</b> / demo123
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="font-size:.75rem;color:#94a3b8;text-align:center;margin-top:14px;">
                ⚠️ Registration is disabled. Use a whitelisted account above.
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ONBOARDING WIZARD
# ─────────────────────────────────────────────────────────────────────────────
def show_onboarding(username):
    _, hc, _ = st.columns([1, 3, 1])
    with hc:
        st.markdown("""
            <div class="sf-header" style="padding-top:24px;">
                <div class="sf-header-title">StudySmart AI</div>
                <div class="sf-header-subtitle">Let's personalise your experience 🎯</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    _, sc, _ = st.columns([0.5, 4, 0.5])
    with sc:
        render_step_indicator(st.session_state.ob_step)
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    _, mc, _ = st.columns([0.5, 4, 0.5])

    with mc:
        # ══════════════════════════════════════════════════════════════════
        # STEP 1 — CATEGORY
        # ══════════════════════════════════════════════════════════════════
        if st.session_state.ob_step == 1:
            st.markdown("""
                <div style="text-align:center;margin-bottom:18px;">
                    <div style="font-size:1.4rem;font-weight:800;color:#0f172a;">
                        📚 What are you studying?
                    </div>
                    <div style="font-size:.88rem;color:#64748b;margin-top:5px;">
                        Tick one card to select your education level.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            available_cats = list(STUDY_DATA.keys()) if STUDY_DATA else list(CATEGORY_META.keys())
            sync_checkbox_group("ob_cat", available_cats, "ob_category")

            for row_start in range(0, len(available_cats), 3):
                row_cats = available_cats[row_start: row_start + 3]
                cols = st.columns(len(row_cats))
                for col, cat in zip(cols, row_cats):
                    meta = CATEGORY_META.get(cat, {"icon": "📘", "desc": cat, "color": "#3b82f6"})
                    is_sel = (st.session_state.ob_category == cat)
                    with col:
                        render_checkbox_card(cat, meta["desc"], meta["icon"], is_sel)
                        st.checkbox(
                            "Select",
                            key=f"ob_cat_chk_{_safe_state_key(cat)}",
                            on_change=handle_single_select_checkbox,
                            args=("ob_cat", cat, available_cats, "ob_category",
                                  ["ob_course", "ob_stream", "ob_board"],
                                  ["ob_course", "ob_stream", "ob_board"])
                        )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            selected_cat = st.session_state.ob_category

            if selected_cat:
                meta = CATEGORY_META.get(selected_cat, {"icon": "📘"})
                skip_course = category_skips_course(selected_cat)
                if skip_course:
                    st.session_state.ob_course = selected_cat

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);
                    border:2px solid #bfdbfe;border-radius:14px;
                    padding:14px 18px;margin-bottom:12px;text-align:center;">
                    <span style="font-size:1.3rem;">{meta['icon']}</span>
                    <span style="font-weight:700;font-size:.95rem;color:#1d4ed8;margin-left:8px;">
                        {selected_cat} selected ✓
                    </span>
                </div>
                """, unsafe_allow_html=True)

                btn_label = "Continue → Stream & Board" if skip_course else "Continue → Choose Course"
                if st.button(btn_label, key="ob_next_1", use_container_width=True):
                    st.session_state.ob_step = 3 if skip_course else 2
                    st.rerun()
            else:
                st.info("👆 Please tick one option to continue.")

        # ══════════════════════════════════════════════════════════════════
        # STEP 2 — COURSE (only shown for category-level selections)
        # ══════════════════════════════════════════════════════════════════
        elif st.session_state.ob_step == 2:
            cat = st.session_state.ob_category
            # Safety: auto-skip if not needed
            if category_skips_course(cat):
                st.session_state.ob_course = cat
                st.session_state.ob_step = 3
                st.rerun()

            meta = CATEGORY_META.get(cat, {"icon": "📘", "color": "#3b82f6"})
            courses = get_courses(cat)

            st.markdown(f"""
                <div style="text-align:center;margin-bottom:18px;">
                    <div style="font-size:1.4rem;font-weight:800;color:#0f172a;">
                        {meta['icon']} Choose Your Course
                    </div>
                    <div style="font-size:.88rem;color:#64748b;margin-top:5px;">
                        Category: <b>{cat}</b> — Tick one course and continue.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if not courses:
                st.warning("⚠️ No courses found for this category.")
            else:
                sync_checkbox_group("ob_course", courses, "ob_course")
                for row_start in range(0, len(courses), 3):
                    row_courses = courses[row_start: row_start + 3]
                    cols = st.columns(len(row_courses))
                    for col, course in zip(cols, row_courses):
                        is_sel = (st.session_state.ob_course == course)
                        with col:
                            render_checkbox_card(course, "Program / Class", "📖", is_sel)
                            st.checkbox(
                                "Select",
                                key=f"ob_course_chk_{_safe_state_key(course)}",
                                on_change=handle_single_select_checkbox,
                                args=("ob_course", course, courses, "ob_course",
                                      ["ob_stream", "ob_board"],
                                      ["ob_stream", "ob_board"])
                            )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("← Back", key="ob_back_2", use_container_width=True):
                    st.session_state.ob_step = 1
                    st.rerun()
            with col_next:
                if st.session_state.ob_course:
                    if st.button("Continue → Stream & Board", key="ob_next_2", use_container_width=True):
                        st.session_state.ob_step = 3
                        st.rerun()
                else:
                    st.info("👆 Please tick one course to continue.")

        # ══════════════════════════════════════════════════════════════════
        # STEP 3 — STREAM + BOARD
        # ══════════════════════════════════════════════════════════════════
        elif st.session_state.ob_step == 3:
            cat = st.session_state.ob_category
            course = st.session_state.ob_course or st.session_state.ob_category
            streams = get_streams(cat, course)

            stream_icons = {
                "Science": "🔬", "Commerce": "💹", "Arts": "🎨", "Humanities": "📜",
                "Engineering": "⚙️", "Medical": "🏥", "General": "📚",
                "Mathematics": "📐", "Biology": "🧬",
            }

            st.markdown(f"""
                <div style="text-align:center;margin-bottom:18px;">
                    <div style="font-size:1.4rem;font-weight:800;color:#0f172a;">
                        🔀 Choose Your Stream
                    </div>
                    <div style="font-size:.88rem;color:#64748b;margin-top:5px;">
                        Course: <b>{course}</b> — Tick one stream and continue.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if not streams:
                st.warning("⚠️ No streams found for this selection.")
            else:
                sync_checkbox_group("ob_stream", streams, "ob_stream")
                for row_start in range(0, len(streams), 3):
                    row_streams = streams[row_start: row_start + 3]
                    cols = st.columns(len(row_streams))
                    for col, stream in zip(cols, row_streams):
                        icon = stream_icons.get(stream, "📂")
                        is_sel = (st.session_state.ob_stream == stream)
                        with col:
                            render_checkbox_card(stream, "Specialisation / Stream", icon, is_sel)
                            st.checkbox(
                                "Select",
                                key=f"ob_stream_chk_{_safe_state_key(stream)}",
                                on_change=handle_single_select_checkbox,
                                args=("ob_stream", stream, streams, "ob_stream",
                                      ["ob_board"], ["ob_board"])
                            )

            # Board selector
            if st.session_state.ob_stream:
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                if needs_board_selection(cat, course):
                    st.markdown("""
                        <div style="font-weight:700;font-size:.95rem;
                            color:#0f172a;margin-bottom:8px;">
                            🏫 Select Your Board
                        </div>
                    """, unsafe_allow_html=True)
                    sync_checkbox_group("ob_board", BOARDS, "ob_board")
                    board_cols = st.columns(len(BOARDS))
                    for bcol, board in zip(board_cols, BOARDS):
                        is_sel = (st.session_state.ob_board == board)
                        with bcol:
                            render_checkbox_card(board, "School Board", "🏫", is_sel)
                            st.checkbox(
                                "Select",
                                key=f"ob_board_chk_{_safe_state_key(board)}",
                                on_change=handle_single_select_checkbox,
                                args=("ob_board", board, BOARDS, "ob_board", [], [])
                            )
                else:
                    st.session_state.ob_board = "University / National Syllabus"

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("← Back", key="ob_back_3", use_container_width=True):
                    st.session_state.ob_step = 2 if not category_skips_course(cat) else 1
                    st.rerun()
            with col_next:
                if st.session_state.ob_stream:
                    if st.button("Continue → Confirm", key="ob_next_3", use_container_width=True):
                        st.session_state.ob_step = 4
                        st.rerun()
                else:
                    st.info("👆 Please tick one stream to continue.")

        # ══════════════════════════════════════════════════════════════════
        # STEP 4 — CONFIRMATION
        # ══════════════════════════════════════════════════════════════════
        elif st.session_state.ob_step == 4:
            cat = st.session_state.ob_category
            course = st.session_state.ob_course or st.session_state.ob_category
            stream = st.session_state.ob_stream
            board = st.session_state.ob_board
            meta = CATEGORY_META.get(cat, {"icon": "📘"})

            st.markdown("""
                <div style="text-align:center;margin-bottom:18px;">
                    <div style="font-size:1.4rem;font-weight:800;color:#0f172a;">
                        ✅ Confirm Your Profile
                    </div>
                    <div style="font-size:.88rem;color:#64748b;margin-top:5px;">
                        Review your choices and launch your dashboard.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);
                border:2px solid #bfdbfe;border-radius:20px;
                padding:28px 24px;margin:0 auto 18px auto;max-width:480px;">
                <div style="text-align:center;font-size:3rem;margin-bottom:12px;">
                    {meta['icon']}
                </div>
                <table style="width:100%;border-collapse:collapse;">
                    <tr>
                        <td style="padding:8px 12px;font-weight:600;color:#475569;font-size:.85rem;width:40%;">📚 Category</td>
                        <td style="padding:8px 12px;font-weight:800;color:#1d4ed8;font-size:.9rem;">{cat}</td>
                    </tr>
                    <tr style="background:rgba(255,255,255,0.5);">
                        <td style="padding:8px 12px;font-weight:600;color:#475569;font-size:.85rem;">🎓 Course</td>
                        <td style="padding:8px 12px;font-weight:800;color:#1d4ed8;font-size:.9rem;">{course}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px 12px;font-weight:600;color:#475569;font-size:.85rem;">🔀 Stream</td>
                        <td style="padding:8px 12px;font-weight:800;color:#1d4ed8;font-size:.9rem;">{stream}</td>
                    </tr>
                    <tr style="background:rgba(255,255,255,0.5);">
                        <td style="padding:8px 12px;font-weight:600;color:#475569;font-size:.85rem;">🏫 Board / Syllabus</td>
                        <td style="padding:8px 12px;font-weight:800;color:#1d4ed8;font-size:.9rem;">{board}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            col_back, col_confirm = st.columns(2)
            with col_back:
                if st.button("← Edit", key="ob_back_4", use_container_width=True):
                    st.session_state.ob_step = 3
                    st.rerun()
            with col_confirm:
                if st.button("✅ Launch Dashboard", key="ob_confirm", use_container_width=True):
                    save_user_profile(username, cat, course, stream, board)
                    st.session_state.page = "dashboard"
                    st.rerun()
# ─────────────────────────────────────────────────────────────────────────────
# Part 6 EXTRA SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "daily_checkin_done" not in st.session_state:
    st.session_state.daily_checkin_done = False
if "study_timer_active" not in st.session_state:
    st.session_state.study_timer_active = False
if "study_timer_start" not in st.session_state:
    st.session_state.study_timer_start = None
if "current_subject_for_timer" not in st.session_state:
    st.session_state.current_subject_for_timer = "General"

# ─────────────────────────────────────────────────────────────────────────────
# ACTIVITY LOG HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def save_activity_log(username, tool, chapter, subject, preview):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
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
    c.execute("""
        INSERT INTO activity_log (username, tool, chapter, subject, preview, log_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        tool,
        chapter,
        subject,
        preview[:250],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_activity_log(username, limit=8):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("""
            SELECT tool, chapter, subject, preview, log_time
            FROM activity_log
            WHERE username=?
            ORDER BY id DESC
            LIMIT ?
        """, (username, limit))
        rows = c.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()

    result = []
    for row in rows:
        result.append({
            "tool": row[0],
            "chapter": row[1] or "—",
            "subject": row[2] or "—",
            "preview": row[3] or "",
            "time": row[4][11:16] if row[4] and len(row[4]) >= 16 else "—",
        })
    return result

# ─────────────────────────────────────────────────────────────────────────────
# GEMINI MODEL HELPER
# ─────────────────────────────────────────────────────────────────────────────
def get_available_models():
    try:
        models = []
        for m in genai.list_models():
            if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                models.append(m.name)
        return models
    except Exception:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# HISTORY HELPER
# ─────────────────────────────────────────────────────────────────────────────
def add_to_history(tool, chapter, subject, preview, username=None):
    """Add to in-memory session history AND persist to DB."""
    entry = {
        "time": datetime.now().strftime("%H:%M"),
        "tool": tool,
        "chapter": chapter,
        "subject": subject,
        "preview": preview[:110] + "..." if len(preview) > 110 else preview,
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:10]

    if username:
        save_activity_log(username, tool, chapter, subject, preview)

# ─────────────────────────────────────────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────────────────────────────────────────
def get_earned_badges(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("SELECT badge_id FROM badges WHERE username=?", (username,))
        rows = c.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return {r[0] for r in rows}

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS badges (
                username TEXT,
                badge_id TEXT,
                earned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (username, badge_id)
            )
        """)
        c.execute(
            "INSERT OR IGNORE INTO badges (username, badge_id) VALUES (?, ?)",
            (username, badge_id)
        )
        conn.commit()
    except Exception:
        pass
    conn.close()

def auto_check_badges(username):
    stats = get_user_stats(username) or {}
    earned = get_earned_badges(username)

    streak = stats.get("streak_days", 0)
    total_min = stats.get("total_study_minutes", stats.get("total_minutes", 0))

    if streak >= 3 and "streak_3" not in earned:
        award_badge(username, "streak_3")
    if streak >= 7 and "streak_7" not in earned:
        award_badge(username, "streak_7")
    if streak >= 14 and "streak_14" not in earned:
        award_badge(username, "streak_14")
    if streak >= 30 and "streak_30" not in earned:
        award_badge(username, "streak_30")
    if total_min >= 60 and "study_60" not in earned:
        award_badge(username, "study_60")
    if total_min >= 300 and "study_300" not in earned:
        award_badge(username, "study_300")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
        fc_count = c.fetchone()[0]
    except sqlite3.OperationalError:
        fc_count = 0
    conn.close()

    if fc_count >= 10 and "fc_10" not in earned:
        award_badge(username, "fc_10")

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard(username):
    render_header("StudySmart AI", "Your Daily Learning Companion")
    stats = get_user_stats(username) or {}

    total_xp = stats.get("total_xp", stats.get("xp_points", 0))
    streak_days = stats.get("streak_days", 0)
    total_minutes = stats.get("total_study_minutes", stats.get("total_minutes", 0))
    weekly_minutes = stats.get("weekly_study_minutes", stats.get("weekly_minutes", 0))
    flashcards_due = stats.get("flashcards_due", 0)
    level = (total_xp // 500) + 1
    level_progress = total_xp % 500
    pct = min(100, int((level_progress / 500) * 100))

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "mc-blue", "🔥", streak_days, "Day Streak"),
        (c2, "mc-green", "⭐", f"Level {level}", "Your Level"),
        (c3, "mc-purple", "📚", flashcards_due, "Cards Due"),
        (c4, "mc-amber", "⏱️", f"{weekly_minutes} min", "This Week"),
    ]
    for col, cls, icon, val, lbl in cards:
        with col:
            st.markdown(
                f'<div class="mc {cls}"><div class="icon">{icon}</div><div class="val">{val}</div><div class="lbl">{lbl}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(
        f"""<div style="display:flex;justify-content:space-between;font-size:.85rem;font-weight:700;margin-bottom:5px;">
            <span>⭐ Level {level}</span>
            <span>{total_xp} XP · {500 - level_progress} XP to next level</span>
        </div>
        <div class="xp-wrap"><div class="xp-fill" style="width:{pct}%;"></div></div>""",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🌱 Study Momentum**")

        growth = min(100, total_minutes // 10)
        if growth < 20:
            plant = ("🌱", "Seedling")
        elif growth < 40:
            plant = ("🌿", "Sprout")
        elif growth < 70:
            plant = ("🪴", "Growing Plant")
        elif growth < 90:
            plant = ("🌳", "Strong Tree")
        else:
            plant = ("🌲", "Master Tree")

        st.markdown(
            f"""<div class="sf-soft-card" style="text-align:center;margin-bottom:10px;">
                <div style="font-size:2.6rem;">{plant[0]}</div>
                <div style="font-weight:800;font-size:.93rem;">{plant[1]}</div>
                <div style="font-size:.8rem;margin-top:3px;">{total_minutes} min total studied</div>
            </div>""",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions**")
        if st.button("📚 Open Study Tools", use_container_width=True, key="d_study"):
            go_to("study_tools")
        if st.button("🗂️ Review Flashcards", use_container_width=True, key="d_fc"):
            go_to("flashcards")
        if st.button("🏅 View Achievements", use_container_width=True, key="d_ach"):
            go_to("achievements")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**⏱️ Study Timer**")
        subject = st.text_input(
            "Subject / Topic",
            value=st.session_state.current_subject_for_timer,
            key="timer_subject_input"
        )
        st.session_state.current_subject_for_timer = subject

        if not st.session_state.study_timer_active:
            if st.button("▶️ Start Timer", use_container_width=True, key="start_timer"):
                st.session_state.study_timer_active = True
                st.session_state.study_timer_start = datetime.now()
                st.rerun()
        else:
            elapsed_min = int((datetime.now() - st.session_state.study_timer_start).total_seconds() // 60)
            st.info(f"🟢 Running: {elapsed_min} min — {st.session_state.current_subject_for_timer}")
            if st.button("⏹️ Stop & Save", use_container_width=True, key="stop_timer"):
                st.session_state.study_timer_active = False
                duration = max(1, elapsed_min)
                record_study_session(username, st.session_state.current_subject_for_timer, duration)
                add_study_minutes(username, duration)
                award_xp(username, max(5, duration * 2))
                auto_check_badges(username)
                st.success(f"Saved {duration} minutes of study time.")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**📜 Recent Activity**")
        db_history = get_activity_log(username)
        if not db_history:
            st.info("No activity yet. Generate your first study content!")
        else:
            for h in db_history:
                st.markdown(
                    f"""<div class="sf-hist">
                        🕐 {h['time']} | <b>{h['tool']}</b><br>
                        📖 {h['chapter']} — {h['subject']}<br>
                        <small>{h['preview']}</small>
                    </div>""",
                    unsafe_allow_html=True
                )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🏅 Badge Snapshot**")
        earned = get_earned_badges(username)
        earned_list = [b for b in ALL_BADGES if b["id"] in earned][:4]

        if earned_list:
            bc = st.columns(2)
            for i, badge in enumerate(earned_list):
                with bc[i % 2]:
                    st.markdown(
                        f"""<div class="bdg earned">
                            <div class="bi">{badge['icon']}</div>
                            <div class="bn">{badge['name']}</div>
                            <div class="bs">✅ Earned</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
        else:
            st.info("Complete daily check-in to earn your first badge!")
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STUDY TOOLS
# ─────────────────────────────────────────────────────────────────────────────
def show_study_tools(username):
    render_back_button()
    render_header("Study Tools", "AI-powered exam preparation")

    tool = st.radio(
        "🛠️ Select Tool",
        ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "🧪 Question Paper", "❓ Exam Q&A"],
        horizontal=True,
        key="study_tool_radio"
    )

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown("### ✍️ Enter Topic Details")
    subject = st.text_input("Subject", key="tool_subject")
    chapter = st.text_input("Chapter / Topic", key="tool_chapter")
    topic_text = st.text_area("What do you want help with?", height=140, key="tool_prompt")
    st.markdown("</div>", unsafe_allow_html=True)

    model_names = get_available_models()
    chosen_model = model_names[0] if model_names else None

    if model_names:
        st.caption(f"✅ Available Gemini models: {', '.join(model_names[:3])}")
    else:
        st.warning("No Gemini models detected. Check your API key and internet connection.")

    generate_clicked = st.button(f"🚀 Generate {tool}", use_container_width=True, key="generate_tool")

    if generate_clicked:
        if not subject or not topic_text:
            st.error("Please fill in the subject and topic/prompt.")
            return

        result = ""
        if chosen_model:
            try:
                model = genai.GenerativeModel(chosen_model)
                prompt = f"""
You are an expert study assistant.

Task: {tool}
Subject: {subject}
Chapter: {chapter}

User request:
{topic_text}

Give a helpful, well-structured response.
"""
                response = model.generate_content(prompt)
                result = response.text if hasattr(response, "text") else str(response)
            except Exception as e:
                result = f"AI generation failed: {e}"
        else:
            result = f"Generated {tool} content for {subject} - {chapter}.\n\n{topic_text}"

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Output")
        st.markdown(result)
        st.markdown("</div>", unsafe_allow_html=True)

        add_to_history(tool, chapter or "General", subject, result, username=username)
        log_study_history(username, tool, subject)
        award_xp(username, 20)
        try:
            if tool == "🧪 Question Paper":
                award_badge(username, "qp_generated")
            if tool == "🧠 Quiz":
                award_badge(username, "quiz_done")
            if tool == "📝 Summary":
                award_badge(username, "first_gen")
        except Exception:
            pass
        auto_check_badges(username)

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────────────────────────────────────
def show_flashcards(username):
    render_back_button()
    render_header("Flashcards", "Spaced repetition for lasting memory")

    tab1, tab2, tab3 = st.tabs(["📖 Review Due", "➕ Create", "📋 My Library"])

    with tab1:
        due = get_due_flashcards(username)
        if not due:
            st.success("🎉 No flashcards due today — great job!")
            total = len(get_all_flashcards(username))
            st.caption(f"Total cards in your library: {total}")
        else:
            st.caption(f"{len(due)} flashcards due for review today")
            for row in due:
                card_id, front, back, subject, chapter, next_review_date, review_count = row
                with st.expander(f"📌 {front[:60]}{'...' if len(front) > 60 else ''}"):
                    st.markdown(f"**Q:** {front}")
                    st.markdown(f"**A:** {back}")
                    st.caption(
                        f"Subject: {subject or '—'} | Chapter: {chapter or '—'} | "
                        f"Next review: {next_review_date} | Reviews done: {review_count}"
                    )
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("😊 Easy", key=f"easy_{card_id}", use_container_width=True):
                            update_flashcard_review(card_id, 1)
                            st.rerun()
                    with c2:
                        if st.button("😐 Medium", key=f"med_{card_id}", use_container_width=True):
                            update_flashcard_review(card_id, 2)
                            st.rerun()
                    with c3:
                        if st.button("😓 Hard", key=f"hard_{card_id}", use_container_width=True):
                            update_flashcard_review(card_id, 3)
                            st.rerun()

    with tab2:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        front = st.text_area("Front / Question", key="fc_front")
        back = st.text_area("Back / Answer", key="fc_back")
        subject = st.text_input("Subject", key="fc_subject")
        chapter = st.text_input("Chapter", key="fc_chapter")

        if st.button("➕ Save Flashcard", use_container_width=True, key="save_fc"):
            if not front or not back:
                st.error("Please enter both question and answer.")
            else:
                add_flashcard(username, front, back, subject, chapter)
                add_study_minutes(username, 1)
                award_xp(username, 10)
                auto_check_badges(username)
                st.success("Flashcard saved successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        all_cards = get_all_flashcards(username)
        if not all_cards:
            st.markdown(
                "<div style='text-align:center;padding:30px;color:#64748b;'>"
                "📭 No flashcards yet.<br>Create your first card in the ➕ Create tab."
                "</div>",
                unsafe_allow_html=True
            )
        else:
            st.caption(f"📚 Total: {len(all_cards)} flashcards in your library")
            for row in all_cards:
                c_id, front, back, subject, chapter, nrd, rc = row
                with st.expander(f"📌 {front[:60]}{'...' if len(front) > 60 else ''}"):
                    st.markdown(f"**Q:** {front}")
                    st.markdown(f"**A:** {back}")
                    st.caption(
                        f"Subject: {subject or '—'} | Chapter: {chapter or '—'} | "
                        f"Next review: {nrd} | Reviews done: {rc}"
                    )
                    if st.button("🗑️ Delete this card", key=f"del_fc_{c_id}", use_container_width=True):
                        delete_flashcard(c_id)
                        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS
# ─────────────────────────────────────────────────────────────────────────────
def show_achievements(username):
    render_back_button()
    render_header("Achievements", "Badges unlock automatically as you learn")

    auto_check_badges(username)
    stats = get_user_stats(username) or {}
    earned = get_earned_badges(username)

    earned_list = [b for b in ALL_BADGES if b["id"] in earned]
    locked_list = [b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(f"**✅ {len(earned_list)} / {len(ALL_BADGES)} badges earned**")
    st.progress(len(earned_list) / len(ALL_BADGES) if ALL_BADGES else 0)

    st.markdown("""
    <div style="font-size:.82rem;color:#475569;margin-top:8px;">
    🔥 <b>Streaks</b> — log in every day &nbsp;|&nbsp;
    ⏱️ <b>Study time</b> — use the Study Timer &nbsp;|&nbsp;
    🗂️ <b>Flashcards</b> — create 10 cards
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🏅 Earned Badges**")
        if earned_list:
            cols = st.columns(2)
            for i, badge in enumerate(earned_list):
                with cols[i % 2]:
                    st.markdown(
                        f"""<div class="sf-soft-card" style="text-align:center;margin-bottom:10px;">
                            <div style="font-size:2rem;">{badge['icon']}</div>
                            <div style="font-weight:800;">{badge['name']}</div>
                            <div style="font-size:.75rem;color:#64748b;">{badge['desc']}</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
        else:
            st.info("No badges earned yet — start studying to unlock some!")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🔒 Locked Badges**")
        for b in locked_list:
            hint = b["desc"]
            st.markdown(
                f"""<div class="sf-soft-card" style="margin-bottom:10px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="font-size:1.4rem;opacity:.28;">{b['icon']}</div>
                        <div>
                            <div style="font-weight:800;">{b['name']}</div>
                            <div style="font-size:.75rem;color:#64748b;">{hint}</div>
                        </div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sf-card" style="margin-top:14px;">', unsafe_allow_html=True)
    st.markdown("**📈 Your Progress Towards Next Badge**")

    streak = stats.get("streak_days", 0)
    total_min = stats.get("total_study_minutes", stats.get("total_minutes", 0))

    shown = False
    for b in locked_list:
        bid = b["id"]
        if bid == "streak_3" and streak < 3:
            st.caption(f"🔥 Streak: {streak}/3 days")
            st.progress(streak / 3)
            shown = True
            break
        elif bid == "streak_7" and streak < 7:
            st.caption(f"🔥 Streak: {streak}/7 days")
            st.progress(streak / 7)
            shown = True
            break
        elif bid == "streak_14" and streak < 14:
            st.caption(f"🔥 Streak: {streak}/14 days")
            st.progress(streak / 14)
            shown = True
            break
        elif bid == "streak_30" and streak < 30:
            st.caption(f"🔥 Streak: {streak}/30 days")
            st.progress(streak / 30)
            shown = True
            break
        elif bid == "study_60" and total_min < 60:
            st.caption(f"⏱️ Study: {total_min}/60 min")
            st.progress(total_min / 60)
            shown = True
            break
        elif bid == "study_300" and total_min < 300:
            st.caption(f"⏱️ Study: {total_min}/300 min")
            st.progress(total_min / 300)
            shown = True
            break
        elif bid == "fc_10":
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            try:
                c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
                fc = c.fetchone()[0] or 0
            except sqlite3.OperationalError:
                fc = 0
            conn.close()
            if fc < 10:
                st.caption(f"🗂️ Flashcards: {fc}/10")
                st.progress(fc / 10)
                shown = True
                break

    if not shown:
        st.success("🎉 Great work — keep studying to unlock more badges!")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ENHANCED STUDY TOOLS WITH PDF EXPORT
# ─────────────────────────────────────────────────────────────────────────────
def show_study_tools_enhanced(username):
    render_back_button()
    render_header("Study Tools", "AI-powered exam preparation")

    profile = get_user_profile(username) or {}
    p_cat = profile.get("category", "")
    p_course = profile.get("course", "")
    p_stream = profile.get("stream", "")
    p_board = profile.get("board", "")
    
    meta = CATEGORY_META.get(p_cat, {"icon": "📘"})
    st.markdown(f"""
        <div style="text-align:center;margin-bottom:18px;">
            <div style="font-size:1.4rem;font-weight:800;color:#0f172a;">
                {meta['icon']} Study Tools
            </div>
            <div style="font-size:.88rem;color:#64748b;margin-top:5px;">
                {p_course} · {p_stream} · {p_board}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Profile lock banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);
        border:1.5px solid #bfdbfe;border-radius:14px;
        padding:10px 18px;margin-bottom:14px;
        display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.3rem;">🔒</span>
        <div>
            <span style="font-weight:700;color:#1d4ed8;font-size:.88rem;">
                Content locked to your profile:
            </span>
            <span style="color:#374151;font-size:.85rem;margin-left:6px;">
                {p_cat} → {p_course} → {p_stream} → {p_board}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    
    # Tool selection
    tool = st.radio(
        "🛠️ Select Tool",
        ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "🧪 Question Paper", "❓ Exam Q&A"],
        horizontal=True,
        key="study_tool_radio"
    )
    
    # Subject selection based on profile
    category_options = list(STUDY_DATA.keys())
    default_category = profile.get("category", category_options[0] if category_options else "")
    category_index = category_options.index(default_category) if default_category in category_options else 0
    
    category = st.selectbox(
        "📚 Category",
        category_options,
        index=category_index,
        key="sel_cat"
    )
    
    course_options = get_courses(category)
    default_course = profile.get("course", course_options[0] if course_options else "")
    course_index = course_options.index(default_course) if default_course in course_options else 0
    course = st.selectbox(
        "🎓 Program / Class",
        course_options,
        index=course_index,
        key="sel_course"
    )
    
    stream_options = get_streams(category, course)
    default_stream = profile.get("stream", stream_options[0] if stream_options else "")
    stream_index = stream_options.index(default_stream) if default_stream in stream_options else 0
    stream = st.selectbox(
        "📖 Stream",
        stream_options,
        index=stream_index,
        key="sel_stream"
    )
    
    subject_options = get_subjects(category, course, stream)
    subject = st.selectbox(
        "📘 Subject",
        subject_options,
        key="sel_subject"
    )
    
    # Advanced options based on tool
    if tool == "📝 Summary":
        style = st.radio(
            "Style",
            ["📋 Notes Format", "📄 Detailed", "⚡ Short & Quick"],
            horizontal=True,
            key="summary_style"
        )
    elif tool == "🧪 Question Paper":
        year = st.selectbox("Year", ["2025", "2024", "2023", "2022", "2021"])
        difficulty = st.slider("Difficulty", 1, 5, 3)
    
    chapter = st.text_input("Chapter / Topic", key="tool_chapter")
    topic_text = st.text_area("What do you want help with?", height=140, key="tool_prompt")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Generate button
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_clicked = st.button(f"🚀 Generate {tool}", use_container_width=True, key="generate_tool")
    with col2:
        if st.button("📊 View History", use_container_width=True, key="view_history"):
            go_to("history")
    
    if generate_clicked:
        if not subject or not topic_text:
            st.error("Please fill in the subject and topic/prompt.")
            return
        
        # AI generation with progress
        with st.spinner(f"Generating {tool}..."):
            result = generate_ai_content(tool, subject, chapter, topic_text, username)
        
        # Display result
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Generated Content")
        st.markdown(result)
        
        # PDF export
        if len(result) > 100:
            pdf_buffer = generate_pdf(result)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_buffer,
                file_name=f"{tool}_{subject}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Log activity
        add_to_history(tool, chapter or "General", subject, result, username=username)
        log_study_history(username, tool, subject)
        award_xp(username, 20)
        auto_check_badges(username)

# ─────────────────────────────────────────────────────────────────────────────
# Part 7 SETTINGS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_settings(username):
    render_back_button()
    render_header("Settings", "Customize your StudySmart experience")

    profile = get_user_profile(username)
    stats = get_user_stats(username) or {}

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown("### 👤 Profile Information")
    if profile:
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Category", value=profile.get("category", ""), disabled=True)
            st.text_input("Course", value=profile.get("course", ""), disabled=True)
        with col2:
            st.text_input("Stream", value=profile.get("stream", ""), disabled=True)
            st.text_input("Board/Syllabus", value=profile.get("board", ""), disabled=True)
    else:
        st.info("No profile data found. Complete onboarding first.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Study Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔥 Streak Days", stats.get("streak_days", 0))
    with col2:
        st.metric("⏱️ Total Minutes", stats.get("total_study_minutes", 0))
    with col3:
        st.metric("⭐ XP Points", stats.get("xp_points", 0))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ App Settings")

    # Theme toggle
    theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
    if theme != "Light":
        st.info(f"Note: Theme '{theme}' will be applied on next page refresh.")

    # Notifications
    notif_email = st.checkbox("Email notifications", value=False)
    notif_push = st.checkbox("Push notifications", value=True)

    # Study preferences
    pomodoro_length = st.slider("Pomodoro timer length (minutes)", 15, 60, 25)
    daily_goal = st.number_input("Daily study goal (minutes)", 15, 480, 120, step=15)

    if st.button("💾 Save Settings", use_container_width=True, key="save_settings"):
        st.success("Settings saved successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown("### 🔧 Advanced")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset Onboarding", use_container_width=True, key="reset_ob"):
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("UPDATE user_profiles SET onboarded=0 WHERE username=?", (username,))
            conn.commit()
            conn.close()
            st.session_state.page = "onboarding"
            st.session_state.ob_step = 1
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Activity Log", use_container_width=True, key="clear_log"):
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("DELETE FROM activity_log WHERE username=?", (username,))
            conn.commit()
            conn.close()
            st.success("Activity log cleared!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Configuration")
    models = get_available_models()
    if models:
        st.selectbox("Preferred Gemini Model", models, key="pref_model")
        st.caption(f"Detected {len(models)} available Gemini models")
    else:
        st.warning("No Gemini models detected. Check your API key and internet connection.")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MISSING HELPER FUNCTIONS (from search results)
# ─────────────────────────────────────────────────────────────────────────────
def check_daily_login(username):
    """Check and update daily login streak."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute("""
        SELECT COALESCE(streak_days, 0), COALESCE(last_login, '')
        FROM user_stats WHERE username=?
    """, (username,))
    row = c.fetchone()
    streak_days, last_login = row if row else (0, "")

    if last_login == today:
        conn.close()
        return {"message": f"✅ Already checked in today · 🔥 {streak_days} day streak!", "xp": 0}

    if last_login == yesterday:
        streak_days += 1
    else:
        streak_days = 1

    xp = 20
    c.execute("""
        UPDATE user_stats
        SET streak_days=?, last_login=?, total_xp=COALESCE(total_xp,0)+?
        WHERE username=?
    """, (streak_days, today, xp, username))
    conn.commit()
    conn.close()
    return {"message": f"🔥 {streak_days} day streak! +{xp} XP", "xp": xp, "streak": streak_days}

def award_xp(username, amount):
    """Award XP to user."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute("UPDATE user_stats SET total_xp = total_xp + ? WHERE username=?", (amount, username))
    conn.commit()
    conn.close()

def record_study_session(username, subject, minutes):
    """Record a study session in the database."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    # Create study_sessions table if not exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            subject TEXT,
            minutes INTEGER,
            sess_date TEXT
        )
    """)

    c.execute("""
        INSERT INTO study_sessions (username, subject, minutes, sess_date)
        VALUES (?, ?, ?, ?)
    """, (username, subject, int(minutes), today))

    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute("""
        UPDATE user_stats
        SET total_minutes = COALESCE(total_minutes, 0) + ?
        WHERE username=?
    """, (int(minutes), username))

    conn.commit()
    conn.close()

    try:
        auto_check_badges(username)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# ROUTER / MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # Sidebar (only when logged in)
    if st.session_state.page != "login" and st.session_state.username:
        render_sidebar(st.session_state.username)

    # Page router
    if st.session_state.page == "login":
        show_login()
    elif st.session_state.page == "onboarding":
        show_onboarding(st.session_state.username)
    elif st.session_state.page == "dashboard":
        show_dashboard(st.session_state.username)
    elif st.session_state.page == "study_tools":
        show_study_tools(st.session_state.username)
    elif st.session_state.page == "flashcards":
        show_flashcards(st.session_state.username)
    elif st.session_state.page == "achievements":
        show_achievements(st.session_state.username)
    elif st.session_state.page == "settings":
        show_settings(st.session_state.username)
    else:
        # Default fallback
        st.session_state.page = "login"
        st.rerun()

    # Auto-redirect to onboarding if needed
    if (st.session_state.page != "login" and st.session_state.page != "onboarding" and
        st.session_state.username):
        profile = get_user_profile(st.session_state.username)
        if not profile or not profile.get("onboarded"):
            st.session_state.page = "onboarding"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
