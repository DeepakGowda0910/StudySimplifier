# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — app.py
# ✅ Day/Night Mode Auto-Adapt   ✅ Mobile & Laptop Responsive
# ✅ Premium UI / UX             ✅ Streamlit Banners Removed
# ✅ All Study Features & AI Integrations Retained
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
# RESPONSIVE & DAY/NIGHT MODE CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Dynamic Theme Variables */
:root {
    --bg-color: #f8fbff;
    --card-bg: #ffffff;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --border-color: #dde5f0;
    --accent-blue: #2563eb;
    --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    --card-rad: 16px;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: #0e1117;
        --card-bg: #1e293b;
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
        --border-color: #334155;
        --accent-blue: #3b82f6;
        --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }
}

/* Global Setup */
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

/* Hide ALL Streamlit Elements & Banners */
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton, [data-testid="baseButton-header"],
div[class*="viewerBadge"], [data-testid="manage-app-button"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

.block-container {
    max-width: 1200px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
}

/* Cards & UI Elements */
.sf-card {
    background-color: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--card-rad) !important;
    padding: 24px !important;
    margin-bottom: 16px !important;
    box-shadow: var(--shadow-sm) !important;
    color: var(--text-main) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.sf-card:hover {
    box-shadow: var(--shadow-md) !important;
}

.sf-card * { color: var(--text-main) !important; }
.sf-card .text-muted { color: var(--text-muted) !important; }

/* Hero Section */
.sf-hero { text-align: center; padding: 2rem 1rem 1rem 1rem; }
.sf-hero-title {
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 800;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.sf-hero-sub { color: var(--text-muted); font-size: 1.1rem; font-weight: 500; }

/* Metric Cards */
.mc-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 1rem;}
.mc {
    border-radius: var(--card-rad); padding: 20px;
    color: white !important; text-align: center;
    box-shadow: var(--shadow-sm);
}
.mc * { color: white !important; }
.mc-blue   { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.mc-green  { background: linear-gradient(135deg, #10b981, #059669); }
.mc-purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.mc-amber  { background: linear-gradient(135deg, #f59e0b, #d97706); }
.mc .icon  { font-size: 1.8rem; margin-bottom: 8px;}
.mc .val   { font-size: 1.6rem; font-weight: 800; }
.mc .lbl   { font-size: 0.9rem; opacity: 0.9; }

/* Badges */
.bdg {
    text-align: center; padding: 16px 12px;
    border-radius: var(--card-rad); border: 1px solid var(--border-color);
    background: var(--card-bg); margin: 6px; box-shadow: var(--shadow-sm);
    height: 100%;
}
.bi { font-size: 2.5rem; margin-bottom: 8px; }
.bn { font-weight: 700; font-size: 0.9rem; color: var(--text-main) !important; }
.bs { font-size: 0.8rem; color: var(--text-muted) !important; margin-top: 4px; }

/* Output Boxes */
.sf-output {
    background-color: rgba(59, 130, 246, 0.05) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    border-radius: var(--card-rad) !important;
    padding: 24px !important;
    color: var(--text-main) !important;
}

/* XP Bar */
.xp-wrap { background: var(--border-color); border-radius: 999px; height: 12px; overflow: hidden; margin: 8px 0; }
.xp-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #3b82f6, #8b5cf6); transition: width 0.5s ease; }

/* Buttons Customization */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
}

/* Mobile Enhancements */
@media(max-width: 768px) {
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .stTabs [data-baseweb="tab-list"] { overflow-x: auto !important; flex-wrap: nowrap !important; }
    .stTabs [data-baseweb="tab"] { white-space: nowrap !important; font-size: 0.9rem !important; }
    .sf-card { padding: 16px !important; }
}
</style>
""", unsafe_allow_html=True)

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
# STUDY DATA LOADER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_study_data():
    try:
        if Path("data/study_data.json").exists():
            with open(Path("data/study_data.json"), "r", encoding="utf-8") as f: return json.load(f)
        elif Path("study_data.json").exists():
            with open("study_data.json", "r", encoding="utf-8") as f: return json.load(f)
    except Exception:
        pass
    return {}

STUDY_DATA = load_study_data()
BOARDS     = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge", "University", "Other"]

CATEGORY_META = {
    "K-12th":              {"icon": "🏫", "desc": "Class 1 to 12 · School Curriculum"},
    "Undergraduate":       {"icon": "🎓", "desc": "Bachelor's Degree Programs"},
    "Postgraduate":        {"icon": "🔬", "desc": "Master's & PhD Programs"},
    "Competitive Exams":   {"icon": "🏆", "desc": "JEE · NEET · UPSC · CAT & more"},
    "Professional":        {"icon": "💼", "desc": "CA · CS · CMA · Law & more"},
    "Skill & Certification":{"icon":"📜", "desc": "Tech · Design · Language Courses"},
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
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT NOT NULL)")
    c.execute("""CREATE TABLE IF NOT EXISTS user_profile(
        username TEXT PRIMARY KEY, category TEXT DEFAULT '', course TEXT DEFAULT '',
        stream TEXT DEFAULT '', board TEXT DEFAULT '', onboarded INTEGER DEFAULT 0, created_at TEXT DEFAULT '')""")
    c.execute("""CREATE TABLE IF NOT EXISTS user_stats(
        username TEXT PRIMARY KEY, total_xp INTEGER DEFAULT 0, streak_days INTEGER DEFAULT 0,
        last_login TEXT DEFAULT '', total_minutes INTEGER DEFAULT 0)""")
    c.execute("CREATE TABLE IF NOT EXISTS achievements(username TEXT, badge_id TEXT, earned_at TEXT, PRIMARY KEY(username, badge_id))")
    c.execute("""CREATE TABLE IF NOT EXISTS flashcards(
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, front_text TEXT, back_text TEXT,
        subject TEXT DEFAULT '', chapter TEXT DEFAULT '', ease_factor REAL DEFAULT 2.5,
        interval_days INTEGER DEFAULT 1, next_review_date TEXT, review_count INTEGER DEFAULT 0, created_date TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS study_sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, subject TEXT, minutes INTEGER DEFAULT 0, sess_date TEXT)""")

    def cols(t):
        c.execute(f"PRAGMA table_info({t})")
        return [r[1] for r in c.fetchall()]
    def add_col(t, col, defn):
        if col not in cols(t): c.execute(f"ALTER TABLE {t} ADD COLUMN {col} {defn}")

    add_col("user_stats","total_xp","INTEGER DEFAULT 0"); add_col("user_stats","streak_days","INTEGER DEFAULT 0")
    add_col("user_stats","last_login","TEXT DEFAULT ''"); add_col("user_stats","total_minutes","INTEGER DEFAULT 0")
    add_col("flashcards","ease_factor","REAL DEFAULT 2.5"); add_col("flashcards","interval_days","INTEGER DEFAULT 1")
    add_col("flashcards","next_review_date","TEXT"); add_col("flashcards","review_count","INTEGER DEFAULT 0")
    add_col("flashcards","created_date","TEXT"); add_col("study_sessions","subject","TEXT")
    add_col("study_sessions","minutes","INTEGER DEFAULT 0"); add_col("study_sessions","sess_date","TEXT")
    conn.commit(); conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STUDY HIERARCHY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_courses(cat): return list(STUDY_DATA.get(cat, {}).keys())
def get_streams(cat, crs): return list(STUDY_DATA.get(cat, {}).get(crs, {}).keys())
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
# AUTH & PROFILES & STATS
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

def get_user_profile(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT category,course,stream,board,onboarded FROM user_profile WHERE username=?", (username,))
    row = c.fetchone(); conn.close()
    if row: return {"category":row[0],"course":row[1],"stream":row[2],"board":row[3],"onboarded":bool(row[4])}
    return {"category":"","course":"","stream":"","board":"","onboarded":False}

def save_profile(username, category, course, stream, board):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_profile(username,category,course,stream,board,onboarded,created_at) VALUES(?,?,?,?,?,1,?)",
              (username, category, course, stream, board, datetime.datetime.now().isoformat()))
    conn.commit(); conn.close()

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
    fc_due = c.fetchone()[0]; conn.close()
    total_xp = row[0] or 0
    return {
        "total_xp": total_xp, "streak_days": row[1] or 0, "last_login": row[2] or "",
        "total_study_minutes": row[3] or 0, "weekly_study_minutes": weekly,
        "flashcards_due": fc_due, "level": (total_xp // 500) + 1, "level_progress": total_xp % 500,
    }

def award_xp(username, amount):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("UPDATE user_stats SET total_xp=total_xp+? WHERE username=?", (amount, username))
    conn.commit(); conn.close()

def check_daily_login(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT streak_days,last_login FROM user_stats WHERE username=?", (username,))
    row = c.fetchone(); streak, last = row[0] or 0, row[1] or ""
    today = datetime.date.today().isoformat(); yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if last == today: conn.close(); return {"message": f"✅ Already checked in today · 🔥 {streak} day streak", "xp": 0}
    streak = streak + 1 if last == yesterday else 1
    xp = 20 + (10 if streak % 7 == 0 else 0)
    c.execute("UPDATE user_stats SET streak_days=?,last_login=?,total_xp=total_xp+? WHERE username=?", (streak, today, xp, username))
    conn.commit(); conn.close()
    return {"message": f"🔥 {streak} day streak! +{xp} XP", "xp": xp}

def record_study_session(username, subject, minutes):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("INSERT INTO study_sessions(username,subject,minutes,sess_date) VALUES(?,?,?,?)", (username, subject, int(minutes), today))
    c.execute("UPDATE user_stats SET total_minutes=COALESCE(total_minutes,0)+? WHERE username=?", (int(minutes), username))
    conn.commit(); conn.close(); auto_check_badges(username)

# ─────────────────────────────────────────────────────────────────────────────
# BADGES & FLASHCARDS
# ─────────────────────────────────────────────────────────────────────────────
def get_earned_badges(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT badge_id FROM achievements WHERE username=?", (username,))
    earned = {r[0] for r in c.fetchall()}; conn.close(); return earned

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO achievements(username,badge_id,earned_at) VALUES(?,?,?)", (username, badge_id, datetime.datetime.now().isoformat()))
    conn.commit(); conn.close()

def auto_check_badges(username):
    stats = get_user_stats(username); earned = get_earned_badges(username)
    streak = stats.get("streak_days", 0); mins = stats.get("total_study_minutes", 0)
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,)); fc_count = c.fetchone()[0]; conn.close()
    checks = [("streak_3", streak>=3),("streak_7", streak>=7),("streak_14", streak>=14),("streak_30", streak>=30),
              ("study_60", mins>=60),("study_300", mins>=300),("fc_10", fc_count>=10)]
    for badge_id, condition in checks:
        if condition and badge_id not in earned:
            award_badge(username, badge_id); award_xp(username, 50)

def add_flashcard(username, front, back, subject, chapter):
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("INSERT INTO flashcards(username,front_text,back_text,subject,chapter,ease_factor,interval_days,next_review_date,review_count,created_date) VALUES(?,?,?,?,?,2.5,1,?,0,?)", (username, front, back, subject, chapter, today, today))
    conn.commit(); conn.close()

def get_due_flashcards(username):
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT id,front_text,back_text,subject,chapter,ease_factor,interval_days,review_count FROM flashcards WHERE username=? AND (next_review_date<=? OR next_review_date IS NULL) ORDER BY next_review_date", (username, today))
    rows = c.fetchall(); conn.close(); return rows

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT id,front_text,back_text,subject,chapter,next_review_date,review_count FROM flashcards WHERE username=? ORDER BY id DESC", (username,))
    rows = c.fetchall(); conn.close(); return rows

def update_flashcard_review(card_id, quality):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT ease_factor,interval_days FROM flashcards WHERE id=?", (card_id,)); row = c.fetchone()
    if not row: conn.close(); return
    ef, iv = row
    if quality == 5: ef = min(3.0, ef + 0.1); iv = max(1, int(iv * ef))
    elif quality == 3: iv = max(1, int(iv * 1.2))
    else: ef = max(1.3, ef - 0.2); iv = 1
    next_date = (datetime.date.today() + datetime.timedelta(days=iv)).isoformat()
    c.execute("UPDATE flashcards SET ease_factor=?,interval_days=?,next_review_date=?,review_count=review_count+1 WHERE id=?", (ef, iv, next_date, card_id))
    conn.commit(); conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,)); conn.commit(); conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# AI GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(title, content, profile):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#1d4ed8"), spaceAfter=10, alignment=TA_CENTER)
    body_style  = ParagraphStyle("Body2", parent=styles["Normal"], fontSize=11, leading=17, textColor=colors.black)
    sub_style   = ParagraphStyle("Sub2", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#64748b"), alignment=TA_CENTER)
    story = [Paragraph("StudySmart AI", title_style), Paragraph(f"{profile.get('category','')} · {profile.get('course','')} · {profile.get('board','')}", sub_style), Spacer(1, 0.3*cm), HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb")), Spacer(1, 0.3*cm), Paragraph(title, title_style), Spacer(1, 0.4*cm)]
    for line in content.split("\n"):
        line = line.strip()
        if not line: story.append(Spacer(1, 0.2*cm)); continue
        if line.startswith("##"): story.append(Paragraph(f"<b>{line.replace('##','').strip()}</b>", ParagraphStyle("H2", parent=styles["Normal"], fontSize=13, textColor=colors.HexColor("#1e40af"), spaceBefore=8, spaceAfter=4)))
        elif line.startswith("#"): story.append(Paragraph(f"<b>{line.replace('#','').strip()}</b>", ParagraphStyle("H1", parent=styles["Normal"], fontSize=14, textColor=colors.HexColor("#1d4ed8"), spaceBefore=10, spaceAfter=5)))
        elif line.startswith(("- ","* ","• ")): story.append(Paragraph(f"• {line[2:].strip()}", body_style))
        else: story.append(Paragraph(line.replace("**","<b>").replace("**","</b>"), body_style))
    doc.build(story); buf.seek(0); return buf.read()

def generate_ai_content(prompt_type, details):
    if not configure_gemini(): return "⚠️ Gemini API key not found in Streamlit Secrets."
    try: model = genai.GenerativeModel(get_available_models()[0])
    except Exception as e: return f"❌ Model init error: {e}"
    ctx = f"Level: {details.get('category','')} - {details.get('course','')} ({details.get('stream','')})\nBoard: {details.get('board','')}\nSubject: {details.get('subject','')}\nTopic: {details.get('topic','')}\nChapter: {details.get('chapter','')}"
    prompts = {
        "notes": f"Act as an expert teacher. Write detailed study notes using markdown (bullet points, bold text). End with a Summary.\nContext:\n{ctx}",
        "quiz": f"Generate 5 MCQs for practice. Format: Q1. [Question] \n A).. B).. \n Correct: [] \n Expl: []\nContext:\n{ctx}",
        "roadmap": f"Create a 7-day realistic exam revision roadmap. Focus on active recall.\nContext:\n{ctx}",
        "qpaper": f"Generate a question paper: 5 MCQs (1m), 5 Short Ans (3m), 2 Long Ans (5m). Add ANSWER KEY at the end.\nContext:\n{ctx}",
        "qa": f"Answer this question clearly and deeply.\nContext:\n{ctx}\nQuestion: {details.get('custom_question', '')}"
    }
    try:
        return model.generate_content(prompts.get(prompt_type, prompts["notes"])).text
    except Exception as e: return f"❌ AI Error: {e}"

# ─────────────────────────────────────────────────────────────────────────────
# UI ROUTING & HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    for k, v in {"logged_in": False, "username": "", "active_page": "dashboard", "daily_checkin_done": False, "study_timer_active": False, "study_timer_start": None, "current_subject_for_timer": "General", "history": [], "fc_review_index": 0, "fc_show_answer": False}.items():
        if k not in st.session_state: st.session_state[k] = v

def go_to(page): st.session_state.active_page = page; st.rerun()
def do_logout(): 
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def render_header(title, subtitle=""):
    st.markdown(f'<div class="sf-hero"><div class="sf-hero-title">{title}</div><div class="sf-hero-sub">{subtitle}</div></div>', unsafe_allow_html=True)

def render_back_button():
    if st.button("← Back to Dashboard"): go_to("dashboard")

# ─────────────────────────────────────────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="sf-hero"><div class="sf-hero-title">StudySmart AI 🎓</div><div class="sf-hero-sub">Your Personal AI Exam Preparation Partner</div></div><br>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
        with tab1:
            with st.form("login_form"):
                u = st.text_input("👤 Username")
                p = st.text_input("🔑 Password", type="password")
                if st.form_submit_button("Sign In 🚀", use_container_width=True):
                    if login_user(u, p):
                        st.session_state.update({"logged_in": True, "username": u.strip()})
                        st.success("✅ Welcome back!")
                        time.sleep(0.4); st.rerun()
                    else: st.error("❌ Invalid credentials.")
        with tab2:
            with st.form("register_form"):
                nu = st.text_input("👤 Choose Username", placeholder="Min 3 characters")
                np = st.text_input("🔑 Choose Password", type="password", placeholder="Min 6 characters")
                if st.form_submit_button("Create Account ✨", use_container_width=True):
                    ok, msg = register_user(nu, np)
                    if ok: st.success(msg)
                    else: st.error(msg)

def show_onboarding(username):
    render_header("Welcome! 👋", "Let's personalise your study experience")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### 📋 Your Academic Profile")
        category = st.selectbox("📂 Category", list(CATEGORY_META.keys()))
        course   = st.selectbox("📚 Course", get_courses(category) or ["General"])
        stream   = st.selectbox("🎯 Stream", get_streams(category, course) or ["General"])
        board    = st.selectbox("🏫 Board", BOARDS)
    with c2:
        st.markdown("### 📖 What you'll get")
        st.markdown(f'<div class="sf-card" style="text-align:center;"><h1>{CATEGORY_META.get(category, {}).get("icon", "🎓")}</h1><h4>{category}</h4><p class="text-muted">{CATEGORY_META.get(category, {}).get("desc", "")}</p><hr><p>📝 AI Notes &nbsp;•&nbsp; 🧠 Smart Quizzes &nbsp;•&nbsp; 📅 Roadmaps</p></div>', unsafe_allow_html=True)
    if st.button("✅ Save Profile & Start Learning →", use_container_width=True):
        save_profile(username, category, course, stream, board)
        award_badge(username, "onboarded"); award_badge(username, "first_login"); award_xp(username, 50)
        st.success("🎉 Profile saved!"); time.sleep(0.5); st.rerun()

def render_sidebar(username):
    profile = get_user_profile(username); stats = get_user_stats(username)
    with st.sidebar:
        st.markdown(f"### 👋 {username}")
        if profile.get("course"): st.caption(f"📚 {profile['course']} · {profile['board']}")
        
        c1, c2 = st.columns(2)
        c1.markdown(f'<div style="background:linear-gradient(135deg,#f59e0b,#d97706);border-radius:10px;color:white;text-align:center;padding:10px;">🔥 <b>{stats["streak_days"]}</b><br><small>Streak</small></div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="background:linear-gradient(135deg,#8b5cf6,#7c3aed);border-radius:10px;color:white;text-align:center;padding:10px;">⭐ <b>Lv {stats["level"]}</b><br><small>{stats["total_xp"]} XP</small></div>', unsafe_allow_html=True)
        st.write("")

        if not st.session_state.daily_checkin_done:
            if st.button("✅ Daily Check-in (+20 XP)", use_container_width=True):
                st.success(check_daily_login(username).get("message")); st.session_state.daily_checkin_done = True; auto_check_badges(username); st.rerun()
        
        st.divider()
        st.markdown("**⏱️ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed = int((datetime.datetime.now() - st.session_state.study_timer_start).total_seconds() // 60)
            st.info(f"🟢 Running: {elapsed} min")
            if st.button("⏹️ Stop & Save", use_container_width=True):
                record_study_session(username, st.session_state.get("current_subject_for_timer","General"), max(1, elapsed))
                st.session_state.study_timer_active = False; st.session_state.study_timer_start = None
                award_xp(username, max(5, (max(1, elapsed)//10)*10)); st.rerun()
        else:
            if st.button("▶️ Start Timer", use_container_width=True):
                st.session_state.study_timer_active = True; st.session_state.study_timer_start = datetime.datetime.now(); st.rerun()

        st.divider()
        st.markdown("**🧭 Menu**")
        for key, lbl in [("dashboard","📊 Dashboard"),("study","📚 Study Tools"),("flashcards","🗂️ Flashcards"),("achievements","🏅 Achievements")]:
            if st.button(lbl, use_container_width=True, type="primary" if st.session_state.active_page == key else "secondary"): go_to(key)

        if stats["flashcards_due"] > 0: st.warning(f"📚 {stats['flashcards_due']} cards due!")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True): do_logout()

def show_dashboard(username):
    render_header("StudySmart Dashboard", "Your Learning Hub")
    stats = get_user_stats(username); profile = get_user_profile(username)

    st.markdown('<div class="mc-grid">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="mc mc-blue"><div class="icon">🔥</div><div class="val">{stats["streak_days"]}</div><div class="lbl">Day Streak</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mc mc-green"><div class="icon">⭐</div><div class="val">Lv {stats["level"]}</div><div class="lbl">Level Progress</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mc mc-purple"><div class="icon">📚</div><div class="val">{stats["flashcards_due"]}</div><div class="lbl">Cards Due</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="mc mc-amber"><div class="icon">⏱️</div><div class="val">{stats["weekly_study_minutes"]}</div><div class="lbl">Mins This Week</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    lp = stats["level_progress"]; pct = min(100, int((lp/500)*100))
    st.markdown(f'<b>⭐ Level {stats["level"]}</b> <span style="float:right;">{lp}/500 XP</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="xp-wrap"><div class="xp-fill" style="width:{pct}%;"></div></div><small class="text-muted">{500-lp} XP to Level {stats["level"]+1}</small>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Actions")
    qa1, qa2, qa3 = st.columns(3)
    if qa1.button("📝 AI Notes", use_container_width=True): go_to("study")
    if qa2.button("🧠 Take Quiz", use_container_width=True): go_to("study")
    if qa3.button("🗂️ Flashcards", use_container_width=True): go_to("flashcards")

def show_study_tools(username):
    render_back_button()
    render_header("Study Tools 🧠", "AI-powered exam preparation")
    profile = get_user_profile(username)

    st.markdown("### 🔍 Select Topic")
    s1, s2, s3 = st.columns(3)
    with s1: sel_subj = st.selectbox("📖 Subject", get_subjects(profile["category"], profile["course"], profile["stream"]) or ["General"])
    with s2: sel_topic = st.selectbox("📌 Topic", get_topics(profile["category"], profile["course"], profile["stream"], sel_subj) or ["All"])
    with s3: sel_chap = st.selectbox("📑 Chapter", get_chapters(profile["category"], profile["course"], profile["stream"], sel_subj, sel_topic) or ["Introduction"])

    details = {**profile, "subject": sel_subj, "topic": sel_topic, "chapter": sel_chap}
    st.divider()

    tool = st.radio("🛠️ Choose Tool", ["📝 Smart Notes", "🧠 Quiz", "🧪 Question Paper", "📅 Roadmap", "❓ Ask AI"], horizontal=True)
    
    if st.button(f"✨ Generate {tool}", use_container_width=True):
        with st.spinner("AI is generating content..."):
            prompt_key = "notes" if "Notes" in tool else "quiz" if "Quiz" in tool else "qpaper" if "Paper" in tool else "roadmap" if "Roadmap" in tool else "qa"
            res = generate_ai_content(prompt_key, details)
            
            st.markdown('<div class="sf-output">', unsafe_allow_html=True)
            st.markdown(res)
            st.markdown('</div>', unsafe_allow_html=True)

            if tool in ["📝 Smart Notes", "🧪 Question Paper", "📅 Roadmap"]:
                pdf = generate_pdf(f"{tool}: {sel_chap}", res, profile)
                st.download_button("📥 Download PDF", pdf, f"{sel_chap}_{prompt_key}.pdf", "application/pdf")
            
            award_xp(username, 10); award_badge(username, "first_gen")

def show_flashcards(username):
    render_back_button()
    render_header("Flashcards 🗂️", "Spaced repetition memory")
    t1, t2, t3 = st.tabs(["📖 Review Due", "➕ Create", "📋 Library"])

    with t1:
        due = get_due_flashcards(username)
        if not due: st.success("🎉 All caught up for today!")
        else:
            card = due[st.session_state.fc_review_index % len(due)]
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown(f"### ❓ {card[2]}")
            if st.session_state.fc_show_answer:
                st.divider(); st.markdown(f"**✅ Answer:** {card[3]}"); st.markdown('</div>', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                if c1.button("😓 Hard", use_container_width=True): update_flashcard_review(card[0], 1); st.session_state.fc_show_answer = False; st.session_state.fc_review_index += 1; st.rerun()
                if c2.button("😐 Good", use_container_width=True): update_flashcard_review(card[0], 3); st.session_state.fc_show_answer = False; st.session_state.fc_review_index += 1; st.rerun()
                if c3.button("😊 Easy", use_container_width=True): update_flashcard_review(card[0], 5); st.session_state.fc_show_answer = False; st.session_state.fc_review_index += 1; st.rerun()
            else:
                st.markdown('</div>', unsafe_allow_html=True)
                if st.button("👁️ Show Answer", use_container_width=True): st.session_state.fc_show_answer = True; st.rerun()

    with t2:
        with st.form("new_fc"):
            front = st.text_area("Question"); back = st.text_area("Answer")
            if st.form_submit_button("💾 Save Card", use_container_width=True):
                add_flashcard(username, front, back, "General", "General")
                st.success("✅ Card saved!"); award_xp(username, 5); auto_check_badges(username); time.sleep(0.5); st.rerun()
    with t3:
        cards = get_all_flashcards(username)
        for c in cards:
            with st.expander(f"📌 {c[1][:50]}"):
                st.write(c[2]); 
                if st.button("🗑️ Delete", key=f"del_{c[0]}"): delete_flashcard(c[0]); st.rerun()

def show_achievements(username):
    render_back_button()
    render_header("Achievements 🏅", "Your Trophy Room")
    earned = get_earned_badges(username)
    e_list = [b for b in ALL_BADGES if b["id"] in earned]; l_list = [b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown(f"### 🏆 Earned ({len(e_list)}/{len(ALL_BADGES)})")
    if e_list:
        cols = st.columns(4)
        for i, b in enumerate(e_list):
            with cols[i%4]: st.markdown(f'<div class="bdg"><div class="bi">{b["icon"]}</div><div class="bn">{b["name"]}</div><div class="bs">{b["desc"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("### 🔒 Locked")
    cols = st.columns(4)
    for i, b in enumerate(l_list):
        with cols[i%4]: st.markdown(f'<div class="bdg"><div class="bi" style="opacity:0.3;">🔒</div><div class="bn">{b["name"]}</div><div class="bs">{b["desc"]}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BOOTSTRAP
# ─────────────────────────────────────────────────────────────────────────────
def main_app():
    username = st.session_state.username
    if not get_user_profile(username)["onboarded"]: show_onboarding(username); return
    render_sidebar(username)
    pages = {"dashboard": show_dashboard, "study": show_study_tools, "flashcards": show_flashcards, "achievements": show_achievements}
    pages.get(st.session_state.active_page, show_dashboard)(username)

init_db()
init_session_state()
if st.session_state.logged_in: main_app()
else: auth_ui()
