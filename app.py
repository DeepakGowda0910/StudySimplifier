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

st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_study_data():
    try:
        data_path = Path("data/study_data.json")
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Error: data/study_data.json not found!")
        return {}
    except json.JSONDecodeError:
        st.error("❌ Error: study_data.json is not valid JSON!")
        return {}

STUDY_DATA = load_study_data()
BOARDS = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge"]

# ─────────────────────────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* ═══════════════════════════════
   QUICK ACTIONS BUTTON FIX
   ═══════════════════════════════ */

/* Ensure quick action buttons are clickable */
.stButton > button {
    position: relative !important;
    z-index: 100 !important;
}

/* Fix any overlapping elements */
div[data-testid="stVerticalBlock"] > div > div {
    z-index: auto !important;
}

/* Ensure dashboard cards don't block buttons */
.sf-card {
    position: relative !important;
    z-index: 50 !important;
    overflow: visible !important;
}

/* Fix sidebar overlap */
[data-testid="stSidebar"] {
    z-index: 999 !important;
}

/* Mobile-specific button click fix */
@media (max-width: 768px) {
    .stButton > button {
        z-index: 200 !important;
        pointer-events: all !important;
    }
    
    /* Prevent any mobile overlay */
    .block-container {
        position: relative !important;
        z-index: 1 !important;
    }
}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1220px;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* App background */
.stApp {
    background:
        radial-gradient(circle at top right, rgba(37,99,235,0.08), transparent 28%),
        linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%) !important;
}

/* Header */
.sf-hero {
    text-align: center;
    padding: 24px 0 12px 0;
}
.sf-hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 55%, #0f172a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sf-hero-subtitle {
    color: #64748b;
    font-size: 1rem;
    font-weight: 500;
    margin-top: 0.35rem;
}
.sf-watermark {
    margin-top: 0.5rem;
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.08);
    color: #2563eb;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
}

/* Cards */
.sf-card {
    background: rgba(255,255,255,0.95) !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 18px;
    padding: 22px 24px;
    margin-bottom: 16px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(6px);
}

.sf-soft-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.sf-section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.75rem;
}

