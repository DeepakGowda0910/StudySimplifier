# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — app.py  v4.0  (FULL SINGLE-FILE — ALL FEATURES)
# ─ Daily Streak & XP System
# ─ Study Plant Growth
# ─ Flashcard System (Spaced Repetition)
# ─ Achievement Badges
# ─ Progress Dashboard
# ─ Study Timer
# ─ All original exam prep tools retained
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
# PAGE CONFIG  ← must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 1200px;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* ══════════════════════════════════════
   LIGHT MODE
══════════════════════════════════════ */
.stApp { background: #f0f4f8 !important; }

/* Header */
.sf-header { text-align: center; padding: 20px 0 8px 0; }
.sf-header-title {
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1;
}
.sf-header-subtitle {
    color: #64748b; font-weight: 500; margin-top: 4px; font-size: 0.95rem;
}

/* Cards */
.sf-card {
    background: #ffffff !important; border-radius: 14px;
    padding: 20px 24px; border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05); margin-bottom: 14px;
}

/* Dashboard metric cards */
.dash-card {
    border-radius: 14px; padding: 18px 16px;
    text-align: center; color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    margin-bottom: 10px;
}
.dash-card-blue  { background: linear-gradient(135deg,#3b82f6,#2563eb); }
.dash-card-green { background: linear-gradient(135deg,#10b981,#059669); }
.dash-card-purple{ background: linear-gradient(135deg,#8b5cf6,#7c3aed); }
.dash-card-amber { background: linear-gradient(135deg,#f59e0b,#d97706); }
.dash-card-rose  { background: linear-gradient(135deg,#f43f5e,#e11d48); }
.dash-card .dc-icon  { font-size: 1.8rem; }
.dash-card .dc-value { font-size: 1.6rem; font-weight: 800; margin: 4px 0; }
.dash-card .dc-label { font-size: 0.75rem; opacity: 0.9; }

/* Activity feed */
.activity-item {
    background: #f8fafc; padding: 10px 14px; border-radius: 10px;
    margin-bottom: 8px; border-left: 4px solid #3b82f6;
    transition: transform 0.2s;
}
.activity-item:hover { transform: translateX(4px); background: #f1f5f9; }
.activity-item .ai-title { font-weight: 600; color: #1e293b; font-size: 0.9rem; }
.activity-item .ai-meta  { display:flex; justify-content:space-between;
    font-size:0.8rem; color:#64748b; margin-top:2px; }
.activity-item .ai-xp   { color:#10b981; font-weight:600; }

/* Flashcard */
.flashcard {
    background: linear-gradient(135deg,#667eea,#764ba2);
    border-radius: 16px; padding: 30px 24px; color: white;
    text-align: center; min-height: 160px; cursor: pointer;
    box-shadow: 0 8px 25px rgba(102,126,234,0.4);
    transition: transform 0.3s;
}
.flashcard:hover { transform: scale(1.02); }
.flashcard-answer {
    background: linear-gradient(135deg,#11998e,#38ef7d);
    border-radius: 16px; padding: 30px 24px; color: white;
    text-align: center; min-height: 160px;
    box-shadow: 0 8px 25px rgba(17,153,142,0.4);
}

/* Badge */
.badge-card {
    background: #ffffff; border: 2px solid #e2e8f0;
    border-radius: 12px; padding: 14px; text-align: center;
    transition: transform 0.2s, border-color 0.2s;
}
.badge-card:hover  { transform: translateY(-3px); border-color: #3b82f6; }
.badge-card.earned { border-color: #f59e0b; background: #fffbeb; }
.badge-card .badge-icon  { font-size: 2.2rem; }
.badge-card .badge-name  { font-size: 0.8rem; font-weight:700; color:#1e293b; margin-top:6px; }
.badge-card .badge-status{ font-size:0.7rem; color:#64748b; }

/* Streak fire */
.streak-display {
    text-align: center; padding: 12px 16px;
    background: linear-gradient(135deg,#ff6b6b,#feca57);
    border-radius: 12px; color: white; font-weight: 800;
}

/* Progress bar custom */
.xp-bar-wrap {
    background: #e2e8f0; border-radius: 99px; height: 10px; overflow: hidden;
}
.xp-bar-fill {
    background: linear-gradient(90deg,#3b82f6,#8b5cf6);
    height: 100%; border-radius: 99px;
    transition: width 0.6s ease;
}

/* Output boxes */
.sf-output {
    background: #eff6ff !important; border-left: 4px solid #2563eb !important;
    border-radius: 14px; padding: 20px 22px;
    border: 1px solid #bfdbfe !important; margin-top: 12px;
}
.sf-output h1,.sf-output h2,.sf-output h3 { color:#1d4ed8 !important; margin-top:0; }
.sf-output p,.sf-output li,.sf-output span,.sf-output strong { color:#1e293b !important; }

.sf-answers {
    background: #f0fdf4 !important; border-left: 4px solid #16a34a !important;
    border-radius: 14px; padding: 20px 22px;
    border: 1px solid #bbf7d0 !important; margin-top: 14px;
}
.sf-answers h1,.sf-answers h2,.sf-answers h3 { color:#15803d !important; margin-top:0; }
.sf-answers p,.sf-answers li,.sf-answers span,.sf-answers strong { color:#1e293b !important; }

.sf-fullpaper {
    background: #faf5ff !important; border-left: 4px solid #7c3aed !important;
    border-radius: 14px; padding: 20px 22px;
    border: 1px solid #ddd6fe !important; margin-top: 14px;
}
.sf-fullpaper h1,.sf-fullpaper h2,.sf-fullpaper h3 { color:#6d28d9 !important; margin-top:0; }
.sf-fullpaper p,.sf-fullpaper li,.sf-fullpaper span,.sf-fullpaper strong { color:#1e293b !important; }

/* History */
.sf-history-item {
    background:#eff6ff; border-left:3px solid #3b82f6;
    border-radius:8px; padding:10px 12px; margin-bottom:8px; font-size:0.87rem;
}
.sf-history-item b    { color:#1d4ed8 !important; }
.sf-history-item small{ color:#64748b !important; }

/* Radio */
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] > div > label > div > p { color:#1e293b !important; font-weight:500 !important; }

/* Widget labels */
[data-testid="stWidgetLabel"] p,
div.stSelectbox > label, div.stTextInput > label,
div.stRadio > label, label[data-testid="stWidgetLabel"] {
    color:#1e293b !important; font-weight:600 !important; font-size:0.87rem !important;
}

/* Selectbox — arrow preserved */
div[data-baseweb="select"] { border-radius:10px !important; }
div[data-baseweb="select"] > div:first-child {
    border:1.5px solid #cbd5e1 !important; border-radius:10px !important;
    background:#ffffff !important;
}
div[data-baseweb="select"] > div > div > div { color:#1e293b !important; }
div[data-baseweb="select"] svg {
    fill:#64748b !important; display:block !important;
    visibility:visible !important; opacity:1 !important;
}
div[data-baseweb="popover"] {
    background:#ffffff !important; border:1px solid #e2e8f0 !important;
    border-radius:10px !important; box-shadow:0 4px 20px rgba(0,0,0,0.1) !important;
}
div[role="listbox"] { background:#ffffff !important; }
div[role="option"]  { color:#1e293b !important; background:#ffffff !important; }
div[role="option"]:hover { background:#eff6ff !important; color:#1d4ed8 !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background:#ffffff !important; border-right:1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * { color:#1e293b !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { border-bottom:2px solid #e2e8f0 !important; }
.stTabs [data-baseweb="tab"]      { color:#64748b !important; font-weight:500 !important; }
.stTabs [aria-selected="true"]    { color:#1e293b !important; border-bottom:3px solid #3b82f6 !important; }

/* Expanders */
details { background:#ffffff !important; border:1px solid #e2e8f0 !important; border-radius:10px !important; }
details summary { color:#1e293b !important; font-weight:600 !important; }

/* Markdown text */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span { color:#1e293b !important; }

/* Buttons */
.stButton > button {
    background:linear-gradient(135deg,#3b82f6,#2563eb) !important;
    color:#ffffff !important; border:none !important; border-radius:11px !important;
    font-weight:600 !important; padding:0.55rem 1.3rem !important;
    box-shadow:0 3px 12px rgba(59,130,246,0.22) !important;
    transition:all 0.18s ease !important;
}
.stButton > button:hover {
    box-shadow:0 6px 20px rgba(59,130,246,0.35) !important;
    transform:translateY(-1px) !important;
}
.stDownloadButton > button {
    background:linear-gradient(135deg,#10b981,#059669) !important;
    color:#ffffff !important; border:none !important; border-radius:11px !important;
    font-weight:600 !important; box-shadow:0 3px 12px rgba(16,185,129,0.22) !important;
}
.stFormSubmitButton > button {
    background:linear-gradient(135deg,#3b82f6,#2563eb) !important;
    color:#ffffff !important; border:none !important; border-radius:11px !important;
    font-weight:600 !important; padding:0.55rem 1.3rem !important;
    width:100% !important; box-shadow:0 3px 12px rgba(59,130,246,0.22) !important;
}

/* Alerts */
div[data-testid="stSuccessMessage"] {
    background:rgba(16,185,129,0.08) !important;
    border:1.5px solid rgba(16,185,129,0.3) !important; border-radius:10px !important;
}
div[data-testid="stWarningMessage"] {
    background:rgba(245,158,11,0.08) !important;
    border:1.5px solid rgba(245,158,11,0.3) !important; border-radius:10px !important;
}
div[data-testid="stErrorMessage"] {
    background:rgba(239,68,68,0.08) !important;
    border:1.5px solid rgba(239,68,68,0.3) !important; border-radius:10px !important;
}
hr { border-color:#e2e8f0 !important; }

/* ══════════════════════════════════════════════
   DARK MODE  [data-theme="dark"]  ← CORRECT selector
   @media (prefers-color-scheme) does NOT work in Streamlit
══════════════════════════════════════════════ */
[data-theme="dark"] .stApp { background:#0f172a !important; }
[data-theme="dark"] .sf-card  { background:#1e293b !important; border-color:#334155 !important; }

[data-theme="dark"] .dash-card-blue  { background:linear-gradient(135deg,#1d4ed8,#1e40af); }
[data-theme="dark"] .dash-card-green { background:linear-gradient(135deg,#059669,#047857); }
[data-theme="dark"] .dash-card-purple{ background:linear-gradient(135deg,#7c3aed,#6d28d9); }
[data-theme="dark"] .dash-card-amber { background:linear-gradient(135deg,#d97706,#b45309); }

[data-theme="dark"] .activity-item { background:#1e293b; border-left-color:#3b82f6; }
[data-theme="dark"] .activity-item:hover { background:#334155; }
[data-theme="dark"] .activity-item .ai-title { color:#e2e8f0; }

[data-theme="dark"] .badge-card { background:#1e293b; border-color:#334155; }
[data-theme="dark"] .badge-card.earned { background:#1c1917; border-color:#f59e0b; }
[data-theme="dark"] .badge-card .badge-name { color:#e2e8f0; }

[data-theme="dark"] .sf-output  { background:rgba(37,99,235,0.13) !important; border-color:#3b82f6 !important; }
[data-theme="dark"] .sf-output h1,[data-theme="dark"] .sf-output h2,
[data-theme="dark"] .sf-output h3  { color:#93c5fd !important; }
[data-theme="dark"] .sf-output p,[data-theme="dark"] .sf-output li,
[data-theme="dark"] .sf-output span,[data-theme="dark"] .sf-output strong { color:#dbeafe !important; }

[data-theme="dark"] .sf-answers { background:rgba(22,163,74,0.13) !important; border-color:#16a34a !important; }
[data-theme="dark"] .sf-answers h1,[data-theme="dark"] .sf-answers h2,
[data-theme="dark"] .sf-answers h3 { color:#86efac !important; }
[data-theme="dark"] .sf-answers p,[data-theme="dark"] .sf-answers li,
[data-theme="dark"] .sf-answers span,[data-theme="dark"] .sf-answers strong { color:#dcfce7 !important; }

[data-theme="dark"] .sf-fullpaper { background:rgba(109,40,217,0.13) !important; border-color:#7c3aed !important; }
[data-theme="dark"] .sf-fullpaper h1,[data-theme="dark"] .sf-fullpaper h2,
[data-theme="dark"] .sf-fullpaper h3 { color:#c4b5fd !important; }
[data-theme="dark"] .sf-fullpaper p,[data-theme="dark"] .sf-fullpaper li,
[data-theme="dark"] .sf-fullpaper span,[data-theme="dark"] .sf-fullpaper strong { color:#ede9fe !important; }

[data-theme="dark"] .sf-history-item { background:rgba(37,99,235,0.15) !important; border-left-color:#60a5fa; color:#cbd5e1 !important; }
[data-theme="dark"] .sf-history-item b     { color:#93c5fd !important; }
[data-theme="dark"] .sf-history-item small  { color:#94a3b8 !important; }

[data-theme="dark"] div[data-testid="stRadio"] label p,
[data-theme="dark"] div[data-testid="stRadio"] label span,
[data-theme="dark"] div[data-testid="stRadio"] > div > label > div > p { color:#e2e8f0 !important; }

[data-theme="dark"] [data-testid="stWidgetLabel"] p,
[data-theme="dark"] div.stSelectbox > label,
[data-theme="dark"] div.stTextInput > label,
[data-theme="dark"] div.stRadio > label,
[data-theme="dark"] label[data-testid="stWidgetLabel"] { color:#e2e8f0 !important; }

[data-theme="dark"] div[data-baseweb="select"] > div:first-child {
    border-color:#475569 !important; background:#1e293b !important;
}
[data-theme="dark"] div[data-baseweb="select"] > div > div > div { color:#e2e8f0 !important; }
[data-theme="dark"] div[data-baseweb="select"] svg { fill:#94a3b8 !important; }
[data-theme="dark"] div[data-baseweb="popover"] { background:#1e293b !important; border-color:#334155 !important; }
[data-theme="dark"] div[role="listbox"] { background:#1e293b !important; }
[data-theme="dark"] div[role="option"]  { color:#e2e8f0 !important; background:#1e293b !important; }
[data-theme="dark"] div[role="option"]:hover { background:#334155 !important; color:#f1f5f9 !important; }

[data-theme="dark"] [data-testid="stSidebar"] {
    background:#0f172a !important; border-right-color:#334155 !important;
}
[data-theme="dark"] [data-testid="stSidebar"] * { color:#e2e8f0 !important; }

[data-theme="dark"] .stTabs [data-baseweb="tab-list"] { border-bottom-color:#334155 !important; }
[data-theme="dark"] .stTabs [data-baseweb="tab"]      { color:#94a3b8 !important; }
[data-theme="dark"] .stTabs [aria-selected="true"]    { color:#f1f5f9 !important; border-bottom-color:#60a5fa !important; }

[data-theme="dark"] details { background:#1e293b !important; border-color:#334155 !important; }
[data-theme="dark"] details summary { color:#e2e8f0 !important; }

[data-theme="dark"] [data-testid="stMarkdownContainer"] p,
[data-theme="dark"] [data-testid="stMarkdownContainer"] li,
[data-theme="dark"] [data-testid="stMarkdownContainer"] span,
[data-theme="dark"] [data-testid="stMarkdownContainer"] h1,
[data-theme="dark"] [data-testid="stMarkdownContainer"] h2,
[data-theme="dark"] [data-testid="stMarkdownContainer"] h3 { color:#e2e8f0 !important; }

[data-theme="dark"] div[data-testid="stSuccessMessage"] { background:rgba(16,185,129,0.15) !important; border-color:rgba(16,185,129,0.4) !important; }
[data-theme="dark"] div[data-testid="stWarningMessage"] { background:rgba(245,158,11,0.15) !important; border-color:rgba(245,158,11,0.4) !important; }
[data-theme="dark"] div[data-testid="stErrorMessage"]   { background:rgba(239,68,68,0.15) !important;  border-color:rgba(239,68,68,0.4) !important; }
[data-theme="dark"] hr { border-color:#334155 !important; }

[data-theme="dark"] .xp-bar-wrap { background:#334155; }
[data-theme="dark"] .activity-item .ai-meta { color:#94a3b8; }

@media (max-width: 768px) {
    .sf-header-title { font-size:2rem !important; }
    .sf-card,.sf-output,.sf-answers,.sf-fullpaper { padding:12px 14px; }
    .block-container { padding-left:0.5rem !important; padding-right:0.5rem !important; }
    .dash-card { padding:14px 10px; }
    .dash-card .dc-value { font-size:1.3rem; }
}
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# STUDY DATA
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

STUDY_DATA = load_study_data()
BOARDS = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge"]

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE — all tables in one place
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # ── Original auth table ──────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    # ── User progress (streak, XP, level) ───────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            username         TEXT PRIMARY KEY,
            streak_days      INTEGER DEFAULT 0,
            last_active_date TEXT,
            total_xp         INTEGER DEFAULT 0,
            level            INTEGER DEFAULT 1,
            total_study_min  INTEGER DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # ── Flashcards (spaced repetition) ──────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT,
            front_text       TEXT,
            back_text        TEXT,
            subject          TEXT,
            chapter          TEXT,
            ease_factor      REAL    DEFAULT 2.5,
            interval_days    INTEGER DEFAULT 1,
            next_review_date TEXT,
            review_count     INTEGER DEFAULT 0,
            created_date     TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # ── Achievements / badges ────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT,
            badge_id    TEXT,
            badge_name  TEXT,
            earned_date TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    # ── Study sessions (timer log) ───────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT,
            subject          TEXT,
            activity_type    TEXT,
            duration_minutes INTEGER,
            session_date     TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# CORE HELPER FUNCTIONS
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

def hash_p(password):
    return hashlib.sha256(password.encode()).hexdigest()

def do_login(username, password):
    username = username.strip()
    if not username or not password.strip():
        return False, "⚠️ Please fill in both fields."
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_p(password)))
    user = c.fetchone()
    conn.close()
    if user:
        return True, username
    return False, "❌ Invalid username or password."

def add_to_history(label, chapter, subject, result_preview):
    if "history" not in st.session_state:
        st.session_state.history = []
    entry = {
        "time":    time.strftime("%H:%M"),
        "tool":    label,
        "chapter": chapter,
        "subject": subject,
        "preview": result_preview[:120] + "..." if len(result_preview) > 120 else result_preview
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:5]

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

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        # Auth
        "logged_in": False, "username": "", "history": [],
        # Study tool
        "current_chapters": [], "last_chapter_key": "",
        "generated_result": None, "generated_model": None,
        "generated_label": None,  "generated_tool": None,
        "generated_chapter": None,"generated_subject": None,
        "generated_topic": None,  "generated_course": None,
        "generated_stream": None, "generated_board": None,
        "generated_audience": None, "generated_output_style": None,
        "answers_result": None, "answers_model": None, "show_answers": False,
        "fullpaper_result": None,"fullpaper_model": None,"show_fullpaper": False,
        # Daily engagement
        "streak_days": 0,
        "total_xp": 0,
        "user_level": 1,
        "today_study_min": 0,
        "daily_checkin_done": False,
        "study_timer_active": False,
        "study_timer_start": None,
        # Navigation
        "active_page": "dashboard",      # dashboard | study | flashcards | achievements
        # Flashcard state
        "fc_index": 0,
        "fc_show_answer": False,
        "fc_front": "",
        "fc_back": "",
        "fc_subject": "",
        "fc_chapter": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_generation_state():
    for k in ["generated_result","generated_model","generated_label","generated_tool",
              "generated_chapter","generated_subject","generated_topic","generated_course",
              "generated_stream","generated_board","generated_audience","generated_output_style",
              "answers_result","answers_model","fullpaper_result","fullpaper_model"]:
        st.session_state[k] = None
    st.session_state.show_answers   = False
    st.session_state.show_fullpaper = False
# ─────────────────────────────────────────────────────────────────────────────
# BADGE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────
ALL_BADGES = [
    {"id":"first_login",     "name":"First Step",       "icon":"👣", "desc":"Logged in for the first time"},
    {"id":"streak_3",        "name":"Heatwave",         "icon":"🔥", "desc":"3-day study streak"},
    {"id":"streak_7",        "name":"Weekly Warrior",   "icon":"🎖️","desc":"7-day study streak"},
    {"id":"streak_14",       "name":"Fortnight Champ",  "icon":"🏆", "desc":"14-day study streak"},
    {"id":"streak_30",       "name":"Monthly Master",   "icon":"👑", "desc":"30-day study streak"},
    {"id":"first_gen",       "name":"Content Creator",  "icon":"✍️","desc":"Generated first AI content"},
    {"id":"flashcard_10",    "name":"Card Collector",   "icon":"🗂️","desc":"Created 10 flashcards"},
    {"id":"flashcard_50",    "name":"Card Master",      "icon":"📚", "desc":"Created 50 flashcards"},
    {"id":"study_60",        "name":"Hour Power",       "icon":"⏱️","desc":"Studied 60 minutes total"},
    {"id":"study_300",       "name":"Study Beast",      "icon":"💪", "desc":"Studied 300 minutes total"},
    {"id":"level_5",         "name":"Rising Star",      "icon":"⭐", "desc":"Reached Level 5"},
    {"id":"level_10",        "name":"Scholar",          "icon":"🎓", "desc":"Reached Level 10"},
    {"id":"qp_generated",    "name":"Paper Setter",     "icon":"📝", "desc":"Generated a Question Paper"},
    {"id":"quiz_done",       "name":"Quiz Taker",       "icon":"🧠", "desc":"Generated a Quiz"},
]

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("SELECT id FROM achievements WHERE username=? AND badge_id=?", (username, badge_id))
    if not c.fetchone():
        badge  = next((b for b in ALL_BADGES if b["id"] == badge_id), None)
        if badge:
            c.execute("""INSERT INTO achievements (username, badge_id, badge_name, earned_date)
                         VALUES (?,?,?,?)""",
                      (username, badge_id, badge["name"],
                       datetime.date.today().isoformat()))
            conn.commit()
            conn.close()
            return True   # newly awarded
    conn.close()
    return False  # already had it

def award_xp(username, xp):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("UPDATE user_progress SET total_xp = total_xp + ? WHERE username=?", (xp, username))
    c.execute("SELECT total_xp FROM user_progress WHERE username=?", (username,))
    row = c.fetchone()
    if row:
        new_xp    = row[0]
        new_level = new_xp // 500 + 1        # level up every 500 XP
        c.execute("UPDATE user_progress SET level=? WHERE username=?", (new_level, username))
        # Level badges
        if new_level >= 5:  award_badge(username, "level_5")
        if new_level >= 10: award_badge(username, "level_10")
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# DAILY CHECK-IN
# ─────────────────────────────────────────────────────────────────────────────
def daily_checkin(username):
    """Run once per session. Returns dict with streak + message."""
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    yest  = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    c.execute("SELECT streak_days, last_active_date, total_xp, level FROM user_progress WHERE username=?",
              (username,))
    row = c.fetchone()

    if not row:
        # First ever login — create row
        c.execute("""INSERT INTO user_progress
                     (username, streak_days, last_active_date, total_xp, level, total_study_min)
                     VALUES (?,1,?,50,1,0)""", (username, today))
        conn.commit()
        conn.close()
        award_badge(username, "first_login")
        award_xp(username, 50)
        return {"streak": 1, "xp_earned": 50,
                "message": "🎉 Welcome to StudySmart! Streak started! +50 XP",
                "new_badge": "first_login"}

    streak, last_date, total_xp, level = row

    if last_date == today:
        conn.close()
        return {"streak": streak, "xp_earned": 0,
                "message": f"✅ Already checked in today. Keep it up! 🔥 {streak} day streak"}

    if last_date == yest:
        new_streak = streak + 1
    else:
        new_streak = 1        # reset

    xp_earned = 20 + (10 if new_streak % 7 == 0 else 0)   # bonus on weekly milestone
    c.execute("""UPDATE user_progress
                 SET streak_days=?, last_active_date=?, total_xp=total_xp+?, level=?
                 WHERE username=?""",
              (new_streak, today, xp_earned,
               (total_xp + xp_earned) // 500 + 1, username))
    conn.commit()
    conn.close()

    # Milestone badges
    new_badge = None
    if new_streak == 3:  new_badge = award_badge(username,"streak_3")  and "streak_3"
    if new_streak == 7:  new_badge = award_badge(username,"streak_7")  and "streak_7"
    if new_streak == 14: new_badge = award_badge(username,"streak_14") and "streak_14"
    if new_streak == 30: new_badge = award_badge(username,"streak_30") and "streak_30"

    msg = (f"🔥 Day {new_streak} streak! +{xp_earned} XP"
           if new_streak > 1 else f"🔄 Streak reset. Day 1 starts now! +{xp_earned} XP")

    return {"streak": new_streak, "xp_earned": xp_earned,
            "message": msg, "new_badge": new_badge}

# ─────────────────────────────────────────────────────────────────────────────
# USER STATS
# ─────────────────────────────────────────────────────────────────────────────
def get_user_stats(username):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()

    c.execute("""SELECT streak_days, total_xp, level, total_study_min
                 FROM user_progress WHERE username=?""", (username,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {}
    streak, total_xp, level, total_study_min = row

    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=? AND next_review_date <= ?",
              (username, today))
    fc_due = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
    fc_total = c.fetchone()[0] or 0

    c.execute("""SELECT COALESCE(SUM(duration_minutes),0), COUNT(*)
                 FROM study_sessions WHERE username=? AND session_date >= ?""",
              (username, week_ago))
    weekly_min, weekly_sessions = c.fetchone()

    c.execute("SELECT COUNT(*) FROM achievements WHERE username=?", (username,))
    badge_count = c.fetchone()[0] or 0

    c.execute("SELECT badge_id FROM achievements WHERE username=?", (username,))
    earned_badge_ids = [r[0] for r in c.fetchall()]

    conn.close()

    level_progress = total_xp % 500           # XP within current level
    xp_to_next     = 500 - level_progress

    return {
        "streak_days":      streak,
        "total_xp":         total_xp,
        "level":            level,
        "level_progress":   level_progress,
        "xp_to_next":       xp_to_next,
        "total_study_min":  total_study_min or 0,
        "flashcards_due":   fc_due,
        "flashcards_total": fc_total,
        "weekly_min":       weekly_min or 0,
        "weekly_sessions":  weekly_sessions or 0,
        "badge_count":      badge_count,
        "earned_badge_ids": earned_badge_ids,
    }

# ─────────────────────────────────────────────────────────────────────────────
# STUDY TIMER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def log_study_session(username, subject, activity_type, duration_minutes):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("""INSERT INTO study_sessions
                 (username, subject, activity_type, duration_minutes)
                 VALUES (?,?,?,?)""",
              (username, subject, activity_type, duration_minutes))
    c.execute("""UPDATE user_progress
                 SET total_study_min = total_study_min + ?
                 WHERE username=?""", (duration_minutes, username))
    conn.commit()
    conn.close()
    # Study badges
    c2 = sqlite3.connect("users.db").cursor()
    c2.execute("SELECT total_study_min FROM user_progress WHERE username=?", (username,))
    row = c2.fetchone()
    if row:
        if row[0] >= 60:  award_badge(username, "study_60")
        if row[0] >= 300: award_badge(username, "study_300")
    xp = (duration_minutes // 5) * 10      # 10 XP per 5 minutes
    if xp > 0:
        award_xp(username, xp)

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def save_flashcard(username, front, back, subject, chapter):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""INSERT INTO flashcards
                 (username, front_text, back_text, subject, chapter, next_review_date)
                 VALUES (?,?,?,?,?,?)""",
              (username, front, back, subject, chapter, today))
    conn.commit()

    # Count total flashcards for badges
    c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
    total = c.fetchone()[0]
    conn.close()
    if total >= 10: award_badge(username, "flashcard_10")
    if total >= 50: award_badge(username, "flashcard_50")
    award_xp(username, 5)   # 5 XP per card

def get_due_flashcards(username):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""SELECT id, front_text, back_text, subject, chapter,
                        ease_factor, interval_days, review_count
                 FROM flashcards
                 WHERE username=? AND next_review_date <= ?
                 ORDER BY next_review_date ASC""", (username, today))
    cards = c.fetchall()
    conn.close()
    return cards

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("""SELECT id, front_text, back_text, subject, chapter, next_review_date, review_count
                 FROM flashcards WHERE username=?
                 ORDER BY created_date DESC""", (username,))
    cards = c.fetchall()
    conn.close()
    return cards

def update_flashcard_review(card_id, performance):
    """
    SM-2 simplified spaced repetition.
    performance: 1=Again, 2=Hard, 3=Good, 4=Easy
    """
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("SELECT ease_factor, interval_days, review_count FROM flashcards WHERE id=?", (card_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    ef, interval, reviews = row

    if performance == 1:        # Again
        interval = 1
        ef = max(1.3, ef - 0.2)
    elif performance == 2:      # Hard
        interval = max(1, int(interval * 1.2))
        ef = max(1.3, ef - 0.1)
    elif performance == 3:      # Good
        interval = max(1, int(interval * ef))
    elif performance == 4:      # Easy
        interval = max(1, int(interval * ef * 1.3))
        ef = ef + 0.1

    next_review = (datetime.date.today() + datetime.timedelta(days=interval)).isoformat()
    c.execute("""UPDATE flashcards
                 SET ease_factor=?, interval_days=?, next_review_date=?, review_count=review_count+1
                 WHERE id=?""",
              (round(ef, 2), interval, next_review, card_id))
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
    earned = {r[0] for r in c.fetchall()}
    conn.close()
    return earned
# ─────────────────────────────────────────────────────────────────────────────
# QP FORMAT SPECS
# ─────────────────────────────────────────────────────────────────────────────
def get_qp_format_spec(board, course, subject):
    b = board.upper()
    if "CBSE" in b:
        if any(x in course for x in ["10","X","Class 10"]):
            return {"board_label":"CENTRAL BOARD OF SECONDARY EDUCATION",
                    "exam_label":"BOARD EXAMINATION","class_label":"CLASS X",
                    "total_marks":80,"time":"3 Hours",
                    "instructions":["Paper contains Sections A, B, C, D and E.",
                                    "All questions are compulsory.",
                                    "Section A — MCQ (1 mark each).",
                                    "Section B — Very Short Answer (2 marks each).",
                                    "Section C — Short Answer (3 marks each).",
                                    "Section D — Long Answer (5 marks each).",
                                    "Section E — Case/Source Based (4 marks each).",
                                    "Internal choices provided in some questions."],
                    "sections":[
                        {"name":"SECTION A","type":"MCQ","q_count":20,"marks_each":1,"total":20},
                        {"name":"SECTION B","type":"Very Short Answer","q_count":5,"marks_each":2,"total":10},
                        {"name":"SECTION C","type":"Short Answer","q_count":6,"marks_each":3,"total":18},
                        {"name":"SECTION D","type":"Long Answer","q_count":4,"marks_each":5,"total":20},
                        {"name":"SECTION E","type":"Case Based","q_count":3,"marks_each":4,"total":12},
                    ]}
        if any(x in course for x in ["12","XII","Class 12"]):
            return {"board_label":"CENTRAL BOARD OF SECONDARY EDUCATION",
                    "exam_label":"BOARD EXAMINATION","class_label":"CLASS XII",
                    "total_marks":70,"time":"3 Hours",
                    "instructions":["Paper contains Sections A, B, C, D and E.",
                                    "All questions are compulsory.",
                                    "Section A — MCQ (1 mark each).",
                                    "Section B — Very Short Answer (2 marks each).",
                                    "Section C — Short Answer (3 marks each).",
                                    "Section D — Long Answer (5 marks each).",
                                    "Section E — Case Based (4 marks each).",
                                    "Internal choices in Sections B, C and D."],
                    "sections":[
                        {"name":"SECTION A","type":"MCQ","q_count":18,"marks_each":1,"total":18},
                        {"name":"SECTION B","type":"Very Short Answer","q_count":4,"marks_each":2,"total":8},
                        {"name":"SECTION C","type":"Short Answer","q_count":5,"marks_each":3,"total":15},
                        {"name":"SECTION D","type":"Long Answer","q_count":2,"marks_each":5,"total":10},
                        {"name":"SECTION E","type":"Case Based","q_count":3,"marks_each":4,"total":12},
                    ]}
        return {"board_label":"CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label":"ANNUAL EXAMINATION","class_label":course.upper(),
                "total_marks":80,"time":"3 Hours",
                "instructions":["All questions are compulsory.","Read each section carefully."],
                "sections":[
                    {"name":"SECTION A","type":"Objective","q_count":20,"marks_each":1,"total":20},
                    {"name":"SECTION B","type":"Short Answer I","q_count":6,"marks_each":2,"total":12},
                    {"name":"SECTION C","type":"Short Answer II","q_count":6,"marks_each":3,"total":18},
                    {"name":"SECTION D","type":"Long Answer","q_count":4,"marks_each":5,"total":20},
                ]}
    if "ICSE" in b:
        return {"board_label":"COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
                "exam_label":"ICSE EXAMINATION","class_label":course.upper(),
                "total_marks":80,"time":"2 Hours",
                "instructions":["Attempt all from Section A.","Attempt any four from Section B.","Marks in brackets [ ]."],
                "sections":[
                    {"name":"SECTION A","type":"Compulsory Short Answer","q_count":10,"marks_each":"varied","total":40},
                    {"name":"SECTION B","type":"Descriptive (Attempt 4 of 6)","q_count":6,"marks_each":10,"total":40},
                ]}
    if "ISC" in b:
        return {"board_label":"COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
                "exam_label":"ISC EXAMINATION","class_label":course.upper(),
                "total_marks":70,"time":"3 Hours",
                "instructions":["Attempt all from Section A.","Attempt any four from Section B.",
                                 "Marks in brackets [ ].","Draw neat labelled diagrams."],
                "sections":[
                    {"name":"SECTION A","type":"Compulsory","q_count":10,"marks_each":"varied","total":30},
                    {"name":"SECTION B","type":"Descriptive (4 of 6)","q_count":6,"marks_each":10,"total":40},
                ]}
    if "IB" in b:
        return {"board_label":"INTERNATIONAL BACCALAUREATE",
                "exam_label":"FINAL EXAMINATION","class_label":course.upper(),
                "total_marks":100,"time":"2 Hours 30 Minutes",
                "instructions":["Answer all required questions.","Show all reasoning."],
                "sections":[
                    {"name":"SECTION A","type":"Structured","q_count":20,"marks_each":"varied","total":40},
                    {"name":"SECTION B","type":"Extended Response","q_count":4,"marks_each":15,"total":60},
                ]}
    if "CAMBRIDGE" in b:
        return {"board_label":"CAMBRIDGE ASSESSMENT INTERNATIONAL EDUCATION",
                "exam_label":"INTERNATIONAL EXAMINATION","class_label":course.upper(),
                "total_marks":80,"time":"2 Hours",
                "instructions":["Answer all questions.","Show all working."],
                "sections":[
                    {"name":"SECTION A","type":"Structured Questions","q_count":10,"marks_each":4,"total":40},
                    {"name":"SECTION B","type":"Extended Response","q_count":4,"marks_each":10,"total":40},
                ]}
    return {"board_label":"UNIVERSITY EXAMINATIONS",
            "exam_label":f"{course.upper()} SEMESTER EXAMINATION","class_label":course.upper(),
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
def build_question_paper_prompt(board, course, subject, chapter, topic, audience):
    fmt  = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
    secs  = "\n".join([f"- {s['name']} | {s['type']} | {s['q_count']} Qs | {s['marks_each']} marks each | Total {s['total']}"
                       for s in fmt["sections"]])
    return f"""You are an official academic question paper setter.
Generate a CHAPTER-LEVEL question paper using the EXACT format below.

BOARD: {fmt['board_label']}
EXAM: {fmt['exam_label']} | CLASS: {fmt['class_label']}
SUBJECT: {subject} | TOPIC: {topic} | CHAPTER: {chapter}
TIME: {fmt['time']} | MAX MARKS: {fmt['total_marks']}

INSTRUCTIONS (print in paper):
{instr}

SECTION STRUCTURE (follow exactly):
{secs}

RULES:
1. Follow structure exactly — section names, question counts, marks.
2. Print a proper academic header at the top.
3. Number all questions (Q1, Q2...).
4. MCQs must have exactly (a)(b)(c)(d). DO NOT mark the answer.
5. Show marks in square brackets [X marks].
6. Cover the chapter comprehensively.
7. Difficulty: 30% easy, 50% medium, 20% hard.
8. DO NOT include answers or hints.

Generate the complete question paper now."""

def build_full_subject_qp_prompt(board, course, stream, subject, audience):
    fmt  = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
    secs  = "\n".join([f"- {s['name']} | {s['type']} | {s['q_count']} Qs | {s['marks_each']} marks each | Total {s['total']}"
                       for s in fmt["sections"]])
    return f"""You are an official academic question paper setter.
Generate a FULL SUBJECT question paper covering the complete syllabus.

BOARD: {fmt['board_label']} | EXAM: {fmt['exam_label']} | CLASS: {fmt['class_label']}
STREAM: {stream} | SUBJECT: {subject}
TIME: {fmt['time']} | MAX MARKS: {fmt['total_marks']}

INSTRUCTIONS: {instr}
STRUCTURE: {secs}

RULES:
1. Cover the FULL syllabus — not just one chapter.
2. Distribute questions across all major units.
3. MCQs have 4 options (a)(b)(c)(d). No answers.
4. Show marks [X marks]. DO NOT include answers or hints.

Generate the complete full subject question paper now."""

def build_answers_prompt(qp_text, board, course, subject, chapter):
    return f"""You are preparing the OFFICIAL ANSWER KEY for the EXACT question paper below.
BOARD: {board} | COURSE: {course} | SUBJECT: {subject} | CHAPTER: {chapter}

RULES:
1. Answer ONLY the questions in the paper below.
2. Keep EXACT same section names and question numbers.
3. MCQs: correct option letter + 2-3 line explanation.
4. Very Short: 2-3 lines. Short: 4-6 lines. Long: 150-250 words.
5. If OR choices exist, answer BOTH. DO NOT create a new paper.

===== QUESTION PAPER =====
{qp_text}
===== END =====

Generate the answer key now."""

def build_prompt(tool, chapter, topic, subject, audience, output_style, board="", course=""):
    if output_style == "🧪 Question Paper" or tool == "🧪 Question Paper":
        return build_question_paper_prompt(board, course, subject, chapter, topic, audience)
    base = f"You are an expert educator creating study material for {audience}.\nSubject: {subject} | Topic: {topic} | Chapter: {chapter}\nRequirements: Accurate, exam-focused, well-structured, with examples.\n\n"
    if tool == "📝 Summary":
        if output_style == "📄 Detailed":
            return base + "Create a detailed summary: chapter overview (150-200 words), key concepts (300-400 words), important definitions and formulas, 2-3 worked examples, common mistakes to avoid, exam tips."
        elif output_style == "⚡ Short & Quick":
            return base + "Create a concise quick-reference guide (max 500 words): one-line definition, 5-7 key points, important formulas/facts, quick revision tips."
        elif output_style == "📋 Notes Format":
            return base + "Create structured study notes: clear headings and subheadings, bullet points per concept, definitions highlighted, important facts and examples, revision points."
    if tool == "🧠 Quiz":
        return base + "Create a quiz: 5 MCQs with 4 options (mark correct answer), 5 short answer questions with answers, 3 long answer questions with answers."
    if tool == "📌 Revision Notes":
        return base + "Create revision notes: top 10 must-know points, formula/fact sheet, mnemonics and memory tricks, key comparisons/tables, exam focus areas."
    if tool == "❓ Exam Q&A":
        return base + "Create an exam Q&A bank: 8-10 frequently asked questions with answers, 5 conceptual questions, 5 application questions, 5 why/how questions with answers."
    return base + "Create comprehensive exam-ready study material."

def build_flashcard_prompt(subject, chapter, topic):
    return f"""You are an expert educator.
Create exactly 10 high-quality study flashcards for:
Subject: {subject} | Chapter: {chapter} | Topic: {topic}

Format STRICTLY as follows (10 cards, no extra text):
CARD 1
FRONT: [question or concept]
BACK: [concise answer, max 3 lines]

CARD 2
FRONT: [question or concept]
BACK: [concise answer, max 3 lines]

...continue for all 10 cards.

Rules:
- Front: clear question or key term
- Back: concise factual answer
- Cover key concepts, definitions, formulas, dates
- No duplicates"""

# ─────────────────────────────────────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ("⚠️ API key missing! Add GEMINI_API_KEY to `.streamlit/secrets.toml`", "None")
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Gemini config failed: {e}", "None")
    available = []
    try:
        for m in genai.list_models():
            name    = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "gemini" in name.lower() and "generateContent" in methods:
                available.append(name)
    except Exception as e:
        return (f"❌ Could not list models: {e}", "None")
    if not available:
        return ("❌ No Gemini models available.", "None")
    for model_name in available:
        try:
            model    = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0, max_output_tokens=8192, top_p=0.9))
            if response and getattr(response, "text", None):
                return response.text, model_name
        except Exception:
            continue
    return ("❌ All models failed.", "None")

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD PARSER  (parses AI output into list of dicts)
# ─────────────────────────────────────────────────────────────────────────────
def parse_flashcards(raw_text):
    cards = []
    blocks = raw_text.strip().split("CARD ")
    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().split("\n")
        front, back = "", ""
        for line in lines:
            if line.upper().startswith("FRONT:"):
                front = line[6:].strip()
            elif line.upper().startswith("BACK:"):
                back = line[5:].strip()
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
        fontSize=20, textColor=colors.HexColor(color_hex),
        spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold")))
    story.append(Paragraph(subtitle, ParagraphStyle("S", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#64748b"),
        spaceAfter=10, alignment=TA_CENTER, fontName="Helvetica")))
    story.append(HRFlowable(width="100%", thickness=2,
        color=colors.HexColor(color_hex), spaceAfter=14))
    body_sty = ParagraphStyle("B", parent=styles["Normal"],fontSize=10.5,leading=15,
        textColor=colors.HexColor("#1e293b"),spaceAfter=5,fontName="Helvetica")
    head_sty = ParagraphStyle("H", parent=styles["Heading2"],fontSize=12.5,
        textColor=colors.HexColor(color_hex),spaceBefore=10,spaceAfter=6,fontName="Helvetica-Bold")
    bull_sty = ParagraphStyle("BL", parent=styles["Normal"],fontSize=10.5,leading=15,
        leftIndent=16,bulletIndent=6,textColor=colors.HexColor("#334155"),
        spaceAfter=4,fontName="Helvetica")
    for line in content.split("\n"):
        line = line.strip()
        if not line: story.append(Spacer(1,0.18*cm)); continue
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if line.startswith(("###","##","#")):
            story.append(Paragraph(line.lstrip("#").strip(), head_sty))
        elif line.startswith(("- ","• ","* ")):
            story.append(Paragraph(f"• {safe[2:]}", bull_sty))
        else:
            story.append(Paragraph(safe, body_sty))
    story.append(Spacer(1,0.3*cm))
    story.append(HRFlowable(width="100%",thickness=1,
        color=colors.HexColor("#e2e8f0"),spaceAfter=5))
    story.append(Paragraph(f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle("F",parent=styles["Normal"],fontSize=8,
        textColor=colors.HexColor("#94a3b8"),alignment=TA_CENTER)))
    doc.build(story)
    buffer.seek(0)
    return buffer
# ─────────────────────────────────────────────────────────────────────────────
# WEEKLY BAR CHART  (pure HTML — no extra libraries needed)
# ─────────────────────────────────────────────────────────────────────────────
def render_weekly_chart(username):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    days_data = []
    for i in range(6, -1, -1):
        d = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
        c.execute("""SELECT COALESCE(SUM(duration_minutes),0)
                     FROM study_sessions WHERE username=? AND session_date LIKE ?""",
                  (username, f"{d}%"))
        mins = c.fetchone()[0]
        days_data.append({"day": datetime.date.fromisoformat(d).strftime("%a"), "min": mins})
    conn.close()

    max_min = max((d["min"] for d in days_data), default=1) or 1
    bars = ""
    for d in days_data:
        h = max(4, int((d["min"] / max_min) * 80))
        bars += f"""
        <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:4px;">
            <div style="font-size:0.7rem;color:#64748b;">{d['min']}m</div>
            <div style="width:70%;background:linear-gradient(to top,#3b82f6,#60a5fa);
                        height:{h}px;border-radius:4px 4px 0 0;min-height:4px;"></div>
            <div style="font-size:0.75rem;font-weight:600;">{d['day']}</div>
        </div>"""
    st.markdown(f"""
        <div style="display:flex;align-items:flex-end;height:130px;gap:6px;
                    padding:10px 0 0 0;margin-top:8px;">
            {bars}
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard(username):
    stats = get_user_stats(username)
    if not stats:
        st.info("📊 Stats will appear after your first study session!")
        return

    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">📊 Dashboard</div>
            <div class="sf-header-subtitle">Your Daily Learning Hub</div>
        </div>
    """, unsafe_allow_html=True)

    # ── Top 5 metric cards ─────────────────────────────────────────────────
    c1,c2,c3,c4,c5 = st.columns(5)
    cards = [
        (c1, "dash-card-blue",   "🔥", stats["streak_days"], "Day Streak"),
        (c2, "dash-card-green",  "🎯", f"Lv {stats['level']}", "Your Level"),
        (c3, "dash-card-purple", "📚", stats["flashcards_due"], "Cards Due Today"),
        (c4, "dash-card-amber",  "⏱️", f"{stats['weekly_min']}m", "Week Study"),
        (c5, "dash-card-rose",   "🏅", stats["badge_count"], "Badges Earned"),
    ]
    for col, cls, icon, value, label in cards:
        with col:
            st.markdown(f"""
                <div class="dash-card {cls}">
                    <div class="dc-icon">{icon}</div>
                    <div class="dc-value">{value}</div>
                    <div class="dc-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # ── XP Progress Bar ────────────────────────────────────────────────────
    pct = int((stats["level_progress"] / 500) * 100)
    st.markdown(f"""
        <div style="margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;font-size:0.85rem;font-weight:600;margin-bottom:4px;">
                <span>⭐ Level {stats['level']} Progress</span>
                <span>{stats['level_progress']} / 500 XP &nbsp;({stats['xp_to_next']} to next level)</span>
            </div>
            <div class="xp-bar-wrap">
                <div class="xp-bar-fill" style="width:{pct}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Left: Study Plant + Quick Actions  |  Right: Chart ────────────────
    left, right = st.columns([1, 1])

    with left:
        # Study Plant
        st.markdown("#### 🌱 Study Plant")
        total_min   = stats["total_study_min"]
        growth_pct  = min(100, total_min // 6)
        stages = [("🌱","Seedling",0),("🌿","Sprout",20),("🪴","Young Plant",40),
                  ("🌳","Mature Tree",70),("🌲","Giant Redwood",90)]
        current_stage = stages[0]
        for stage in stages:
            if growth_pct >= stage[2]:
                current_stage = stage
        st.markdown(f"""
            <div style="text-align:center;padding:16px;background:#f0fdf4;
                        border-radius:14px;border:1px solid #bbf7d0;">
                <div style="font-size:3.5rem;animation:none;">{current_stage[0]}</div>
                <div style="font-weight:700;color:#15803d;font-size:1rem;">{current_stage[1]}</div>
                <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">
                    {growth_pct}% grown · {total_min} total minutes studied
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Quick actions
        st.markdown("#### ⚡ Quick Actions")
        if st.button("🗂️ Review Flashcards", use_container_width=True):
            st.session_state.active_page = "flashcards"
            st.rerun()
        if st.button("🏅 View Achievements", use_container_width=True):
            st.session_state.active_page = "achievements"
            st.rerun()
        if st.button("📚 Go to Study Tools", use_container_width=True):
            st.session_state.active_page = "study"
            st.rerun()

    with right:
        st.markdown("#### 📅 This Week's Study")
        render_weekly_chart(username)

        st.markdown("#### 📊 Quick Stats")
        stat_rows = [
            ("📚 Total Flashcards",  stats["flashcards_total"]),
            ("🎯 Weekly Sessions",   stats["weekly_sessions"]),
            ("⭐ Total XP",         stats["total_xp"]),
            ("⏱️ Total Study Time",  f"{stats['total_study_min']} min"),
        ]
        for label, val in stat_rows:
            st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:6px 10px;
                            background:#f8fafc;border-radius:8px;margin-bottom:6px;font-size:0.88rem;">
                    <span style="color:#475569;">{label}</span>
                    <span style="font-weight:700;color:#1e293b;">{val}</span>
                </div>
            """, unsafe_allow_html=True)

    # ── Recent Achievements preview ─────────────────────────────────────────
    st.markdown("#### 🏅 Recent Badges")
    earned = get_earned_badges(username)
    recent = [b for b in ALL_BADGES if b["id"] in earned][-4:] or []
    if recent:
        cols = st.columns(4)
        for i, badge in enumerate(recent):
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="badge-card earned">
                        <div class="badge-icon">{badge['icon']}</div>
                        <div class="badge-name">{badge['name']}</div>
                        <div class="badge-status">✅ Earned</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🎯 Complete daily tasks to earn your first badge!")

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARDS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_flashcards(username):
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">🗂️ Flashcards</div>
            <div class="sf-header-subtitle">Spaced Repetition Review System</div>
        </div>
    """, unsafe_allow_html=True)

    fc_tab1, fc_tab2, fc_tab3 = st.tabs(["📖 Review Due Cards","➕ Create Cards","📋 All My Cards"])

    # ── TAB 1: Review Due Cards ────────────────────────────────────────────
    with fc_tab1:
        due_cards = get_due_flashcards(username)
        if not due_cards:
            st.success("🎉 No cards due for review today! Great job keeping up.")
            st.info(f"📚 You have {get_user_stats(username).get('flashcards_total',0)} total cards.")
        else:
            st.info(f"📚 **{len(due_cards)} cards** due for review today")
            if "review_idx" not in st.session_state:
                st.session_state.review_idx       = 0
                st.session_state.review_show_ans  = False
                st.session_state.review_done      = 0

            idx = st.session_state.review_idx
            if idx >= len(due_cards):
                st.success(f"🎉 All {len(due_cards)} cards reviewed! +{len(due_cards)*5} XP earned")
                award_xp(username, len(due_cards)*5)
                if st.button("🔄 Review Again", use_container_width=True):
                    st.session_state.review_idx      = 0
                    st.session_state.review_show_ans = False
                    st.rerun()
            else:
                card = due_cards[idx]
                card_id, front, back = card[0], card[1], card[2]

                st.progress(idx / len(due_cards))
                st.caption(f"Card {idx+1} of {len(due_cards)} | Subject: {card[3]} | Chapter: {card[4]}")

                if not st.session_state.review_show_ans:
                    st.markdown(f"""
                        <div class="flashcard">
                            <div style="font-size:0.85rem;opacity:0.8;margin-bottom:12px;">❓ QUESTION</div>
                            <div style="font-size:1.2rem;font-weight:600;">{front}</div>
                            <div style="font-size:0.8rem;opacity:0.7;margin-top:16px;">Click to reveal answer</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("👁️ Reveal Answer", use_container_width=True):
                        st.session_state.review_show_ans = True
                        st.rerun()
                else:
                    st.markdown(f"""
                        <div class="flashcard-answer">
                            <div style="font-size:0.85rem;opacity:0.8;margin-bottom:12px;">✅ ANSWER</div>
                            <div style="font-size:1.1rem;font-weight:600;">{back}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("**How well did you know this?**")
                    r1,r2,r3,r4 = st.columns(4)
                    with r1:
                        if st.button("😓 Again",  use_container_width=True):
                            update_flashcard_review(card_id, 1)
                            st.session_state.review_idx      += 1
                            st.session_state.review_show_ans  = False
                            st.rerun()
                    with r2:
                        if st.button("😐 Hard",   use_container_width=True):
                            update_flashcard_review(card_id, 2)
                            st.session_state.review_idx      += 1
                            st.session_state.review_show_ans  = False
                            st.rerun()
                    with r3:
                        if st.button("🙂 Good",   use_container_width=True):
                            update_flashcard_review(card_id, 3)
                            st.session_state.review_idx      += 1
                            st.session_state.review_show_ans  = False
                            st.rerun()
                    with r4:
                        if st.button("😄 Easy",   use_container_width=True):
                            update_flashcard_review(card_id, 4)
                            st.session_state.review_idx      += 1
                            st.session_state.review_show_ans  = False
                            st.rerun()

    # ── TAB 2: Create Cards ────────────────────────────────────────────────
    with fc_tab2:
        st.markdown("#### ✍️ Create Manually")
        with st.form("manual_fc_form"):
            fc_front   = st.text_input("Front (Question / Term)")
            fc_back    = st.text_area("Back (Answer)", height=80)
            fc_subject = st.text_input("Subject")
            fc_chapter = st.text_input("Chapter")
            if st.form_submit_button("➕ Save Flashcard", use_container_width=True):
                if fc_front.strip() and fc_back.strip():
                    save_flashcard(username, fc_front.strip(), fc_back.strip(),
                                   fc_subject.strip(), fc_chapter.strip())
                    st.success("✅ Flashcard saved! +5 XP")
                else:
                    st.warning("⚠️ Front and Back cannot be empty.")

        st.markdown("---")
        st.markdown("#### 🤖 AI-Generate Flashcards")
        with st.form("ai_fc_form"):
            ai_subj  = st.text_input("Subject",    placeholder="e.g. Physics")
            ai_chap  = st.text_input("Chapter",    placeholder="e.g. Laws of Motion")
            ai_topic = st.text_input("Topic",      placeholder="e.g. Newton's Third Law")
            if st.form_submit_button("🤖 Generate 10 Flashcards", use_container_width=True):
                if ai_subj.strip() and ai_chap.strip():
                    with st.spinner("Generating flashcards with AI... ⏳"):
                        raw, model = generate_with_fallback(
                            build_flashcard_prompt(ai_subj.strip(), ai_chap.strip(), ai_topic.strip()))
                    if model != "None":
                        cards = parse_flashcards(raw)
                        if cards:
                            for card in cards:
                                save_flashcard(username, card["front"], card["back"],
                                               ai_subj.strip(), ai_chap.strip())
                            st.success(f"✅ {len(cards)} flashcards created! +{len(cards)*5} XP")
                            log_study_session(username, ai_subj, "flashcard", 5)
                        else:
                            st.warning("⚠️ Could not parse AI response. Try again.")
                    else:
                        st.error("❌ AI generation failed.")
                else:
                    st.warning("⚠️ Please fill Subject and Chapter.")

    # ── TAB 3: All Cards ──────────────────────────────────────────────────
    with fc_tab3:
        all_cards = get_all_flashcards(username)
        if not all_cards:
            st.info("📭 No flashcards yet. Create some in the tab above!")
        else:
            st.caption(f"📚 Total: {len(all_cards)} flashcards")
            for card in all_cards:
                c_id, front, back, subj, chap, nrd, rc = card
                with st.expander(f"📌 {front[:60]}{'...' if len(front)>60 else ''}"):
                    st.markdown(f"**Q:** {front}")
                    st.markdown(f"**A:** {back}")
                    st.caption(f"Subject: {subj} | Chapter: {chap} | Next review: {nrd} | Reviews: {rc}")
                    if st.button(f"🗑️ Delete", key=f"del_{c_id}"):
                        delete_flashcard(c_id)
                        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_achievements(username):
    earned = get_earned_badges(username)
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">🏅 Achievements</div>
            <div class="sf-header-subtitle">Collect badges by learning every day</div>
        </div>
    """, unsafe_allow_html=True)

    earned_list   = [b for b in ALL_BADGES if b["id"] in earned]
    unearned_list = [b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown(f"**{len(earned_list)} / {len(ALL_BADGES)} badges earned** 🎖️")
    st.progress(len(earned_list) / len(ALL_BADGES))

    if earned_list:
        st.markdown("### ✅ Earned")
        cols = st.columns(4)
        for i, b in enumerate(earned_list):
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="badge-card earned">
                        <div class="badge-icon">{b['icon']}</div>
                        <div class="badge-name">{b['name']}</div>
                        <div class="badge-status" style="color:#d97706;">✅ Earned</div>
                        <div class="badge-status">{b['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)

    if unearned_list:
        st.markdown("### 🔒 Locked")
        cols = st.columns(4)
        for i, b in enumerate(unearned_list):
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="badge-card">
                        <div class="badge-icon" style="opacity:0.3;">🔒</div>
                        <div class="badge-name" style="color:#94a3b8;">{b['name']}</div>
                        <div class="badge-status">{b['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(username):
    stats = get_user_stats(username)

    with st.sidebar:
        # Brand
        st.markdown(f"""
            <div style="text-align:center;padding:16px 0 12px 0;">
                <div style="font-size:2.4rem;">🎓</div>
                <div style="font-size:1.15rem;font-weight:800;color:#2563eb;">StudySmart AI</div>
                <div style="font-size:0.82rem;color:#64748b;margin-top:3px;">
                    Hi, {username} 👋
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Streak & Level
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="streak-display">
                    🔥 {stats.get('streak_days',0)}<br>
                    <span style="font-size:0.7rem;font-weight:400;">day streak</span>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div style="text-align:center;padding:10px;background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                            border-radius:12px;color:white;font-weight:800;">
                    ⭐ Lv {stats.get('level',1)}<br>
                    <span style="font-size:0.7rem;font-weight:400;">{stats.get('total_xp',0)} XP</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin:8px 0;'></div>", unsafe_allow_html=True)

        # Daily check-in button
        if not st.session_state.daily_checkin_done:
            if st.button("✅ Daily Check-in (+20 XP)", use_container_width=True):
                result = daily_checkin(username)
                st.session_state.streak_days        = result["streak"]
                st.session_state.daily_checkin_done = True
                st.success(result["message"])
                if result.get("xp_earned", 0) > 0:
                    st.balloons()
        else:
            st.success(f"✅ Checked in! 🔥 {stats.get('streak_days',0)} day streak")

        # Study Timer
        st.markdown("---")
        st.markdown("**⏱️ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed = int((datetime.datetime.now() -
                           st.session_state.study_timer_start).total_seconds() // 60)
            st.info(f"🟢 Running: {elapsed} min")
            if st.button("⏹️ Stop & Save", use_container_width=True):
                st.session_state.study_timer_active = False
                subj = st.session_state.get("current_subject_for_timer","General")
                log_study_session(username, subj, "study_session", max(1, elapsed))
                st.session_state.today_study_min += elapsed
                award_xp(username, max(1, elapsed // 5) * 10)
                st.success(f"✅ Saved {elapsed} min study! XP awarded 🎉")
                st.session_state.study_timer_start = None
        else:
            if st.button("▶️ Start Study Timer", use_container_width=True):
                st.session_state.study_timer_active = True
                st.session_state.study_timer_start  = datetime.datetime.now()
                st.info("⏱️ Timer running...")

        # Navigation
        st.markdown("---")
        st.markdown("**🧭 Navigate**")
        nav = st.radio("", [
            "📊 Dashboard",
            "📚 Study Tools",
            "🗂️ Flashcards",
            "🏅 Achievements"
        ], key="sidebar_nav", label_visibility="collapsed")

        page_map = {
            "📊 Dashboard":   "dashboard",
            "📚 Study Tools": "study",
            "🗂️ Flashcards":  "flashcards",
            "🏅 Achievements":"achievements"
        }
        if page_map[nav] != st.session_state.active_page:
            st.session_state.active_page = page_map[nav]
            st.rerun()

        # Flashcards due reminder
        fc_due = stats.get("flashcards_due", 0)
        if fc_due > 0:
            st.markdown("---")
            st.warning(f"📚 **{fc_due} flashcard{'s' if fc_due>1 else ''}** due for review!")

        # History expander
        st.markdown("---")
        with st.expander("📜 Recent Activity"):
            if not st.session_state.history:
                st.caption("No activity yet.")
            else:
                for h in st.session_state.history:
                    st.markdown(f"""
                        <div class="sf-history-item">
                            🕐 {h['time']} | <b>{h['tool']}</b><br>
                            📖 {h['chapter']}<br>
                            <small>{h['preview']}</small>
                        </div>
                    """, unsafe_allow_html=True)

        # AI Model status
        with st.expander("🤖 AI Status"):
            if st.button("Check Models", use_container_width=True):
                with st.spinner("Checking..."):
                    mdls = get_available_models()
                for m in mdls:
                    st.write(f"✅ {m}")

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# STUDY TOOLS PAGE  (all original exam prep features)
# ─────────────────────────────────────────────────────────────────────────────
def show_study_tools(username):
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">📚 Study Tools</div>
            <div class="sf-header-subtitle">AI-Powered Exam Preparation</div>
        </div>
    """, unsafe_allow_html=True)

    # Tool selector in sidebar — we read from a radio inside the page
    tool = st.radio("🛠️ Tool", [
        "📝 Summary","🧠 Quiz","📌 Revision Notes","🧪 Question Paper","❓ Exam Q&A"
    ], horizontal=True)

    # Selection card
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    if not STUDY_DATA:
        st.error("No study data found. Check data/study_data.json")
        st.stop()

    category = st.selectbox("📚 Category",        list(STUDY_DATA.keys()))
    course   = st.selectbox("🎓 Program / Class",  get_courses(category))
    stream   = st.selectbox("📖 Stream",           get_streams(category, course))
    subject  = st.selectbox("🧾 Subject",          get_subjects(category, course, stream))
    board    = (st.selectbox("🏫 Board", BOARDS)
                if category == "K-12th" else "University / National Syllabus")
    topic    = st.selectbox("🗂️ Topic",            get_topics(category, course, stream, subject))

    chapter_key = f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key
        reset_generation_state()

    chapter = st.selectbox("📝 Chapter", st.session_state.current_chapters)

    # Save current subject for timer
    st.session_state.current_subject_for_timer = subject

    st.markdown('</div>', unsafe_allow_html=True)

    output_style    = st.radio("⚙️ Output Style",
        ["📄 Detailed","⚡ Short & Quick","📋 Notes Format","🧪 Question Paper"],
        horizontal=True)
    effective_label = get_effective_output_name(tool, output_style)
    btn_label       = get_button_label(tool, output_style)

    st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)

    # GENERATE BUTTON
    if st.button(btn_label, use_container_width=True):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter first.")
            return
        audience = f"{board} {course} students" if category=="K-12th" else f"{course} students"
        prompt   = build_prompt(tool, chapter, topic, subject, audience,
                                output_style, board=board, course=course)
        with st.spinner(f"Generating {effective_label}... ⏳"):
            result, model_used = generate_with_fallback(prompt)

        st.session_state.update({
            "generated_result":       result,
            "generated_model":        model_used,
            "generated_label":        effective_label,
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
            add_to_history(effective_label, chapter, subject, result)
            award_xp(username, 25)
            log_study_session(username, subject, effective_label.lower().replace(" ","_"), 10)
            award_badge(username, "first_gen")
            if effective_label == "Question Paper": award_badge(username, "qp_generated")
            if effective_label == "Quiz":           award_badge(username, "quiz_done")

    # OUTPUT SECTION
    if st.session_state.generated_result and st.session_state.generated_model != "None":
        result    = st.session_state.generated_result
        g_label   = st.session_state.generated_label
        g_chapter = st.session_state.generated_chapter
        g_subject = st.session_state.generated_subject
        g_topic   = st.session_state.generated_topic
        g_course  = st.session_state.generated_course
        g_stream  = st.session_state.generated_stream
        g_board   = st.session_state.generated_board
        g_audience= st.session_state.generated_audience

        st.markdown("---")
        st.markdown('<div class="sf-output">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Save as Flashcards (non-QP content) ────────────────────────────
        if g_label != "Question Paper":
            st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
            if st.button("🗂️ Save Key Points as Flashcards", use_container_width=True,
                         key="save_fc_btn"):
                with st.spinner("Creating flashcards from this content... ⏳"):
                    fc_prompt = build_flashcard_prompt(g_subject, g_chapter, g_topic or "")
                    fc_raw, fc_model = generate_with_fallback(fc_prompt)
                if fc_model != "None":
                    fc_cards = parse_flashcards(fc_raw)
                    for card in fc_cards:
                        save_flashcard(username, card["front"], card["back"],
                                       g_subject, g_chapter)
                    st.success(f"✅ {len(fc_cards)} flashcards saved to your library! +{len(fc_cards)*5} XP")
                else:
                    st.error("❌ Could not generate flashcards.")

        is_qp = (g_label == "Question Paper")

        if is_qp:
            st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
            try:
                qp_pdf  = generate_pdf(f"Question Paper — {g_chapter}",
                    f"{g_subject} | {g_board} | {g_course}", result, "#1d4ed8")
                safe_qp = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_QP.pdf"
                st.download_button("⬇️ Download Question Paper PDF",
                    data=qp_pdf, file_name=safe_qp, mime="application/pdf",
                    use_container_width=True, key="dl_qp")
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

            st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
            if st.button("📋 Get Answers for this Paper", use_container_width=True,
                         key="get_ans_btn"):
                with st.spinner("Generating answer key... ⏳"):
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
                        st.download_button("⬇️ Download Answer Key PDF",
                            data=ans_pdf, file_name=safe_ans, mime="application/pdf",
                            use_container_width=True, key="dl_ans")
                    except Exception as e:
                        st.warning(f"⚠️ PDF error: {e}")
                else:
                    st.error("❌ Failed to generate answers.")

            st.markdown("---")
            st.info(f"💡 Want a full **{g_subject}** paper for the entire syllabus ({g_board})?")
            if st.button(f"🗂️ Generate Full {g_subject} Question Paper",
                         use_container_width=True, key="full_qp_btn"):
                with st.spinner(f"Generating full {g_subject} paper... ⏳"):
                    full_r, full_m = generate_with_fallback(
                        build_full_subject_qp_prompt(g_board, g_course, g_stream,
                                                     g_subject, g_audience))
                st.session_state.fullpaper_result = full_r
                st.session_state.fullpaper_model  = full_m
                st.session_state.show_fullpaper   = True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Paper — {g_subject} ({g_board} · {g_course})")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf = generate_pdf(f"Full Question Paper — {g_subject}",
                            f"{g_board} | {g_course} | {g_stream}",
                            st.session_state.fullpaper_result, "#6d28d9")
                        safe_f = f"{g_subject}_{g_board}_FullPaper.pdf".replace(" ","_")
                        st.download_button("⬇️ Download Full Paper PDF",
                            data=full_pdf, file_name=safe_f, mime="application/pdf",
                            use_container_width=True, key="dl_full")
                    except Exception as e:
                        st.warning(f"⚠️ PDF error: {e}")
                else:
                    st.error("❌ Failed to generate full subject paper.")
        else:
            st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
            try:
                pdf  = generate_pdf(f"{g_label} — {g_chapter}",
                    f"{g_subject} | {g_topic} | {g_course}", result)
                safe = g_chapter.replace(" ","_").replace(":","").replace("/","-") + ".pdf"
                st.download_button("⬇️ Download PDF",
                    data=pdf, file_name=safe, mime="application/pdf",
                    use_container_width=True, key="dl_main")
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

    elif st.session_state.generated_result and st.session_state.generated_model == "None":
        st.markdown("---")
        st.error("❌ AI generation failed")
        st.markdown(st.session_state.generated_result)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main_app():
    username = st.session_state.username
    render_sidebar(username)

    page = st.session_state.active_page
    if page == "dashboard":
        show_dashboard(username)
    elif page == "study":
        show_study_tools(username)
    elif page == "flashcards":
        show_flashcards(username)
    elif page == "achievements":
        show_achievements(username)
    else:
        show_dashboard(username)

# ─────────────────────────────────────────────────────────────────────────────
# AUTH UI  (Enter key login via st.form)
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
            <div class="sf-header">
                <div class="sf-header-title">StudySmart AI</div>
                <div class="sf-header-subtitle">Your Daily Learning Companion 🎓</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("👤 Username", placeholder="Enter your username",   key="login_u")
                p = st.text_input("🔑 Password", placeholder="Press Enter to sign in",
                                  type="password", key="login_p")
                submitted = st.form_submit_button("Sign In 🚀", use_container_width=True)
            if submitted:
                ok, res = do_login(u, p)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username  = res
                    # Auto checkin on login
                    checkin_result = daily_checkin(res)
                    st.session_state.streak_days        = checkin_result["streak"]
                    st.session_state.daily_checkin_done = True
                    st.success(f"✅ Welcome back, {res}! {checkin_result['message']}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res)

        with tab2:
            with st.form("register_form", clear_on_submit=True):
                nu = st.text_input("👤 New Username",     placeholder="Min 3 characters",    key="reg_u")
                np = st.text_input("🔑 New Password",     placeholder="Min 6 characters",    type="password", key="reg_p")
                cp = st.text_input("🔑 Confirm Password", placeholder="Re-enter password",   type="password", key="reg_cp")
                reg_sub = st.form_submit_button("Create Account ✨", use_container_width=True)
            if reg_sub:
                if not nu.strip():          st.error("❌ Username cannot be empty")
                elif len(nu.strip()) < 3:   st.error("❌ Username min 3 characters")
                elif len(np.strip()) < 6:   st.error("❌ Password min 6 characters")
                elif np != cp:              st.error("❌ Passwords do not match")
                else:
                    try:
                        conn = sqlite3.connect("users.db")
                        c    = conn.cursor()
                        c.execute("INSERT INTO users (username, password) VALUES (?,?)",
                                  (nu.strip(), hash_p(np)))
                        conn.commit()
                        conn.close()
                        st.success("✅ Account created! Logging you in...")
                        st.session_state.logged_in = True
                        st.session_state.username  = nu.strip()
                        checkin_result = daily_checkin(nu.strip())
                        st.session_state.streak_days        = checkin_result["streak"]
                        st.session_state.daily_checkin_done = True
                        time.sleep(0.8)
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists. Choose another.")
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
init_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
