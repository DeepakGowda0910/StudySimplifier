# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — app.py  (Complete Fixed Version)
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

from daily_engagement import (
    init_enhanced_db,
    check_daily_login,
    get_user_stats,
    record_study_session,
    award_xp,
    award_badge
)

# ── Page config — MUST be first Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_study_data():
    try:
        with open(Path("data/study_data.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ data/study_data.json not found!")
        return {}
    except json.JSONDecodeError:
        st.error("❌ study_data.json is not valid JSON!")
        return {}

STUDY_DATA  = load_study_data()
BOARDS      = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge"]

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 1200px;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(160deg, #f8fbff 0%, #eef3fb 60%, #e8f0fa 100%) !important;
}

/* ── Hero Header ── */
.sf-hero {
    text-align: center;
    padding: 18px 0 6px 0;
}
.sf-hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}
.sf-hero-sub {
    color: #64748b;
    font-size: 0.97rem;
    font-weight: 500;
    margin-top: 4px;
}
.sf-powered {
    display: inline-block;
    margin-top: 8px;
    padding: 4px 14px;
    border-radius: 999px;
    background: rgba(37,99,235,0.09);
    color: #2563eb;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.1em;
}

/* ── Cards ── */
.sf-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: 0 4px 20px rgba(15,23,42,0.05);
}
.sf-soft-card {
    background: linear-gradient(160deg,#f8fbff,#f1f5f9);
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 16px;
}

/* ── Metric cards ── */
.mc {
    border-radius: 14px;
    padding: 16px 14px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.10);
    margin-bottom: 8px;
}
.mc-blue   { background: linear-gradient(135deg,#3b82f6,#1d4ed8); }
.mc-green  { background: linear-gradient(135deg,#10b981,#059669); }
.mc-purple { background: linear-gradient(135deg,#8b5cf6,#7c3aed); }
.mc-amber  { background: linear-gradient(135deg,#f59e0b,#d97706); }
.mc .icon  { font-size: 1.3rem; }
.mc .val   { font-size: 1.55rem; font-weight: 800; margin: 3px 0; }
.mc .lbl   { font-size: 0.78rem; opacity: 0.92; }

/* ── XP Bar ── */
.xp-wrap { background:#e2e8f0; border-radius:999px; height:10px; overflow:hidden; }
.xp-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,#3b82f6,#8b5cf6); }

/* ── History item ── */
.sf-hist {
    background: #f8fbff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 9px 12px;
    margin-bottom: 8px;
    font-size: 0.86rem;
}
.sf-hist b     { color: #1d4ed8; }
.sf-hist small { color: #64748b; }

/* ── Output boxes ── */
.sf-output {
    background: #f0f6ff;
    border: 1px solid #bfdbfe;
    border-left: 4px solid #2563eb;
    border-radius: 14px;
    padding: 20px 22px;
    margin-top: 12px;
}
.sf-output h1,.sf-output h2,.sf-output h3 { color:#1d4ed8 !important; }
.sf-output p,.sf-output li,.sf-output strong { color:#1e293b !important; }

.sf-answers {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #16a34a;
    border-radius: 14px;
    padding: 20px 22px;
    margin-top: 14px;
}
.sf-answers h1,.sf-answers h2,.sf-answers h3 { color:#15803d !important; }
.sf-answers p,.sf-answers li,.sf-answers strong { color:#1e293b !important; }

.sf-fullpaper {
    background: #faf5ff;
    border: 1px solid #ddd6fe;
    border-left: 4px solid #7c3aed;
    border-radius: 14px;
    padding: 20px 22px;
    margin-top: 14px;
}
.sf-fullpaper h1,.sf-fullpaper h2,.sf-fullpaper h3 { color:#6d28d9 !important; }
.sf-fullpaper p,.sf-fullpaper li,.sf-fullpaper strong { color:#1e293b !important; }

/* ── Flashcards ── */
.fc-front {
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    border-radius: 16px; padding: 28px 22px;
    color: white; text-align: center; min-height: 170px;
    box-shadow: 0 10px 26px rgba(79,70,229,0.28);
}
.fc-back {
    background: linear-gradient(135deg,#059669,#10b981);
    border-radius: 16px; padding: 28px 22px;
    color: white; text-align: center; min-height: 170px;
    box-shadow: 0 10px 26px rgba(16,185,129,0.24);
}

/* ── Badge cards ── */
.bdg {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 14px 10px;
    text-align: center; margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(15,23,42,0.04);
}
.bdg.earned { border-color: #f59e0b; background: #fffbeb; }
.bdg .bi  { font-size: 2rem; }
.bdg .bn  { font-weight: 700; font-size: 0.84rem; color: #0f172a; margin-top: 5px; }
.bdg .bs  { font-size: 0.74rem; color: #64748b; margin-top: 3px; }

/* ── Nav buttons (sidebar) ── */
.nav-btn {
    width: 100%; padding: 10px 14px; margin-bottom: 6px;
    border-radius: 10px; border: 1.5px solid #e2e8f0;
    background: #f8fbff; color: #334155;
    font-weight: 600; font-size: 0.9rem;
    cursor: pointer; text-align: left;
    transition: all 0.15s ease;
}
.nav-btn.active, .nav-btn:hover {
    background: #eff6ff; border-color: #bfdbfe; color: #1d4ed8;
}

/* ── Form inputs ── */
[data-testid="stWidgetLabel"] p { color:#1e293b !important; font-weight:700 !important; font-size:0.87rem !important; }
div[data-baseweb="select"] > div:first-child {
    border: 1.5px solid #cbd5e1 !important; border-radius: 11px !important;
    background: #ffffff !important; min-height: 42px !important;
}
div[data-baseweb="select"] > div > div > div { color: #1e293b !important; }
div[data-baseweb="select"] svg { fill: #64748b !important; display: block !important; visibility: visible !important; opacity: 1 !important; }
div[data-baseweb="popover"] { background: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 11px !important; box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important; }
div[role="option"] { color: #1e293b !important; background: #ffffff !important; }
div[role="option"]:hover { background: #eff6ff !important; color: #1d4ed8 !important; }

/* ── Buttons ── */
.stButton > button, .stFormSubmitButton > button {
    border: none !important; border-radius: 11px !important;
    background: linear-gradient(135deg,#3b82f6,#2563eb) !important;
    color: #ffffff !important; font-weight: 700 !important;
    padding: 0.6rem 1.1rem !important;
    box-shadow: 0 6px 16px rgba(37,99,235,0.2) !important;
    transition: all 0.16s ease !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 10px 22px rgba(37,99,235,0.28) !important; }
.stDownloadButton > button {
    border: none !important; border-radius: 11px !important;
    background: linear-gradient(135deg,#10b981,#059669) !important;
    color: white !important; font-weight: 700 !important;
    box-shadow: 0 6px 16px rgba(16,185,129,0.2) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
[data-testid="stSidebar"] * { color: #1e293b !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #e2e8f0 !important; }
.stTabs [data-baseweb="tab"]      { color: #64748b !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"]    { color: #1e293b !important; border-bottom: 3px solid #3b82f6 !important; }

/* ── Alerts ── */
div[data-testid="stSuccessMessage"],
div[data-testid="stWarningMessage"],
div[data-testid="stErrorMessage"] { border-radius: 11px !important; }

/* ── Dark mode ── */
[data-theme="dark"] .stApp { background: linear-gradient(160deg,#0f172a,#111827) !important; }
[data-theme="dark"] .sf-card,.sf-soft-card { background: #1e293b !important; border-color: #334155 !important; }
[data-theme="dark"] .sf-hist { background: #1e293b !important; }
[data-theme="dark"] [data-testid="stSidebar"] { background: #0f172a !important; border-right-color: #334155 !important; }
[data-theme="dark"] div[data-baseweb="select"] > div:first-child { background: #1e293b !important; border-color: #475569 !important; }
[data-theme="dark"] div[data-baseweb="select"] > div > div > div { color: #e2e8f0 !important; }
[data-theme="dark"] div[data-baseweb="select"] svg { fill: #94a3b8 !important; }
[data-theme="dark"] div[data-baseweb="popover"] { background: #1e293b !important; border-color: #334155 !important; }
[data-theme="dark"] div[role="option"] { background: #1e293b !important; color: #e2e8f0 !important; }
[data-theme="dark"] div[role="option"]:hover { background: #334155 !important; }
[data-theme="dark"] .bdg { background: #1e293b !important; border-color: #334155 !important; }
[data-theme="dark"] .bdg.earned { background: #1c1917 !important; }
[data-theme="dark"] .bdg .bn { color: #f1f5f9 !important; }
[data-theme="dark"] .sf-hero-title { background: linear-gradient(135deg,#60a5fa,#3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* ── Mobile ── */
@media (max-width: 768px) {
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    .sf-hero-title   { font-size: 2rem !important; }
    .sf-card         { padding: 14px 12px !important; }
    .mc              { padding: 14px 10px !important; }
    .mc .val         { font-size: 1.3rem !important; }
    .fc-front,.fc-back { min-height: 140px !important; padding: 20px 14px !important; }
}
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        # Auth
        "logged_in": False,
        "username": "",

        # ── Navigation: single source of truth ──────────────────────────────
        # Values: "dashboard" | "study" | "flashcards" | "achievements"
        "active_page": "dashboard",

        # History
        "history": [],

        # Study tool selections
        "current_chapters": [],
        "last_chapter_key": "",

        # Generated content
        "generated_result":       None,
        "generated_model":        None,
        "generated_label":        None,
        "generated_tool":         None,
        "generated_chapter":      None,
        "generated_subject":      None,
        "generated_topic":        None,
        "generated_course":       None,
        "generated_stream":       None,
        "generated_board":        None,
        "generated_audience":     None,
        "generated_output_style": None,

        # Answers / full paper
        "answers_result":   None,
        "answers_model":    None,
        "show_answers":     False,
        "fullpaper_result": None,
        "fullpaper_model":  None,
        "show_fullpaper":   False,

        # Engagement
        "daily_checkin_done":         False,
        "study_timer_active":         False,
        "study_timer_start":          None,
        "current_subject_for_timer":  "General",

        # Flashcard review
        "review_idx":      0,
        "review_show_ans": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION HELPER  ← THE KEY FIX
# All navigation goes through this one function.
# No st.rerun() inside the sidebar — only here.
# ─────────────────────────────────────────────────────────────────────────────
def go_to(page: str):
    """
    Set active_page and trigger a rerun.
    Call this from ANY button or nav element.
    page: 'dashboard' | 'study' | 'flashcards' | 'achievements'
    """
    st.session_state.active_page = page
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STUDY DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_courses(category):
    try:    return list(STUDY_DATA[category].keys())
    except: return []

def get_streams(category, course):
    try:    return list(STUDY_DATA[category][course].keys())
    except: return []

def get_subjects(category, course, stream):
    try:    return list(STUDY_DATA[category][course][stream].keys())
    except: return []

def get_topics(category, course, stream, subject):
    try:    return list(STUDY_DATA[category][course][stream][subject].keys())
    except: return []

def get_chapters(category, course, stream, subject, topic):
    try:    return STUDY_DATA[category][course][stream][subject][topic]
    except: return ["No chapters found"]

# ─────────────────────────────────────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def hash_p(password):
    return hashlib.sha256(password.encode()).hexdigest()

def do_login(username, password):
    username = username.strip()
    if not username or not password.strip():
        return False, "⚠️ Please fill in both fields."
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_p(password)))
    user = c.fetchone()
    conn.close()
    return (True, username) if user else (False, "❌ Invalid username or password.")

# ─────────────────────────────────────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────────────────────────────────────
def add_to_history(label, chapter, subject, result_preview):
    entry = {
        "time":    time.strftime("%H:%M"),
        "tool":    label,
        "chapter": chapter,
        "subject": subject,
        "preview": result_preview[:120] + "..." if len(result_preview) > 120 else result_preview,
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:6]

# ─────────────────────────────────────────────────────────────────────────────
# AI MODEL UTILS
# ─────────────────────────────────────────────────────────────────────────────
def get_available_models():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ["Error: GEMINI_API_KEY not found"]
    try:
        genai.configure(api_key=api_key)
        working = []
        for m in genai.list_models():
            name    = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "gemini" in name.lower() and "generateContent" in methods:
                working.append(name)
        return working if working else ["No models available"]
    except Exception as e:
        return [f"Error: {e}"]

# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT LABEL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_effective_output_name(tool, output_style):
    if output_style == "🧪 Question Paper" or tool == "🧪 Question Paper":
        return "Question Paper"
    if tool == "📝 Summary":
        if output_style == "📋 Notes Format":  return "Notes"
        if output_style == "📄 Detailed":      return "Detailed Summary"
        if output_style == "⚡ Short & Quick": return "Quick Summary"
        return "Summary"
    if tool == "🧠 Quiz":           return "Quiz"
    if tool == "📌 Revision Notes": return "Revision Notes"
    if tool == "❓ Exam Q&A":       return "Exam Q&A"
    return "Content"

def get_button_label(tool, output_style):
    name  = get_effective_output_name(tool, output_style)
    icons = {"Question Paper":"🧪","Notes":"📋","Detailed Summary":"📄",
             "Quick Summary":"⚡","Summary":"📝","Quiz":"🧠",
             "Revision Notes":"📌","Exam Q&A":"❓"}
    return f"{icons.get(name,'✨')} Generate {name}"

def reset_generation_state():
    for k in ["generated_result","generated_model","generated_label","generated_tool",
              "generated_chapter","generated_subject","generated_topic","generated_course",
              "generated_stream","generated_board","generated_audience","generated_output_style",
              "answers_result","answers_model","fullpaper_result","fullpaper_model"]:
        st.session_state[k] = None
    st.session_state.show_answers   = False
    st.session_state.show_fullpaper = False

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD DB HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def save_flashcard(username, front, back, subject, chapter):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        INSERT INTO flashcards (username,front_text,back_text,subject,chapter,next_review_date)
        VALUES (?,?,?,?,?,?)
    """, (username, front, back, subject, chapter, today))
    conn.commit()
    conn.close()

def get_due_flashcards(username):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        SELECT id,front_text,back_text,subject,chapter,ease_factor,interval_days,review_count
        FROM flashcards
        WHERE username=? AND next_review_date<=?
        ORDER BY next_review_date ASC
    """, (username, today))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("""
        SELECT id,front_text,back_text,subject,chapter,next_review_date,review_count
        FROM flashcards WHERE username=? ORDER BY created_date DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_flashcard_review(card_id, performance):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("SELECT ease_factor,interval_days FROM flashcards WHERE id=?", (card_id,))
    row  = c.fetchone()
    if not row:
        conn.close()
        return
    ef, interval = row
    if performance == 1:
        interval = 1;          ef = max(1.3, ef - 0.2)
    elif performance == 2:
        interval = max(1, int(interval * 1.2)); ef = max(1.3, ef - 0.1)
    elif performance == 3:
        interval = max(1, int(interval * ef))
    elif performance == 4:
        interval = max(1, int(interval * ef * 1.3)); ef += 0.1
    next_review = (datetime.date.today() + datetime.timedelta(days=interval)).isoformat()
    c.execute("""
        UPDATE flashcards
        SET ease_factor=?,interval_days=?,next_review_date=?,review_count=review_count+1
        WHERE id=?
    """, (round(ef,2), interval, next_review, card_id))
    conn.commit()
    conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()

def get_earned_badges(username):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("SELECT badge_id FROM achievements WHERE username=?", (username,))
    ids  = {r[0] for r in c.fetchall()}
    conn.close()
    return ids

ALL_BADGES = [
    {"id":"first_login",  "name":"First Step",      "icon":"👣","desc":"Logged in for the first time"},
    {"id":"streak_3",     "name":"Heatwave",         "icon":"🔥","desc":"3-day study streak"},
    {"id":"streak_7",     "name":"Weekly Warrior",   "icon":"🎖️","desc":"7-day study streak"},
    {"id":"streak_14",    "name":"Fortnight Champ",  "icon":"🏆","desc":"14-day study streak"},
    {"id":"streak_30",    "name":"Monthly Master",   "icon":"👑","desc":"30-day study streak"},
    {"id":"first_gen",    "name":"Starter Spark",    "icon":"✨","desc":"Generated first AI content"},
    {"id":"qp_generated", "name":"Paper Setter",     "icon":"📝","desc":"Generated a question paper"},
    {"id":"quiz_done",    "name":"Quiz Taker",        "icon":"🧠","desc":"Generated a quiz"},
]
# ─────────────────────────────────────────────────────────────────────────────
# QP FORMAT SPECS
# ─────────────────────────────────────────────────────────────────────────────
def get_qp_format_spec(board, course, subject):
    b = board.upper()
    if "CBSE" in b:
        if any(x in course for x in ["10","X","Class 10"]):
            return {"board_label":"CENTRAL BOARD OF SECONDARY EDUCATION","exam_label":"BOARD EXAMINATION",
                    "class_label":"CLASS X","total_marks":80,"time":"3 Hours",
                    "instructions":["This paper contains Sections A, B, C, D and E.",
                                    "All questions are compulsory.",
                                    "Section A — MCQ (1 mark each).",
                                    "Section B — Very Short Answer (2 marks each).",
                                    "Section C — Short Answer (3 marks each).",
                                    "Section D — Long Answer (5 marks each).",
                                    "Section E — Case / Source Based (4 marks each)."],
                    "sections":[
                        {"name":"SECTION A","type":"MCQ","q_count":20,"marks_each":1,"total":20},
                        {"name":"SECTION B","type":"Very Short Answer","q_count":5,"marks_each":2,"total":10},
                        {"name":"SECTION C","type":"Short Answer","q_count":6,"marks_each":3,"total":18},
                        {"name":"SECTION D","type":"Long Answer","q_count":4,"marks_each":5,"total":20},
                        {"name":"SECTION E","type":"Case Based","q_count":3,"marks_each":4,"total":12},
                    ]}
        if any(x in course for x in ["12","XII","Class 12"]):
            return {"board_label":"CENTRAL BOARD OF SECONDARY EDUCATION","exam_label":"BOARD EXAMINATION",
                    "class_label":"CLASS XII","total_marks":70,"time":"3 Hours",
                    "instructions":["This paper contains Sections A, B, C, D and E.",
                                    "All questions are compulsory.",
                                    "Section A — MCQ (1 mark each).",
                                    "Section B — Very Short Answer (2 marks each).",
                                    "Section C — Short Answer (3 marks each).",
                                    "Section D — Long Answer (5 marks each).",
                                    "Section E — Case / Source Based (4 marks each)."],
                    "sections":[
                        {"name":"SECTION A","type":"MCQ","q_count":18,"marks_each":1,"total":18},
                        {"name":"SECTION B","type":"Very Short Answer","q_count":4,"marks_each":2,"total":8},
                        {"name":"SECTION C","type":"Short Answer","q_count":5,"marks_each":3,"total":15},
                        {"name":"SECTION D","type":"Long Answer","q_count":2,"marks_each":5,"total":10},
                        {"name":"SECTION E","type":"Case Based","q_count":3,"marks_each":4,"total":12},
                    ]}
    if "ICSE" in b:
        return {"board_label":"COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
                "exam_label":"ICSE EXAMINATION","class_label":course.upper(),
                "total_marks":80,"time":"2 Hours",
                "instructions":["Attempt all from Section A.","Attempt any four from Section B.","Marks in brackets."],
                "sections":[
                    {"name":"SECTION A","type":"Compulsory","q_count":10,"marks_each":"varied","total":40},
                    {"name":"SECTION B","type":"Descriptive","q_count":6,"marks_each":10,"total":40},
                ]}
    return {"board_label":"UNIVERSITY EXAMINATIONS",
            "exam_label":f"{course.upper()} EXAMINATION","class_label":course.upper(),
            "total_marks":100,"time":"3 Hours",
            "instructions":["Answer all in Section A.","Answer any five from Section B.","Marks in brackets."],
            "sections":[
                {"name":"SECTION A","type":"Short Answer","q_count":10,"marks_each":2,"total":20},
                {"name":"SECTION B","type":"Medium Answer","q_count":8,"marks_each":5,"total":40},
                {"name":"SECTION C","type":"Long Answer","q_count":4,"marks_each":10,"total":40},
            ]}

# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────────────
def build_qp_prompt(board, course, subject, chapter, topic, audience):
    fmt   = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
    secs  = "\n".join([f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}" for s in fmt["sections"]])
    return f"""You are an official academic question paper setter.
Generate a CHAPTER-LEVEL question paper.
BOARD: {fmt['board_label']} | EXAM: {fmt['exam_label']} | CLASS: {fmt['class_label']}
SUBJECT: {subject} | TOPIC: {topic} | CHAPTER: {chapter}
TIME: {fmt['time']} | MARKS: {fmt['total_marks']}
INSTRUCTIONS:\n{instr}
STRUCTURE:\n{secs}
RULES: Follow structure exactly. Number all questions. MCQs have (a)(b)(c)(d). Show marks [X]. No answers included.
Generate the complete paper now."""

def build_full_qp_prompt(board, course, stream, subject, audience):
    fmt   = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
    secs  = "\n".join([f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}" for s in fmt["sections"]])
    return f"""You are an official academic question paper setter.
Generate a FULL SUBJECT question paper (entire syllabus).
BOARD: {fmt['board_label']} | STREAM: {stream} | SUBJECT: {subject}
TIME: {fmt['time']} | MARKS: {fmt['total_marks']}
INSTRUCTIONS:\n{instr}
STRUCTURE:\n{secs}
RULES: Cover full syllabus. No answers. Official academic format.
Generate the complete paper now."""

def build_answers_prompt(qp_text, board, course, subject, chapter):
    return f"""You are preparing the official answer key.
BOARD: {board} | COURSE: {course} | SUBJECT: {subject} | CHAPTER: {chapter}
RULES: Answer only the questions in the paper below. Keep same section names and numbering.
MCQs: correct option + brief explanation. Short: concise. Long: complete.
QUESTION PAPER:\n{qp_text}\nGenerate the answer key now."""

def build_prompt(tool, chapter, topic, subject, audience, output_style, board="", course=""):
    if output_style == "🧪 Question Paper" or tool == "🧪 Question Paper":
        return build_qp_prompt(board, course, subject, chapter, topic, audience)
    base = f"You are an expert educator for {audience}.\nSubject: {subject} | Topic: {topic} | Chapter: {chapter}\nMake it accurate, exam-oriented and structured.\n\n"
    if tool == "📝 Summary":
        if output_style == "📄 Detailed":
            return base + "Create a detailed summary: overview, key concepts, definitions, formulas, 2 examples, common mistakes, exam tips."
        if output_style == "⚡ Short & Quick":
            return base + "Create a quick-reference summary: one-line definition, 5-7 key points, formulas, quick tips. Max 500 words."
        if output_style == "📋 Notes Format":
            return base + "Create structured notes: clear headings, bullets, definitions, examples, revision points."
    if tool == "🧠 Quiz":
        return base + "Create: 5 MCQs with 4 options (mark answer), 5 short-answer Q&As, 3 long-answer Q&As."
    if tool == "📌 Revision Notes":
        return base + "Create revision notes: top 10 must-know points, formula sheet, mnemonics, comparisons, exam focus areas."
    if tool == "❓ Exam Q&A":
        return base + "Create exam Q&A bank: 8-10 frequently asked Qs with answers, conceptual Qs, application Qs, why/how Qs."
    return base + "Create complete exam-ready study material."

def build_flashcard_prompt(subject, chapter, topic):
    return f"""Create exactly 10 study flashcards.
Subject: {subject} | Chapter: {chapter} | Topic: {topic}
Format EXACTLY as:
CARD 1
FRONT: ...
BACK: ...
CARD 2
FRONT: ...
BACK: ...
(continue for all 10 cards — no extra text)"""

# ─────────────────────────────────────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY","")
    if not api_key:
        return ("⚠️ API key missing! Add GEMINI_API_KEY to .streamlit/secrets.toml", "None")
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Gemini config failed: {e}", "None")
    try:
        available = [m.name for m in genai.list_models()
                     if "gemini" in m.name.lower() and "generateContent" in getattr(m,"supported_generation_methods",[])]
    except Exception as e:
        return (f"❌ Could not list models: {e}", "None")
    if not available:
        return ("❌ No Gemini models available.", "None")
    for model_name in available:
        try:
            model    = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.0, max_output_tokens=8192, top_p=0.9)
            )
            if response and getattr(response,"text",None):
                return response.text, model_name
        except Exception:
            continue
    return ("❌ All models failed.", "None")

def parse_flashcards(raw_text):
    cards  = []
    blocks = raw_text.strip().split("CARD ")
    for block in blocks:
        if not block.strip(): continue
        front = back = ""
        for line in block.splitlines():
            l = line.strip()
            if l.upper().startswith("FRONT:"): front = l[6:].strip()
            elif l.upper().startswith("BACK:"): back  = l[5:].strip()
        if front and back:
            cards.append({"front": front, "back": back})
    return cards

# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(title, subtitle, content, color_hex="#1d4ed8"):
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
             topMargin=2*cm, bottomMargin=2*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story  = []
    story.append(Paragraph(title, ParagraphStyle("T", parent=styles["Heading1"],
        fontSize=20, textColor=colors.HexColor(color_hex), alignment=TA_CENTER,
        spaceAfter=6, fontName="Helvetica-Bold")))
    story.append(Paragraph(subtitle, ParagraphStyle("S", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#64748b"), alignment=TA_CENTER, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(color_hex), spaceAfter=14))
    body = ParagraphStyle("B", parent=styles["Normal"], fontSize=10.5, leading=15,
        textColor=colors.HexColor("#1e293b"), spaceAfter=5)
    head = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12.5,
        textColor=colors.HexColor(color_hex), spaceBefore=10, spaceAfter=6, fontName="Helvetica-Bold")
    for line in content.split("\n"):
        line = line.strip()
        if not line: story.append(Spacer(1,0.15*cm)); continue
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if line.startswith(("#","##","###")):
            story.append(Paragraph(line.lstrip("#").strip(), head))
        else:
            story.append(Paragraph(safe, body))
    story.append(Spacer(1,0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=5))
    story.append(Paragraph(f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle("F", parent=styles["Normal"], fontSize=8,
        textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)))
    doc.build(story)
    buffer.seek(0)
    return buffer
# ─────────────────────────────────────────────────────────────────────────────
# HEADER RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_header(title, subtitle):
    st.markdown(f"""
        <div class="sf-hero">
            <div class="sf-hero-title">{title}</div>
            <div class="sf-hero-sub">{subtitle}</div>
            <div class="sf-powered">POWERED BY AI</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR  ← NO st.rerun() inside here — navigation handled via go_to()
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(username):
    stats = get_user_stats(username) or {}

    with st.sidebar:

        # Brand
        st.markdown(f"""
            <div style="text-align:center;padding:12px 0 10px 0;">
                <div style="font-size:2.2rem;">🎓</div>
                <div style="font-size:1.1rem;font-weight:800;color:#2563eb;">StudySmart AI</div>
                <div style="font-size:0.8rem;color:#64748b;margin-top:3px;">Hi, {username} 👋</div>
            </div>
        """, unsafe_allow_html=True)

        # Streak + Level chips
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div style="text-align:center;padding:8px;background:linear-gradient(135deg,#ff6b6b,#feca57);
                     border-radius:10px;color:white;font-weight:800;font-size:0.9rem;">
                    🔥 {stats.get('streak_days',0)}<br>
                    <span style="font-size:0.68rem;font-weight:500;">day streak</span>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div style="text-align:center;padding:8px;background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                     border-radius:10px;color:white;font-weight:800;font-size:0.9rem;">
                    ⭐ Lv {stats.get('level',1)}<br>
                    <span style="font-size:0.68rem;font-weight:500;">{stats.get('total_xp',0)} XP</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # Daily check-in
        if not st.session_state.daily_checkin_done:
            if st.button("✅ Daily Check-in  (+20 XP)", use_container_width=True, key="sidebar_checkin"):
                result = check_daily_login(username)
                st.session_state.daily_checkin_done = True
                st.success(result.get("message","Checked in!"))
        else:
            st.success(f"✅ Checked in · 🔥 {stats.get('streak_days',0)} day streak")

        st.divider()

        # Study Timer
        st.markdown("**⏱️ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed = int((datetime.datetime.now() - st.session_state.study_timer_start).total_seconds() // 60)
            st.info(f"🟢 Running: {elapsed} min")
            if st.button("⏹️ Stop & Save", use_container_width=True, key="sidebar_stop_timer"):
                st.session_state.study_timer_active = False
                dur  = max(1, elapsed)
                subj = st.session_state.get("current_subject_for_timer","General")
                record_study_session(username, subj, "study", dur)
                award_xp(username, max(5, (dur//10)*10))
                st.session_state.study_timer_start = None
                st.success(f"✅ {dur} min recorded!")
        else:
            if st.button("▶️ Start Study Timer", use_container_width=True, key="sidebar_start_timer"):
                st.session_state.study_timer_active = True
                st.session_state.study_timer_start  = datetime.datetime.now()
                st.info("Timer running...")

        st.divider()

        # ── NAVIGATION — uses go_to(), no competing reruns ─────────────────
        st.markdown("**🧭 Navigate**")

        current = st.session_state.active_page

        nav_items = [
            ("dashboard",     "📊 Dashboard"),
            ("study",         "📚 Study Tools"),
            ("flashcards",    "🗂️ Flashcards"),
            ("achievements",  "🏅 Achievements"),
        ]

        for page_key, label in nav_items:
            is_active = current == page_key
            # Use a unique key per button so Streamlit doesn't confuse them
            btn_style = "primary" if is_active else "secondary"
            if st.button(label, use_container_width=True,
                         key=f"nav_{page_key}",
                         type=btn_style):
                if not is_active:   # only rerun if actually changing page
                    go_to(page_key)

        # Flashcard due reminder
        fc_due = stats.get("flashcards_due", 0)
        if fc_due > 0:
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            st.warning(f"📚 {fc_due} flashcard{'s' if fc_due>1 else ''} due today!")

        st.divider()

        # Recent history
        with st.expander("📜 Recent History"):
            if not st.session_state.history:
                st.caption("No activity yet.")
            else:
                for h in st.session_state.history:
                    st.markdown(f"""
                        <div class="sf-hist">
                            🕐 {h['time']} | <b>{h['tool']}</b><br/>
                            📖 {h['chapter']} — {h['subject']}<br/>
                            <small>{h['preview']}</small>
                        </div>
                    """, unsafe_allow_html=True)

        # AI status
        with st.expander("🤖 AI Status"):
            if st.button("Check Models", use_container_width=True, key="check_models_btn"):
                with st.spinner("Checking..."):
                    mdls = get_available_models()
                for m in mdls:
                    st.write(f"✅ {m}")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard(username):
    render_header("StudySmart", "Your Daily Learning Companion")

    stats = get_user_stats(username) or {}

    # Metric row
    c1, c2, c3, c4 = st.columns(4)
    metric_data = [
        (c1, "mc-blue",   "🔥", stats.get("streak_days",0),            "Day Streak"),
        (c2, "mc-green",  "⭐", f"Level {stats.get('level',1)}",        "Your Level"),
        (c3, "mc-purple", "📚", stats.get("flashcards_due",0),          "Cards Due"),
        (c4, "mc-amber",  "⏱️", f"{stats.get('weekly_study_minutes',0)} min","This Week"),
    ]
    for col, cls, icon, val, lbl in metric_data:
        with col:
            st.markdown(f"""
                <div class="mc {cls}">
                    <div class="icon">{icon}</div>
                    <div class="val">{val}</div>
                    <div class="lbl">{lbl}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # XP Progress bar
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    total_xp = stats.get("total_xp",0)
    lvl      = stats.get("level",1)
    lp       = stats.get("level_progress", total_xp % 500)
    pct      = min(100, int((lp/500)*100))
    st.markdown(f"""
        <div style="display:flex;justify-content:space-between;font-size:0.87rem;font-weight:700;margin-bottom:5px;">
            <span>⭐ Level {lvl}</span>
            <span>{total_xp} XP total &nbsp;·&nbsp; {500-lp} XP to next level</span>
        </div>
        <div class="xp-wrap"><div class="xp-fill" style="width:{pct}%;"></div></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])

    with left:
        # Study Plant
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🌱 Study Momentum**")
        mins   = stats.get("total_study_minutes",0)
        growth = min(100, mins // 10)
        if   growth < 20: plant = ("🌱","Seedling")
        elif growth < 40: plant = ("🌿","Sprout")
        elif growth < 70: plant = ("🪴","Growing Plant")
        elif growth < 90: plant = ("🌳","Strong Tree")
        else:             plant = ("🌲","Master Tree")
        st.markdown(f"""
            <div class="sf-soft-card" style="text-align:center;margin-bottom:12px;">
                <div style="font-size:3rem;">{plant[0]}</div>
                <div style="font-weight:800;color:#0f172a;">{plant[1]}</div>
                <div style="color:#64748b;font-size:0.84rem;margin-top:4px;">
                    {mins} minutes studied total
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Quick Actions — THE FIX: direct go_to() calls, no nested rerun
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions**")

        if st.button("📚 Open Study Tools", use_container_width=True, key="dash_to_study"):
            go_to("study")

        if st.button("🗂️ Review Flashcards", use_container_width=True, key="dash_to_fc"):
            go_to("flashcards")

        if st.button("🏅 View Achievements", use_container_width=True, key="dash_to_ach"):
            go_to("achievements")

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        # Recent activity
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**📜 Recent Activity**")
        if not st.session_state.history:
            st.info("No activity yet. Generate your first study content to get started!")
        else:
            for h in st.session_state.history:
                st.markdown(f"""
                    <div class="sf-hist">
                        🕐 {h['time']} | <b>{h['tool']}</b><br/>
                        📖 {h['chapter']} — {h['subject']}<br/>
                        <small>{h['preview']}</small>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Badge snapshot
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🏅 Badge Snapshot**")
        earned       = get_earned_badges(username)
        earned_list  = [b for b in ALL_BADGES if b["id"] in earned][:4]
        if earned_list:
            bc = st.columns(2)
            for i, badge in enumerate(earned_list):
                with bc[i % 2]:
                    st.markdown(f"""
                        <div class="bdg earned">
                            <div class="bi">{badge['icon']}</div>
                            <div class="bn">{badge['name']}</div>
                            <div class="bs">✅ Earned</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Complete daily tasks to earn your first badge!")
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARDS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_flashcards(username):
    render_header("Flashcards", "Daily review with spaced repetition")

    tab1, tab2, tab3 = st.tabs(["📖 Review Due", "➕ Create", "📋 My Library"])

    # ── TAB 1: Review ────────────────────────────────────────────────────────
    with tab1:
        due = get_due_flashcards(username)
        if not due:
            st.success("🎉 No flashcards due today — you're fully caught up!")
            st.info(f"You have {len(get_all_flashcards(username))} total cards in your library.")
        else:
            idx = st.session_state.review_idx
            if idx >= len(due):
                st.success(f"✅ All {len(due)} cards reviewed! Great work!")
                if st.button("🔄 Review Again", use_container_width=True, key="fc_restart"):
                    st.session_state.review_idx      = 0
                    st.session_state.review_show_ans = False
                    st.rerun()
            else:
                card = due[idx]
                card_id, front, back, subj, chap = card[0], card[1], card[2], card[3], card[4]

                st.progress((idx+1)/len(due))
                st.caption(f"Card {idx+1} of {len(due)} · {subj} · {chap}")

                if not st.session_state.review_show_ans:
                    st.markdown(f"""
                        <div class="fc-front">
                            <div style="font-size:0.8rem;opacity:0.8;margin-bottom:10px;">QUESTION</div>
                            <div style="font-size:1.1rem;font-weight:700;line-height:1.5;">{front}</div>
                            <div style="font-size:0.75rem;opacity:0.7;margin-top:14px;">Click to reveal answer ↓</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    if st.button("👁️ Reveal Answer", use_container_width=True, key="fc_reveal"):
                        st.session_state.review_show_ans = True
                        st.rerun()
                else:
                    st.markdown(f"""
                        <div class="fc-back">
                            <div style="font-size:0.8rem;opacity:0.8;margin-bottom:10px;">ANSWER</div>
                            <div style="font-size:1.05rem;font-weight:700;line-height:1.5;">{back}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    st.markdown("**How well did you remember this?**")
                    b1, b2, b3, b4 = st.columns(4)
                    with b1:
                        if st.button("😓 Again", use_container_width=True, key=f"fc_again_{card_id}"):
                            update_flashcard_review(card_id, 1)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()
                    with b2:
                        if st.button("😐 Hard",  use_container_width=True, key=f"fc_hard_{card_id}"):
                            update_flashcard_review(card_id, 2)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()
                    with b3:
                        if st.button("🙂 Good",  use_container_width=True, key=f"fc_good_{card_id}"):
                            update_flashcard_review(card_id, 3)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()
                    with b4:
                        if st.button("😄 Easy",  use_container_width=True, key=f"fc_easy_{card_id}"):
                            update_flashcard_review(card_id, 4)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()

    # ── TAB 2: Create ─────────────────────────────────────────────────────────
    with tab2:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### ✍️ Create Manually")
            with st.form("manual_fc_form"):
                front   = st.text_input("Front (Question / Term)")
                back    = st.text_area("Back (Answer)", height=90)
                fc_subj = st.text_input("Subject")
                fc_chap = st.text_input("Chapter")
                if st.form_submit_button("➕ Save Flashcard", use_container_width=True):
                    if front.strip() and back.strip():
                        save_flashcard(username, front.strip(), back.strip(), fc_subj.strip(), fc_chap.strip())
                        award_xp(username, 5)
                        st.success("✅ Flashcard saved! +5 XP")
                    else:
                        st.warning("⚠️ Front and Back cannot be empty.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### 🤖 Generate with AI")
            with st.form("ai_fc_form"):
                ai_subj  = st.text_input("Subject",  placeholder="e.g. Physics")
                ai_chap  = st.text_input("Chapter",  placeholder="e.g. Laws of Motion")
                ai_topic = st.text_input("Topic",    placeholder="e.g. Newton's Third Law")
                if st.form_submit_button("⚡ Generate 10 Flashcards", use_container_width=True):
                    if ai_subj.strip() and ai_chap.strip():
                        with st.spinner("Generating flashcards..."):
                            raw, mdl = generate_with_fallback(
                                build_flashcard_prompt(ai_subj.strip(), ai_chap.strip(), ai_topic.strip()))
                        if mdl != "None":
                            cards = parse_flashcards(raw)
                            for card in cards:
                                save_flashcard(username, card["front"], card["back"], ai_subj.strip(), ai_chap.strip())
                            award_xp(username, len(cards)*5)
                            st.success(f"✅ {len(cards)} flashcards created! +{len(cards)*5} XP")
                        else:
                            st.error("❌ Generation failed.")
                    else:
                        st.warning("⚠️ Subject and Chapter are required.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 3: Library ────────────────────────────────────────────────────────
    with tab3:
        all_cards = get_all_flashcards(username)
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        if not all_cards:
            st.info("No flashcards yet. Create some above!")
        else:
            st.caption(f"📚 Total: {len(all_cards)} flashcards")
            for row in all_cards:
                c_id, front, back, subj, chap, nrd, rc = row
                with st.expander(f"📌 {front[:65]}{'...' if len(front)>65 else ''}"):
                    st.markdown(f"**Q:** {front}")
                    st.markdown(f"**A:** {back}")
                    st.caption(f"Subject: {subj} | Chapter: {chap} | Next review: {nrd} | Reviews: {rc}")
                    if st.button("🗑️ Delete", key=f"del_fc_{c_id}"):
                        delete_flashcard(c_id)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_achievements(username):
    render_header("Achievements", "Collect badges by learning every day")

    earned      = get_earned_badges(username)
    earned_list = [b for b in ALL_BADGES if b["id"] in earned]
    locked_list = [b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(f"**{len(earned_list)} / {len(ALL_BADGES)} badges earned**")
    prog = len(earned_list)/len(ALL_BADGES) if ALL_BADGES else 0
    st.progress(prog)
    st.markdown('</div>', unsafe_allow_html=True)

    if earned_list:
        st.markdown("### ✅ Earned")
        cols = st.columns(4)
        for i, b in enumerate(earned_list):
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="bdg earned">
                        <div class="bi">{b['icon']}</div>
                        <div class="bn">{b['name']}</div>
                        <div class="bs">✅ Earned</div>
                        <div class="bs">{b['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)

    if locked_list:
        st.markdown("### 🔒 Locked")
        cols = st.columns(4)
        for i, b in enumerate(locked_list):
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="bdg">
                        <div class="bi" style="opacity:0.3;">🔒</div>
                        <div class="bn" style="color:#94a3b8;">{b['name']}</div>
                        <div class="bs">{b['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# STUDY TOOLS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_study_tools(username):
    render_header("Study Tools", "AI-powered exam preparation at your fingertips")

    # Tool selector
    tool = st.radio("🛠️ Select Tool", [
        "📝 Summary","🧠 Quiz","📌 Revision Notes","🧪 Question Paper","❓ Exam Q&A"
    ], horizontal=True, key="study_tool_radio")

    # Selection card
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)

    if not STUDY_DATA:
        st.error("❌ No study data loaded. Check data/study_data.json")
        st.stop()

    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        category = st.selectbox("📚 Category", list(STUDY_DATA.keys()), key="sel_category")
    with col_b:
        st.markdown("""
            <div class="sf-soft-card" style="height:100%;display:flex;align-items:center;">
                <div>
                    <div style="font-weight:700;color:#0f172a;font-size:0.9rem;">Quick Setup</div>
                    <div style="color:#64748b;font-size:0.82rem;margin-top:3px;">
                        Choose your path and generate AI content instantly.
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    course  = st.selectbox("🎓 Program / Class", get_courses(category),          key="sel_course")
    stream  = st.selectbox("📖 Stream",          get_streams(category, course),   key="sel_stream")
    subject = st.selectbox("🧾 Subject",          get_subjects(category, course, stream), key="sel_subject")

    if category == "K-12th":
        board = st.selectbox("🏫 Board", BOARDS, key="sel_board")
    else:
        board = "University / National Syllabus"
        st.info(f"📌 Syllabus: {board}")

    topic = st.selectbox("🗂️ Topic", get_topics(category, course, stream, subject), key="sel_topic")

    chapter_key = f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key
        reset_generation_state()

    chapter = st.selectbox("📝 Chapter", st.session_state.current_chapters, key="sel_chapter")
    st.session_state.current_subject_for_timer = subject

    st.markdown('</div>', unsafe_allow_html=True)

    output_style = st.radio("⚙️ Output Style", [
        "📄 Detailed","⚡ Short & Quick","📋 Notes Format","🧪 Question Paper"
    ], horizontal=True, key="study_output_radio")

    eff_label = get_effective_output_name(tool, output_style)
    btn_label = get_button_label(tool, output_style)

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    if st.button(btn_label, use_container_width=True, key="generate_btn"):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter.")
            return

        audience = f"{board} {course} students" if category == "K-12th" else f"{course} students"
        prompt   = build_prompt(tool, chapter, topic, subject, audience, output_style, board=board, course=course)

        with st.spinner(f"Generating {eff_label}..."):
            result, model_used = generate_with_fallback(prompt)

        st.session_state.update({
            "generated_result":       result,
            "generated_model":        model_used,
            "generated_label":        eff_label,
            "generated_tool":         tool,
            "generated_chapter":      chapter,
            "generated_subject":      subject,
            "generated_topic":        topic,
            "generated_course":       course,
            "generated_stream":       stream,
            "generated_board":        board,
            "generated_audience":     audience,
            "generated_output_style": output_style,
            "answers_result": None, "answers_model": None, "show_answers": False,
            "fullpaper_result": None,"fullpaper_model": None,"show_fullpaper": False,
        })

        if model_used != "None":
            add_to_history(eff_label, chapter, subject, result)
            award_xp(username, 25)
            award_badge(username, "first_gen",    "Starter Spark")
            if eff_label == "Question Paper": award_badge(username, "qp_generated","Paper Setter")
            if eff_label == "Quiz":           award_badge(username, "quiz_done",   "Quiz Taker")

    # ── Output display ────────────────────────────────────────────────────────
    if st.session_state.generated_result:
        result    = st.session_state.generated_result
        g_label   = st.session_state.generated_label
        g_chapter = st.session_state.generated_chapter
        g_subject = st.session_state.generated_subject
        g_topic   = st.session_state.generated_topic
        g_course  = st.session_state.generated_course
        g_stream  = st.session_state.generated_stream
        g_board   = st.session_state.generated_board
        g_audience= st.session_state.generated_audience

        if st.session_state.generated_model == "None":
            st.error("❌ Generation failed.")
            st.markdown(result)
            return

        st.markdown('<div class="sf-output">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        is_qp = (g_label == "Question Paper")

        if not is_qp:
            # Save as flashcards button
            if st.button("🗂️ Save Key Points as Flashcards", use_container_width=True, key="save_as_fc"):
                with st.spinner("Creating flashcards..."):
                    raw, mdl = generate_with_fallback(
                        build_flashcard_prompt(g_subject, g_chapter, g_topic or ""))
                if mdl != "None":
                    cards = parse_flashcards(raw)
                    for card in cards:
                        save_flashcard(username, card["front"], card["back"], g_subject, g_chapter)
                    award_xp(username, len(cards)*5)
                    st.success(f"✅ {len(cards)} flashcards saved! +{len(cards)*5} XP")
                else:
                    st.error("❌ Flashcard generation failed.")
            # Download PDF
            try:
                pdf  = generate_pdf(f"{g_label} — {g_chapter}", f"{g_subject} | {g_topic} | {g_course}", result)
                safe = g_chapter.replace(" ","_").replace(":","").replace("/","-") + ".pdf"
                st.download_button("⬇️ Download PDF", data=pdf, file_name=safe,
                                   mime="application/pdf", use_container_width=True, key="dl_main")
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

        else:
            # Question Paper actions
            try:
                qp_pdf  = generate_pdf(f"Question Paper — {g_chapter}",
                    f"{g_subject} | {g_board} | {g_course}", result, "#1d4ed8")
                safe_qp = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_QP.pdf"
                st.download_button("⬇️ Download Question Paper PDF", data=qp_pdf,
                    file_name=safe_qp, mime="application/pdf",
                    use_container_width=True, key="dl_qp")
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

            if st.button("📋 Get Answers for this Paper", use_container_width=True, key="get_answers_btn"):
                with st.spinner("Generating answer key..."):
                    ans_r, ans_m = generate_with_fallback(
                        build_answers_prompt(result, g_board, g_course, g_subject, g_chapter))
                st.session_state.answers_result = ans_r
                st.session_state.answers_model  = ans_m
                st.session_state.show_answers   = True

            if st.session_state.show_answers and st.session_state.answers_result:
                if st.session_state.answers_model != "None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 📚 Answer Key — {g_chapter}")
                    st.markdown(st.session_state.answers_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        ans_pdf  = generate_pdf(f"Answer Key — {g_chapter}",
                            f"{g_subject} | {g_board} | {g_course}",
                            st.session_state.answers_result, "#15803d")
                        safe_ans = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_Answers.pdf"
                        st.download_button("⬇️ Download Answer Key PDF", data=ans_pdf,
                            file_name=safe_ans, mime="application/pdf",
                            use_container_width=True, key="dl_ans")
                    except Exception as e:
                        st.warning(f"⚠️ PDF error: {e}")

            st.info(f"💡 Want a full **{g_subject}** paper covering the entire syllabus ({g_board})?")

            if st.button(f"🗂️ Generate Full {g_subject} Question Paper",
                         use_container_width=True, key="full_qp_btn"):
                with st.spinner("Generating full subject paper..."):
                    full_r, full_m = generate_with_fallback(
                        build_full_qp_prompt(g_board, g_course, g_stream, g_subject, g_audience))
                st.session_state.fullpaper_result = full_r
                st.session_state.fullpaper_model  = full_m
                st.session_state.show_fullpaper   = True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Paper — {g_subject}")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf = generate_pdf(f"Full Paper — {g_subject}",
                            f"{g_board} | {g_course} | {g_stream}",
                            st.session_state.fullpaper_result, "#7c3aed")
                        safe_f   = f"{g_subject}_{g_board}_FullPaper.pdf".replace(" ","_")
                        st.download_button("⬇️ Download Full Paper PDF", data=full_pdf,
                            file_name=safe_f, mime="application/pdf",
                            use_container_width=True, key="dl_full")
                    except Exception as e:
                        st.warning(f"⚠️ PDF error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# AUTH UI
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        render_header("StudySmart", "Your Smart Exam Preparation Platform")
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("👤 Username", placeholder="Enter your username",  key="login_u")
                p = st.text_input("🔑 Password", placeholder="Enter password",
                                  type="password", key="login_p")
                submitted = st.form_submit_button("Sign In 🚀", use_container_width=True)
            if submitted:
                ok, res = do_login(u, p)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username  = res
                    result = check_daily_login(res)
                    st.session_state.daily_checkin_done = True
                    st.success(f"✅ Welcome back, {res}! {result.get('message','')}")
                    time.sleep(0.7)
                    st.rerun()
                else:
                    st.error(res)

        with tab2:
            with st.form("register_form", clear_on_submit=True):
                nu = st.text_input("👤 Username",         placeholder="Min 3 characters",  key="reg_u")
                np = st.text_input("🔑 Password",         placeholder="Min 6 characters",  type="password", key="reg_p")
                cp = st.text_input("🔑 Confirm Password", placeholder="Re-enter password", type="password", key="reg_cp")
                reg_sub = st.form_submit_button("Create Account ✨", use_container_width=True)
            if reg_sub:
                if   not nu.strip():      st.error("❌ Username cannot be empty")
                elif len(nu.strip()) < 3: st.error("❌ Username: min 3 characters")
                elif len(np.strip()) < 6: st.error("❌ Password: min 6 characters")
                elif np != cp:            st.error("❌ Passwords do not match")
                else:
                    try:
                        conn = sqlite3.connect("users.db")
                        c    = conn.cursor()
                        c.execute("INSERT INTO users (username,password) VALUES (?,?)",
                                  (nu.strip(), hash_p(np)))
                        conn.commit()
                        conn.close()
                        st.session_state.logged_in = True
                        st.session_state.username  = nu.strip()
                        check_daily_login(nu.strip())
                        st.session_state.daily_checkin_done = True
                        st.success("✅ Account created!")
                        time.sleep(0.7)
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists.")

        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main_app():
    username = st.session_state.username
    render_sidebar(username)

    page = st.session_state.active_page

    if   page == "dashboard":     show_dashboard(username)
    elif page == "study":         show_study_tools(username)
    elif page == "flashcards":    show_flashcards(username)
    elif page == "achievements":  show_achievements(username)
    else:                         show_dashboard(username)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
init_db()
init_enhanced_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