/* Dashboard metrics */
.metric-card {
    border-radius: 16px;
    padding: 18px 16px;
    color: white;
    box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    min-height: 120px;
}
.metric-blue   { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.metric-green  { background: linear-gradient(135deg, #10b981, #059669); }
.metric-purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.metric-amber  { background: linear-gradient(135deg, #f59e0b, #d97706); }

.metric-icon {
    font-size: 1.4rem;
    opacity: 0.95;
}
.metric-value {
    font-size: 1.65rem;
    font-weight: 800;
    margin-top: 0.35rem;
}
.metric-label {
    font-size: 0.82rem;
    margin-top: 0.25rem;
    opacity: 0.92;
}

/* Top chips */
.sf-chip-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 12px;
}
.sf-chip {
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    background: #ffffff;
    color: #334155;
    border: 1px solid #dbeafe;
    font-size: 0.8rem;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(37,99,235,0.08);
}

/* Progress */
.sf-progress-wrap {
    background: #e2e8f0;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
}
.sf-progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
}

/* History / activity */
.sf-history-item {
    background: #f8fbff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 8px;
    font-size: 0.87rem;
}
.sf-history-item b {
    color: #1d4ed8 !important;
}
.sf-history-item small {
    color: #64748b !important;
}

/* Output cards */
.sf-output {
    background: linear-gradient(180deg, #f8fbff 0%, #eff6ff 100%) !important;
    border-left: 4px solid #2563eb !important;
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid #bfdbfe !important;
    margin-top: 14px;
}
.sf-output h1,.sf-output h2,.sf-output h3 { color: #1d4ed8 !important; margin-top: 0; }
.sf-output p,.sf-output li,.sf-output span,.sf-output strong { color: #1e293b !important; }

.sf-answers {
    background: linear-gradient(180deg, #f7fff9 0%, #f0fdf4 100%) !important;
    border-left: 4px solid #16a34a !important;
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid #bbf7d0 !important;
    margin-top: 16px;
}
.sf-answers h1,.sf-answers h2,.sf-answers h3 { color: #15803d !important; margin-top: 0; }
.sf-answers p,.sf-answers li,.sf-answers span,.sf-answers strong { color: #1e293b !important; }

.sf-fullpaper {
    background: linear-gradient(180deg, #fcfaff 0%, #faf5ff 100%) !important;
    border-left: 4px solid #7c3aed !important;
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid #ddd6fe !important;
    margin-top: 16px;
}
.sf-fullpaper h1,.sf-fullpaper h2,.sf-fullpaper h3 { color: #6d28d9 !important; margin-top: 0; }
.sf-fullpaper p,.sf-fullpaper li,.sf-fullpaper span,.sf-fullpaper strong { color: #1e293b !important; }

/* Flashcards */
.flashcard-front {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-radius: 18px;
    padding: 30px 24px;
    color: white;
    text-align: center;
    min-height: 180px;
    box-shadow: 0 12px 28px rgba(79,70,229,0.3);
}
.flashcard-back {
    background: linear-gradient(135deg, #059669, #10b981);
    border-radius: 18px;
    padding: 30px 24px;
    color: white;
    text-align: center;
    min-height: 180px;
    box-shadow: 0 12px 28px rgba(16,185,129,0.25);
}

/* Badge */
.badge-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 16px 12px;
    text-align: center;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}
.badge-card.earned {
    border-color: #f59e0b;
    background: linear-gradient(180deg, #fffdf7 0%, #fffbeb 100%);
}
.badge-icon {
    font-size: 2rem;
}
.badge-name {
    margin-top: 6px;
    font-weight: 700;
    color: #0f172a;
    font-size: 0.85rem;
}
.badge-status {
    color: #64748b;
    font-size: 0.75rem;
    margin-top: 4px;
}

/* Inputs */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
div.stSelectbox > label,
div.stTextInput > label,
div.stRadio > label,
label[data-testid="stWidgetLabel"] {
    color: #1e293b !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

input[type="text"], input[type="password"], textarea {
    border-radius: 12px !important;
}

/* Selectbox fix - keep dropdown arrow visible */
div[data-baseweb="select"] {
    border-radius: 12px !important;
}
div[data-baseweb="select"] > div:first-child {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    background: #ffffff !important;
    min-height: 44px !important;
}
div[data-baseweb="select"] > div > div > div {
    color: #1e293b !important;
}
div[data-baseweb="select"] svg {
    fill: #64748b !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
div[data-baseweb="popover"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.08) !important;
}
div[role="option"] {
    color: #1e293b !important;
    background: #ffffff !important;
}
div[role="option"]:hover {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {
    border: none !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    padding: 0.65rem 1.2rem !important;
    box-shadow: 0 8px 18px rgba(37,99,235,0.22) !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 24px rgba(37,99,235,0.28) !important;
}
.stDownloadButton > button {
    border: none !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(16,185,129,0.22) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * {
    color: #1e293b !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #e2e8f0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: #1e293b !important;
    border-bottom: 3px solid #3b82f6 !important;
}

/* Messages */
div[data-testid="stSuccessMessage"],
div[data-testid="stWarningMessage"],
div[data-testid="stErrorMessage"] {
    border-radius: 12px !important;
}

/* Dark mode */
[data-theme="dark"] .stApp {
    background:
        radial-gradient(circle at top right, rgba(59,130,246,0.1), transparent 28%),
        linear-gradient(180deg, #0f172a 0%, #111827 100%) !important;
}
[data-theme="dark"] .sf-card,
[data-theme="dark"] .sf-soft-card,
[data-theme="dark"] .badge-card {
    background: #1e293b !important;
    border-color: #334155 !important;
}
[data-theme="dark"] .sf-hero-subtitle,
[data-theme="dark"] .badge-status {
    color: #94a3b8 !important;
}
[data-theme="dark"] .sf-chip {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #334155 !important;
}
[data-theme="dark"] .sf-watermark {
    background: rgba(59,130,246,0.18) !important;
    color: #93c5fd !important;
}
[data-theme="dark"] div[data-baseweb="select"] > div:first-child {
    background: #1e293b !important;
    border-color: #475569 !important;
}
[data-theme="dark"] div[data-baseweb="select"] > div > div > div {
    color: #e2e8f0 !important;
}
[data-theme="dark"] div[data-baseweb="select"] svg {
    fill: #94a3b8 !important;
}
[data-theme="dark"] div[data-baseweb="popover"] {
    background: #1e293b !important;
    border-color: #334155 !important;
}
[data-theme="dark"] div[role="option"] {
    background: #1e293b !important;
    color: #e2e8f0 !important;
}
[data-theme="dark"] div[role="option"]:hover {
    background: #334155 !important;
    color: #f8fafc !important;
}
[data-theme="dark"] [data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right-color: #334155 !important;
}
[data-theme="dark"] [data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-theme="dark"] .sf-history-item {
    background: #1e293b !important;
    border-color: #334155 !important;
}
[data-theme="dark"] .sf-history-item b {
    color: #93c5fd !important;
}
[data-theme="dark"] .metric-card {
    box-shadow: none !important;
}
[data-theme="dark"] .badge-name,
[data-theme="dark"] .sf-section-title {
    color: #f1f5f9 !important;
}
[data-theme="dark"] .sf-output p,
[data-theme="dark"] .sf-output li,
[data-theme="dark"] .sf-output span,
[data-theme="dark"] .sf-output strong,
[data-theme="dark"] .sf-answers p,
[data-theme="dark"] .sf-answers li,
[data-theme="dark"] .sf-fullpaper p,
[data-theme="dark"] .sf-fullpaper li {
    color: #e2e8f0 !important;
}

/* Mobile */
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.55rem !important;
        padding-right: 0.55rem !important;
        padding-top: 0.7rem !important;
    }
    .sf-hero {
        padding-top: 14px;
    }
    .sf-hero-title {
        font-size: 2.15rem !important;
    }
    .sf-hero-subtitle {
        font-size: 0.92rem !important;
    }
    .sf-card {
        padding: 16px 14px !important;
        border-radius: 16px !important;
    }
    .metric-card {
        min-height: auto !important;
        padding: 16px 14px !important;
    }
    .flashcard-front, .flashcard-back {
        min-height: 150px !important;
        padding: 22px 16px !important;
    }
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
        "logged_in": False,
        "username": "",
        "history": [],
        "active_page": "dashboard",

        "current_chapters": [],
        "last_chapter_key": "",

        "generated_result": None,
        "generated_model": None,
        "generated_label": None,
        "generated_tool": None,
        "generated_chapter": None,
        "generated_subject": None,
        "generated_topic": None,
        "generated_course": None,
        "generated_stream": None,
        "generated_board": None,
        "generated_audience": None,
        "generated_output_style": None,

        "answers_result": None,
        "answers_model": None,
        "show_answers": False,

        "fullpaper_result": None,
        "fullpaper_model": None,
        "show_fullpaper": False,

        "daily_checkin_done": False,
        "study_timer_active": False,
        "study_timer_start": None,
        "current_subject_for_timer": "General",

        "review_idx": 0,
        "review_show_ans": False,
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_generation_state():
    keys = [
        "generated_result", "generated_model", "generated_label", "generated_tool",
        "generated_chapter", "generated_subject", "generated_topic",
        "generated_course", "generated_stream", "generated_board",
        "generated_audience", "generated_output_style",
        "answers_result", "answers_model",
        "fullpaper_result", "fullpaper_model"
    ]
    for k in keys:
        st.session_state[k] = None

    st.session_state.show_answers = False
    st.session_state.show_fullpaper = False

# ─────────────────────────────────────────────────────────────────────────────
# BASIC HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_courses(category):
    try:
        return list(STUDY_DATA[category].keys())
    except KeyError:
        return []

def get_streams(category, course):
    try:
        return list(STUDY_DATA[category][course].keys())
    except KeyError:
        return []

def get_subjects(category, course, stream):
    try:
        return list(STUDY_DATA[category][course][stream].keys())
    except KeyError:
        return []

def get_topics(category, course, stream, subject):
    try:
        return list(STUDY_DATA[category][course][stream][subject].keys())
    except KeyError:
        return []

def get_chapters(category, course, stream, subject, topic):
    try:
        return STUDY_DATA[category][course][stream][subject][topic]
    except KeyError:
        return ["No chapters found"]

def hash_p(password):
    return hashlib.sha256(password.encode()).hexdigest()

def do_login(username, password):
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return False, "⚠️ Please fill in both fields."

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_p(password))
    )
    user = c.fetchone()
    conn.close()

    if user:
        return True, username
    return False, "❌ Invalid username or password."

def add_to_history(label, chapter, subject, result_preview):
    if "history" not in st.session_state:
        st.session_state.history = []

    entry = {
        "time": time.strftime("%H:%M"),
        "tool": label,
        "chapter": chapter,
        "subject": subject,
        "preview": result_preview[:120] + "..." if len(result_preview) > 120 else result_preview
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:6]

def get_available_models():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ["Error: GEMINI_API_KEY not found"]

    try:
        genai.configure(api_key=api_key)
        working = []
        for m in genai.list_models():
            name = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "gemini" in name.lower() and "generateContent" in methods:
                working.append(name)
        return working if working else ["No models available"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def get_effective_output_name(tool, output_style):
    if output_style == "🧪 Question Paper" or tool == "🧪 Question Paper":
        return "Question Paper"

    if tool == "📝 Summary":
        if output_style == "📋 Notes Format":
            return "Notes"
        if output_style == "📄 Detailed":
            return "Detailed Summary"
        if output_style == "⚡ Short & Quick":
            return "Quick Summary"
        return "Summary"

    if tool == "🧠 Quiz":
        return "Quiz"
    if tool == "📌 Revision Notes":
        return "Revision Notes"
    if tool == "❓ Exam Q&A":
        return "Exam Q&A"

    return "Content"

def get_button_label(tool, output_style):
    name = get_effective_output_name(tool, output_style)
    icons = {
        "Question Paper": "🧪",
        "Notes": "📋",
        "Detailed Summary": "📄",
        "Quick Summary": "⚡",
        "Summary": "📝",
        "Quiz": "🧠",
        "Revision Notes": "📌",
        "Exam Q&A": "❓",
    }
    return f"{icons.get(name, '✨')} Generate {name}"

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def save_flashcard(username, front, back, subject, chapter):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        INSERT INTO flashcards
        (username, front_text, back_text, subject, chapter, next_review_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, front, back, subject, chapter, today))
    conn.commit()
    conn.close()

def get_due_flashcards(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        SELECT id, front_text, back_text, subject, chapter, ease_factor, interval_days, review_count
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
        SELECT id, front_text, back_text, subject, chapter, next_review_date, review_count
        FROM flashcards
        WHERE username=?
        ORDER BY created_date DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_flashcard_review(card_id, performance):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT ease_factor, interval_days, review_count
        FROM flashcards
        WHERE id=?
    """, (card_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return

    ef, interval, review_count = row

    if performance == 1:
        interval = 1
        ef = max(1.3, ef - 0.2)
    elif performance == 2:
        interval = max(1, int(interval * 1.2))
        ef = max(1.3, ef - 0.1)
    elif performance == 3:
        interval = max(1, int(interval * ef))
    elif performance == 4:
        interval = max(1, int(interval * ef * 1.3))
        ef = ef + 0.1

    next_review = (datetime.date.today() + datetime.timedelta(days=interval)).isoformat()

    c.execute("""
        UPDATE flashcards
        SET ease_factor=?, interval_days=?, next_review_date=?, review_count=review_count+1
        WHERE id=?
    """, (round(ef, 2), interval, next_review, card_id))
    conn.commit()
    conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()

def get_earned_badges(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT badge_id FROM achievements WHERE username=?", (username,))
    rows = {r[0] for r in c.fetchall()}
    conn.close()
    return rows
# ─────────────────────────────────────────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────────────────────────────────────────
ALL_BADGES = [
    {"id": "first_login", "name": "First Step", "icon": "👣", "desc": "Logged in for the first time"},
    {"id": "streak_3", "name": "Heatwave", "icon": "🔥", "desc": "Reached a 3-day streak"},
    {"id": "streak_7", "name": "Weekly Warrior", "icon": "🎖️", "desc": "Reached a 7-day streak"},
    {"id": "streak_14", "name": "Fortnight Champ", "icon": "🏆", "desc": "Reached a 14-day streak"},
    {"id": "streak_30", "name": "Monthly Master", "icon": "👑", "desc": "Reached a 30-day streak"},
    {"id": "first_gen", "name": "Starter Spark", "icon": "✨", "desc": "Generated first AI content"},
    {"id": "qp_generated", "name": "Paper Setter", "icon": "📝", "desc": "Generated a question paper"},
    {"id": "quiz_done", "name": "Quiz Taker", "icon": "🧠", "desc": "Generated a quiz"},
]

# ─────────────────────────────────────────────────────────────────────────────
# QUESTION PAPER FORMAT
# ─────────────────────────────────────────────────────────────────────────────
def get_qp_format_spec(board, course, subject):
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
                    {"name": "SECTION A", "type": "MCQ / Objective", "q_count": 20, "marks_each": 1, "total": 20},
                    {"name": "SECTION B", "type": "Very Short Answer", "q_count": 5, "marks_each": 2, "total": 10},
                    {"name": "SECTION C", "type": "Short Answer", "q_count": 6, "marks_each": 3, "total": 18},
                    {"name": "SECTION D", "type": "Long Answer", "q_count": 4, "marks_each": 5, "total": 20},
                    {"name": "SECTION E", "type": "Case Based", "q_count": 3, "marks_each": 4, "total": 12},
                ]
            }

        if any(x in course for x in ["12", "XII", "Class 12"]):
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "BOARD EXAMINATION",
                "class_label": "CLASS XII",
                "total_marks": 70,
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
                    {"name": "SECTION A", "type": "MCQ / Objective", "q_count": 18, "marks_each": 1, "total": 18},
                    {"name": "SECTION B", "type": "Very Short Answer", "q_count": 4, "marks_each": 2, "total": 8},
                    {"name": "SECTION C", "type": "Short Answer", "q_count": 5, "marks_each": 3, "total": 15},
                    {"name": "SECTION D", "type": "Long Answer", "q_count": 2, "marks_each": 5, "total": 10},
                    {"name": "SECTION E", "type": "Case Based", "q_count": 3, "marks_each": 4, "total": 12},
                ]
            }

    if "ICSE" in b:
        return {
            "board_label": "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label": "ICSE EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 80,
            "time": "2 Hours",
            "instructions": [
                "Attempt all from Section A.",
                "Attempt any four from Section B.",
                "Marks in brackets indicate marks."
            ],
            "sections": [
                {"name": "SECTION A", "type": "Compulsory", "q_count": 10, "marks_each": "varied", "total": 40},
                {"name": "SECTION B", "type": "Descriptive", "q_count": 6, "marks_each": 10, "total": 40},
            ]
        }

    return {
        "board_label": "UNIVERSITY EXAMINATIONS",
        "exam_label": f"{course.upper()} EXAMINATION",
        "class_label": course.upper(),
        "total_marks": 100,
        "time": "3 Hours",
        "instructions": [
            "Answer all in Section A.",
            "Answer any five from Section B.",
            "Figures in brackets indicate marks."
        ],
        "sections": [
            {"name": "SECTION A", "type": "Short Answer", "q_count": 10, "marks_each": 2, "total": 20},
            {"name": "SECTION B", "type": "Medium Answer", "q_count": 8, "marks_each": 5, "total": 40},
            {"name": "SECTION C", "type": "Long Answer", "q_count": 4, "marks_each": 10, "total": 40},
        ]
    }

# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────────────
def build_question_paper_prompt(board, course, subject, chapter, topic, audience):
    fmt = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i, x in enumerate(fmt["instructions"])])
    secs = "\n".join([
        f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}"
        for s in fmt["sections"]
    ])

    return f"""
You are an official academic question paper setter.

Generate a CHAPTER-LEVEL question paper.

BOARD: {fmt['board_label']}
EXAM: {fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
SUBJECT: {subject}
TOPIC: {topic}
CHAPTER: {chapter}
TIME: {fmt['time']}
MAXIMUM MARKS: {fmt['total_marks']}

INSTRUCTIONS:
{instr}

STRUCTURE:
{secs}

RULES:
1. Follow the structure exactly.
2. Number all questions clearly.
3. MCQs must have (a), (b), (c), (d).
4. Show marks in square brackets.
5. Do not include answers.
6. Cover the chapter comprehensively.

Generate the complete paper now.
"""

def build_full_subject_qp_prompt(board, course, stream, subject, audience):
    fmt = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i, x in enumerate(fmt["instructions"])])
    secs = "\n".join([
        f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}"
        for s in fmt["sections"]
    ])

    return f"""
You are an official academic question paper setter.

Generate a FULL SUBJECT question paper for the complete syllabus.

BOARD: {fmt['board_label']}
EXAM: {fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
STREAM: {stream}
SUBJECT: {subject}
TIME: {fmt['time']}
MAXIMUM MARKS: {fmt['total_marks']}

INSTRUCTIONS:
{instr}

STRUCTURE:
{secs}

RULES:
1. Cover the full syllabus.
2. Follow official academic format.
3. MCQs must have four options.
4. Do not include answers or hints.

Generate the complete full subject paper now.
"""

def build_answers_prompt(question_paper_text, board, course, subject, chapter):
    return f"""
You are preparing the official answer key for the exact paper below.

BOARD: {board}
COURSE: {course}
SUBJECT: {subject}
CHAPTER: {chapter}

RULES:
1. Answer only the questions from this paper.
2. Keep exact section names and question numbering.
3. MCQs: correct answer plus short explanation.
4. Short answers: concise and correct.
5. Long answers: clear, complete and exam-oriented.

QUESTION PAPER:
{question_paper_text}

Generate the answer key now.
"""

def build_prompt(tool, chapter, topic, subject, audience, output_style, board="", course=""):
    if output_style == "🧪 Question Paper" or tool == "🧪 Question Paper":
        return build_question_paper_prompt(board, course, subject, chapter, topic, audience)

    base = f"""
You are an expert educator creating study material for {audience}.
Subject: {subject}
Topic: {topic}
Chapter: {chapter}

Make it accurate, exam-oriented, structured and easy to revise.
"""

    if tool == "📝 Summary":
        if output_style == "📄 Detailed":
            return base + """
Create a detailed summary with:
- chapter overview
- key concepts
- definitions
- formulas
- 2 examples
- common mistakes
- exam tips
"""
        elif output_style == "⚡ Short & Quick":
            return base + """
Create a quick revision summary with:
- one-line definition
- 5 to 7 key points
- important formulas or facts
- quick exam revision tips
"""
        elif output_style == "📋 Notes Format":
            return base + """
Create structured notes with clear headings, bullets, definitions, examples, and revision points.
"""

    if tool == "🧠 Quiz":
        return base + """
Create:
- 5 MCQs with 4 options and answers
- 5 short-answer questions with answers
- 3 long-answer questions with answers
"""

    if tool == "📌 Revision Notes":
        return base + """
Create revision notes with:
- top 10 must-know points
- formula / fact sheet
- memory tricks
- important comparisons
- exam focus areas
"""

    if tool == "❓ Exam Q&A":
        return base + """
Create an exam Q&A bank with:
- 8 to 10 frequently asked questions with answers
- conceptual questions
- application questions
- why/how questions
"""

    return base + "Create complete study material."

def build_flashcard_prompt(subject, chapter, topic):
    return f"""
You are an expert educator.

Create exactly 10 flashcards for:
Subject: {subject}
Chapter: {chapter}
Topic: {topic}

Strict format:

CARD 1
FRONT: ...
BACK: ...

CARD 2
FRONT: ...
BACK: ...

Continue exactly for 10 cards.
No extra commentary.
"""

# ─────────────────────────────────────────────────────────────────────────────
# AI GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ("⚠️ API key missing! Add GEMINI_API_KEY in secrets.", "None")

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Gemini configuration failed: {str(e)}", "None")

    available = []
    try:
        for m in genai.list_models():
            name = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "gemini" in name.lower() and "generateContent" in methods:
                available.append(name)
    except Exception as e:
        return (f"❌ Could not list models: {str(e)}", "None")

    if not available:
        return ("❌ No Gemini models available.", "None")

    last_error = ""
    for model_name in available:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=8192,
                    top_p=0.9
                )
            )
            if response and getattr(response, "text", None):
                return response.text, model_name
        except Exception as e:
            last_error = str(e)
            continue

    return (f"❌ All models failed. Last error: {last_error}", "None")

def parse_flashcards(raw_text):
    cards = []
    blocks = raw_text.split("CARD ")
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        front = ""
        back = ""

        for line in block.splitlines():
            line = line.strip()
            if line.upper().startswith("FRONT:"):
                front = line[6:].strip()
            elif line.upper().startswith("BACK:"):
                back = line[5:].strip()

        if front and back:
            cards.append({"front": front, "back": back})

    return cards

# ─────────────────────────────────────────────────────────────────────────────
# PDF
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(title, subtitle, content, color_hex="#1d4ed8"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2*cm,
        bottomMargin=2*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(
        title,
        ParagraphStyle(
            "T",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor(color_hex),
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName="Helvetica-Bold"
        )
    ))
    story.append(Paragraph(
        subtitle,
        ParagraphStyle(
            "S",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#64748b"),
            alignment=TA_CENTER,
            spaceAfter=10
        )
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(color_hex), spaceAfter=14))

    body = ParagraphStyle(
        "B",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5
    )
    heading = ParagraphStyle(
        "H",
        parent=styles["Heading2"],
        fontSize=12.5,
        textColor=colors.HexColor(color_hex),
        spaceBefore=10,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.15*cm))
            continue

        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith(("###", "##", "#")):
            story.append(Paragraph(line.lstrip("#").strip(), heading))
        else:
            story.append(Paragraph(safe, body))

    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"), spaceAfter=5))
    story.append(Paragraph(
        f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle(
            "F",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#94a3b8"),
            alignment=TA_CENTER
        )
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ─────────────────────────────────────────────────────────────────────────────
# UI UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def render_top_header(title="StudySmart", subtitle="Your Smart Exam Preparation Platform", show_powered=True):
    watermark_html = '<div class="sf-watermark">POWERED BY AI</div>' if show_powered else ''
    st.markdown(f"""
        <div class="sf-hero">
            <div class="sf-hero-title">{title}</div>
            <div class="sf-hero-subtitle">{subtitle}</div>
            {watermark_html}
        </div>
    """, unsafe_allow_html=True)
def show_dashboard(username):
    stats = get_user_stats(username) or {}

    render_top_header(
        title="StudySmart",
        subtitle="Your Daily Learning Companion"
    )

    st.markdown("""
        <div class="sf-chip-row">
            <div class="sf-chip">🔥 Daily streak motivation</div>
            <div class="sf-chip">📚 Revision made smarter</div>
            <div class="sf-chip">🧠 AI-powered study flow</div>
            <div class="sf-chip">📱 Mobile friendly experience</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "metric-blue", "🔥", stats.get("streak_days", 0), "Current Streak"),
        (c2, "metric-green", "⭐", f"Level {stats.get('level', 1)}", "Progress Level"),
        (c3, "metric-purple", "📚", stats.get("flashcards_due", 0), "Cards Due Today"),
        (c4, "metric-amber", "⏱️", f"{stats.get('weekly_study_minutes', 0)} min", "Weekly Study"),
    ]

    for col, klass, icon, value, label in cards:
        with col:
            st.markdown(f"""
                <div class="metric-card {klass}">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown('<div class="sf-section-title">⭐ XP Progress</div>', unsafe_allow_html=True)

    total_xp = stats.get("total_xp", 0)
    level = stats.get("level", 1)
    level_progress = stats.get("level_progress", 0)
    next_level_xp = stats.get("next_level_xp", 1000)

    progress_pct = 0 if next_level_xp == 0 else min(100, int((level_progress / 1000) * 100))

    st.markdown(f"""
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;font-size:0.88rem;font-weight:600;">
            <span>Level {level}</span>
            <span>{total_xp} XP</span>
        </div>
        <div class="sf-progress-wrap">
            <div class="sf-progress-fill" style="width:{progress_pct}%;"></div>
        </div>
        <div style="margin-top:6px;color:#64748b;font-size:0.82rem;">
            Keep studying daily to unlock more levels and badges.
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<div class="sf-section-title">🌱 Study Momentum</div>', unsafe_allow_html=True)

        total_minutes = stats.get("total_study_minutes", 0)
        growth = min(100, total_minutes // 10)

        if growth < 20:
            plant = "🌱 Seedling"
        elif growth < 40:
            plant = "🌿 Sprout"
        elif growth < 70:
            plant = "🪴 Growing Plant"
        elif growth < 90:
            plant = "🌳 Strong Tree"
        else:
            plant = "🌲 Master Tree"

        st.markdown(f"""
            <div class="sf-soft-card" style="text-align:center;">
                <div style="font-size:3.5rem;">{plant.split()[0]}</div>
                <div style="font-size:1rem;font-weight:800;color:#0f172a;">{plant}</div>
                <div style="margin-top:6px;color:#64748b;font-size:0.86rem;">
                    Your plant grows with every productive study session.
                </div>
                <div style="margin-top:10px;color:#1e293b;font-weight:700;">
                    Total Study Time: {total_minutes} minutes
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<div class="sf-section-title">⚡ Quick Actions</div>', unsafe_allow_html=True)

        if st.button("📚 Open Study Tools", use_container_width=True, key="dash_study"):
            st.session_state.active_page = "study"
            st.rerun()

        if st.button("🗂️ Review Flashcards", use_container_width=True, key="dash_fc"):
            st.session_state.active_page = "flashcards"
            st.rerun()

        if st.button("🏅 View Achievements", use_container_width=True, key="dash_badges"):
            st.session_state.active_page = "achievements"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<div class="sf-section-title">📜 Recent Activity</div>', unsafe_allow_html=True)

        if not st.session_state.history:
            st.info("No recent study activity yet. Start generating content to populate your timeline.")
        else:
            for item in st.session_state.history:
                st.markdown(f"""
                    <div class="sf-history-item">
                        🕐 {item['time']} &nbsp;|&nbsp; <b>{item['tool']}</b><br/>
                        📖 {item['chapter']} — {item['subject']}<br/>
                        <small>{item['preview']}</small>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        earned = get_earned_badges(username)
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown('<div class="sf-section-title">🏅 Badge Snapshot</div>', unsafe_allow_html=True)

        earned_badges = [b for b in ALL_BADGES if b["id"] in earned][:4]
        if earned_badges:
            cols = st.columns(2)
            for i, badge in enumerate(earned_badges):
                with cols[i % 2]:
                    st.markdown(f"""
                        <div class="badge-card earned">
                            <div class="badge-icon">{badge['icon']}</div>
                            <div class="badge-name">{badge['name']}</div>
                            <div class="badge-status">✅ Earned</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Your first badges will appear here as you use the app consistently.")

        st.markdown('</div>', unsafe_allow_html=True)

def show_flashcards(username):
    render_top_header(
        title="Flashcards",
        subtitle="Daily review with spaced repetition"
    )

    tab1, tab2, tab3 = st.tabs(["📖 Review Due", "➕ Create", "📋 My Library"])

    with tab1:
        due_cards = get_due_flashcards(username)

        if not due_cards:
            st.success("🎉 No flashcards due today. You're fully caught up!")
        else:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.write(f"**{len(due_cards)} card(s)** are due today.")

            idx = st.session_state.review_idx
            if idx >= len(due_cards):
                st.success("✅ Review complete for today!")
                if st.button("🔄 Restart Review", use_container_width=True):
                    st.session_state.review_idx = 0
                    st.session_state.review_show_ans = False
                    st.rerun()
            else:
                card = due_cards[idx]
                card_id, front, back, subject, chapter = card[0], card[1], card[2], card[3], card[4]

                st.progress((idx + 1) / len(due_cards))
                st.caption(f"Card {idx + 1} of {len(due_cards)} | {subject} | {chapter}")

                if not st.session_state.review_show_ans:
                    st.markdown(f"""
                        <div class="flashcard-front">
                            <div style="font-size:0.82rem;opacity:0.85;margin-bottom:10px;">QUESTION</div>
                            <div style="font-size:1.15rem;font-weight:700;line-height:1.5;">{front}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.button("👁️ Reveal Answer", use_container_width=True):
                        st.session_state.review_show_ans = True
                        st.rerun()
                else:
                    st.markdown(f"""
                        <div class="flashcard-back">
                            <div style="font-size:0.82rem;opacity:0.85;margin-bottom:10px;">ANSWER</div>
                            <div style="font-size:1.08rem;font-weight:700;line-height:1.5;">{back}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("**How well did you remember this?**")
                    r1, r2, r3, r4 = st.columns(4)

                    with r1:
                        if st.button("😓 Again", use_container_width=True, key=f"again_{card_id}"):
                            update_flashcard_review(card_id, 1)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()

                    with r2:
                        if st.button("😐 Hard", use_container_width=True, key=f"hard_{card_id}"):
                            update_flashcard_review(card_id, 2)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()

                    with r3:
                        if st.button("🙂 Good", use_container_width=True, key=f"good_{card_id}"):
                            update_flashcard_review(card_id, 3)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()

                    with r4:
                        if st.button("😄 Easy", use_container_width=True, key=f"easy_{card_id}"):
                            update_flashcard_review(card_id, 4)
                            st.session_state.review_idx += 1
                            st.session_state.review_show_ans = False
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        left, right = st.columns(2)

        with left:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### ✍️ Create Manually")
            with st.form("manual_flashcard_form"):
                front = st.text_input("Front")
                back = st.text_area("Back", height=90)
                subject = st.text_input("Subject")
                chapter = st.text_input("Chapter")
                manual_submit = st.form_submit_button("➕ Save Flashcard", use_container_width=True)

            if manual_submit:
                if front.strip() and back.strip():
                    save_flashcard(username, front.strip(), back.strip(), subject.strip(), chapter.strip())
                    award_xp(username, 5)
                    st.success("✅ Flashcard saved.")
                else:
                    st.warning("⚠️ Front and Back are required.")
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### 🤖 Generate with AI")
            with st.form("ai_flashcard_form"):
                ai_subject = st.text_input("Subject", placeholder="e.g. Physics")
                ai_chapter = st.text_input("Chapter", placeholder="e.g. Laws of Motion")
                ai_topic = st.text_input("Topic", placeholder="e.g. Force and inertia")
                ai_submit = st.form_submit_button("⚡ Generate 10 Flashcards", use_container_width=True)

            if ai_submit:
                if ai_subject.strip() and ai_chapter.strip():
                    with st.spinner("Generating flashcards..."):
                        raw, model = generate_with_fallback(
                            build_flashcard_prompt(ai_subject.strip(), ai_chapter.strip(), ai_topic.strip())
                        )
                    if model != "None":
                        cards = parse_flashcards(raw)
                        if cards:
                            for card in cards:
                                save_flashcard(
                                    username,
                                    card["front"],
                                    card["back"],
                                    ai_subject.strip(),
                                    ai_chapter.strip()
                                )
                            award_xp(username, len(cards) * 5)
                            st.success(f"✅ {len(cards)} flashcards created successfully.")
                        else:
                            st.warning("⚠️ AI response could not be parsed into flashcards.")
                    else:
                        st.error("❌ Flashcard generation failed.")
                else:
                    st.warning("⚠️ Subject and Chapter are required.")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        cards = get_all_flashcards(username)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        if not cards:
            st.info("No flashcards saved yet.")
        else:
            st.caption(f"Total flashcards: {len(cards)}")
            for row in cards:
                c_id, front, back, subject, chapter, next_review, review_count = row
                with st.expander(f"📌 {front[:70]}{'...' if len(front) > 70 else ''}"):
                    st.markdown(f"**Front:** {front}")
                    st.markdown(f"**Back:** {back}")
                    st.caption(f"Subject: {subject} | Chapter: {chapter} | Next review: {next_review} | Reviews: {review_count}")
                    if st.button("🗑️ Delete Flashcard", key=f"delete_fc_{c_id}"):
                        delete_flashcard(c_id)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def show_achievements(username):
    render_top_header(
        title="Achievements",
        subtitle="Track your progress and earn badges"
    )

    earned = get_earned_badges(username)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.write(f"**{len(earned)} / {len(ALL_BADGES)} badges earned**")
    st.progress(len(earned) / len(ALL_BADGES))
    st.markdown('</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, badge in enumerate(ALL_BADGES):
        with cols[i % 4]:
            is_earned = badge["id"] in earned
            st.markdown(f"""
                <div class="badge-card {'earned' if is_earned else ''}">
                    <div class="badge-icon">{badge['icon'] if is_earned else '🔒'}</div>
                    <div class="badge-name">{badge['name']}</div>
                    <div class="badge-status">{'✅ Earned' if is_earned else badge['desc']}</div>
                </div>
            """, unsafe_allow_html=True)

def render_sidebar(username):
    stats = get_user_stats(username) or {}

    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:10px 0 14px 0;">
                <div style="font-size:2.35rem;">🎓</div>
                <div style="font-size:1.15rem;font-weight:800;color:#2563eb;">StudySmart AI</div>
                <div style="font-size:0.82rem;color:#64748b;margin-top:4px;">Welcome, {username} 👋</div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.metric("🔥 Streak", f"{stats.get('streak_days', 0)} days")
        with c2:
            st.metric("⭐ Level", stats.get("level", 1))

        if not st.session_state.daily_checkin_done:
            if st.button("✅ Daily Check-in", use_container_width=True):
                result = check_daily_login(username)
                st.session_state.daily_checkin_done = True
                st.success(result.get("message", "Checked in successfully!"))
                st.rerun()
        else:
            st.success("✅ Daily check-in complete")

        st.divider()

        st.markdown("**⏱️ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed = int((datetime.datetime.now() - st.session_state.study_timer_start).total_seconds() // 60)
            st.info(f"Running: {elapsed} min")
            if st.button("⏹️ Stop Timer", use_container_width=True):
                st.session_state.study_timer_active = False
                duration = max(1, elapsed)
                record_study_session(
                    username,
                    st.session_state.get("current_subject_for_timer", "General"),
                    "study",
                    duration
                )
                award_xp(username, (duration // 10) * 10 if duration >= 10 else 5)
                st.session_state.study_timer_start = None
                st.success(f"✅ Recorded {duration} minutes.")
                st.rerun()
        else:
            if st.button("▶️ Start Timer", use_container_width=True):
                st.session_state.study_timer_active = True
                st.session_state.study_timer_start = datetime.datetime.now()
                st.rerun()

        st.divider()

        nav = st.radio(
            "Navigate",
            ["📊 Dashboard", "📚 Study Tools", "🗂️ Flashcards", "🏅 Achievements"]
        )

        page_map = {
            "📊 Dashboard": "dashboard",
            "📚 Study Tools": "study",
            "🗂️ Flashcards": "flashcards",
            "🏅 Achievements": "achievements",
        }

        if st.session_state.active_page != page_map[nav]:
            st.session_state.active_page = page_map[nav]
            st.rerun()

        st.divider()

        with st.expander("📜 Recent History"):
            if not st.session_state.history:
                st.caption("No history yet.")
            else:
                for h in st.session_state.history:
                    st.markdown(f"""
                        <div class="sf-history-item">
                            🕐 {h['time']} &nbsp;|&nbsp; <b>{h['tool']}</b><br/>
                            📖 {h['chapter']} — {h['subject']}<br/>
                            <small>{h['preview']}</small>
                        </div>
                    """, unsafe_allow_html=True)

        with st.expander("🤖 AI Model Status"):
            if st.button("Check Models", use_container_width=True):
                with st.spinner("Checking..."):
                    models = get_available_models()
                for m in models:
                    st.write(f"✅ {m}")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
def show_study_tools(username):
    render_top_header(
        title="Study Tools",
        subtitle="Professional AI support for smarter exam preparation"
    )

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)

    tool = st.radio(
        "Select Tool",
        ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "🧪 Question Paper", "❓ Exam Q&A"],
        horizontal=True
    )

    if not STUDY_DATA:
        st.error("No study data found.")
        st.stop()

    c1, c2 = st.columns([1.4, 1])
    with c1:
        category = st.selectbox("📚 Category", list(STUDY_DATA.keys()))
    with c2:
        st.markdown("""
            <div class="sf-soft-card" style="height:100%;">
                <div style="font-weight:800;color:#0f172a;margin-bottom:6px;">Study Setup</div>
                <div style="font-size:0.86rem;color:#64748b;">
                    Choose your academic path below and generate precise learning material instantly.
                </div>
            </div>
        """, unsafe_allow_html=True)

    course = st.selectbox("🎓 Program / Class", get_courses(category))
    stream = st.selectbox("📖 Stream", get_streams(category, course))
    subject = st.selectbox("🧾 Subject", get_subjects(category, course, stream))

    if category == "K-12th":
        board = st.selectbox("🏫 Board", BOARDS)
    else:
        board = "University / National Syllabus"
        st.info(f"📌 Syllabus: {board}")

    topic = st.selectbox("🗂️ Topic", get_topics(category, course, stream, subject))

    chapter_key = f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key
        reset_generation_state()

    chapter = st.selectbox("📝 Chapter", st.session_state.current_chapters)
    st.session_state.current_subject_for_timer = subject

    st.markdown('</div>', unsafe_allow_html=True)

    output_style = st.radio(
        "⚙️ Output Style",
        ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format", "🧪 Question Paper"],
        horizontal=True
    )

    effective_label = get_effective_output_name(tool, output_style)
    btn_label = get_button_label(tool, output_style)

    if st.button(btn_label, use_container_width=True):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter first.")
            return

        audience = f"{board} {course} students" if category == "K-12th" else f"{course} students"

        prompt = build_prompt(
            tool, chapter, topic, subject, audience,
            output_style, board=board, course=course
        )

        with st.spinner(f"Generating {effective_label}..."):
            result, model_used = generate_with_fallback(prompt)

        st.session_state.update({
            "generated_result": result,
            "generated_model": model_used,
            "generated_label": effective_label,
            "generated_tool": tool,
            "generated_chapter": chapter,
            "generated_subject": subject,
            "generated_topic": topic,
            "generated_course": course,
            "generated_stream": stream,
            "generated_board": board,
            "generated_audience": audience,
            "generated_output_style": output_style,
            "answers_result": None,
            "answers_model": None,
            "show_answers": False,
            "fullpaper_result": None,
            "fullpaper_model": None,
            "show_fullpaper": False,
        })

        if model_used != "None":
            add_to_history(effective_label, chapter, subject, result)
            award_xp(username, 25)
            award_badge(username, "first_gen")

            if effective_label == "Question Paper":
                award_badge(username, "qp_generated")
            if effective_label == "Quiz":
                award_badge(username, "quiz_done")

    if st.session_state.generated_result and st.session_state.generated_model != "None":
        result = st.session_state.generated_result
        g_label = st.session_state.generated_label
        g_chapter = st.session_state.generated_chapter
        g_subject = st.session_state.generated_subject
        g_topic = st.session_state.generated_topic
        g_course = st.session_state.generated_course
        g_stream = st.session_state.generated_stream
        g_board = st.session_state.generated_board
        g_audience = st.session_state.generated_audience

        st.markdown('<div class="sf-output">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        if g_label != "Question Paper":
            if st.button("🗂️ Save Key Points as Flashcards", use_container_width=True):
                with st.spinner("Generating flashcards..."):
                    raw, model = generate_with_fallback(
                        build_flashcard_prompt(g_subject, g_chapter, g_topic)
                    )
                if model != "None":
                    cards = parse_flashcards(raw)
                    for card in cards:
                        save_flashcard(username, card["front"], card["back"], g_subject, g_chapter)
                    award_xp(username, len(cards) * 5 if cards else 0)
                    st.success(f"✅ {len(cards)} flashcards saved.")
                else:
                    st.error("❌ Flashcard generation failed.")

        if g_label == "Question Paper":
            try:
                qp_pdf = generate_pdf(
                    f"Question Paper — {g_chapter}",
                    f"{g_subject} | {g_board} | {g_course}",
                    result,
                    "#1d4ed8"
                )
                safe_qp = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + "_QP.pdf"
                st.download_button(
                    "⬇️ Download Question Paper PDF",
                    data=qp_pdf,
                    file_name=safe_qp,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"⚠️ PDF generation error: {e}")

            if st.button("📋 Get Answers for this Paper", use_container_width=True):
                with st.spinner("Generating answer key..."):
                    ans_r, ans_m = generate_with_fallback(
                        build_answers_prompt(result, g_board, g_course, g_subject, g_chapter)
                    )
                st.session_state.answers_result = ans_r
                st.session_state.answers_model = ans_m
                st.session_state.show_answers = True

            if st.session_state.show_answers and st.session_state.answers_result:
                if st.session_state.answers_model != "None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 📚 Answer Key — {g_chapter}")
                    st.markdown(st.session_state.answers_result)
                    st.markdown('</div>', unsafe_allow_html=True)

            st.info(f"💡 Need a full **{g_subject}** paper covering the whole syllabus in **{g_board}** format?")

            if st.button(f"🗂️ Generate Full {g_subject} Question Paper", use_container_width=True):
                with st.spinner("Generating full subject paper..."):
                    full_r, full_m = generate_with_fallback(
                        build_full_subject_qp_prompt(g_board, g_course, g_stream, g_subject, g_audience)
                    )
                st.session_state.fullpaper_result = full_r
                st.session_state.fullpaper_model = full_m
                st.session_state.show_fullpaper = True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Paper — {g_subject}")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)

        else:
            try:
                pdf = generate_pdf(
                    f"{g_label} — {g_chapter}",
                    f"{g_subject} | {g_topic} | {g_course}",
                    result
                )
                safe = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + ".pdf"
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf,
                    file_name=safe,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"⚠️ PDF generation error: {e}")

    elif st.session_state.generated_result and st.session_state.generated_model == "None":
        st.error("❌ AI generation failed")
        st.markdown(st.session_state.generated_result)

def auth_ui():
    _, col, _ = st.columns([1, 1.6, 1])

    with col:
        render_top_header(
            title="StudySmart",
            subtitle="Your Smart Exam Preparation Platform"
        )

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("👤 Username", placeholder="Enter your username", key="login_u")
                p = st.text_input(
                    "🔑 Password",
                    type="password",
                    placeholder="Enter password — press Enter to login",
                    key="login_p"
                )
                submitted = st.form_submit_button("Sign In 🚀", use_container_width=True)

            if submitted:
                success, result = do_login(u, p)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = result
                    check_result = check_daily_login(result)
                    st.session_state.daily_checkin_done = True
                    st.success(f"✅ Login successful! {check_result.get('message', '')}")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.error(result)

        with tab2:
            with st.form("register_form", clear_on_submit=True):
                nu = st.text_input("👤 New Username", placeholder="Minimum 3 characters", key="reg_u")
                np = st.text_input("🔑 New Password", type="password", placeholder="Minimum 6 characters", key="reg_p")
                cp = st.text_input("🔑 Confirm Password", type="password", placeholder="Re-enter your password", key="reg_cp")
                reg_submitted = st.form_submit_button("Create Account ✨", use_container_width=True)

            if reg_submitted:
                if not nu.strip():
                    st.error("❌ Username cannot be empty")
                elif len(nu.strip()) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif len(np.strip()) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif np != cp:
                    st.error("❌ Passwords do not match")
                else:
                    try:
                        conn = sqlite3.connect("users.db")
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO users (username, password) VALUES (?, ?)",
                            (nu.strip(), hash_p(np))
                        )
                        conn.commit()
                        conn.close()

                        st.session_state.logged_in = True
                        st.session_state.username = nu.strip()
                        check_daily_login(nu.strip())
                        st.session_state.daily_checkin_done = True

                        st.success("✅ Account created successfully!")
                        time.sleep(0.8)
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists. Please choose another.")

        st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    render_sidebar(st.session_state.username)

    if st.session_state.active_page == "dashboard":
        show_dashboard(st.session_state.username)
    elif st.session_state.active_page == "study":
        show_study_tools(st.session_state.username)
    elif st.session_state.active_page == "flashcards":
        show_flashcards(st.session_state.username)
    elif st.session_state.active_page == "achievements":
        show_achievements(st.session_state.username)
    else:
        show_dashboard(st.session_state.username)

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
