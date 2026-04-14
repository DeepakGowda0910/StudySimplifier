# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — app.py
# ✅ Open Registration    ✅ Streamlit Secrets API Key   ✅ Study Hierarchy
# ✅ Streak + XP System   ✅ Study Timer (saves minutes) ✅ Auto-unlock Badges
# ✅ Flashcards (Spaced Repetition)  ✅ AI Tools (Notes/Quiz/QP/Roadmap)
# ✅ Dashboard + Achievements        ✅ Mobile Friendly  ✅ No external files
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import io
import json
import time
import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# GEMINI — load key safely from Streamlit Secrets
# ─────────────────────────────────────────────────────────────────────────────
def configure_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def get_available_models():
    try:
        configure_gemini()
        return [m.name for m in genai.list_models()
                if "generateContent" in m.supported_generation_methods
                and "flash" in m.name.lower()]
    except:
        return ["models/gemini-1.5-flash"]

# ─────────────────────────────────────────────────────────────────────────────
# STUDY DATA LOADER — reads from data/study_data.json in your GitHub repo
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_study_data():
    try:
        if Path("data/study_data.json").exists():
            with open(Path("data/study_data.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        elif Path("study_data.json").exists():
            with open("study_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except FileNotFoundError:
        st.error("❌ data/study_data.json not found!")
    except json.JSONDecodeError:
        st.error("❌ study_data.json is not valid JSON!")
    return {}

STUDY_DATA = load_study_data()
BOARDS     = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge", "University", "None / Other"]

CATEGORY_META = {
    "K-12th":              {"icon": "🏫", "desc": "Class 1 to 12 · School Curriculum",    "color": "#3b82f6"},
    "Undergraduate":       {"icon": "🎓", "desc": "Bachelor's Degree Programs",            "color": "#8b5cf6"},
    "Postgraduate":        {"icon": "🔬", "desc": "Master's & PhD Programs",               "color": "#10b981"},
    "Competitive Exams":   {"icon": "🏆", "desc": "JEE · NEET · UPSC · CAT & more",       "color": "#f59e0b"},
    "Professional":        {"icon": "💼", "desc": "CA · CS · CMA · Law & more",            "color": "#ef4444"},
    "Skill & Certification":{"icon":"📜", "desc": "Tech · Design · Language Courses",      "color": "#06b6d4"},
}

ALL_BADGES = [
    {"id":"first_login",  "name":"First Step",       "icon":"👣", "desc":"Logged in for the first time"},
    {"id":"streak_3",     "name":"Heatwave",          "icon":"🔥", "desc":"3-day study streak"},
    {"id":"streak_7",     "name":"Weekly Warrior",    "icon":"🎖️", "desc":"7-day study streak"},
    {"id":"streak_14",    "name":"Fortnight Champ",   "icon":"🏆", "desc":"14-day study streak"},
    {"id":"streak_30",    "name":"Monthly Master",    "icon":"👑", "desc":"30-day study streak"},
    {"id":"first_gen",    "name":"Starter Spark",     "icon":"✨", "desc":"Generated first AI content"},
    {"id":"qp_generated", "name":"Paper Setter",      "icon":"📝", "desc":"Generated a question paper"},
    {"id":"quiz_done",    "name":"Quiz Taker",         "icon":"🧠", "desc":"Generated a quiz"},
    {"id":"fc_10",        "name":"Card Collector",    "icon":"🗂️", "desc":"Created 10 flashcards"},
    {"id":"study_60",     "name":"Hour Hero",          "icon":"⏱️", "desc":"Studied 60 minutes total"},
    {"id":"study_300",    "name":"Study Champion",    "icon":"🎓", "desc":"Studied 5 hours total"},
    {"id":"onboarded",    "name":"Profile Complete",  "icon":"🙌", "desc":"Completed your study profile"},
    {"id":"roadmap_done", "name":"Planner",           "icon":"📅", "desc":"Generated a study roadmap"},
]

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],[class*="st-"]{font-family:'Inter',sans-serif!important;box-sizing:border-box;}

#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],.stDeployButton,[data-testid="baseButton-header"],
div[class*="viewerBadge"],.st-emotion-cache-zq5wmm,.st-emotion-cache-1dp5vir,
[data-testid="manage-app-button"]{display:none!important;visibility:hidden!important;height:0!important;}

.block-container{max-width:1180px!important;padding-top:0.6rem!important;padding-bottom:2.5rem!important;padding-left:1rem!important;padding-right:1rem!important;}
.stApp{background:linear-gradient(160deg,#f8fbff 0%,#eef3fb 60%,#e8f0fa 100%)!important;color:#0f172a!important;}
.stApp p,.stApp span,.stApp li,.stApp label,.stApp div,.stApp strong,.stApp small,.stApp h1,.stApp h2,.stApp h3,.stApp h4{color:#0f172a;}
[data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] *{color:#0f172a!important;}

.sf-hero{text-align:center;padding:14px 0 8px 0;}
.sf-hero-title{font-size:2.6rem;font-weight:800;background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1;margin:0;}
.sf-hero-sub{color:#475569!important;font-size:.94rem;font-weight:500;margin-top:4px;}
.sf-powered{display:inline-block;margin-top:7px;padding:3px 14px;border-radius:999px;background:rgba(37,99,235,0.09);color:#2563eb!important;font-size:.69rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;}

.sf-card{position:relative!important;z-index:10!important;background:#ffffff!important;border:1px solid #dde5f0!important;border-radius:16px!important;padding:20px 22px!important;margin-bottom:14px!important;box-shadow:0 4px 18px rgba(15,23,42,.05)!important;overflow:visible!important;}
.sf-card *,.sf-card p,.sf-card span,.sf-card li,.sf-card strong,.sf-card small{color:#0f172a!important;}
.sf-soft-card{background:linear-gradient(160deg,#f8fbff,#f1f5f9)!important;border:1px solid #dde5f0!important;border-radius:14px!important;padding:14px!important;color:#0f172a!important;}

.mc{border-radius:14px;padding:14px 10px;color:white!important;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,.09);margin-bottom:10px;}
.mc *{color:white!important;}
.mc-blue{background:linear-gradient(135deg,#3b82f6,#1d4ed8);}
.mc-green{background:linear-gradient(135deg,#10b981,#059669);}
.mc-purple{background:linear-gradient(135deg,#8b5cf6,#7c3aed);}
.mc-amber{background:linear-gradient(135deg,#f59e0b,#d97706);}
.mc .icon{font-size:1.25rem;}.mc .val{font-size:1.45rem;font-weight:800;margin:3px 0;}.mc .lbl{font-size:.75rem;opacity:.93;}

.xp-wrap{background:#e2e8f0;border-radius:999px;height:10px;overflow:hidden;}
.xp-fill{height:10px;border-radius:999px;background:linear-gradient(90deg,#2563eb,#7c3aed);transition:width .4s ease;}

.bdg{text-align:center;padding:14px 10px;border-radius:14px;border:1.5px solid #e2e8f0;background:#fff;margin:4px;box-shadow:0 3px 10px rgba(0,0,0,.05);}
.bi{font-size:2rem;line-height:1;margin-bottom:5px;}
.bn{font-weight:700;font-size:.82rem;color:#0f172a!important;}
.bs{font-size:.72rem;color:#64748b!important;margin-top:2px;}

.sf-output{background:linear-gradient(160deg,#f0f7ff,#e8f0fe)!important;border:1.5px solid #bfdbfe!important;border-radius:14px!important;padding:18px 20px!important;color:#0f172a!important;}
.sf-output *,.sf-output p,.sf-output li,.sf-output strong{color:#0f172a!important;}
.sf-answers{background:linear-gradient(160deg,#f0fdf4,#dcfce7)!important;border:1.5px solid #86efac!important;border-radius:14px!important;padding:18px!important;}
.sf-fullpaper{background:#fffdf5!important;border:1.5px solid #fcd34d!important;border-radius:14px!important;padding:18px!important;}

.sf-hist{background:#f8fafc;border-radius:10px;padding:9px 12px;margin-bottom:7px;border:1px solid #e2e8f0;font-size:.82rem;color:#334155!important;}

div[data-testid="stSuccessMessage"]{background:rgba(16,185,129,0.08)!important;border:1.5px solid rgba(16,185,129,0.3)!important;border-radius:10px!important;}
div[data-testid="stWarningMessage"]{background:rgba(245,158,11,0.08)!important;border:1.5px solid rgba(245,158,11,0.3)!important;border-radius:10px!important;}
div[data-testid="stErrorMessage"]{background:rgba(239,68,68,0.08)!important;border:1.5px solid rgba(239,68,68,0.3)!important;border-radius:10px!important;}
div[data-testid="stInfoMessage"]{background:rgba(59,130,246,0.08)!important;border:1.5px solid rgba(59,130,246,0.3)!important;border-radius:10px!important;}
hr{border:none;border-top:1px solid #e2e8f0;margin:20px 0;}

@media(max-width:768px){
    .sf-hero-title{font-size:2rem!important;}
    .stButton>button{height:3rem!important;font-size:.9rem!important;}
    .stTabs [data-baseweb="tab-list"]{overflow-x:auto!important;flex-wrap:nowrap!important;}
    .stTabs [data-baseweb="tab"]{white-space:nowrap!important;font-size:.8rem!important;}
    div[role="listbox"]{max-height:38vh!important;overflow-y:auto!important;position:fixed!important;z-index:9999!important;}
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY, password TEXT NOT NULL)""")

    c.execute("""CREATE TABLE IF NOT EXISTS user_profile(
        username TEXT PRIMARY KEY,
        category TEXT DEFAULT '', course TEXT DEFAULT '',
        stream   TEXT DEFAULT '', board  TEXT DEFAULT '',
        onboarded INTEGER DEFAULT 0, created_at TEXT DEFAULT '')""")

    c.execute("""CREATE TABLE IF NOT EXISTS user_stats(
        username      TEXT PRIMARY KEY,
        total_xp      INTEGER DEFAULT 0,
        streak_days   INTEGER DEFAULT 0,
        last_login    TEXT DEFAULT '',
        total_minutes INTEGER DEFAULT 0)""")

    c.execute("""CREATE TABLE IF NOT EXISTS achievements(
        username TEXT, badge_id TEXT, earned_at TEXT,
        PRIMARY KEY(username, badge_id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS flashcards(
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        username         TEXT,
        front_text       TEXT,
        back_text        TEXT,
        subject          TEXT DEFAULT '',
        chapter          TEXT DEFAULT '',
        ease_factor      REAL DEFAULT 2.5,
        interval_days    INTEGER DEFAULT 1,
        next_review_date TEXT,
        review_count     INTEGER DEFAULT 0,
        created_date     TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS study_sessions(
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        username  TEXT,
        subject   TEXT,
        minutes   INTEGER DEFAULT 0,
        sess_date TEXT)""")

    # Safe migrations
    def cols(t):
        c.execute(f"PRAGMA table_info({t})")
        return [r[1] for r in c.fetchall()]
    def add_col(t, col, defn):
        if col not in cols(t):
            c.execute(f"ALTER TABLE {t} ADD COLUMN {col} {defn}")

    add_col("user_stats","total_xp","INTEGER DEFAULT 0")
    add_col("user_stats","streak_days","INTEGER DEFAULT 0")
    add_col("user_stats","last_login","TEXT DEFAULT ''")
    add_col("user_stats","total_minutes","INTEGER DEFAULT 0")
    add_col("flashcards","ease_factor","REAL DEFAULT 2.5")
    add_col("flashcards","interval_days","INTEGER DEFAULT 1")
    add_col("flashcards","next_review_date","TEXT")
    add_col("flashcards","review_count","INTEGER DEFAULT 0")
    add_col("flashcards","created_date","TEXT")
    add_col("study_sessions","subject","TEXT")
    add_col("study_sessions","minutes","INTEGER DEFAULT 0")
    add_col("study_sessions","sess_date","TEXT")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STUDY HIERARCHY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_courses(cat):
    return list(STUDY_DATA.get(cat, {}).keys())
def get_streams(cat, crs):
    return list(STUDY_DATA.get(cat, {}).get(crs, {}).keys())
def get_subjects(cat, crs, strm):
    d = STUDY_DATA.get(cat, {}).get(crs, {}).get(strm, {})
    return list(d.keys()) if isinstance(d, dict) else d if isinstance(d, list) else []
def get_topics(cat, crs, strm, subj):
    d = STUDY_DATA.get(cat, {}).get(crs, {}).get(strm, {}).get(subj, {})
    return list(d.keys()) if isinstance(d, dict) else []
def get_chapters(cat, crs, strm, subj, topic):
    d = STUDY_DATA.get(cat, {}).get(crs, {}).get(strm, {}).get(subj, {}).get(topic, [])
    return d if isinstance(d, list) else []

# ─────────────────────────────────────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def hash_p(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password):
    u, p = username.strip(), password.strip()
    if len(u) < 3: return False, "❌ Username must be at least 3 characters."
    if len(p) < 6: return False, "❌ Password must be at least 6 characters."
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (u,))
    if c.fetchone(): conn.close(); return False, "❌ Username already taken."
    c.execute("INSERT INTO users(username,password) VALUES(?,?)", (u, hash_p(p)))
    c.execute("INSERT OR IGNORE INTO user_stats(username) VALUES(?)", (u,))
    conn.commit(); conn.close()
    return True, "✅ Account created! Please sign in."

def login_user(username, password):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=? AND password=?", (username.strip(), hash_p(password.strip())))
    row = c.fetchone(); conn.close()
    return row is not None

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_user_profile(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT category,course,stream,board,onboarded FROM user_profile WHERE username=?", (username,))
    row = c.fetchone(); conn.close()
    if row: return {"category":row[0],"course":row[1],"stream":row[2],"board":row[3],"onboarded":bool(row[4])}
    return {"category":"","course":"","stream":"","board":"","onboarded":False}

def save_profile(username, category, course, stream, board):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO user_profile(username,category,course,stream,board,onboarded,created_at)
                 VALUES(?,?,?,?,?,1,?)""",
              (username, category, course, stream, board, datetime.datetime.now().isoformat()))
    conn.commit(); conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STATS / STREAK / XP
# ─────────────────────────────────────────────────────────────────────────────
def get_user_stats(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats(username) VALUES(?)", (username,))
    conn.commit()
    c.execute("SELECT total_xp,streak_days,last_login,total_minutes FROM user_stats WHERE username=?", (username,))
    row = c.fetchone()

    today = datetime.date.today().isoformat()
    week_start = (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())).isoformat()
    c.execute("SELECT SUM(minutes) FROM study_sessions WHERE username=? AND sess_date>=?", (username, week_start))
    weekly = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=? AND next_review_date<=?", (username, today))
    fc_due = c.fetchone()[0]
    conn.close()

    total_xp = row[0] or 0
    return {
        "total_xp":           total_xp,
        "streak_days":        row[1] or 0,
        "last_login":         row[2] or "",
        "total_study_minutes":row[3] or 0,
        "weekly_study_minutes":weekly,
        "flashcards_due":     fc_due,
        "level":              (total_xp // 500) + 1,
        "level_progress":     total_xp % 500,
    }

def award_xp(username, amount):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats(username) VALUES(?)", (username,))
    c.execute("UPDATE user_stats SET total_xp=total_xp+? WHERE username=?", (amount, username))
    conn.commit(); conn.close()

def check_daily_login(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats(username) VALUES(?)", (username,))
    c.execute("SELECT streak_days,last_login FROM user_stats WHERE username=?", (username,))
    row = c.fetchone()
    streak, last = row[0] or 0, row[1] or ""
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if last == today:
        conn.close()
        return {"message": f"✅ Already checked in today · 🔥 {streak} day streak", "xp": 0, "streak": streak}
    streak = streak + 1 if last == yesterday else 1
    xp = 20 + (10 if streak % 7 == 0 else 0)
    c.execute("UPDATE user_stats SET streak_days=?,last_login=?,total_xp=total_xp+? WHERE username=?",
              (streak, today, xp, username))
    conn.commit(); conn.close()
    return {"message": f"🔥 {streak} day streak! +{xp} XP", "xp": xp, "streak": streak}

def record_study_session(username, subject, minutes):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("INSERT INTO study_sessions(username,subject,minutes,sess_date) VALUES(?,?,?,?)",
              (username, subject, int(minutes), today))
    c.execute("INSERT OR IGNORE INTO user_stats(username) VALUES(?)", (username,))
    c.execute("UPDATE user_stats SET total_minutes=COALESCE(total_minutes,0)+? WHERE username=?",
              (int(minutes), username))
    conn.commit(); conn.close()
    try: auto_check_badges(username)
    except: pass

# ─────────────────────────────────────────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────────────────────────────────────────
def get_earned_badges(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT badge_id FROM achievements WHERE username=?", (username,))
    earned = {r[0] for r in c.fetchall()}; conn.close()
    return earned

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute("INSERT OR IGNORE INTO achievements(username,badge_id,earned_at) VALUES(?,?,?)",
              (username, badge_id, now))
    conn.commit(); conn.close()

def auto_check_badges(username):
    stats  = get_user_stats(username)
    earned = get_earned_badges(username)
    streak = stats.get("streak_days", 0)
    mins   = stats.get("total_study_minutes", 0)

    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
    fc_count = c.fetchone()[0]; conn.close()

    checks = [
        ("streak_3",  streak >= 3),
        ("streak_7",  streak >= 7),
        ("streak_14", streak >= 14),
        ("streak_30", streak >= 30),
        ("study_60",  mins   >= 60),
        ("study_300", mins   >= 300),
        ("fc_10",     fc_count >= 10),
    ]
    for badge_id, condition in checks:
        if condition and badge_id not in earned:
            award_badge(username, badge_id)
            award_xp(username, 50)

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def add_flashcard(username, front, back, subject, chapter):
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("""INSERT INTO flashcards(username,front_text,back_text,subject,chapter,
                 ease_factor,interval_days,next_review_date,review_count,created_date)
                 VALUES(?,?,?,?,?,2.5,1,?,0,?)""",
              (username, front, back, subject, chapter, today, today))
    conn.commit(); conn.close()

def get_due_flashcards(username):
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("""SELECT id,front_text,back_text,subject,chapter,ease_factor,interval_days,review_count
                 FROM flashcards WHERE username=? AND (next_review_date<=? OR next_review_date IS NULL)
                 ORDER BY next_review_date""", (username, today))
    rows = c.fetchall(); conn.close()
    return rows

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT id,front_text,back_text,subject,chapter,next_review_date,review_count FROM flashcards WHERE username=? ORDER BY id DESC", (username,))
    rows = c.fetchall(); conn.close()
    return rows

def update_flashcard_review(card_id, quality):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT ease_factor,interval_days FROM flashcards WHERE id=?", (card_id,))
    row = c.fetchone()
    if not row: conn.close(); return
    ef, iv = row
    if quality == 5: ef = min(3.0, ef + 0.1); iv = max(1, int(iv * ef))
    elif quality == 3: iv = max(1, int(iv * 1.2))
    else: ef = max(1.3, ef - 0.2); iv = 1
    next_date = (datetime.date.today() + datetime.timedelta(days=iv)).isoformat()
    c.execute("UPDATE flashcards SET ease_factor=?,interval_days=?,next_review_date=?,review_count=review_count+1 WHERE id=?",
              (ef, iv, next_date, card_id))
    conn.commit(); conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit(); conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATION (ReportLab)
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(title, content, profile):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                 fontSize=18, textColor=colors.HexColor("#1d4ed8"),
                                 spaceAfter=10, alignment=TA_CENTER)
    body_style  = ParagraphStyle("Body2", parent=styles["Normal"],
                                 fontSize=11, leading=17, textColor=colors.black)
    sub_style   = ParagraphStyle("Sub2", parent=styles["Normal"],
                                 fontSize=9, textColor=colors.HexColor("#64748b"), alignment=TA_CENTER)
    story = [
        Paragraph("StudySmart AI", title_style),
        Paragraph(f"{profile.get('category','')} · {profile.get('course','')} · {profile.get('board','')}", sub_style),
        Spacer(1, 0.3*cm),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb")),
        Spacer(1, 0.3*cm),
        Paragraph(title, title_style),
        Spacer(1, 0.4*cm),
    ]
    for line in content.split("\n"):
        line = line.strip()
        if not line: story.append(Spacer(1, 0.2*cm)); continue
        if line.startswith("##"):
            story.append(Paragraph(f"<b>{line.replace('##','').strip()}</b>",
                                   ParagraphStyle("H2", parent=styles["Normal"], fontSize=13,
                                                  textColor=colors.HexColor("#1e40af"), spaceBefore=8, spaceAfter=4)))
        elif line.startswith("#"):
            story.append(Paragraph(f"<b>{line.replace('#','').strip()}</b>",
                                   ParagraphStyle("H1", parent=styles["Normal"], fontSize=14,
                                                  textColor=colors.HexColor("#1d4ed8"), spaceBefore=10, spaceAfter=5)))
        elif line.startswith(("- ","* ","• ")):
            story.append(Paragraph(f"• {line[2:].strip()}", body_style))
        else:
            story.append(Paragraph(line.replace("**","<b>",1).replace("**","</b>",1), body_style))
    doc.build(story)
    buf.seek(0)
    return buf.read()

# ─────────────────────────────────────────────────────────────────────────────
# AI GENERATION — uses Streamlit Secrets (no hardcoded key)
# ─────────────────────────────────────────────────────────────────────────────
def generate_ai_content(prompt_type, details):
    if not configure_gemini():
        return "⚠️ Gemini API key not found in Streamlit Secrets. Please add GEMINI_API_KEY to your secrets."
    try:
        models = get_available_models()
        model  = genai.GenerativeModel(models[0] if models else "models/gemini-1.5-flash")
    except Exception as e:
        return f"❌ Model init error: {e}"

    ctx = f"""
Student Level : {details.get('category','')} — {details.get('course','')} ({details.get('stream','')})
Board/Univ    : {details.get('board','')}
Subject       : {details.get('subject','')}
Topic         : {details.get('topic','')}
Chapter       : {details.get('chapter','')}
"""
    prompts = {
        "notes": f"""You are an expert teacher. Write detailed, easy-to-understand study notes.
Use markdown: headers (##), bullet points (- ), **bold** key terms.
End with a '## Quick Summary' section.
Context:\n{ctx}""",

        "quiz": f"""Generate 5 high-quality MCQs for exam practice.
Format each as:
Q1. [Question]
A) ... B) ... C) ... D) ...
Correct Answer: [X]
Explanation: [brief reason]
Context:\n{ctx}""",

        "roadmap": f"""Create a 7-day realistic exam revision roadmap.
Each day: specify what to study, how long, and one active-recall tip.
Context:\n{ctx}""",

        "qpaper": f"""Generate a complete question paper (like an actual exam).
Include: 5 MCQs (1 mark), 5 Short Answers (3 marks), 2 Long Answers (5 marks).
Put answers in a separate 'ANSWER KEY' section at the end.
Context:\n{ctx}""",

        "qa": f"""You are a helpful exam tutor. Answer the following study question clearly and in depth, with examples.
Context:\n{ctx}
Question: {details.get('custom_question', 'Explain the main concepts of this topic.')}"""
    }
    try:
        resp = model.generate_content(prompts.get(prompt_type, prompts["notes"]))
        return resp.text
    except Exception as e:
        return f"❌ AI Error: {e}"

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "logged_in":                False,
        "username":                 "",
        "active_page":              "dashboard",
        "daily_checkin_done":       False,
        "study_timer_active":       False,
        "study_timer_start":        None,
        "current_subject_for_timer":"General",
        "history":                  [],
        "fc_review_index":          0,
        "fc_show_answer":           False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def go_to(page):
    st.session_state.active_page = page
    st.rerun()

def do_logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def render_header(title, subtitle=""):
    st.markdown(f"""
    <div class="sf-hero">
        <div class="sf-hero-title">{title}</div>
        {"<div class='sf-hero-sub'>"+subtitle+"</div>" if subtitle else ""}
        <span class="sf-powered">Powered by Gemini AI</span>
    </div>""", unsafe_allow_html=True)

def render_back_button():
    if st.button("← Back to Dashboard", key="back_btn"):
        go_to("dashboard")

def add_to_history(tool, subject, chapter, preview):
    st.session_state.history.insert(0, {
        "time":    datetime.datetime.now().strftime("%H:%M"),
        "tool":    tool,
        "subject": subject,
        "chapter": chapter,
        "preview": preview[:80] + "…" if len(preview) > 80 else preview
    })
    st.session_state.history = st.session_state.history[:10]

# ─────────────────────────────────────────────────────────────────────────────
# AUTH UI
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div class="sf-hero" style="padding-top:40px;">
            <div class="sf-hero-title">StudySmart AI 🎓</div>
            <div class="sf-hero-sub">Your Personal AI Exam Preparation Partner</div>
            <span class="sf-powered">Powered by Gemini AI</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab1:
            with st.form("login_form"):
                u = st.text_input("👤 Username")
                p = st.text_input("🔑 Password", type="password")
                if st.form_submit_button("Sign In 🚀", use_container_width=True):
                    if login_user(u, p):
                        st.session_state.logged_in = True
                        st.session_state.username  = u.strip()
                        st.success("✅ Welcome back!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        with tab2:
            with st.form("register_form"):
                nu = st.text_input("👤 Choose Username", placeholder="Min 3 characters")
                np = st.text_input("🔑 Choose Password", type="password", placeholder="Min 6 characters")
                if st.form_submit_button("Create Account ✨", use_container_width=True):
                    ok, msg = register_user(nu, np)
                    if ok: st.success(msg)
                    else:  st.error(msg)

# ─────────────────────────────────────────────────────────────────────────────
# ONBOARDING UI
# ─────────────────────────────────────────────────────────────────────────────
def show_onboarding(username):
    render_header("Welcome! 👋", "Let's personalise your study experience")
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### 📋 Your Academic Profile")
        cats    = list(CATEGORY_META.keys())
        category = st.selectbox("📂 Category", cats, help="Pick your education level")
        
        courses = get_courses(category)
        course  = st.selectbox("📚 Course / Class", courses if courses else ["General"])
        
        streams = get_streams(category, course)
        stream  = st.selectbox("🎯 Stream / Branch", streams if streams else ["General"])
        
        board   = st.selectbox("🏫 Board / University", BOARDS)

    with c2:
        st.markdown("### 📖 What you'll get")
        meta = CATEGORY_META.get(category, {})
        st.markdown(f"""
        <div class="sf-card" style="margin-top:10px;">
            <div style="font-size:2.5rem;text-align:center;">{meta.get('icon','🎓')}</div>
            <div style="text-align:center;font-weight:700;font-size:1.1rem;margin:8px 0;">{category}</div>
            <div style="text-align:center;color:#64748b;font-size:.9rem;">{meta.get('desc','')}</div>
            <hr>
            <ul style="margin-top:10px;">
                <li>📝 AI-generated notes for your syllabus</li>
                <li>🧠 Smart quizzes & question papers</li>
                <li>📅 Personalised 7-day study roadmap</li>
                <li>🗂️ Spaced-repetition flashcards</li>
                <li>🏅 Badges & XP for staying consistent</li>
            </ul>
        </div>""", unsafe_allow_html=True)

        subjects = get_subjects(category, course, stream)
        if subjects:
            st.success(f"✅ Found **{len(subjects)} subjects** for {course} → {stream}")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("✅ Save Profile & Start Learning →", use_container_width=True):
        save_profile(username, category, course, stream, board)
        award_badge(username, "onboarded")
        award_badge(username, "first_login")
        award_xp(username, 50)
        st.success("🎉 Profile saved! Welcome to StudySmart AI!")
        time.sleep(0.5)
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(username):
    profile = get_user_profile(username)
    stats   = get_user_stats(username) or {}

    with st.sidebar:
        st.markdown(f"### 👋 {username}")
        if profile.get("course"):
            st.caption(f"📚 {profile['course']} · {profile['stream']}")
            st.caption(f"🏫 {profile['board']}")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Streak + Level pills
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#f59e0b,#d97706);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                🔥 {stats.get('streak_days',0)}<br>
                <span style="font-size:.62rem;font-weight:500;">day streak</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                ⭐ Lv {stats.get('level',1)}<br>
                <span style="font-size:.62rem;font-weight:500;">{stats.get('total_xp',0)} XP</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Daily Check-in
        if not st.session_state.daily_checkin_done:
            if st.button("✅ Daily Check-in (+20 XP)", use_container_width=True, key="sb_checkin"):
                result = check_daily_login(username)
                st.session_state.daily_checkin_done = True
                auto_check_badges(username)
                st.success(result.get("message", "Checked in!"))
                st.rerun()
        else:
            st.success(f"✅ Checked in · 🔥 {stats.get('streak_days',0)} days")

        st.divider()

        # Study Timer
        st.markdown("**⏱️ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed = int((datetime.datetime.now() - st.session_state.study_timer_start).total_seconds() // 60)
            st.info(f"🟢 Running: {elapsed} min — {st.session_state.current_subject_for_timer}")
            if st.button("⏹️ Stop & Save", use_container_width=True, key="sb_stop"):
                st.session_state.study_timer_active = False
                dur  = max(1, elapsed)
                subj = st.session_state.get("current_subject_for_timer", "General")
                record_study_session(username, subj, dur)
                xp_earned = max(5, (dur // 10) * 10)
                award_xp(username, xp_earned)
                auto_check_badges(username)
                st.session_state.study_timer_start = None
                st.success(f"✅ {dur} min saved! +{xp_earned} XP")
                st.rerun()
        else:
            if st.button("▶️ Start Timer", use_container_width=True, key="sb_start"):
                st.session_state.study_timer_active = True
                st.session_state.study_timer_start  = datetime.datetime.now()
                st.rerun()

        st.divider()

        # Navigation
        st.markdown("**🧭 Navigate**")
        cur = st.session_state.active_page
        for key, label in [("dashboard","📊 Dashboard"),("study","📚 Study Tools"),
                            ("flashcards","🗂️ Flashcards"),("achievements","🏅 Achievements")]:
            if st.button(label, use_container_width=True, key=f"nav_{key}",
                         type="primary" if cur == key else "secondary"):
                if cur != key: go_to(key)

        fc_due = stats.get("flashcards_due", 0)
        if fc_due > 0:
            st.warning(f"📚 {fc_due} card{'s' if fc_due>1 else ''} due for review!")

        st.divider()

        with st.expander("📜 Recent Activity"):
            if not st.session_state.history:
                st.caption("No activity yet.")
            else:
                for h in st.session_state.history:
                    st.markdown(f"""<div class="sf-hist">
                        🕐 {h['time']} | <b>{h['tool']}</b><br>
                        📖 {h['chapter']} — {h['subject']}<br>
                        <small>{h['preview']}</small>
                    </div>""", unsafe_allow_html=True)

        st.divider()
        if st.button("🚪 Logout", use_container_width=True, key="sb_logout"):
            do_logout()

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard(username):
    render_header("StudySmart AI 🎓", "Your Daily Learning Companion")
    stats   = get_user_stats(username) or {}
    profile = get_user_profile(username)

    # Metric cards
    c1, c2, c3, c4 = st.columns(4)
    for col, cls, icon, val, lbl in [
        (c1, "mc-blue",   "🔥", stats.get("streak_days", 0),           "Day Streak"),
        (c2, "mc-green",  "⭐", f"Level {stats.get('level',1)}",        "Your Level"),
        (c3, "mc-purple", "📚", stats.get("flashcards_due", 0),         "Cards Due"),
        (c4, "mc-amber",  "⏱️", f"{stats.get('weekly_study_minutes',0)} min", "This Week"),
    ]:
        with col:
            st.markdown(f'<div class="mc {cls}"><div class="icon">{icon}</div>'
                        f'<div class="val">{val}</div><div class="lbl">{lbl}</div></div>',
                        unsafe_allow_html=True)

    # XP Bar
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    total_xp = stats.get("total_xp", 0)
    lp  = stats.get("level_progress", total_xp % 500)
    pct = min(100, int((lp / 500) * 100))
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:.85rem;font-weight:700;margin-bottom:5px;">
        <span>⭐ Level {stats.get('level',1)}</span><span>{lp}/500 XP</span>
    </div>
    <div class="xp-wrap"><div class="xp-fill" style="width:{pct}%;"></div></div>
    <div style="font-size:.75rem;color:#64748b;margin-top:4px;">{500-lp} XP to Level {stats.get('level',1)+1}</div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Study profile summary
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Your Study Profile")
    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.metric("📂 Category", profile.get("category") or "—")
    pc2.metric("📚 Course",   profile.get("course")   or "—")
    pc3.metric("🎯 Stream",   profile.get("stream")   or "—")
    pc4.metric("🏫 Board",    profile.get("board")    or "—")
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("📝 Generate Notes",     use_container_width=True): go_to("study")
    if qa2.button("🧠 Practice Quiz",      use_container_width=True): go_to("study")
    if qa3.button("🗂️ Review Flashcards",  use_container_width=True): go_to("flashcards")
    if qa4.button("🏅 View Achievements",  use_container_width=True): go_to("achievements")

    # Recent badges
    st.markdown("### 🏅 Recent Badges")
    earned = get_earned_badges(username)
    earned_list = [b for b in ALL_BADGES if b["id"] in earned]
    if earned_list:
        cols = st.columns(min(len(earned_list), 5))
        for i, b in enumerate(earned_list[-5:]):
            with cols[i]:
                st.markdown(f'<div class="bdg"><div class="bi">{b["icon"]}</div>'
                            f'<div class="bn">{b["name"]}</div>'
                            f'<div class="bs">{b["desc"]}</div></div>', unsafe_allow_html=True)
    else:
        st.info("🏅 Complete daily check-in and study sessions to earn your first badge!")

# ─────────────────────────────────────────────────────────────────────────────
# STUDY TOOLS
# ─────────────────────────────────────────────────────────────────────────────
def show_study_tools(username):
    render_back_button()
    render_header("Study Tools 🧠", "AI-powered exam preparation")
    profile = get_user_profile(username)

    # Selector row
    st.markdown("### 🔍 Select Your Topic")
    s1, s2, s3 = st.columns(3)
    with s1:
        subjects = get_subjects(profile["category"], profile["course"], profile["stream"])
        sel_subj = st.selectbox("📖 Subject", subjects if subjects else ["General"])
    with s2:
        topics   = get_topics(profile["category"], profile["course"], profile["stream"], sel_subj)
        sel_topic = st.selectbox("📌 Topic", topics if topics else ["All Topics"])
    with s3:
        chapters = get_chapters(profile["category"], profile["course"], profile["stream"], sel_subj, sel_topic)
        sel_chap = st.selectbox("📑 Chapter", chapters if chapters else ["Introduction"])

    details = {**profile, "subject": sel_subj, "topic": sel_topic, "chapter": sel_chap}

    st.divider()
    tool = st.radio("🛠️ Choose AI Tool",
                    ["📝 Smart Notes", "🧠 Practice Quiz", "📌 Revision Notes",
                     "🧪 Question Paper", "❓ Ask AI", "📅 Study Roadmap"],
                    horizontal=True, key="study_tool_select")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Smart Notes ───────────────────────────────────────────────────────────
    if tool == "📝 Smart Notes":
        if st.button("✨ Generate Smart Notes", use_container_width=True):
            with st.spinner("AI is writing your notes..."):
                res = generate_ai_content("notes", details)
            award_badge(username, "first_gen"); award_xp(username, 10)
            add_to_history("Smart Notes", sel_subj, sel_chap, res)
            st.markdown('<div class="sf-output">', unsafe_allow_html=True)
            st.markdown(res)
            st.markdown('</div>', unsafe_allow_html=True)
            pdf = generate_pdf(f"Notes: {sel_chap}", res, profile)
            st.download_button("📥 Download PDF", pdf, f"{sel_chap}_notes.pdf", "application/pdf")

    # ── Practice Quiz ─────────────────────────────────────────────────────────
    elif tool == "🧠 Practice Quiz":
        if st.button("✨ Generate Quiz", use_container_width=True):
            with st.spinner("AI is preparing questions..."):
                res = generate_ai_content("quiz", details)
            award_badge(username, "quiz_done"); award_xp(username, 10)
            add_to_history("Quiz", sel_subj, sel_chap, res)
            st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
            st.markdown(res)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Revision Notes ────────────────────────────────────────────────────────
    elif tool == "📌 Revision Notes":
        if st.button("✨ Generate Revision Notes", use_container_width=True):
            with st.spinner("AI is creating revision notes..."):
                res = generate_ai_content("notes", {**details, "chapter": f"Quick Revision — {sel_chap}"})
            award_xp(username, 10)
            add_to_history("Revision Notes", sel_subj, sel_chap, res)
            st.markdown('<div class="sf-output">', unsafe_allow_html=True)
            st.markdown(res)
            st.markdown('</div>', unsafe_allow_html=True)
            pdf = generate_pdf(f"Revision: {sel_chap}", res, profile)
            st.download_button("📥 Download PDF", pdf, f"{sel_chap}_revision.pdf", "application/pdf")

    # ── Question Paper ────────────────────────────────────────────────────────
    elif tool == "🧪 Question Paper":
        if st.button("✨ Generate Question Paper", use_container_width=True):
            with st.spinner("AI is generating the question paper..."):
                res = generate_ai_content("qpaper", details)
            award_badge(username, "qp_generated"); award_xp(username, 15)
            add_to_history("Question Paper", sel_subj, sel_chap, res)
            st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
            st.markdown(res)
            st.markdown('</div>', unsafe_allow_html=True)
            pdf = generate_pdf(f"Question Paper: {sel_chap}", res, profile)
            st.download_button("📥 Download PDF", pdf, f"{sel_chap}_qpaper.pdf", "application/pdf")

    # ── Ask AI ────────────────────────────────────────────────────────────────
    elif tool == "❓ Ask AI":
        question = st.text_area("💬 Type your question", placeholder=f"e.g. Explain {sel_chap} with examples...")
        if st.button("✨ Ask", use_container_width=True) and question:
            with st.spinner("AI is thinking..."):
                res = generate_ai_content("qa", {**details, "custom_question": question})
            award_xp(username, 5)
            add_to_history("Ask AI", sel_subj, sel_chap, res)
            st.markdown('<div class="sf-output">', unsafe_allow_html=True)
            st.markdown(res)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Study Roadmap ─────────────────────────────────────────────────────────
    elif tool == "📅 Study Roadmap":
        if st.button("✨ Generate 7-Day Roadmap", use_container_width=True):
            with st.spinner("AI is designing your study plan..."):
                res = generate_ai_content("roadmap", details)
            award_badge(username, "roadmap_done"); award_xp(username, 10)
            add_to_history("Roadmap", sel_subj, sel_chap, res)
            st.markdown('<div class="sf-output">', unsafe_allow_html=True)
            st.markdown(res)
            st.markdown('</div>', unsafe_allow_html=True)
            pdf = generate_pdf(f"Study Roadmap: {sel_subj}", res, profile)
            st.download_button("📥 Download PDF", pdf, f"{sel_subj}_roadmap.pdf", "application/pdf")

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────────────────────────────────────
def show_flashcards(username):
    render_back_button()
    render_header("Flashcards 🗂️", "Spaced repetition for lasting memory")
    tab1, tab2, tab3 = st.tabs(["📖 Review Due", "➕ Create", "📋 My Library"])

    # ── Review Due ────────────────────────────────────────────────────────────
    with tab1:
        due = get_due_flashcards(username)
        if not due:
            st.success("🎉 No cards due today! Come back tomorrow or create new cards.")
        else:
            idx = st.session_state.fc_review_index % len(due)
            card = due[idx]
            cid, front, back, subj, chap, ef, iv, rc = card

            st.markdown(f"**Card {idx+1} of {len(due)}** · Subject: `{subj}` · Chapter: `{chap}`")
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown(f"### ❓ {front}")
            if st.session_state.fc_show_answer:
                st.divider()
                st.markdown(f"**✅ Answer:** {back}")
                st.markdown('</div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                if c1.button("😓 Hard",  use_container_width=True, key="fc_hard"):
                    update_flashcard_review(cid, 1)
                    st.session_state.fc_show_answer = False
                    st.session_state.fc_review_index += 1
                    st.rerun()
                if c2.button("😐 Good",  use_container_width=True, key="fc_good"):
                    update_flashcard_review(cid, 3)
                    st.session_state.fc_show_answer = False
                    st.session_state.fc_review_index += 1
                    st.rerun()
                if c3.button("😊 Easy",  use_container_width=True, key="fc_easy"):
                    update_flashcard_review(cid, 5)
                    st.session_state.fc_show_answer = False
                    st.session_state.fc_review_index += 1
                    auto_check_badges(username)
                    st.rerun()
            else:
                st.markdown('</div>', unsafe_allow_html=True)
                if st.button("👁️ Show Answer", use_container_width=True, key="fc_show"):
                    st.session_state.fc_show_answer = True
                    st.rerun()

    # ── Create ────────────────────────────────────────────────────────────────
    with tab2:
        profile = get_user_profile(username)
        subjects = get_subjects(profile["category"], profile["course"], profile["stream"])
        with st.form("new_fc_form"):
            front   = st.text_area("❓ Question / Front", placeholder="e.g. What is Newton's 2nd Law?")
            back    = st.text_area("✅ Answer / Back",    placeholder="e.g. F = ma")
            fc_subj = st.selectbox("📖 Subject", subjects if subjects else ["General"])
            fc_chap = st.text_input("📑 Chapter", placeholder="e.g. Laws of Motion")
            if st.form_submit_button("💾 Save Flashcard", use_container_width=True):
                if front and back:
                    add_flashcard(username, front, back, fc_subj, fc_chap)
                    award_xp(username, 5)
                    auto_check_badges(username)
                    st.success("✅ Flashcard saved!")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("❌ Both Question and Answer are required.")

    # ── Library ───────────────────────────────────────────────────────────────
    with tab3:
        all_cards = get_all_flashcards(username)
        if not all_cards:
            st.info("📭 No flashcards yet. Create your first one!")
        else:
            st.caption(f"Total: {len(all_cards)} cards")
            for card in all_cards:
                cid, front, back, subj, chap, nrd, rc = card
                with st.expander(f"📌 {front[:60]}{'...' if len(front)>60 else ''}"):
                    st.markdown(f"**Subject:** {subj} | **Chapter:** {chap}")
                    st.markdown(f"**Answer:** {back}")
                    st.markdown(f"**Next Review:** {nrd or 'Today'} | **Reviews:** {rc}")
                    if st.button("🗑️ Delete", key=f"del_{cid}"):
                        delete_flashcard(cid)
                        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS
# ─────────────────────────────────────────────────────────────────────────────
def show_achievements(username):
    render_back_button()
    render_header("Achievements 🏅", "Your trophy room")
    stats   = get_user_stats(username) or {}
    earned  = get_earned_badges(username)

    earned_list = [b for b in ALL_BADGES if b["id"] in earned]
    locked_list = [b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown(f"### 🏆 Earned — {len(earned_list)} / {len(ALL_BADGES)}")
    if earned_list:
        cols = st.columns(4)
        for i, b in enumerate(earned_list):
            with cols[i % 4]:
                st.markdown(f'<div class="bdg"><div class="bi">{b["icon"]}</div>'
                            f'<div class="bn">{b["name"]}</div>'
                            f'<div class="bs">{b["desc"]}</div></div>', unsafe_allow_html=True)
    else:
        st.info("Complete your daily check-in to earn your first badge! 🎯")

    st.markdown("### 🔒 Locked Badges")
    if locked_list:
        cols = st.columns(4)
        for i, b in enumerate(locked_list):
            with cols[i % 4]:
                st.markdown(f'<div class="bdg"><div class="bi" style="opacity:.25;">🔒</div>'
                            f'<div class="bn">{b["name"]}</div>'
                            f'<div class="bs">{b["desc"]}</div></div>', unsafe_allow_html=True)

    # Progress bars toward next badge
    st.markdown('<div class="sf-card" style="margin-top:16px;">', unsafe_allow_html=True)
    st.markdown("### 📈 Progress Toward Next Badge")
    streak    = stats.get("streak_days", 0)
    total_min = stats.get("total_study_minutes", 0)
    shown = False
    for b in locked_list:
        bid = b["id"]
        if   bid == "streak_3"  and streak < 3:
            st.caption(f"🔥 Streak: {streak}/3 days");   st.progress(streak/3);     shown=True
        elif bid == "streak_7"  and streak < 7:
            st.caption(f"🔥 Streak: {streak}/7 days");   st.progress(streak/7);     shown=True
        elif bid == "streak_14" and streak < 14:
            st.caption(f"🔥 Streak: {streak}/14 days");  st.progress(streak/14);    shown=True
        elif bid == "streak_30" and streak < 30:
            st.caption(f"🔥 Streak: {streak}/30 days");  st.progress(streak/30);    shown=True
        elif bid == "study_60"  and total_min < 60:
            st.caption(f"⏱️ Study: {total_min}/60 min"); st.progress(total_min/60); shown=True
        elif bid == "study_300" and total_min < 300:
            st.caption(f"⏱️ Study: {total_min}/300 min");st.progress(total_min/300);shown=True
        elif bid == "fc_10":
            conn = sqlite3.connect("users.db"); cc = conn.cursor()
            cc.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
            fc = cc.fetchone()[0]; conn.close()
            if fc < 10:
                st.caption(f"🗂️ Flashcards: {fc}/10"); st.progress(fc/10); shown=True
    if not shown:
        st.success("🎉 Amazing! Keep studying to unlock more milestones!")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main_app():
    username = st.session_state.username
    profile  = get_user_profile(username)

    if not profile["onboarded"]:
        show_onboarding(username)
        return

    render_sidebar(username)
    page = st.session_state.active_page

    if   page == "dashboard":    show_dashboard(username)
    elif page == "study":        show_study_tools(username)
    elif page == "flashcards":   show_flashcards(username)
    elif page == "achievements": show_achievements(username)
    else:                        show_dashboard(username)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
init_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
