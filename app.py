# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — app.py  (Complete · Self-Contained · All Fixes Applied)
# ✅ Streak works  ✅ Timer saves weekly minutes  ✅ Badges auto-unlock
# ✅ No flashcard library banner  ✅ No external daily_engagement.py needed
# ✅ Quick Actions clickable  ✅ Lighter dark mode  ✅ Mobile friendly
# ✅ Registration closed  ✅ Whitelisted login
# ✅ BUG FIXES: auth_ui nested def, init_db order, badge ID mismatch,
#              column layout, do_login whitelist enforcement
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
reportlab.lib.units import cm
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
# DATA LOADER
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
BOARDS     = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge"]

# ─────────────────────────────────────────────────────────────────────────────
# CSS
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
.sf-hero-sub  { color:#475569 !important; font-size:.94rem; font-weight:500; margin-top:4px; }
.sf-powered   {
    display:inline-block; margin-top:8px;
    background:rgba(37,99,235,.08); color:#2563eb !important;
    font-size:.72rem; font-weight:700; letter-spacing:.08em;
    padding:3px 12px; border-radius:999px;
}

/* ── Cards ── */
.sf-card {
    background:#ffffff !important; border:1px solid #dde5f0 !important;
    border-radius:16px !important; padding:16px 18px !important;
    margin-bottom:14px !important; color:#0f172a !important;
    box-shadow:0 4px 16px rgba(15,23,42,.05) !important;
}
.sf-card *,.sf-card p,.sf-card span,.sf-card li,.sf-card strong,.sf-card small { color:#0f172a !important; }
.sf-soft-card {
    background:#f8fbff !important; border:1px solid #e2e8f0 !important;
    border-radius:12px !important; padding:12px 14px !important;
    margin-bottom:10px !important;
}
.sf-soft-card * { color:#0f172a !important; }

/* ── Metric Cards ── */
.mc {
    border-radius:14px !important; padding:14px 10px !important;
    text-align:center !important; margin-bottom:10px !important;
    color:white !important; font-weight:700 !important;
}
.mc-blue   { background:linear-gradient(135deg,#3b82f6,#2563eb); }
.mc-green  { background:linear-gradient(135deg,#10b981,#059669); }
.mc-purple { background:linear-gradient(135deg,#8b5cf6,#7c3aed); }
.mc-amber  { background:linear-gradient(135deg,#f59e0b,#d97706); }
.mc .icon  { font-size:1.25rem; }
.mc .val   { font-size:1.45rem; font-weight:800; margin:3px 0; }
.mc .lbl   { font-size:.75rem; opacity:.93; }

/* ── XP bar ── */
.xp-wrap { background:#e2e8f0; border-radius:999px; height:10px; overflow:hidden; }
.xp-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,#3b82f6,#8b5cf6); }

/* ── History ── */
.sf-hist {
    background:#f8fbff !important; border:1px solid #e2e8f0 !important;
    border-left:4px solid #3b82f6 !important; border-radius:12px !important;
    padding:9px 12px !important; margin-bottom:8px !important;
    font-size:.84rem !important; color:#0f172a !important;
}
.sf-hist * { color:#0f172a !important; }
.sf-hist b { color:#1d4ed8 !important; }
.sf-hist small { color:#475569 !important; }

/* ── Output boxes ── */
.sf-output {
    background:#eff6ff !important; border:1px solid #bfdbfe !important;
    border-left:4px solid #2563eb !important; border-radius:14px !important;
    padding:18px 20px !important; margin-top:12px !important; color:#0f172a !important;
}
.sf-output *,.sf-output p,.sf-output li,.sf-output span,.sf-output strong { color:#0f172a !important; }
.sf-output h1,.sf-output h2,.sf-output h3 { color:#1d4ed8 !important; }

.sf-answers {
    background:#f0fdf4 !important; border:1px solid #bbf7d0 !important;
    border-left:4px solid #16a34a !important; border-radius:14px !important;
    padding:18px 20px !important; margin-top:12px !important; color:#0f172a !important;
}
.sf-answers *,.sf-answers p,.sf-answers li,.sf-answers span,.sf-answers strong { color:#0f172a !important; }
.sf-answers h1,.sf-answers h2,.sf-answers h3 { color:#15803d !important; }

.sf-fullpaper {
    background:#faf5ff !important; border:1px solid #ddd6fe !important;
    border-left:4px solid #7c3aed !important; border-radius:14px !important;
    padding:18px 20px !important; margin-top:12px !important; color:#0f172a !important;
}
.sf-fullpaper *,.sf-fullpaper p,.sf-fullpaper li,.sf-fullpaper span,.sf-fullpaper strong { color:#0f172a !important; }
.sf-fullpaper h1,.sf-fullpaper h2,.sf-fullpaper h3 { color:#6d28d9 !important; }

/* ── Flashcards ── */
.fc-front {
    background:linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    border-radius:16px; padding:24px 18px; color:white !important;
    text-align:center; min-height:155px;
    box-shadow:0 10px 26px rgba(79,70,229,.24);
}
.fc-front * { color:white !important; }
.fc-back {
    background:linear-gradient(135deg,#059669,#10b981) !important;
    border-radius:16px; padding:24px 18px; color:white !important;
    text-align:center; min-height:155px;
    box-shadow:0 10px 26px rgba(16,185,129,.22);
}
.fc-back * { color:white !important; }

/* ── Badges ── */
.bdg {
    background:#ffffff !important; border:1px solid #e2e8f0 !important;
    border-radius:14px !important; padding:12px 8px !important;
    text-align:center !important; margin-bottom:10px !important;
    box-shadow:0 4px 12px rgba(15,23,42,.04) !important; color:#0f172a !important;
}
.bdg * { color:#0f172a !important; }
.bdg.earned { border-color:#f59e0b !important; background:#fffbeb !important; }
.bdg .bi  { font-size:1.85rem; }
.bdg .bn  { font-weight:700; font-size:.82rem; margin-top:4px; color:#0f172a !important; }
.bdg .bs  { font-size:.72rem; color:#475569 !important; margin-top:2px; }

/* ── Selectbox ── */
div[data-baseweb="select"] > div:first-child {
    border:1.5px solid #c7d4e8 !important; border-radius:11px !important;
    background:#ffffff !important; min-height:42px !important;
}
div[data-baseweb="select"] > div > div > div { color:#0f172a !important; }
div[data-baseweb="select"] svg {
    fill:#64748b !important; display:block !important;
    visibility:visible !important; opacity:1 !important;
}
div[data-baseweb="popover"] {
    background:#ffffff !important; border:1px solid #e2e8f0 !important;
    border-radius:11px !important; box-shadow:0 8px 24px rgba(0,0,0,.08) !important;
}
div[role="option"] { color:#0f172a !important; background:#ffffff !important; }
div[role="option"]:hover { background:#eff6ff !important; color:#1d4ed8 !important; }

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
div[data-testid="stErrorMessage"] p   { color:#7f1d1d !important; }
div[data-testid="stInfoMessage"],div[data-testid="stInfoMessage"] *,
div[data-testid="stInfoMessage"] p    { color:#1e3a5f !important; }
div[data-testid="stSuccessMessage"],div[data-testid="stWarningMessage"],
div[data-testid="stErrorMessage"],div[data-testid="stInfoMessage"] { border-radius:11px !important; }

/* ── Radio ── */
.stRadio [data-testid="stMarkdownContainer"] p { color:#0f172a !important; }
.stRadio > div > div > label > div { color:#0f172a !important; }

/* ── Expander ── */
.streamlit-expanderHeader,.streamlit-expanderHeader p,
.streamlit-expanderHeader span { color:#0f172a !important; font-weight:600 !important; }
.streamlit-expanderContent,.streamlit-expanderContent * { color:#0f172a !important; }
[data-testid="stCaptionContainer"] p { color:#475569 !important; }

/* ══════════ DARK MODE ══════════ */
@media (prefers-color-scheme:dark) {
    .stApp { background:linear-gradient(160deg,#1a2235 0%,#1e2a3a 55%,#1c2840 100%) !important; color:#e2e8f0 !important; }
    .stApp p,.stApp span,.stApp li,.stApp label,
    .stApp div,.stApp strong,.stApp small,
    .stApp h1,.stApp h2,.stApp h3,.stApp h4 { color:#e2e8f0 !important; }
    [data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] *,
    [data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] * { color:#e2e8f0 !important; }
    .sf-card { background:#243045 !important; border-color:#2e3f58 !important; }
    .sf-card *,.sf-card p,.sf-card span,.sf-card li,.sf-card strong,.sf-card small { color:#e2e8f0 !important; }
    .sf-soft-card { background:#1f2e42 !important; border-color:#2a3c54 !important; }
    .sf-soft-card * { color:#e2e8f0 !important; }
    .sf-hist { background:#243045 !important; border-color:#2e3f58 !important; border-left-color:#3b82f6 !important; color:#e2e8f0 !important; }
    .sf-hist * { color:#e2e8f0 !important; } .sf-hist b { color:#93c5fd !important; } .sf-hist small { color:#94a3b8 !important; }
    .sf-output { background:#1e2f4a !important; border-color:#2d4a7a !important; border-left-color:#3b82f6 !important; }
    .sf-output *,.sf-output p,.sf-output li,.sf-output span,.sf-output strong { color:#e2e8f0 !important; }
    .sf-output h1,.sf-output h2,.sf-output h3 { color:#93c5fd !important; }
    .sf-answers { background:#1a3628 !important; border-color:#1e4d2e !important; border-left-color:#16a34a !important; }
    .sf-answers *,.sf-answers p,.sf-answers li,.sf-answers span,.sf-answers strong { color:#e2e8f0 !important; }
    .sf-answers h1,.sf-answers h2,.sf-answers h3 { color:#86efac !important; }
    .sf-fullpaper { background:#251a40 !important; border-color:#3d2a6e !important; border-left-color:#7c3aed !important; }
    .sf-fullpaper *,.sf-fullpaper p,.sf-fullpaper li,.sf-fullpaper span,.sf-fullpaper strong { color:#e2e8f0 !important; }
    .sf-fullpaper h1,.sf-fullpaper h2,.sf-fullpaper h3 { color:#c4b5fd !important; }
    .bdg { background:#243045 !important; border-color:#2e3f58 !important; }
    .bdg * { color:#e2e8f0 !important; } .bdg .bn { color:#f1f5f9 !important; } .bdg .bs { color:#94a3b8 !important; }
    .bdg.earned { background:#2a2010 !important; border-color:#b45309 !important; }
    [data-testid="stSidebar"] { background:#182030 !important; border-right-color:#243045 !important; }
    [data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label,[data-testid="stSidebar"] div,[data-testid="stSidebar"] strong { color:#e2e8f0 !important; }
    div[data-baseweb="select"] > div:first-child { background:#243045 !important; border-color:#3a506e !important; }
    div[data-baseweb="select"] > div > div > div { color:#e2e8f0 !important; }
    div[data-baseweb="select"] svg { fill:#94a3b8 !important; }
    div[data-baseweb="popover"] { background:#243045 !important; border-color:#2e3f58 !important; }
    div[role="option"] { background:#243045 !important; color:#e2e8f0 !important; }
    div[role="option"]:hover { background:#2e3f58 !important; color:#ffffff !important; }
    input[type="text"],input[type="password"],textarea { color:#e2e8f0 !important; background:#243045 !important; }
    [data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label,
    .stTextInput label,.stSelectbox label,.stRadio label,.stTextArea label { color:#e2e8f0 !important; }
    .stRadio [data-testid="stMarkdownContainer"] p { color:#e2e8f0 !important; }
    .stTabs [data-baseweb="tab"] { color:#94a3b8 !important; }
    .stTabs [aria-selected="true"] { color:#f1f5f9 !important; border-bottom-color:#3b82f6 !important; }
    .streamlit-expanderHeader,.streamlit-expanderHeader p,.streamlit-expanderHeader span { color:#e2e8f0 !important; }
    .streamlit-expanderContent,.streamlit-expanderContent * { color:#e2e8f0 !important; }
    .sf-hero-sub { color:#94a3b8 !important; }
    .sf-powered { background:rgba(59,130,246,.15) !important; color:#93c5fd !important; }
    .xp-wrap { background:#2e3f58 !important; }
    div[data-testid="stSuccessMessage"],div[data-testid="stSuccessMessage"] *,
    div[data-testid="stSuccessMessage"] p { color:#d1fae5 !important; }
    div[data-testid="stWarningMessage"],div[data-testid="stWarningMessage"] *,
    div[data-testid="stWarningMessage"] p { color:#fef3c7 !important; }
    div[data-testid="stErrorMessage"],div[data-testid="stErrorMessage"] *,
    div[data-testid="stErrorMessage"] p   { color:#fee2e2 !important; }
    div[data-testid="stInfoMessage"],div[data-testid="stInfoMessage"] *,
    div[data-testid="stInfoMessage"] p    { color:#dbeafe !important; }
}
[data-theme="dark"] .stApp { background:linear-gradient(160deg,#1a2235 0%,#1e2a3a 55%,#1c2840 100%) !important; }
[data-theme="dark"] .sf-card { background:#243045 !important; border-color:#2e3f58 !important; }
[data-theme="dark"] .sf-card *,[data-theme="dark"] .sf-card p { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-soft-card { background:#1f2e42 !important; }
[data-theme="dark"] .sf-soft-card * { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-hist { background:#243045 !important; border-color:#2e3f58 !important; border-left-color:#3b82f6 !important; }

/* ── Mobile ── */
@media (max-width:768px) {
    .sf-hero-title { font-size:1.8rem !important; }
    .block-container { padding-left:.5rem !important; padding-right:.5rem !important; }
    .sf-card { padding:12px 10px !important; }
    div[role="option"] { min-height:46px !important; padding:12px 14px !important; font-size:15px !important; }
    .stButton > button,.stFormSubmitButton > button,.stDownloadButton > button {
        height:3rem !important; font-size:.92rem !important;
    }
    .stTabs [data-baseweb="tab-list"] { overflow-x:auto !important; flex-wrap:nowrap !important; }
    .stTabs [data-baseweb="tab"] { white-space:nowrap !important; font-size:.82rem !important; padding:8px 10px !important; }
    .sf-output,.sf-answers,.sf-fullpaper { padding:13px 11px !important; border-radius:12px !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE  — fully self-contained, no external daily_engagement.py
# FIX: helper functions defined BEFORE conn.commit()/conn.close() is called
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Core tables
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            username TEXT PRIMARY KEY,
            total_xp INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_login TEXT DEFAULT '',
            total_minutes INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            username TEXT,
            badge_id TEXT,
            earned_at TEXT,
            PRIMARY KEY (username, badge_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            front_text TEXT,
            back_text TEXT,
            subject TEXT DEFAULT '',
            chapter TEXT DEFAULT '',
            ease_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            next_review_date TEXT,
            review_count INTEGER DEFAULT 0,
            created_date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            subject TEXT,
            minutes INTEGER DEFAULT 0,
            sess_date TEXT
        )
    """)

    # ── FIX: define helpers BEFORE calling them ──
    def get_columns(table_name):
        c.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in c.fetchall()]

    def add_column_if_missing(table_name, column_name, column_def):
        cols = get_columns(table_name)
        if column_name not in cols:
            c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")

    # user_stats migrations
    add_column_if_missing("user_stats", "total_xp",     "INTEGER DEFAULT 0")
    add_column_if_missing("user_stats", "streak_days",  "INTEGER DEFAULT 0")
    add_column_if_missing("user_stats", "last_login",   "TEXT DEFAULT ''")
    add_column_if_missing("user_stats", "total_minutes","INTEGER DEFAULT 0")

    # achievements migrations
    add_column_if_missing("achievements", "earned_at", "TEXT")

    # flashcards migrations
    add_column_if_missing("flashcards", "subject",          "TEXT DEFAULT ''")
    add_column_if_missing("flashcards", "chapter",          "TEXT DEFAULT ''")
    add_column_if_missing("flashcards", "ease_factor",      "REAL DEFAULT 2.5")
    add_column_if_missing("flashcards", "interval_days",    "INTEGER DEFAULT 1")
    add_column_if_missing("flashcards", "next_review_date", "TEXT")
    add_column_if_missing("flashcards", "review_count",     "INTEGER DEFAULT 0")
    add_column_if_missing("flashcards", "created_date",     "TEXT")

    # study_sessions migrations
    add_column_if_missing("study_sessions", "subject",   "TEXT")
    add_column_if_missing("study_sessions", "minutes",   "INTEGER DEFAULT 0")
    add_column_if_missing("study_sessions", "sess_date", "TEXT")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STREAK + XP HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _ensure_stats(username, c):
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))

def check_daily_login(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    today     = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute("""
        SELECT COALESCE(streak_days, 0), COALESCE(last_login, '')
        FROM user_stats WHERE username=?
    """, (username,))
    row = c.fetchone()
    streak_days, last_login = row if row else (0, "")

    if last_login == today:
        conn.close()
        return f"🔥 {streak_days} Day Streak!"

    streak_days = streak_days + 1 if last_login == yesterday else 1

    c.execute("""
        UPDATE user_stats
        SET streak_days=?, last_login=?, total_xp=COALESCE(total_xp,0)+20
        WHERE username=?
    """, (streak_days, today, username))

    conn.commit()
    conn.close()
    return f"🔥 Streak Updated! Day {streak_days} (+20 XP)"


def award_xp(username, amount):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    _ensure_stats(username, c)
    c.execute("UPDATE user_stats SET total_xp = total_xp + ? WHERE username=?", (amount, username))
    conn.commit(); conn.close()

def get_user_stats(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute("""
        SELECT COALESCE(total_xp,0), COALESCE(streak_days,0), COALESCE(total_minutes,0)
        FROM user_stats WHERE username=?
    """, (username,))
    row = c.fetchone()
    total_xp, streak_days, total_minutes = row if row else (0, 0, 0)

    # weekly minutes
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    c.execute("""
        SELECT COALESCE(SUM(minutes),0) FROM study_sessions
        WHERE username=? AND sess_date>=?
    """, (username, week_ago))
    weekly_minutes = c.fetchone()[0]

    # flashcards due
    today = datetime.date.today().isoformat()
    c.execute("""
        SELECT COUNT(*) FROM flashcards
        WHERE username=? AND next_review_date<=?
    """, (username, today))
    flashcards_due = c.fetchone()[0]

    conn.commit(); conn.close()
    return {
        "total_xp": total_xp,
        "streak_days": streak_days,
        "total_study_minutes": total_minutes,
        "weekly_study_minutes": weekly_minutes,
        "flashcards_due": flashcards_due,
        "level": (total_xp // 500) + 1,
        "level_progress": total_xp % 500,
    }


def record_study_session(username, subject, minutes):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        INSERT INTO study_sessions (username, subject, minutes, sess_date)
        VALUES (?, ?, ?, ?)
    """, (username, subject, int(minutes), today))
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute("""
        UPDATE user_stats SET total_minutes = COALESCE(total_minutes,0) + ?
        WHERE username=?
    """, (int(minutes), username))
    conn.commit(); conn.close()
    try:
        auto_check_badges(username)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# BADGES — definition + auto-award logic
# ─────────────────────────────────────────────────────────────────────────────
ALL_BADGES = [
    {"id":"first_login",  "name":"First Step",      "icon":"👣","desc":"Logged in for the first time"},
    {"id":"streak_3",     "name":"Heatwave",         "icon":"🔥","desc":"3-day study streak"},
    {"id":"streak_7",     "name":"Weekly Warrior",   "icon":"🎖️","desc":"7-day study streak"},
    {"id":"streak_14",    "name":"Fortnight Champ",  "icon":"🏆","desc":"14-day study streak"},
    {"id":"streak_30",    "name":"Monthly Master",   "icon":"👑","desc":"30-day study streak"},
    {"id":"first_gen",    "name":"Starter Spark",    "icon":"✨","desc":"Generated first AI content"},
    {"id":"qp_generated", "name":"Paper Setter",     "icon":"📝","desc":"Generated a question paper"},
    {"id":"quiz_done",    "name":"Quiz Taker",        "icon":"🧠","desc":"Generated a quiz"},
    {"id":"fc_10",        "name":"Card Collector",   "icon":"🗂️","desc":"Created 10 flashcards"},
    {"id":"study_60",     "name":"Hour Hero",         "icon":"⏱️","desc":"Studied 60 minutes total"},
    {"id":"study_300",    "name":"Study Champion",   "icon":"🎓","desc":"Studied 5 hours total"},
]

def _award_badge_raw(username, badge_id, c):
    earned_at = datetime.datetime.now().isoformat()
    try:
        c.execute(
            "INSERT OR IGNORE INTO achievements (username, badge_id, earned_at) VALUES (?,?,?)",
            (username, badge_id, earned_at)
        )
    except sqlite3.OperationalError:
        try:
            c.execute("ALTER TABLE achievements ADD COLUMN earned_at TEXT")
            c.execute(
                "INSERT OR IGNORE INTO achievements (username, badge_id, earned_at) VALUES (?,?,?)",
                (username, badge_id, earned_at)
            )
        except Exception:
            pass

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    try:
        _award_badge_raw(username, badge_id, c)
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def get_earned_badges(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT badge_id FROM achievements WHERE username=?", (username,))
    ids = {r[0] for r in c.fetchall()}
    conn.close(); return ids

def auto_check_badges(username):
    stats = get_user_stats(username)
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()

    def award(badge_id):
        _award_badge_raw(username, badge_id, c)

    try:
        # FIX: use correct badge IDs "streak_3" / "streak_7" (not "strk_3"/"strk_7")
        if stats["streak_days"] >= 3:  award("streak_3")
        if stats["streak_days"] >= 7:  award("streak_7")
        if stats["streak_days"] >= 14: award("streak_14")
        if stats["streak_days"] >= 30: award("streak_30")
        if stats["total_study_minutes"] >= 60:  award("study_60")
        if stats["total_study_minutes"] >= 300: award("study_300")
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "logged_in": False, "username": "", "active_page": "dashboard",
        "history": [], "current_chapters": [], "last_chapter_key": "",
        "generated_result": None, "generated_model": None,
        "generated_label": None,  "generated_tool": None,
        "generated_chapter": None,"generated_subject": None,
        "generated_topic": None,  "generated_course": None,
        "generated_stream": None, "generated_board": None,
        "generated_audience": None,"generated_output_style": None,
        "answers_result": None,   "answers_model": None, "show_answers": False,
        "fullpaper_result": None, "fullpaper_model": None,"show_fullpaper": False,
        "daily_checkin_done": False,
        "study_timer_active": False,"study_timer_start": None,
        "current_subject_for_timer": "General",
        "review_idx": 0,"review_show_ans": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
def go_to(page):
    st.session_state.active_page = page; st.rerun()

def reset_generation_state():
    for k in ["generated_result","generated_model","generated_label","generated_tool",
              "generated_chapter","generated_subject","generated_topic","generated_course",
              "generated_stream","generated_board","generated_audience","generated_output_style",
              "answers_result","answers_model","fullpaper_result","fullpaper_model"]:
        st.session_state[k] = None
    st.session_state.show_answers   = False
    st.session_state.show_fullpaper = False

# ─────────────────────────────────────────────────────────────────────────────
# STUDY DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_courses(cat):
    try: return list(STUDY_DATA[cat].keys())
    except: return []
def get_streams(cat, course):
    try: return list(STUDY_DATA[cat][course].keys())
    except: return []
def get_subjects(cat, course, stream):
    try: return list(STUDY_DATA[cat][course][stream].keys())
    except: return []
def get_topics(cat, course, stream, subject):
    try: return list(STUDY_DATA[cat][course][stream][subject].keys())
    except: return []
def get_chapters(cat, course, stream, subject, topic):
    try: return STUDY_DATA[cat][course][stream][subject][topic]
    except: return ["No chapters found"]

# ─────────────────────────────────────────────────────────────────────────────
# AUTH  — Whitelisted login, registration CLOSED
# ─────────────────────────────────────────────────────────────────────────────
def hash_p(pw): return hashlib.sha256(pw.encode()).hexdigest()

ALLOWED_USERS = ["Deepak"]   # 👈 Add your username here (case-sensitive)

def do_login(username, password):
    u = username.strip()
    if not u or not password.strip():
        return False, "⚠️ Please fill in both fields."
    if u not in ALLOWED_USERS:
        return False, "❌ Access Denied: You are not authorised to use this app."
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_p(password)))
    user = c.fetchone(); conn.close()
    return (True, u) if user else (False, "❌ Invalid username or password.")

# ─────────────────────────────────────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────────────────────────────────────
def add_to_history(label, chapter, subject, preview):
    entry = {
        "time":    time.strftime("%H:%M"), "tool": label,
        "chapter": chapter, "subject": subject,
        "preview": preview[:110]+"..." if len(preview)>110 else preview
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:6]

# ─────────────────────────────────────────────────────────────────────────────
# LABEL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_effective_output_name(tool, style):
    if style=="🧪 Question Paper" or tool=="🧪 Question Paper": return "Question Paper"
    if tool=="📝 Summary":
        if style=="📋 Notes Format":  return "Notes"
        if style=="📄 Detailed":      return "Detailed Summary"
        if style=="⚡ Short & Quick": return "Quick Summary"
        return "Summary"
    if tool=="🧠 Quiz":           return "Quiz"
    if tool=="📌 Revision Notes": return "Revision Notes"
    if tool=="❓ Exam Q&A":       return "Exam Q&A"
    return "Content"

def get_button_label(tool, style):
    name  = get_effective_output_name(tool, style)
    icons = {"Question Paper":"🧪","Notes":"📋","Detailed Summary":"📄",
             "Quick Summary":"⚡","Summary":"📝","Quiz":"🧠","Revision Notes":"📌","Exam Q&A":"❓"}
    return f"{icons.get(name,'✨')} Generate {name}"

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD DB
# ─────────────────────────────────────────────────────────────────────────────
def save_flashcard(username, front, back, subject, chapter):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute(
        "INSERT INTO flashcards (username,front_text,back_text,subject,chapter,next_review_date,created_date) VALUES (?,?,?,?,?,?,?)",
        (username, front, back, subject, chapter, today, today)
    )
    conn.commit(); conn.close()

def get_due_flashcards(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute(
        "SELECT id,front_text,back_text,subject,chapter,ease_factor,interval_days,review_count "
        "FROM flashcards WHERE username=? AND next_review_date<=? ORDER BY next_review_date ASC",
        (username, today)
    )
    rows = c.fetchall(); conn.close(); return rows

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute(
        "SELECT id,front_text,back_text,subject,chapter,next_review_date,review_count "
        "FROM flashcards WHERE username=? ORDER BY created_date DESC",
        (username,)
    )
    rows = c.fetchall(); conn.close(); return rows

def update_flashcard_review(card_id, performance):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT ease_factor,interval_days FROM flashcards WHERE id=?", (card_id,))
    row = c.fetchone()
    if not row: conn.close(); return
    ef, interval = row
    if   performance==1: interval=1;                         ef=max(1.3,ef-0.2)
    elif performance==2: interval=max(1,int(interval*1.2));  ef=max(1.3,ef-0.1)
    elif performance==3: interval=max(1,int(interval*ef))
    elif performance==4: interval=max(1,int(interval*ef*1.3)); ef=min(3.0,ef+0.1)
    next_date = (datetime.date.today() + datetime.timedelta(days=interval)).isoformat()
    c.execute("""
        UPDATE flashcards SET ease_factor=?,interval_days=?,next_review_date=?,
        review_count=review_count+1 WHERE id=?
    """, (ef, interval, next_date, card_id))
    conn.commit(); conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit(); conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def get_available_models():
    api_key = st.secrets.get("GEMINI_API_KEY","")
    if not api_key: return []
    try:
        genai.configure(api_key=api_key)
        return [m.name for m in genai.list_models()
                if "gemini" in m.name.lower()
                and "generateContent" in getattr(m,"supported_generation_methods",[])]
    except Exception:
        return []

def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY","")
    if not api_key: return ("⚠️ API key missing.","None")
    try: genai.configure(api_key=api_key)
    except Exception as e: return (f"❌ Config failed: {e}","None")
    try:
        available = [m.name for m in genai.list_models()
                     if "gemini" in m.name.lower()
                     and "generateContent" in getattr(m,"supported_generation_methods",[])]
    except Exception as e: return (f"❌ Could not list models: {e}","None")
    if not available: return ("❌ No Gemini models available.","None")
    for model_name in available:
        try:
            model  = genai.GenerativeModel(model_name)
            result = model.generate_content(prompt)
            return (result.text, model_name)
        except Exception:
            continue
    return ("❌ All models failed. Please try again later.","None")

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def build_prompt(board, course, stream, subject, topic, chapter, tool, style, audience="Student"):
    base = (f"You are an expert {subject} teacher.\n"
            f"Board: {board} | Course: {course} | Stream: {stream}\n"
            f"Subject: {subject} | Topic: {topic} | Chapter: {chapter}\n"
            f"Audience: {audience}\n\nTask: ")
    if tool=="📝 Summary":
        if style=="📄 Detailed":      return base+"Create a comprehensive summary: overview, key concepts, definitions, formulas, 2 examples, common mistakes, exam tips."
        if style=="⚡ Short & Quick": return base+"Create a quick-reference summary: one-line definition, 5-7 key points, formulas, quick tips. Max 500 words."
        if style=="📋 Notes Format":  return base+"Create structured notes: clear headings, bullets, definitions, examples, revision points."
    if tool=="🧠 Quiz":           return base+"Create: 5 MCQs (4 options each, mark answer), 5 short-answer Q&As, 3 long-answer Q&As."
    if tool=="📌 Revision Notes": return base+"Create revision notes: top 10 must-know points, formula sheet, mnemonics, comparisons, exam focus areas."
    if tool=="❓ Exam Q&A":       return base+"Create exam Q&A bank: 8-10 frequently asked Qs with answers, conceptual Qs, application Qs."
    return base+"Create complete exam-ready study material."

def build_qp_prompt(board, course, stream, subject, topic, chapter, audience="Student"):
    return (f"Create a formal {subject} question paper.\n"
            f"Board: {board} | Course: {course} | Stream: {stream}\n"
            f"Chapter: {chapter} | Topic: {topic} | For: {audience}\n\n"
            f"Include: Section A (MCQs, 1 mark each x10), "
            f"Section B (Short answers, 3 marks each x5), "
            f"Section C (Long answers, 5 marks each x3). "
            f"Total marks: 40. Add instructions at top.")

def build_answer_key_prompt(qp_text, subject, chapter):
    return (f"Create a complete answer key for this {subject} question paper on {chapter}.\n\n"
            f"Question Paper:\n{qp_text}\n\n"
            f"Provide model answers for all questions with marking scheme.")

def build_full_qp_prompt(board, course, stream, subject, audience="Student"):
    return (f"Create a comprehensive full-year {subject} question paper.\n"
            f"Board: {board} | Course: {course} | Stream: {stream} | For: {audience}\n\n"
            f"Cover all major topics. Include: Section A MCQs (20 marks), "
            f"Section B Short answers (30 marks), Section C Long answers (30 marks), "
            f"Section D Case study (20 marks). Total: 100 marks.")

def build_flashcard_prompt(subject, chapter, topic):
    return (f"Create exactly 10 study flashcards.\nSubject: {subject} | Chapter: {chapter} | Topic: {topic}\n"
            f"Use EXACTLY this format:\nCARD 1\nFRONT: [question or term]\nBACK: [answer or definition]\n"
            f"CARD 2\nFRONT: ...\nBACK: ...\n(Continue for all 10. No extra text.)")

def parse_flashcards(raw):
    cards = []; blocks = raw.split("CARD ")
    for block in blocks[1:]:
        lines = block.strip().split("\n")
        front = back = ""
        for line in lines:
            if line.startswith("FRONT:"): front = line[6:].strip()
            elif line.startswith("BACK:"): back  = line[5:].strip()
        if front and back:
            cards.append({"front": front, "back": back})
    return cards

# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(title, subtitle, content, color_hex="#1d4ed8"):
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer,pagesize=A4,topMargin=2*cm,bottomMargin=2*cm,leftMargin=1.5*cm,rightMargin=1.5*cm)
    styles = getSampleStyleSheet(); story = []
    story.append(Paragraph(title,ParagraphStyle("T",parent=styles["Heading1"],fontSize=20,
        textColor=colors.HexColor(color_hex),alignment=TA_CENTER,spaceAfter=6,fontName="Helvetica-Bold")))
    story.append(Paragraph(subtitle,ParagraphStyle("S",parent=styles["Normal"],fontSize=10,
        textColor=colors.HexColor("#64748b"),alignment=TA_CENTER,spaceAfter=10)))
    story.append(HRFlowable(width="100%",thickness=2,color=colors.HexColor(color_hex),spaceAfter=14))
    body = ParagraphStyle("B",parent=styles["Normal"],fontSize=10.5,leading=15,
        textColor=colors.HexColor("#1e293b"),spaceAfter=5)
    head = ParagraphStyle("H",parent=styles["Heading2"],fontSize=12.5,
        textColor=colors.HexColor(color_hex),spaceBefore=10,spaceAfter=6,fontName="Helvetica-Bold")
    for line in content.split("\n"):
        line = line.strip()
        if not line: story.append(Spacer(1,0.15*cm)); continue
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if line.startswith(("#","##","###")): story.append(Paragraph(line.lstrip("#").strip(),head))
        else: story.append(Paragraph(safe,body))
    story.append(Spacer(1,0.3*cm))
    story.append(HRFlowable(width="100%",thickness=1,color=colors.HexColor("#e2e8f0"),spaceAfter=5))
    story.append(Paragraph(f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle("F",parent=styles["Normal"],fontSize=8,
            textColor=colors.HexColor("#94a3b8"),alignment=TA_CENTER)))
    doc.build(story); buffer.seek(0); return buffer

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
    col_btn,_=st.columns([1,3])
    with col_btn:
        if st.button("← Back to Dashboard",key="back_to_dash",use_container_width=True):
            go_to("dashboard")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(username):
    stats=get_user_stats(username) or {}
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:12px 0 10px 0;">
                <div style="font-size:2rem;">🎓</div>
                <div style="font-size:1.02rem;font-weight:800;color:#2563eb;">StudySmart AI</div>
                <div style="font-size:.77rem;margin-top:3px;">Hi, {username} 👋</div>
            </div>
        """, unsafe_allow_html=True)

        c1,c2=st.columns(2)
        with c1:
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#ff6b6b,#feca57);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                🔥 {stats.get('streak_days',0)}<br>
                <span style="font-size:.62rem;font-weight:500;color:white;">day streak</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                ⭐ Lv{stats.get('level',1)}<br>
                <span style="font-size:.62rem;font-weight:500;color:white;">{stats.get('total_xp',0)} XP</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Daily login streak check
        if not st.session_state.daily_checkin_done:
            msg = check_daily_login(username)
            st.success(msg)
            st.session_state.daily_checkin_done = True
            try: auto_check_badges(username)
            except Exception: pass

        # Study Timer
        st.markdown("---")
        st.markdown("**⏱️ Study Timer**")
        subj_timer = st.session_state.get("current_subject_for_timer","General")
        if not st.session_state.study_timer_active:
            if st.button("▶️ Start Timer",use_container_width=True,key="sb_start_timer"):
                st.session_state.study_timer_active = True
                st.session_state.study_timer_start  = time.time()
                st.rerun()
        else:
            elapsed = int(time.time() - (st.session_state.study_timer_start or time.time()))
            mins,secs = divmod(elapsed,60)
            st.markdown(f"""<div style="text-align:center;font-size:1.6rem;font-weight:800;
                color:#2563eb;padding:6px 0;">⏱️ {mins:02d}:{secs:02d}</div>""", unsafe_allow_html=True)
            st.caption(f"Studying: {subj_timer}")
            if st.button("⏹️ Stop & Save",use_container_width=True,key="sb_stop_timer"):
                minutes_studied = elapsed / 60
                if minutes_studied >= 1:
                    record_study_session(username, subj_timer, round(minutes_studied,1))
                    award_xp(username, int(minutes_studied)*2)
                    st.success(f"✅ {round(minutes_studied,1)} min saved! +{int(minutes_studied)*2} XP")
                st.session_state.study_timer_active = False
                st.session_state.study_timer_start  = None
                st.rerun()

        # Navigation
        st.markdown("---")
        st.markdown("**📍 Navigate**")
        for lbl,pg in [("🏠 Dashboard","dashboard"),("📚 Study Tools","study"),
                       ("🗂️ Flashcards","flashcards"),("🏅 Achievements","achievements")]:
            if st.button(lbl,use_container_width=True,key=f"nav_{pg}"):
                go_to(pg)

        # Recent history
        st.markdown("---")
        with st.expander("📜 Recent Activity"):
            if not st.session_state.history:
                st.caption("No activity yet.")
            for h in st.session_state.history[:3]:
                st.markdown(f"""<div class="sf-hist">
                        🕐 {h['time']} | <b>{h['tool']}</b><br>
                        📖 {h['chapter']} — {h['subject']}<br>
                        <small>{h['preview']}</small>
                    </div>""", unsafe_allow_html=True)

        with st.expander("🤖 AI Status"):
            if st.button("Check Models",use_container_width=True,key="sb_models"):
                with st.spinner("Checking..."):
                    mdls=get_available_models()
                for m in mdls: st.write(f"✅ {m}")

        st.divider()
        if st.button("🚪 Logout",use_container_width=True,key="sb_logout"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard(username):
    render_header("StudySmart","Your Daily Learning Companion")
    stats=get_user_stats(username) or {}

    c1,c2,c3,c4=st.columns(4)
    for col,cls,icon,val,lbl in [
        (c1,"mc-blue",  "🔥",stats.get("streak_days",0),"Day Streak"),
        (c2,"mc-green", "⭐",f"Level {stats.get('level',1)}","Your Level"),
        (c3,"mc-purple","📚",stats.get("flashcards_due",0),"Cards Due"),
        (c4,"mc-amber", "⏱️",f"{stats.get('weekly_study_minutes',0)} min","This Week"),
    ]:
        with col:
            st.markdown(f'<div class="mc {cls}"><div class="icon">{icon}</div><div class="val">{val}</div><div class="lbl">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    total_xp=stats.get("total_xp",0); lvl=stats.get("level",1)
    lp=stats.get("level_progress",total_xp%500); pct=min(100,int((lp/500)*100))
    st.markdown(f"""<div style="display:flex;justify-content:space-between;font-size:.85rem;font-weight:700;margin-bottom:5px;">
        <span>⭐ Level {lvl}</span><span>{total_xp} XP &nbsp;·&nbsp; {500-lp} XP to next level</span>
    </div><div class="xp-wrap"><div class="xp-fill" style="width:{pct}%;"></div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left,right=st.columns([1.1,1])
    with left:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🌱 Study Momentum**")
        mins=stats.get("total_study_minutes",0); growth=min(100,mins//10)
        plant=(("🌱","Seedling") if growth<20 else ("🌿","Sprout") if growth<40 else
               ("🪴","Growing Plant") if growth<70 else ("🌳","Strong Tree") if growth<90 else ("🌲","Master Tree"))
        st.markdown(f"""<div class="sf-soft-card" style="text-align:center;margin-bottom:10px;">
            <div style="font-size:2.6rem;">{plant[0]}</div>
            <div style="font-weight:800;font-size:.93rem;">{plant[1]}</div>
            <div style="font-size:.8rem;margin-top:3px;">{mins} min total studied</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions**")
        if st.button("📚 Open Study Tools",  use_container_width=True,key="d_study"):  go_to("study")
        if st.button("🗂️ Review Flashcards", use_container_width=True,key="d_fc"):     go_to("flashcards")
        if st.button("🏅 View Achievements", use_container_width=True,key="d_ach"):    go_to("achievements")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**📜 Recent Activity**")
        if not st.session_state.history:
            st.info("No activity yet. Start studying to see your history!")
        for h in st.session_state.history:
            st.markdown(f"""<div class="sf-hist">
                        🕐 {h['time']} | <b>{h['tool']}</b><br>
                        📖 {h['chapter']} — {h['subject']}<br>
                        <small>{h['preview']}</small>
                    </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STUDY TOOLS
# FIX: corrected column layout — category in ca, rest in cb
# ─────────────────────────────────────────────────────────────────────────────
def show_study_tools(username):
    render_back_button()
    render_header("Study Tools","AI-powered exam preparation")

    tool=st.radio("🛠️ Select Tool",
        ["📝 Summary","🧠 Quiz","📌 Revision Notes","🧪 Question Paper","❓ Exam Q&A"],
        horizontal=True,key="study_tool_radio")

    if not STUDY_DATA:
        st.error("❌ No study data. Check data/study_data.json"); return

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    ca,cb=st.columns([1,1])
    with ca:
        category = st.selectbox("📚 Category", list(STUDY_DATA.keys()), key="sel_cat")
        course   = st.selectbox("🎓 Program / Class", get_courses(category), key="sel_course")
    with cb:
        stream   = st.selectbox("📖 Stream", get_streams(category, course), key="sel_stream")
        subject  = st.selectbox("🧾 Subject", get_subjects(category, course, stream), key="sel_subject")
        board    = "University / National Syllabus"
        if category == "K-12th":
            board = st.selectbox("🏫 Board", BOARDS, key="sel_board")
        else:
            st.info(f"📌 Syllabus: {board}")

    topic=st.selectbox("🗂️ Topic",get_topics(category,course,stream,subject),key="sel_topic")

    chapter_key=f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key!=chapter_key:
        st.session_state.current_chapters=get_chapters(category,course,stream,subject,topic)
        st.session_state.last_chapter_key=chapter_key
        reset_generation_state()

    chapter=st.selectbox("📝 Chapter",st.session_state.current_chapters,key="sel_chapter")
    st.session_state.current_subject_for_timer=subject
    st.markdown('</div>', unsafe_allow_html=True)

    style=st.radio("⚙️ Output Style",
        ["📄 Detailed","⚡ Short & Quick","📋 Notes Format","🧪 Question Paper"],
        horizontal=True,key="study_style_radio")

    eff_label=get_effective_output_name(tool,style)
    btn_label=get_button_label(tool,style)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button(btn_label,use_container_width=True,key="gen_btn"):
        audience = "Student"
        with st.spinner(f"Generating {eff_label}..."):
            is_qp = (eff_label=="Question Paper")
            if is_qp:
                result,model=generate_with_fallback(build_qp_prompt(board,course,stream,subject,topic,chapter,audience))
            else:
                result,model=generate_with_fallback(build_prompt(board,course,stream,subject,topic,chapter,tool,style,audience))
        st.session_state.generated_result   = result
        st.session_state.generated_model    = model
        st.session_state.generated_label    = eff_label
        st.session_state.generated_tool     = tool
        st.session_state.generated_chapter  = chapter
        st.session_state.generated_subject  = subject
        st.session_state.generated_topic    = topic
        st.session_state.generated_course   = course
        st.session_state.generated_stream   = stream
        st.session_state.generated_board    = board
        st.session_state.generated_audience = audience
        st.session_state.generated_output_style = style
        st.session_state.show_answers       = False
        st.session_state.show_fullpaper     = False
        if model!="None":
            add_to_history(eff_label,chapter,subject,result[:110])
            award_xp(username,15)
            award_badge(username,"first_gen")
            if is_qp:  award_badge(username,"qp_generated")
            if tool=="🧠 Quiz": award_badge(username,"quiz_done")
            auto_check_badges(username)

    # Display result
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

        if st.session_state.generated_model=="None":
            st.error("❌ Generation failed."); st.markdown(result); return

        is_qp=(g_label=="Question Paper")
        box_cls="sf-fullpaper" if is_qp else "sf-output"
        st.markdown(f'<div class="{box_cls}">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        if not is_qp:
            if st.button("🗂️ Save as Flashcards",use_container_width=True,key="save_fc_btn"):
                with st.spinner("Creating flashcards..."):
                    raw,mdl=generate_with_fallback(build_flashcard_prompt(g_subject,g_chapter,g_topic or ""))
                if mdl!="None":
                    cards=parse_flashcards(raw)
                    for c in cards: save_flashcard(username,c["front"],c["back"],g_subject,g_chapter)
                    award_xp(username,len(cards)*5)
                    auto_check_badges(username)
                    st.success(f"✅ {len(cards)} flashcards saved! +{len(cards)*5} XP")
                else: st.error("❌ Flashcard generation failed.")
            try:
                pdf=generate_pdf(f"{g_label} — {g_chapter}",f"{g_subject} | {g_topic} | {g_course}",result)
                safe=(g_chapter.replace(" ","_").replace(":","").replace("/","-")+".pdf")
                st.download_button("⬇️ Download PDF",data=pdf,file_name=safe,mime="application/pdf",use_container_width=True,key="dl_main_pdf")
            except Exception as e: st.warning(f"⚠️ PDF error: {e}")
        else:
            try:
                qp_pdf=generate_pdf(f"Question Paper — {g_chapter}",f"{g_board} | {g_subject} | {g_course}",result,"#7c3aed")
                safe_q=(g_chapter.replace(" ","_").replace(":","").replace("/","-")+".pdf")
                st.download_button("⬇️ Download Question Paper PDF",data=qp_pdf,file_name=safe_q,mime="application/pdf",use_container_width=True,key="dl_qp_pdf")
            except Exception as e: st.warning(f"⚠️ PDF error: {e}")

            if st.button("🔑 Generate Answer Key",use_container_width=True,key="ans_key_btn"):
                with st.spinner("Generating answer key..."):
                    ans_r,ans_m=generate_with_fallback(build_answer_key_prompt(result,g_subject,g_chapter))
                st.session_state.answers_result=ans_r; st.session_state.answers_model=ans_m
                st.session_state.show_answers=True

            if st.session_state.show_answers and st.session_state.answers_result:
                if st.session_state.answers_model!="None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 🔑 Answer Key — {g_chapter}")
                    st.markdown(st.session_state.answers_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        ans_pdf=generate_pdf(f"Answer Key — {g_chapter}",f"{g_board} | {g_subject}",st.session_state.answers_result,"#16a34a")
                        safe_a=(g_chapter.replace(" ","_").replace(":","").replace("/","-")+"_Answers.pdf")
                        st.download_button("⬇️ Download Answer Key PDF",data=ans_pdf,file_name=safe_a,mime="application/pdf",use_container_width=True,key="dl_ans_pdf")
                    except Exception as e: st.warning(f"⚠️ PDF error: {e}")

            if st.button(f"🗂️ Generate Full {g_subject} Paper",use_container_width=True,key="full_qp_btn"):
                with st.spinner("Generating full subject paper..."):
                    full_r,full_m=generate_with_fallback(build_full_qp_prompt(g_board,g_course,g_stream,g_subject,g_audience))
                st.session_state.fullpaper_result=full_r; st.session_state.fullpaper_model=full_m
                st.session_state.show_fullpaper=True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model!="None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Paper — {g_subject}")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf=generate_pdf(f"Full Paper — {g_subject}",f"{g_board} | {g_course} | {g_stream}",st.session_state.fullpaper_result,"#7c3aed")
                        safe_f=f"{g_subject}_{g_board}_FullPaper.pdf".replace(" ","_")
                        st.download_button("⬇️ Download Full Paper PDF",data=full_pdf,file_name=safe_f,mime="application/pdf",use_container_width=True,key="dl_full_pdf")
                    except Exception as e: st.warning(f"⚠️ PDF error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────────────────────────────────────
def show_flashcards(username):
    render_back_button()
    render_header("Flashcards","Spaced-repetition learning")

    tab1,tab2,tab3=st.tabs(["📖 Review Due","➕ Create","📚 My Library"])

    with tab1:
        due=get_due_flashcards(username)
        if not due:
            st.info("🎉 No cards due! Come back later or create new ones.")
        else:
            idx=st.session_state.review_idx % len(due)
            card=due[idx]
            card_id,front,back,subj,chap,ef,interval,review_count=card
            st.markdown(f"**Card {idx+1} of {len(due)}** | Subject: {subj} | Chapter: {chap}")
            st.markdown(f"""<div class="fc-front">
                <div style="font-size:.73rem;opacity:.8;margin-bottom:8px;">QUESTION</div>
                <div style="font-size:1.05rem;font-weight:700;line-height:1.5;">{front}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if not st.session_state.review_show_ans:
                if st.button("👁️ Show Answer",use_container_width=True,key="show_ans_btn"):
                    st.session_state.review_show_ans=True; st.rerun()
            else:
                st.markdown(f"""<div class="fc-back">
                    <div style="font-size:.73rem;opacity:.8;margin-bottom:8px;">ANSWER</div>
                    <div style="font-size:.98rem;font-weight:700;line-height:1.5;">{back}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                st.markdown("**How well did you remember?**")
                b1,b2,b3,b4=st.columns(4)
                for col,lbl,perf,ks in [(b1,"😓 Again",1,"again"),(b2,"😐 Hard",2,"hard"),(b3,"🙂 Good",3,"good"),(b4,"😄 Easy",4,"easy")]:
                    with col:
                        if st.button(lbl,use_container_width=True,key=f"fc_{ks}_{card_id}"):
                            update_flashcard_review(card_id,perf)
                            award_xp(username,3)
                            st.session_state.review_idx+=1; st.session_state.review_show_ans=False; st.rerun()

    with tab2:
        cl,cr=st.columns(2)
        with cl:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### ✍️ Manual")
            with st.form("manual_fc"):
                f_front=st.text_input("Front (Question)")
                f_back=st.text_area("Back (Answer)",height=75)
                f_subj=st.text_input("Subject")
                f_chap=st.text_input("Chapter")
                if st.form_submit_button("➕ Save Card",use_container_width=True):
                    if f_front.strip() and f_back.strip():
                        save_flashcard(username,f_front.strip(),f_back.strip(),f_subj.strip(),f_chap.strip())
                        award_xp(username,5)
                        auto_check_badges(username)
                        st.success("✅ Card saved! +5 XP"); st.rerun()
                    else: st.warning("⚠️ Front and Back are required.")
            st.markdown('</div>', unsafe_allow_html=True)

        with cr:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### 🤖 AI Generate")
            with st.form("ai_fc"):
                ai_subj=st.text_input("Subject",placeholder="e.g. Physics")
                ai_chap=st.text_input("Chapter",placeholder="e.g. Laws of Motion")
                ai_topic=st.text_input("Topic",  placeholder="e.g. Newton's 3rd Law")
                if st.form_submit_button("⚡ Generate 10 Cards",use_container_width=True):
                    if ai_subj.strip() and ai_chap.strip():
                        with st.spinner("Generating flashcards..."):
                            raw,mdl=generate_with_fallback(build_flashcard_prompt(ai_subj.strip(),ai_chap.strip(),ai_topic.strip()))
                        if mdl!="None":
                            cards=parse_flashcards(raw)
                            for card in cards:
                                save_flashcard(username,card["front"],card["back"],ai_subj.strip(),ai_chap.strip())
                            award_xp(username,len(cards)*5)
                            auto_check_badges(username)
                            st.success(f"✅ {len(cards)} cards saved! +{len(cards)*5} XP"); st.rerun()
                        else: st.error("❌ AI generation failed. Try again.")
                    else: st.warning("⚠️ Subject and Chapter are required.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── My Library — NO unwanted banners ──
    with tab3:
        all_cards=get_all_flashcards(username)
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        if not all_cards:
            st.markdown("<div style='text-align:center;padding:30px;color:#64748b;'>"
                        "📭 No flashcards yet.<br>Create your first card in the ➕ Create tab."
                        "</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"**Total cards: {len(all_cards)}**")
            for card in all_cards:
                cid,front,back,subj,chap,nrd,rc=card
                with st.expander(f"📄 {front[:60]}{'...' if len(front)>60 else ''} | {subj}"):
                    col_a,col_b=st.columns(2)
                    with col_a:
                        st.markdown(f"**Front:** {front}")
                        st.markdown(f"**Subject:** {subj} | **Chapter:** {chap}")
                    with col_b:
                        st.markdown(f"**Back:** {back}")
                        st.markdown(f"**Next Review:** {nrd} | **Reviews:** {rc}")
                    if st.button("🗑️ Delete",key=f"del_{cid}",use_container_width=True):
                        delete_flashcard(cid); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS
# ─────────────────────────────────────────────────────────────────────────────
def show_achievements(username):
    render_back_button()
    render_header("Achievements","Your badges & milestones")

    stats       = get_user_stats(username) or {}
    earned_ids  = get_earned_badges(username)
    earned_list = [b for b in ALL_BADGES if b["id"] in earned_ids]
    locked_list = [b for b in ALL_BADGES if b["id"] not in earned_ids]

    st.markdown(f"### 🏅 Earned Badges ({len(earned_list)}/{len(ALL_BADGES)})")
    if not earned_list:
        st.info("No badges earned yet. Keep studying!")
    else:
        cols=st.columns(4)
        for i,b in enumerate(earned_list):
            with cols[i%4]:
                st.markdown(f"""<div class="bdg earned">
                    <div class="bi">{b['icon']}</div>
                    <div class="bn">{b['name']}</div>
                    <div class="bs">{b['desc']}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("### 🔒 Locked Badges")
    if locked_list:
        cols2=st.columns(4)
        for i,b in enumerate(locked_list):
            with cols2[i%4]:
                hints={
                    "streak_3":"Study 3 days in a row","streak_7":"Study 7 days in a row",
                    "streak_14":"Study 14 days in a row","streak_30":"Study 30 days in a row",
                    "first_gen":"Generate any AI content","qp_generated":"Generate a question paper",
                    "quiz_done":"Generate a quiz","fc_10":"Create 10 flashcards",
                    "study_60":"Study for 60 minutes total","study_300":"Study for 5 hours total",
                    "first_login":"Log in for the first time"
                }
                hint=hints.get(b["id"],b["desc"])
                st.markdown(f"""<div class="bdg">
                    <div class="bi" style="opacity:.28;">🔒</div>
                    <div class="bn">{b['name']}</div>
                    <div class="bs">{hint}</div>
                </div>""", unsafe_allow_html=True)

    # Progress nudge
    streak=stats.get("streak_days",0)
    total_min=stats.get("total_study_minutes",0)
    st.markdown('<div class="sf-card" style="margin-top:14px;">', unsafe_allow_html=True)
    st.markdown("**📈 Your Progress Towards Next Badge**")
    for b in locked_list:
        bid=b["id"]
        if bid=="streak_3"   and streak<3:   st.caption(f"🔥 Streak: {streak}/3 days"); st.progress(streak/3)
        elif bid=="streak_7" and streak<7:   st.caption(f"🔥 Streak: {streak}/7 days"); st.progress(streak/7)
        elif bid=="streak_14"and streak<14:  st.caption(f"🔥 Streak: {streak}/14 days"); st.progress(streak/14)
        elif bid=="streak_30"and streak<30:  st.caption(f"🔥 Streak: {streak}/30 days"); st.progress(streak/30)
        elif bid=="study_60" and total_min<60:  st.caption(f"⏱️ Study time: {total_min}/60 min"); st.progress(total_min/60)
        elif bid=="study_300"and total_min<300: st.caption(f"⏱️ Study time: {total_min}/300 min"); st.progress(total_min/300)
        elif bid=="fc_10":
            conn=sqlite3.connect("users.db");c=conn.cursor()
            c.execute("SELECT COUNT(*) FROM flashcards WHERE username=?",(username,))
            fc=c.fetchone()[0];conn.close()
            if fc<10: st.caption(f"🗂️ Flashcards: {fc}/10"); st.progress(fc/10)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUTH UI  — registration CLOSED
# FIX: removed nested duplicate auth_ui() definition; uses do_login() properly
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
    """Login and Registration screen"""

    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
            <div class="sf-hero">
                <div class="sf-hero-title">StudySmart AI</div>
                <div class="sf-hero-sub">Your Smart Exam Preparation Platform</div>
                <div class="sf-powered">✦ POWERED BY AI ✦</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input(
                    "👤 Username",
                    key="login_u",
                    placeholder="Enter your username"
                )
                p = st.text_input(
                    "🔑 Password",
                    type="password",
                    key="login_p",
                    placeholder="Enter your password"
                )
                login_submit = st.form_submit_button("Sign In 🚀", use_container_width=True)

            if login_submit:
                # FIX: use do_login() which enforces ALLOWED_USERS whitelist
                ok, result = do_login(u, p)
                if ok:
                    conn = sqlite3.connect("users.db")
                    c    = conn.cursor()
                    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (result,))
                    conn.commit(); conn.close()

                    st.session_state.logged_in = True
                    st.session_state.username  = result

                    try: auto_check_badges(result)
                    except Exception: pass

                    st.success("✅ Login successful!")
                    time.sleep(0.6)
                    st.rerun()
                else:
                    st.error(result)

        with tab2:
            st.info("📝 Registration is currently closed. Contact admin for access.")
            st.markdown("""
            <div style="padding:16px; background:rgba(59,130,246,0.08); border-radius:10px; margin-top:12px;">
                <strong>ℹ️ Account Access:</strong><br/>
                If you don't have an account, please contact the administrator for registration.
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main_app():
    render_sidebar(st.session_state.username)
    page=st.session_state.active_page
    if   page=="dashboard":    show_dashboard(st.session_state.username)
    elif page=="study":        show_study_tools(st.session_state.username)
    elif page=="flashcards":   show_flashcards(st.session_state.username)
    elif page=="achievements": show_achievements(st.session_state.username)
    else:                      show_dashboard(st.session_state.username)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
init_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
