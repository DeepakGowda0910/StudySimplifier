# ═══════════════════════════════════════════════════════════════════════════════
# Part 1- STUDYSMART AI — app.py  (Personalized Onboarding + Subscription-Ready)
# ═══════════════════════════════════════════════════════════════════════════════
import PyPDF2
import docx
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT


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
# FULL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* ── FIX: Prevent Streamlit icons from rendering as overlapping text ── */
span.stIconMaterial, 
span[class*="stIconMaterial"], 
.material-symbols-rounded {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}

/* ── FIX: Completely hide the expander arrow to keep the banner clean ── */
[data-testid="stExpander"] summary span.stIconMaterial,
[data-testid="stExpander"] summary [data-testid="stIconMaterial"],
[data-testid="stExpander"] summary svg {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
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

#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }

.stTabs [data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 2px solid #e2e8f0 !important;
    gap: 20px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    border: none !important;
    color: #64748b !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    color: #0f172a !important;
    border-bottom: 3px solid #3b82f6 !important;
}

/* ── Login / Onboarding Header ── */
.sf-header { text-align: center; padding: 40px 0 15px 0; }
.sf-header-title {
    font-size: 4rem; font-weight: 800;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0; line-height: 1.1; letter-spacing: -1.5px;
}
.sf-header-subtitle {
    font-size: 1.05rem; color: #64748b; margin-top: 10px;
    font-weight: 500; letter-spacing: 0.4px;
}
.sf-watermark {
    font-size: 3.8rem; font-weight: 900;
    color: rgba(59,130,246,0.07); text-transform: uppercase;
    letter-spacing: 10px; margin-top: 10px;
    pointer-events: none; user-select: none;
    text-align: center; width: 100%;
}

/* ── Onboarding Step Indicator ── */
.ob-step {
    display: inline-flex; align-items: center; justify-content: center;
    width: 36px; height: 36px; border-radius: 50%;
    font-weight: 800; font-size: .9rem;
}
.ob-step-done {
    background: linear-gradient(135deg,#10b981,#059669);
    color: white !important;
}
.ob-step-active {
    background: linear-gradient(135deg,#3b82f6,#2563eb);
    color: white !important;
}
.ob-step-lock {
    background: #e2e8f0; color: #94a3b8 !important;
}
.ob-line { flex: 1; height: 3px; background: #e2e8f0; margin: 0 6px; border-radius: 2px; }
.ob-line-done { background: linear-gradient(90deg,#10b981,#3b82f6); }

/* ── Profile Badge (Sidebar) ── */
.profile-badge {
    background: linear-gradient(135deg,#3b82f6,#1d4ed8);
    border-radius: 14px; padding: 12px 10px; color: white !important;
    text-align: center; margin-bottom: 10px;
}
.profile-badge * { color: white !important; }

/* ── Category Cards on Onboarding ── */
.cat-card {
    background: white; border: 2px solid #e2e8f0;
    border-radius: 16px; padding: 20px 14px;
    text-align: center; cursor: pointer;
    transition: all 0.25s ease;
    box-shadow: 0 2px 12px rgba(15,23,42,.06);
}
.cat-card:hover { border-color: #3b82f6; transform: translateY(-3px); }
.cat-card.selected {
    border-color: #2563eb !important;
    background: linear-gradient(135deg,#eff6ff,#dbeafe) !important;
}
.cat-card .cat-icon { font-size: 2.4rem; }
.cat-card .cat-name { font-weight: 700; font-size: .9rem; margin-top: 8px; color: #0f172a; }

/* ── App hero ── */
.sf-hero { text-align:center; padding:14px 0 8px 0; }
.sf-hero-title {
    font-size:2rem; font-weight:800;
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
    background: rgba(255,255,255,0.80); backdrop-filter: blur(10px);
    border-radius: 20px; padding: 28px;
    box-shadow: 0 4px 30px rgba(15,23,42,0.08), inset 0 1px 0 rgba(255,255,255,0.9);
    margin-bottom: 24px; border: 1px solid rgba(59,130,246,0.15);
}
.sf-soft-card {
    background:linear-gradient(160deg,#f8fbff,#f1f5f9) !important;
    border:1px solid #dde5f0 !important; border-radius:14px !important;
    padding:14px !important; color:#0f172a !important;
}
.sf-soft-card *, .sf-soft-card p, .sf-soft-card span, .sf-soft-card strong { color:#0f172a !important; }

/* ── Metric cards ── */
.mc {
    border-radius:14px; padding:14px 10px;
    color:white !important; text-align:center;
    box-shadow:0 8px 20px rgba(0,0,0,.09); margin-bottom:10px;
}
.mc * { color:white !important; }
.mc-blue   { background:linear-gradient(135deg,#3b82f6,#1d4ed8); }
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
.sf-output *, .sf-output p, .sf-output li, .sf-output span, .sf-output strong { color:#0f172a !important; }
.sf-output h1, .sf-output h2, .sf-output h3 { color:#1d4ed8 !important; }

.sf-answers {
    background:#f0fdf4 !important; border:1px solid #bbf7d0 !important;
    border-left:4px solid #16a34a !important; border-radius:14px !important;
    padding:18px 20px !important; margin-top:12px !important; color:#0f172a !important;
}
.sf-answers *, .sf-answers p, .sf-answers li { color:#0f172a !important; }
.sf-answers h1, .sf-answers h2, .sf-answers h3 { color:#15803d !important; }

.sf-fullpaper {
    background:#faf5ff !important; border:1px solid #ddd6fe !important;
    border-left:4px solid #7c3aed !important; border-radius:14px !important;
    padding:18px 20px !important; margin-top:12px !important; color:#0f172a !important;
}
.sf-fullpaper *, .sf-fullpaper p, .sf-fullpaper li { color:#0f172a !important; }
.sf-fullpaper h1, .sf-fullpaper h2, .sf-fullpaper h3 { color:#6d28d9 !important; }

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
div[data-baseweb="popover"] {
    background:#ffffff !important; border:1px solid #e2e8f0 !important;
    border-radius:12px !important; box-shadow:0 8px 30px rgba(15,23,42,.12) !important;
    z-index:9999 !important;
}
div[role="option"] { background:#ffffff !important; color:#0f172a !important; padding:10px 14px !important; }
div[role="option"]:hover { background:#eff6ff !important; color:#1d4ed8 !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border:1.5px solid #c7d4e8 !important;
    border-radius:11px !important;
    background:#ffffff !important;
    color:#0f172a !important;
}

/* ── Buttons ── */
.stButton > button {
    width:100% !important; border-radius:12px !important;
    height:3.2rem !important;
    background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%) !important;
    color:#ffffff !important; border:none !important;
    font-weight:600 !important; font-size:15px !important;
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow:0 4px 15px rgba(59,130,246,0.3) !important;
}
.stButton > button:hover {
    opacity:0.9 !important; transform:translateY(-2px) !important;
    box-shadow:0 8px 25px rgba(59,130,246,0.4) !important;
}
.stDownloadButton > button {
    background:linear-gradient(135deg,#10b981 0%,#059669 100%) !important;
    color:#ffffff !important;
}

/* ── Radio ── */
.stRadio > div { gap:10px !important; }
.stRadio > div > label {
    background:#f1f5f9 !important; border:1px solid #e2e8f0 !important;
    border-radius:9px !important; padding:8px 14px !important;
    color:#0f172a !important; font-weight:500 !important;
}
.stRadio > div > label[data-checked="true"] {
    background:#eff6ff !important; border-color:#3b82f6 !important;
    color:#1d4ed8 !important; font-weight:700 !important;
}

/* ── Alerts ── */
div[data-testid="stSuccessMessage"] {
    background:rgba(16,185,129,0.08) !important;
    border:1.5px solid rgba(16,185,129,0.3) !important; border-radius:10px !important;
}
div[data-testid="stErrorMessage"] {
    background:rgba(239,68,68,0.08) !important;
    border:1.5px solid rgba(239,68,68,0.3) !important; border-radius:10px !important;
}
div[data-testid="stInfoMessage"] {
    background:rgba(59,130,246,0.08) !important;
    border:1.5px solid rgba(59,130,246,0.3) !important; border-radius:10px !important;
}

hr { border:none; border-top:1px solid #e2e8f0; margin:20px 0; }

@media (max-width:768px) {
    .sf-header-title { font-size:2.6rem !important; }
    .sf-watermark { font-size:2rem !important; letter-spacing:5px !important; }
    .stButton > button { height:3rem !important; font-size:.9rem !important; }
    .stTabs [data-baseweb="tab-list"] { overflow-x:auto !important; flex-wrap:nowrap !important; }
    .stTabs [data-baseweb="tab"] { white-space:nowrap !important; font-size:.8rem !important; }
    div[role="listbox"] {
        max-height:38vh !important; overflow-y:auto !important;
        position:fixed !important; z-index:9999 !important;
    }
}
            
# ── AI Chat Assistant Widget ── (add inside your main CSS block)

/* ═══════════════════════════════════════════════
   AI ASSISTANT — FLOATING CHAT WIDGET (Bottom-Right)
   ═══════════════════════════════════════════════ */

/* Toggle Button */
.chat-fab {
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 58px;
    height: 58px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    cursor: pointer;
    box-shadow: 0 8px 24px rgba(59,130,246,0.45);
    z-index: 99999;
    border: none;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.chat-fab:hover {
    transform: scale(1.08) translateY(-2px);
    box-shadow: 0 12px 32px rgba(59,130,246,0.55);
}

/* Chat Panel */
.chat-panel {
    position: fixed;
    bottom: 100px;
    right: 24px;
    width: 370px;
    max-height: 540px;
    background: rgba(255,255,255,0.97);
    backdrop-filter: blur(14px);
    border-radius: 20px;
    border: 1.5px solid rgba(59,130,246,0.18);
    box-shadow: 0 20px 60px rgba(15,23,42,0.18);
    display: flex;
    flex-direction: column;
    z-index: 99998;
    overflow: hidden;
}

/* Chat Header */
.chat-header {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-radius: 20px 20px 0 0;
}
.chat-header-avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: rgba(255,255,255,0.2);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
}
.chat-header-info { flex: 1; }
.chat-header-name  { color: white; font-weight: 800; font-size: .93rem; }
.chat-header-scope { color: rgba(255,255,255,0.75); font-size: .72rem; margin-top: 1px; }
.chat-header-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #4ade80; box-shadow: 0 0 6px #4ade80;
}

/* Messages Container */
.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 14px 14px 8px 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 360px;
}

/* Message Bubbles */
.msg-user {
    align-self: flex-end;
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white !important;
    border-radius: 16px 16px 4px 16px;
    padding: 9px 13px;
    max-width: 82%;
    font-size: .86rem;
    line-height: 1.5;
    box-shadow: 0 4px 12px rgba(59,130,246,0.25);
}
.msg-ai {
    align-self: flex-start;
    background: #f1f5f9;
    color: #0f172a !important;
    border-radius: 16px 16px 16px 4px;
    padding: 9px 13px;
    max-width: 88%;
    font-size: .86rem;
    line-height: 1.55;
    border: 1px solid #e2e8f0;
}
.msg-ai.denied {
    background: #fff1f2;
    border-color: #fecdd3;
    color: #be123c !important;
}
.msg-label {
    font-size: .68rem;
    font-weight: 700;
    margin-bottom: 3px;
    opacity: 0.7;
}

/* Input Row */
.chat-input-row {
    padding: 10px 12px;
    border-top: 1px solid #e2e8f0;
    background: #f8fafc;
    border-radius: 0 0 20px 20px;
}
            
</style>

""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# Part 2 - DATA LOADER
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

# Category metadata — icons & descriptions shown on onboarding screen

CATEGORY_META = {
    "K-12th": {
        "icon": "🏫",
        "desc": "Class 1 to 12 · School Curriculum",
        "color": "#3b82f6"
    },
    "Undergraduate": {
        "icon": "🎓",
        "desc": "B.Tech · BCA · B.Sc · B.Com · B.A", # Updated
        "color": "#8b5cf6"
    },
    "Postgraduate": {
        "icon": "🔬",
        "desc": "M.Tech · MCA · MBA · M.Sc", # Updated
        "color": "#10b981"
    },
    "Competitive Exams": {
        "icon": "🏆",
        "desc": "JEE · NEET · UPSC · CAT & more",
        "color": "#f59e0b"
    },
    "Professional": {
        "icon": "💼",
        "desc": "CA · CFA · CS · CMA · Law", # Updated
        "color": "#ef4444"
    },
    "Skill & Certification": {
        "icon": "📜",
        "desc": "Tech · Design · Language Courses",
        "color": "#06b6d4"
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE — includes new user_profile table
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()

    # ── Core users ────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    # ── NEW: User Profile (category lock for personalisation) ─────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            username     TEXT PRIMARY KEY,
            category     TEXT DEFAULT '',
            course       TEXT DEFAULT '',
            stream       TEXT DEFAULT '',
            board        TEXT DEFAULT '',
            onboarded    INTEGER DEFAULT 0,
            created_at   TEXT DEFAULT ''
        )
    """)

    # ── XP / Streak Stats ─────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            username       TEXT PRIMARY KEY,
            total_xp       INTEGER DEFAULT 0,
            streak_days    INTEGER DEFAULT 0,
            last_login     TEXT    DEFAULT '',
            total_minutes  INTEGER DEFAULT 0
        )
    """)

    # ── Achievements / Badges ─────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            username   TEXT,
            badge_id   TEXT,
            earned_at  TEXT,
            PRIMARY KEY (username, badge_id)
        )
    """)

    # ── Flashcards ────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
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
            created_date     TEXT
        )
    """)

    # ── Study Sessions ────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT,
            subject   TEXT,
            minutes   INTEGER DEFAULT 0,
            sess_date TEXT
        )
    """)

    # ── Safe migration helper ─────────────────────────────────────────────
    def get_cols(table):
        c.execute(f"PRAGMA table_info({table})")
        return [r[1] for r in c.fetchall()]

    def add_col(table, col, defn):
        if col not in get_cols(table):
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")

    # user_profile migrations
    add_col("user_profile", "category",   "TEXT DEFAULT ''")
    add_col("user_profile", "course",     "TEXT DEFAULT ''")
    add_col("user_profile", "stream",     "TEXT DEFAULT ''")
    add_col("user_profile", "board",      "TEXT DEFAULT ''")
    add_col("user_profile", "onboarded",  "INTEGER DEFAULT 0")
    add_col("user_profile", "created_at", "TEXT DEFAULT ''")

    # user_stats migrations
    add_col("user_stats", "total_xp",      "INTEGER DEFAULT 0")
    add_col("user_stats", "streak_days",   "INTEGER DEFAULT 0")
    add_col("user_stats", "last_login",    "TEXT DEFAULT ''")
    add_col("user_stats", "total_minutes", "INTEGER DEFAULT 0")

    # achievements migrations
    add_col("achievements", "earned_at", "TEXT")

    # flashcards migrations
    add_col("flashcards", "subject",          "TEXT DEFAULT ''")
    add_col("flashcards", "chapter",          "TEXT DEFAULT ''")
    add_col("flashcards", "ease_factor",      "REAL DEFAULT 2.5")
    add_col("flashcards", "interval_days",    "INTEGER DEFAULT 1")
    add_col("flashcards", "next_review_date", "TEXT")
    add_col("flashcards", "review_count",     "INTEGER DEFAULT 0")
    add_col("flashcards", "created_date",     "TEXT")

    # study_sessions migrations
    add_col("study_sessions", "subject",   "TEXT")
    add_col("study_sessions", "minutes",   "INTEGER DEFAULT 0")
    add_col("study_sessions", "sess_date", "TEXT")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# USER PROFILE FUNCTIONS (Onboarding Core)
# ─────────────────────────────────────────────────────────────────────────────
def save_user_profile(username, category, course, stream, board):
    """Save personalised profile after onboarding."""
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    now  = datetime.datetime.now().isoformat()
    c.execute("""
        INSERT INTO user_profile (username, category, course, stream, board, onboarded, created_at)
        VALUES (?,?,?,?,?,1,?)
        ON CONFLICT(username) DO UPDATE SET
            category   = excluded.category,
            course     = excluded.course,
            stream     = excluded.stream,
            board      = excluded.board,
            onboarded  = 1,
            created_at = excluded.created_at
    """, (username, category, course, stream, board, now))
    conn.commit()
    conn.close()

def get_user_profile(username):
    """Return the saved profile dict or None if not onboarded."""
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO user_profile (username) VALUES (?)
    """, (username,))
    conn.commit()
    c.execute("""
        SELECT category, course, stream, board, onboarded
        FROM user_profile WHERE username=?
    """, (username,))
    row = c.fetchone()
    conn.close()
    if row and row[4] == 1 and row[0]:
        return {
            "category": row[0],
            "course":   row[1],
            "stream":   row[2],
            "board":    row[3],
        }
    return None

def is_onboarded(username):
    """Check if user has completed onboarding."""
    profile = get_user_profile(username)
    return profile is not None

def reset_profile(username):
    """Allow user to change their profile/category."""
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("""
        UPDATE user_profile SET onboarded=0, category='', course='', stream='', board=''
        WHERE username=?
    """, (username,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STUDY DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def hash_p(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
# XP & STREAK
# ─────────────────────────────────────────────────────────────────────────────
def award_xp(username, xp):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute(
        "UPDATE user_stats SET total_xp = COALESCE(total_xp,0) + ? WHERE username=?",
        (xp, username)
    )
    conn.commit()
    conn.close()

def check_daily_login(username):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute(
        "SELECT last_login, streak_days FROM user_stats WHERE username=?",
        (username,)
    )
    row = c.fetchone()
    if row:
        last, streak = row
        if last == today:
            conn.close()
            return {"message": f"✅ Already checked in today · 🔥 {streak} day streak!", "xp": 0}
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        streak    = (streak + 1) if last == yesterday else 1
        xp        = 20
        c.execute(
            "UPDATE user_stats SET last_login=?, streak_days=?, total_xp=COALESCE(total_xp,0)+? WHERE username=?",
            (today, streak, xp, username)
        )
        conn.commit()
        conn.close()
        return {"message": f"🔥 {streak} day streak! +{xp} XP", "xp": xp, "streak": streak}
    conn.close()
    return {"message": "Checked in!", "xp": 0}

def update_streak(username):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute(
        "SELECT last_login, streak_days FROM user_stats WHERE username=?",
        (username,)
    )
    row = c.fetchone()
    if row:
        last, streak = row
        if last == today:
            conn.close()
            return
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        streak    = (streak + 1) if last == yesterday else 1
        c.execute(
            "UPDATE user_stats SET last_login=?, streak_days=? WHERE username=?",
            (today, streak, username)
        )
    conn.commit()
    conn.close()

def get_user_stats(username):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute("""
        SELECT COALESCE(total_xp,0), COALESCE(streak_days,0), COALESCE(total_minutes,0)
        FROM user_stats WHERE username=?
    """, (username,))
    row = c.fetchone()
    total_xp, streak_days, total_minutes = row if row else (0, 0, 0)

    # sync total_minutes from study_sessions if zero
    if total_minutes == 0:
        try:
            c.execute(
                "SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE username=?",
                (username,)
            )
            total_minutes = c.fetchone()[0] or 0
            c.execute(
                "UPDATE user_stats SET total_minutes=? WHERE username=?",
                (total_minutes, username)
            )
            conn.commit()
        except: pass

    # weekly minutes
    weekly_minutes = 0
    try:
        week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        c.execute(
            "SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE username=? AND sess_date>=?",
            (username, week_ago)
        )
        weekly_minutes = c.fetchone()[0] or 0
    except: pass

    # flashcards due today
    flashcards_due = 0
    try:
        today = datetime.date.today().isoformat()
        c.execute(
            "SELECT COUNT(*) FROM flashcards WHERE username=? AND next_review_date<=?",
            (username, today)
        )
        flashcards_due = c.fetchone()[0] or 0
    except: pass

    conn.commit()
    conn.close()
    return {
        "total_xp":             total_xp,
        "streak_days":          streak_days,
        "total_minutes":        total_minutes,
        "total_study_minutes":  total_minutes,
        "weekly_study_minutes": weekly_minutes,
        "flashcards_due":       flashcards_due,
        "level":                (total_xp // 500) + 1,
        "level_progress":       total_xp % 500,
    }

def record_study_session(username, subject, minutes):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute(
        "INSERT INTO study_sessions (username, subject, minutes, sess_date) VALUES (?,?,?,?)",
        (username, subject, int(minutes), today)
    )
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))
    c.execute(
        "UPDATE user_stats SET total_minutes = COALESCE(total_minutes,0) + ? WHERE username=?",
        (int(minutes), username)
    )
    conn.commit()
    conn.close()
    try: auto_check_badges(username)
    except: pass

# ─────────────────────────────────────────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────────────────────────────────────────
ALL_BADGES = [
    {"id":"first_login",  "name":"First Step",      "icon":"👣", "desc":"Logged in for the first time"},
    {"id":"streak_3",     "name":"Heatwave",         "icon":"🔥", "desc":"3-day study streak"},
    {"id":"streak_7",     "name":"Weekly Warrior",   "icon":"🎖️", "desc":"7-day study streak"},
    {"id":"streak_14",    "name":"Fortnight Champ",  "icon":"🏆", "desc":"14-day study streak"},
    {"id":"streak_30",    "name":"Monthly Master",   "icon":"👑", "desc":"30-day study streak"},
    {"id":"first_gen",    "name":"Starter Spark",    "icon":"✨", "desc":"Generated first AI content"},
    {"id":"qp_generated", "name":"Paper Setter",     "icon":"📝", "desc":"Generated a question paper"},
    {"id":"quiz_done",    "name":"Quiz Taker",        "icon":"🧠", "desc":"Generated a quiz"},
    {"id":"fc_10",        "name":"Card Collector",   "icon":"🗂️", "desc":"Created 10 flashcards"},
    {"id":"study_60",     "name":"Hour Hero",         "icon":"⏱️", "desc":"Studied 60 minutes total"},
    {"id":"study_300",    "name":"Study Champion",   "icon":"🎓", "desc":"Studied 5 hours total"},
    {"id":"onboarded",    "name":"Profile Set",      "icon":"🧩", "desc":"Completed personalised onboarding"},
]

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    try:
        earned_at = datetime.datetime.now().isoformat()
        c.execute(
            "INSERT OR IGNORE INTO achievements (username, badge_id, earned_at) VALUES (?,?,?)",
            (username, badge_id, earned_at)
        )
        conn.commit()
    except: pass
    finally: conn.close()

def get_earned_badges(username):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("SELECT badge_id FROM achievements WHERE username=?", (username,))
    ids = {r[0] for r in c.fetchall()}
    conn.close()
    return ids

def auto_check_badges(username):
    stats     = get_user_stats(username)
    conn      = sqlite3.connect("users.db")
    c         = conn.cursor()
    earned_at = datetime.datetime.now().isoformat()

    def aw(bid):
        try:
            c.execute(
                "INSERT OR IGNORE INTO achievements (username, badge_id, earned_at) VALUES (?,?,?)",
                (username, bid, earned_at)
            )
        except: pass

    try:
        if stats["streak_days"]   >= 3:   aw("streak_3")
        if stats["streak_days"]   >= 7:   aw("streak_7")
        if stats["streak_days"]   >= 14:  aw("streak_14")
        if stats["streak_days"]   >= 30:  aw("streak_30")
        if stats["total_minutes"] >= 60:  aw("study_60")
        if stats["total_minutes"] >= 300: aw("study_300")
        if is_onboarded(username):        aw("onboarded")
        conn.commit()
    except: pass
    finally: conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARD HELPERS  (SM-2 Spaced Repetition)
# ─────────────────────────────────────────────────────────────────────────────
def save_flashcard(username, front, back, subject="", chapter=""):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        INSERT INTO flashcards
            (username, front_text, back_text, subject, chapter,
             ease_factor, interval_days, next_review_date, review_count, created_date)
        VALUES (?,?,?,?,?,2.5,1,?,0,?)
    """, (username, front, back, subject, chapter, today, today))
    conn.commit()
    conn.close()
    # check fc_10 badge
    conn2 = sqlite3.connect("users.db")
    c2    = conn2.cursor()
    c2.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
    count = c2.fetchone()[0] or 0
    conn2.close()
    if count >= 10:
        award_badge(username, "fc_10")

def get_due_flashcards(username):
    conn  = sqlite3.connect("users.db")
    c     = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""
        SELECT id, front_text, back_text, subject, chapter,
               ease_factor, interval_days, review_count
        FROM flashcards
        WHERE username=? AND next_review_date<=?
        ORDER BY next_review_date ASC
    """, (username, today))
    rows = c.fetchall()
    conn.close()
    return rows

def update_flashcard_review(card_id, performance):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute(
        "SELECT ease_factor, interval_days, review_count FROM flashcards WHERE id=?",
        (card_id,)
    )
    row = c.fetchone()
    if not row:
        conn.close()
        return
    ef, interval, rc = row
    if   performance == 1: interval = 1;                          ef = max(1.3, ef - 0.2)
    elif performance == 2: interval = max(1, int(interval * 1.2))
    elif performance == 3: interval = max(1, int(interval * ef))
    else:                  interval = max(1, int(interval * ef * 1.3)); ef = min(3.0, ef + 0.1)
    next_date = (datetime.date.today() + datetime.timedelta(days=interval)).isoformat()
    c.execute("""
        UPDATE flashcards
        SET ease_factor=?, interval_days=?, next_review_date=?, review_count=?
        WHERE id=?
    """, (ef, interval, next_date, rc + 1, card_id))
    conn.commit()
    conn.close()

def delete_flashcard(card_id):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()

def get_all_flashcards(username):
    conn = sqlite3.connect("users.db")
    c    = conn.cursor()
    c.execute("""
        SELECT id, front_text, back_text, subject, chapter, next_review_date, review_count
        FROM flashcards WHERE username=? ORDER BY created_date DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def get_available_models():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ["Error: GEMINI_API_KEY not found in secrets.toml"]
    try:
        genai.configure(api_key=api_key)
        return [
            m.name for m in genai.list_models()
            if "gemini" in m.name.lower()
            and "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
    except Exception as e:
        return [f"Error: {e}"]

def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ("⚠️ GEMINI_API_KEY not found in .streamlit/secrets.toml", "None")
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Config error: {e}", "None")
    try:
        available = [
            m.name for m in genai.list_models()
            if "gemini" in m.name.lower()
            and "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
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
                    temperature=0.0,
                    max_output_tokens=8192,
                    top_p=0.9
                )
            )
            if response and getattr(response, "text", None):
                return response.text, model_name
        except: continue
    return ("❌ All models failed. Check your API key and quota.", "None")

def parse_flashcards(raw_text):
    cards  = []
    blocks = raw_text.strip().split("CARD ")
    for block in blocks:
        if not block.strip(): continue
        front = back = ""
        for line in block.splitlines():
            l = line.strip()
            if   l.upper().startswith("FRONT:"): front = l[6:].strip()
            elif l.upper().startswith("BACK:"):  back  = l[5:].strip()
        if front and back:
            cards.append({"front": front, "back": back})
    return cards

def build_flashcard_prompt(subject, chapter, topic):
    return (
        f"Create exactly 10 study flashcards.\n"
        f"Subject: {subject} | Chapter: {chapter} | Topic: {topic}\n"
        f"Use EXACTLY this format:\n"
        f"CARD 1\nFRONT: [question or term]\nBACK: [answer or definition]\n"
        f"CARD 2\nFRONT: ...\nBACK: ...\n"
        f"(Continue for all 10. No extra text outside this format.)"
    )

# ── ADD THESE TWO BELOW build_flashcard_prompt ────────────────────────────────

def build_full_qp_prompt(board, course, stream, subject, audience):
    return (
        f"You are an expert exam paper setter.\n"
        f"Board: {board} | Course: {course} | Stream: {stream} | "
        f"Subject: {subject} | For: {audience}\n\n"
        f"Create a COMPLETE full-subject exam question paper.\n\n"
        f"🛑 CRITICAL FORMATTING RULES (FAILURE TO FOLLOW WILL RESULT IN ERROR):\n"
        f"1. DO NOT put MCQ options on the same line as the question.\n"
        f"2. Every question must end with a DOUBLE NEWLINE.\n"
        f"3. Every option (a, b, c, d) MUST be on a NEW line and start with a dash to force Markdown list rendering.\n\n"
        f"EXACT EXAMPLE FORMAT:\n"
        f"Q1. Question text here?\n\n"
        f"- a) Option 1\n"
        f"- b) Option 2\n"
        f"- c) Option 3\n"
        f"- d) Option 4\n\n"
        f"Structure:\n"
        f"- Section A: 15 MCQs (1 mark each). Use the DASH layout shown above.\n"
        f"- Section B: 8 Short Answer Questions (3 marks each)\n"
        f"- Section C: 5 Long Answer Questions (7 marks each)\n"
        f"- Section D: 2 Case Studies (8 marks each)\n"
        f"- Section E: 1 Map / Diagram Question (10 marks)\n\n"
        f"Total: 100 marks | Difficulty: 30% easy, 50% medium, 20% hard\n"
        f"Format professionally. No answers."
    )


def build_answers_prompt(question_paper, board, course, subject, paper_title):
    return (
        f"You are an expert educator and examiner.\n"
        f"Board: {board} | Course: {course} | Subject: {subject}\n\n"
        f"Below is an exam question paper titled '{paper_title}'.\n"
        f"Rewrite the ENTIRE question paper and insert a detailed model answer after EVERY question.\n\n"
        f"🛑 STRICT FORMATTING RULES — FOLLOW EXACTLY:\n"
        f"1. Keep ALL original section headings (## Section A, ## Section B, etc.).\n"
        f"2. Copy each question EXACTLY as written.\n"
        f"3. After EVERY question, add TWO blank lines.\n"
        f"4. Then write '**✅ Answer:**' on its OWN separate line.\n"
        f"5. Then write the answer on the NEXT line after that.\n"
        f"6. Then add a horizontal rule '---' to separate from the next question.\n"
        f"7. For Section D (Case Studies):\n"
        f"   - First write the full case study passage.\n"
        f"   - Then list each sub-question on its OWN line.\n"
        f"   - After EACH sub-question, add TWO blank lines then '**✅ Answer:**'.\n"
        f"   - NEVER place a sub-question and its answer on the same line.\n\n"
        f"EXAMPLE FORMAT:\n"
        f"---\n"
        f"## Section A: MCQs\n\n"
        f"**Q1.** What is Power?\n\n"
        f"(a) Option 1  (b) Option 2  (c) Option 3  (d) Option 4\n\n"
        f"**✅ Answer:** (b) Option 2 — Because...\n\n"
        f"---\n\n"
        f"## Section D: Case Study\n\n"
        f"**Case Study:** Read the following passage carefully...\n\n"
        f"[Passage text here]\n\n"
        f"**Q1.** What does the passage suggest about...?\n\n"
        f"**✅ Answer:**\n"
        f"The passage suggests that...\n\n"
        f"---\n\n"
        f"**Q2.** How does this relate to...?\n\n"
        f"**✅ Answer:**\n"
        f"This relates to...\n\n"
        f"---\n\n"
        f"QUESTION PAPER TO ANSWER:\n{question_paper}"
    )



def build_prompt(tool, chapter, topic, subject, audience, style, board="", course="", language="English"):

    lang_instruction = ""
    if language and language != "English":
        lang_instruction = f"🛑 STRICT RULE: Generate the ENTIRE response fluently in {language}. If using technical terms, you may put the English term in brackets.\n\n"

    # This base forces the AI to stop being lazy and act as a full textbook
    base = (
        f"{lang_instruction}"
        f"You are a world-class academic professor and expert examiner for {board} {course} students.\n"
        f"Subject: {subject}\n"
        f"Topic: {topic}\n"
        f"Target Chapter: {chapter}\n"
        f"Audience: {audience}\n\n"
        f"🚨 CRITICAL INSTRUCTION:\n"
        f"Do NOT give a superficial or brief overview. You must act as the ultimate study guide.\n"
        f"Dive deep into the precise academic syllabus for '{chapter}'. Recall all textbook knowledge, "
        f"core principles, exceptions, dates, formulas, and advanced concepts related to this specific chapter.\n\n"
    )

    # Combined Tool & Style logic with HIGH DETAIL instructions
    if tool == "📄 Detailed":
        return base + (
            "Create an EXHAUSTIVE, textbook-level detailed chapter guide.\n"
            "Include:\n"
            "1. Chapter Overview & Importance\n"
            "2. Deep dive into ALL Key Concepts (use subheadings)\n"
            "3. All important Definitions, Laws, and Formulas (in markdown tables/blocks)\n"
            "4. Step-by-step Worked Examples or Case Studies\n"
            "5. Common student mistakes to avoid\n"
            "Format beautifully with ### headings, bullet points, and **bold** keywords."
        )
        
    if tool == "⚡ Short & Quick":
        return base + (
            "Create a highly efficient Quick-Reference Summary for last-minute revision.\n"
            "Include: One-liner chapter definition, exactly 10 high-yield bullet points, "
            "and a quick-glance table of formulas/facts. Keep it concise but pack it with pure value."
        )
        
    if tool in ["📋 Notes Format", "📝 Summary"]:
        return base + (
            "Create highly structured, classroom-style notes.\n"
            "Use a strict hierarchy: Main Headings (###), Subheadings (####), and bullet points.\n"
            "Include precise definitions, comparisons in Markdown Tables, and clear examples for every sub-topic."
        )
    
    if tool == "🧠 Quiz":
        return base + (
            "Create a comprehensive Chapter Quiz.\n"
            "Include: \n"
            "- 5 tough MCQs (4 options each, with the correct option clearly marked with ✅)\n"
            "- 5 Short-answer questions testing core concepts\n"
            "- 3 Long-answer analytical questions\n"
            "Provide a detailed Answer Key at the very bottom."
        )
        
    if tool == "📌 Revision Notes":
        return base + (
            "Create Master Revision Notes designed to score 100%.\n"
            "Include: Top 10 must-know points, a complete formula/date sheet, mnemonic memory tricks, "
            "and a 'High Probability Exam Focus' section highlighting what examiners usually ask."
        )
        
    if tool == "🧪 Question Paper":
        return base + (
            f"Create a formal, highly realistic Exam Question Paper.\n"
            f"🛑 FORMATTING RULES:\n"
            f"1. DO NOT put MCQ options on the same line as the question text.\n"
            f"2. Use a DOUBLE NEWLINE after every question.\n"
            f"3. Use a NEW LINE and a DASH (-) for every MCQ option to force vertical lists.\n\n"
            f"Paper Structure:\n"
            f"- Section A: 10 MCQs (1 mark each)\n"
            f"- Section B: 5 Short Answer Questions (3 marks each)\n"
            f"- Section C: 4 Long Answer Questions (5 marks each)\n"
            f"- Section D: 1 Case Study / Application Question (8 marks)\n"
            f"DO NOT INCLUDE ANSWERS. This is a blind test paper."
        )

    if tool == "❓ Exam Q&A":
        return base + (
            "Create an ultimate Exam Q&A Bank.\n"
            "Generate 10 highly probable, frequently asked exam questions (mix of direct, conceptual, and application-based).\n"
            "Provide a PERFECT, full-marks model answer for EVERY single question. Explain step-by-step why the answer is correct."
        )
    
    return base + "Create complete, highly detailed, and accurate exam-ready study material."



def get_effective_output_name(tool, style=None):
    return {
        "📝 Summary":        "Summary",
        "🧠 Quiz":           "Quiz",
        "📌 Revision Notes": "Revision Notes",
        "🧪 Question Paper": "Question Paper",
        "❓ Exam Q&A":       "Exam Q&A",
        "📄 Detailed":       "Detailed Summary",
        "⚡ Short & Quick":    "Short & Quick Summary",
        "📋 Notes Format":    "Notes"
    }.get(tool, "Study Material")


def get_button_label(tool, style):
    return f"⚡ Generate {get_effective_output_name(tool, style)}"

# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(title, subtitle, content):
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm
    )
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph(title, ParagraphStyle(
        "T", parent=styles["Heading1"],
        fontSize=22, textColor=colors.HexColor("#3b82f6"),
        spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold"
    )))
    story.append(Paragraph(subtitle, ParagraphStyle(
        "S", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#64748b"),
        spaceAfter=18, alignment=TA_CENTER
    )))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 0.4*cm))

    body = ParagraphStyle(
        "B", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#1e293b"),
        spaceAfter=10, leading=14, alignment=TA_LEFT
    )
    head = ParagraphStyle(
        "H", parent=styles["Heading2"],
        fontSize=12, textColor=colors.HexColor("#2563eb"),
        spaceBefore=8, spaceAfter=5, fontName="Helvetica-Bold"
    )

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.18*cm))
            continue
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if line.startswith(("#","##","###")):
            story.append(Paragraph(line.lstrip("#").strip(), head))
        else:
            try:    story.append(Paragraph(safe, body))
            except: story.append(Paragraph(
                line.encode("ascii","ignore").decode(), body
            ))

    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Paragraph(
        f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle(
            "F", parent=styles["Normal"],
            fontSize=8, textColor=colors.HexColor("#94a3b8"),
            alignment=TA_CENTER
        )
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer
# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "logged_in": False, "username": "", "active_page": "dashboard",
        "ob_step": 1, "ob_category": "", "ob_course": "",
        "ob_stream": "", "ob_board": "", "ai_chat_open":    False,
        "ai_chat_history": [],"ai_chat_input_key": 0,
        "history": [], "current_chapters": [], "last_chapter_key": "",
        "generated_result": None, "generated_model": None,
        "generated_label": None,  "generated_tool": None,
        "generated_chapter": None,"generated_subject": None,
        "generated_topic": None,  "generated_course": None,
        "generated_stream": None, "generated_board": None,
        "generated_audience": None,"generated_output_style": None,
        "answers_result": None,   "answers_model": None, "show_answers": False,
        "fullpaper_result": None, "fullpaper_model": None,"show_fullpaper": False,
        "fullpaper_answers_result": None, "fullpaper_answers_model": None,
        "show_fullpaper_answers": False,
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
    st.session_state.active_page = page
    st.rerun()

def reset_generation_state():
    for k in ["generated_result","generated_model","generated_label","generated_tool",
              "generated_chapter","generated_subject","generated_topic","generated_course",
              "generated_stream","generated_board","generated_audience","generated_output_style",
              "answers_result","answers_model","fullpaper_result","fullpaper_model",
              "fullpaper_answers_result","fullpaper_answers_model"]:
        st.session_state[k] = None
    st.session_state.show_answers           = False
    st.session_state.show_fullpaper         = False
    st.session_state.show_fullpaper_answers = False

def add_to_history(tool, chapter, subject, result):
    entry = {
        "time":    datetime.datetime.now().strftime("%H:%M"),
        "tool":    tool,
        "chapter": chapter,
        "subject": subject,
        "preview": result[:80] + "..." if len(result) > 80 else result,
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:10]

# ─────────────────────────────────────────────────────────────────────────────
# ONBOARDING CHECKBOX HELPERS  ← must live here, BEFORE show_onboarding
# ─────────────────────────────────────────────────────────────────────────────
def _safe_state_key(text):
    """Convert any string into a safe session_state key."""
    return "".join(ch if ch.isalnum() else "_" for ch in str(text)).strip("_").lower()

def category_skips_course(selected_category):
    """
    Returns True when the selected category IS already the course
    (e.g. '10th Standard', 'Class 12', 'Grade 8', 'Semester 1').
    In that case the Course step is skipped entirely.
    """
    if not selected_category:
        return False
    cat = str(selected_category).strip().lower()
    direct_markers = ["standard", "class ", "grade ", "semester", "year"]
    if any(m in cat for m in direct_markers):
        return True
    try:
        courses = get_courses(selected_category) or []
        cleaned = [str(c).strip().lower() for c in courses if str(c).strip()]
        if not cleaned:
            return True
        if len(cleaned) == 1 and cleaned[0] == cat:
            return True
    except Exception:
        pass
    return False

def needs_board_selection(selected_category, selected_course=""):
    """Returns True when the school-board picker should be shown."""
    text = f"{selected_category} {selected_course}".strip().lower()
    school_markers = [
        "k-12","school","class ","grade ","standard",
        "cbse","icse","state board","isc","ib","cambridge"
    ]
    return any(m in text for m in school_markers)

def clear_checkbox_group(prefix):
    """Uncheck every checkbox whose key starts with  prefix_chk_  """
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

def render_checkbox_card(title, subtitle, icon, is_selected):
    """Renders a styled info card. The actual interaction is a checkbox below it."""
    border = "3px solid #2563eb" if is_selected else "2px solid #e2e8f0"
    bg     = "linear-gradient(135deg,#eff6ff,#dbeafe)" if is_selected else "white"
    shadow = "0 4px 18px rgba(37,99,235,.18)" if is_selected else "0 2px 12px rgba(15,23,42,.06)"
    tick   = "<div style='font-size:.72rem;color:#2563eb;font-weight:700;margin-top:7px;'>✓ Selected</div>" if is_selected else ""
    st.markdown(f"""
    <div style="
        background:{bg};border:{border};border-radius:16px;
        padding:16px 10px;text-align:center;box-shadow:{shadow};
        margin-bottom:4px;min-height:130px;
        display:flex;flex-direction:column;
        justify-content:center;align-items:center;">
        <div style="font-size:2.1rem;">{icon}</div>
        <div style="font-weight:800;font-size:.9rem;color:#0f172a;margin-top:7px;">{title}</div>
        <div style="font-size:.74rem;color:#64748b;margin-top:3px;">{subtitle}</div>
        {tick}
    </div>
    """, unsafe_allow_html=True)

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
        if st.button("← Back to Dashboard", key="back_to_dash",
                     use_container_width=True):
            go_to("dashboard")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

def render_step_indicator(current_step):
    labels  = ["Category", "Course", "Stream", "Confirm"]
    cols    = st.columns(len(labels) * 2 - 1)
    col_idx = 0
    for i, label in enumerate(labels, start=1):
        with cols[col_idx]:
            if i < current_step:
                cls  = "ob-step-done";   icon = "✓"
            elif i == current_step:
                cls  = "ob-step-active"; icon = str(i)
            else:
                cls  = "ob-step-lock";   icon = str(i)
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
# ★  ONBOARDING WIZARD
# ─────────────────────────────────────────────────────────────────────────────
def show_onboarding(username):

    _, hc, _ = st.columns([1, 3, 1])
    with hc:
        st.markdown("""
            <div class="sf-header" style="padding-top:24px;">
                <div class="sf-header-title">StudySmart AI</div>
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
                    meta   = CATEGORY_META.get(cat, {"icon": "📘", "desc": cat, "color": "#3b82f6"})
                    is_sel = (st.session_state.ob_category == cat)
                    with col:
                        render_checkbox_card(cat, meta["desc"], meta["icon"], is_sel)
                        st.checkbox(
                            "Select",
                            key=f"ob_cat_chk_{_safe_state_key(cat)}",
                            on_change=handle_single_select_checkbox,
                            args=("ob_cat", cat, available_cats, "ob_category",
                                  ["ob_course","ob_stream","ob_board"],
                                  ["ob_course","ob_stream","ob_board"])
                        )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            selected_cat = st.session_state.ob_category

            if selected_cat:
                meta        = CATEGORY_META.get(selected_cat, {"icon": "📘"})
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
        # STEP 2 — COURSE  (only shown for category-level selections)
        # ══════════════════════════════════════════════════════════════════
        elif st.session_state.ob_step == 2:
            cat = st.session_state.ob_category
            # Safety: auto-skip if not needed
            if category_skips_course(cat):
                st.session_state.ob_course = cat
                st.session_state.ob_step   = 3
                st.rerun()

            meta    = CATEGORY_META.get(cat, {"icon": "📘", "color": "#3b82f6"})
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
                    cols        = st.columns(len(row_courses))
                    for col, course in zip(cols, row_courses):
                        is_sel = (st.session_state.ob_course == course)
                        with col:
                            render_checkbox_card(course, "Program / Class", "📖", is_sel)
                            st.checkbox(
                                "Select",
                                key=f"ob_course_chk_{_safe_state_key(course)}",
                                on_change=handle_single_select_checkbox,
                                args=("ob_course", course, courses, "ob_course",
                                      ["ob_stream","ob_board"],
                                      ["ob_stream","ob_board"])
                            )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            col_back, col_next = st.columns(2)
            with col_back:
                if st.button("← Back", key="ob_back_2", use_container_width=True):
                    st.session_state.ob_step = 1
                    st.rerun()
            with col_next:
                if st.session_state.ob_course:
                    if st.button("Continue → Stream & Board", key="ob_next_2",
                                 use_container_width=True):
                        st.session_state.ob_step = 3
                        st.rerun()
                else:
                    st.info("👆 Please tick one course to continue.")

        # ══════════════════════════════════════════════════════════════════
        # STEP 3 — STREAM + BOARD
        # ══════════════════════════════════════════════════════════════════
        elif st.session_state.ob_step == 3:
            cat     = st.session_state.ob_category
            course  = st.session_state.ob_course or st.session_state.ob_category
            streams = get_streams(cat, course)

            stream_icons = {
                "Science":"🔬","Commerce":"💹","Arts":"🎨","Humanities":"📜",
                "Engineering":"⚙️","Medical":"🏥","General":"📚",
                "Mathematics":"📐","Biology":"🧬",
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
                    cols        = st.columns(len(row_streams))
                    for col, stream in zip(cols, row_streams):
                        icon   = stream_icons.get(stream, "📂")
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
                    st.session_state.ob_step = 1 if category_skips_course(cat) else 2
                    st.rerun()
            with col_next:
                stream_ok = bool(st.session_state.ob_stream)
                board_ok  = bool(st.session_state.ob_board)
                if stream_ok and board_ok:
                    if st.button("Continue → Confirm Profile", key="ob_next_3",
                                 use_container_width=True):
                        st.session_state.ob_step = 4
                        st.rerun()
                else:
                    st.info("👆 Please complete stream and board selection to continue.")

        # ══════════════════════════════════════════════════════════════════
        # STEP 4 — CONFIRM & SAVE
        # ══════════════════════════════════════════════════════════════════
        elif st.session_state.ob_step == 4:
            cat    = st.session_state.ob_category
            course = st.session_state.ob_course or st.session_state.ob_category
            stream = st.session_state.ob_stream
            board  = st.session_state.ob_board or "University / National Syllabus"
            meta   = CATEGORY_META.get(cat, {"icon": "📘", "color": "#3b82f6"})

            st.markdown("""
                <div style="text-align:center;margin-bottom:18px;">
                    <div style="font-size:1.4rem;font-weight:800;color:#0f172a;">
                        🎉 Almost There! Confirm Your Profile
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
                        <td style="padding:8px 12px;font-weight:1000;color:#475569;font-size:.9rem;width:40%;">📚 Category</td>
                        <td style="padding:8px 12px;font-weight:600;color:#1d4ed8;font-size:.8rem;">{cat}</td>
                    </tr>
                    <tr style="background:rgba(255,255,255,0.5);">
                        <td style="padding:8px 12px;font-weight:800;color:#475569;font-size:.9rem;">🎓 Course</td>
                        <td style="padding:8px 12px;font-weight:600;color:#1d4ed8;font-size:.8rem;">{course}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px 12px;font-weight:800;color:#475569;font-size:.9rem;">🔀 Stream</td>
                        <td style="padding:8px 12px;font-weight:600;color:#1d4ed8;font-size:.8rem;">{stream}</td>
                    </tr>
                    <tr style="background:rgba(255,255,255,0.5);">
                        <td style="padding:8px 12px;font-weight:800;color:#475569;font-size:.9rem;">🏫 Board / Syllabus</td>
                        <td style="padding:8px 12px;font-weight:600;color:#1d4ed8;font-size:.8rem;">{board}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            col_back, col_confirm = st.columns(2)
            with col_back:
                if st.button("← Edit Profile", key="ob_back_4", use_container_width=True):
                    st.session_state.ob_step = 3
                    st.rerun()
            with col_confirm:
                if st.button("🚀 Launch My Dashboard", key="ob_confirm", use_container_width=True):
                    save_user_profile(username, cat, course, stream, board)
                    award_badge(username, "onboarded")
                    award_xp(username, 50)
                    # Reset all onboarding state
                    st.session_state.ob_step     = 1
                    st.session_state.ob_category = ""
                    st.session_state.ob_course   = ""
                    st.session_state.ob_stream   = ""
                    st.session_state.ob_board    = ""
                    clear_checkbox_group("ob_cat")
                    clear_checkbox_group("ob_course")
                    clear_checkbox_group("ob_stream")
                    clear_checkbox_group("ob_board")
                    st.success("✅ Profile saved! Welcome to StudySmart AI 🎓")
                    time.sleep(0.8)
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(username):
    stats   = get_user_stats(username) or {}
    profile = get_user_profile(username) or {}

    with st.sidebar:
        cat  = profile.get("category", "—")
        crs  = profile.get("course",   "—")
        strm = profile.get("stream",   "—")
        brd  = profile.get("board",    "—")
        meta = CATEGORY_META.get(cat, {"icon": "🎓", "color": "#3b82f6"})

        st.markdown(f"""
            <div class="profile-badge">
                <div style="font-size:1.8rem;">{meta['icon']}</div>
                <div style="font-size:1rem;font-weight:800;margin-top:4px;">StudySmart AI</div>
                <div style="font-size:.75rem;margin-top:2px;opacity:.9;">Hi, {username} 👋</div>
                <div style="margin-top:8px;background:rgba(255,255,255,.15);
                    border-radius:10px;padding:7px 10px;
                    font-size:.73rem;line-height:1.7;">
                    <b>{cat}</b> · {crs}<br>{strm} · {brd}
                </div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#ff6b6b,#feca57);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                🔥 {stats.get('streak_days', 0)}<br>
                <span style="font-size:.62rem;font-weight:500;">day streak</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                ⭐ Lv {stats.get('level', 1)}<br>
                <span style="font-size:.62rem;font-weight:500;">
                    {stats.get('total_xp', 0)} XP
                </span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if not st.session_state.daily_checkin_done:
            if st.button("✅ Daily Check-in (+20 XP)",
                         use_container_width=True, key="sb_checkin"):
                result = check_daily_login(username)
                st.session_state.daily_checkin_done = True
                auto_check_badges(username)
                st.success(result.get("message", "Checked in!"))
                st.rerun()
        else:
            st.success(f"✅ Checked in · 🔥 {stats.get('streak_days', 0)} days")

        st.divider()

        st.markdown("**⏱️ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed = int(
                (datetime.datetime.now() - st.session_state.study_timer_start)
                .total_seconds() // 60
            )
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

        st.markdown("**🧭 Navigate**")
        cur = st.session_state.active_page
        for key, label in [
            ("dashboard",    "📊 Dashboard"),
            ("study",        "📚 Study Tools"),
            ("flashcards",   "🗂️ Flashcards"),
            ("achievements", "🏅 Achievements"),
        ]:
            btn_type = "primary" if cur == key else "secondary"
            if st.button(label, use_container_width=True,
                         key=f"nav_{key}", type=btn_type):
                if cur != key:
                    go_to(key)

        fc_due = stats.get("flashcards_due", 0)
        if fc_due > 0:
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.warning(f"📚 {fc_due} card{'s' if fc_due > 1 else ''} due for review!")

        st.divider()

        # ── LANGUAGE SELECTOR (Inside the sidebar) ──
        st.markdown("---")
        st.markdown("🌐 **Target Language**")

        lang_options = {
            "English": "English",
            "Hindi (हिन्दी)": "Hindi",
            "Kannada (ಕನ್ನಡ)": "Kannada",
            "Telugu (తెలుగు)": "Telugu",
            "Tamil (தமிழ்)": "Tamil"
        }

        display_lang = st.selectbox(
            "Choose language for study material",
            options=list(lang_options.keys()),
            index=0,
            key="target_lang_selector"
        )

        target_lang = lang_options[display_lang]

        # Store the selected language in session_state so it persists
        st.session_state.target_lang = target_lang

        st.divider()
        with st.expander("📜 Recent History"):
            if not st.session_state.history:
                st.caption("No activity yet.")
            else:
                for h in st.session_state.history:
                    st.markdown(f"""<div class="sf-hist">
                        🕐 {h['time']} | <b>{h['tool']}</b><br>
                        📖 {h['chapter']} — {h['subject']}<br>
                        <small>{h['preview']}</small>
                    </div>""", unsafe_allow_html=True)

        with st.expander("🤖 AI Status"):
            if st.button("Check Models", use_container_width=True, key="sb_models"):
                with st.spinner("Checking..."):
                    mdls = get_available_models()
                for m in mdls:
                    st.write(f"✅ {m}")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True, key="sb_logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # Return the selected language
    return st.session_state.target_lang




# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def show_dashboard(username, target_lang="English"):
    profile = get_user_profile(username) or {}
    cat     = profile.get("category", "")
    course  = profile.get("course",   "")
    stream  = profile.get("stream",   "")
    board   = profile.get("board",    "")
    meta    = CATEGORY_META.get(cat, {"icon": "🎓", "color": "#3b82f6"})

    # ★ FIX 2: NO render_back_button() here — dashboard is the home page.
    # The Testing Tools expander sits cleanly below the hero with no arrow overlap.
    render_header("StudySmart", f"{meta['icon']} {course} · {stream} · {board}")

    # ── 🧪 TESTING TOOLS — clean expander, no banner conflict ─────────────
    with st.expander("🛠️ Testing Tools — Switch Category / Board", expanded=False):
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#fefce8,#fef9c3);
            border:1.5px solid #fde68a;border-radius:12px;
            padding:12px 16px;margin-bottom:10px;">
            <b style="color:#92400e;">🧪 Testing Mode Active</b><br>
            <span style="font-size:.83rem;color:#78350f;">
                Current: <b>{cat}</b> → <b>{course}</b>
                → <b>{stream}</b> → <b>{board}</b><br>
                Click below to reset your profile and pick a different
                category, class, or board. XP and streaks are preserved.
            </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Reset Profile & Switch Category",
                     use_container_width=True, type="primary",
                     key="dash_switch_cat"):
            reset_profile(username)
            st.toast("Profile reset! Loading onboarding...", icon="🔄")
            time.sleep(0.8)
            st.rerun()

    stats = get_user_stats(username) or {}

    # ── Metric Cards ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, cls, icon, val, lbl in [
        (c1, "mc-blue",   "🔥", stats.get("streak_days", 0),                 "Day Streak"),
        (c2, "mc-green",  "⭐", f"Level {stats.get('level', 1)}",             "Your Level"),
        (c3, "mc-purple", "📚", stats.get("flashcards_due", 0),               "Cards Due"),
        (c4, "mc-amber",  "⏱️", f"{stats.get('weekly_study_minutes', 0)} min","This Week"),
    ]:
        with col:
            st.markdown(
                f'<div class="mc {cls}"><div class="icon">{icon}</div>'
                f'<div class="val">{val}</div><div class="lbl">{lbl}</div></div>',
                unsafe_allow_html=True
            )

    # ── XP Progress Bar ───────────────────────────────────────────────────
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    total_xp = stats.get("total_xp", 0)
    lvl      = stats.get("level", 1)
    lp       = stats.get("level_progress", total_xp % 500)
    pct      = min(100, int((lp / 500) * 100))
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;
        font-size:.85rem;font-weight:700;margin-bottom:5px;">
        <span>⭐ Level {lvl}</span>
        <span>{total_xp} XP &nbsp;·&nbsp; {500 - lp} XP to next level</span>
    </div>
    <div class="xp-wrap"><div class="xp-fill" style="width:{pct}%;"></div></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🎯 Your Profile**")
        st.markdown(f"""
        <div class="sf-soft-card">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <div>
                    <div style="font-size:.9rem;color:#64748b;font-weight:800;">CATEGORY</div>
                    <div style="font-weight:500;font-size:.7rem;">{meta['icon']} {cat}</div>
                </div>
                <div>
                    <div style="font-size:.9rem;color:#64748b;font-weight:800;">COURSE</div>
                    <div style="font-weight:500;font-size:.7rem;">📖 {course}</div>
                </div>
                <div>
                    <div style="font-size:.9rem;color:#64748b;font-weight:800;">STREAM</div>
                    <div style="font-weight:500;font-size:.7rem;">🔀 {stream}</div>
                </div>
                <div>
                    <div style="font-size:.9rem;color:#64748b;font-weight:800;">BOARD</div>
                    <div style="font-weight:500;font-size:.7rem;">🏫 {board}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🌱 Study Momentum**")
        mins   = stats.get("total_study_minutes", 0)
        growth = min(100, mins // 10)
        plant  = (
            ("🌱", "Seedling")       if growth < 20 else
            ("🌿", "Sprout")         if growth < 40 else
            ("🪴", "Growing Plant")  if growth < 70 else
            ("🌳", "Strong Tree")    if growth < 90 else
            ("🌲", "Master Tree")
        )
        st.markdown(f"""
        <div class="sf-soft-card" style="text-align:center;margin-bottom:10px;">
            <div style="font-size:2.6rem;">{plant[0]}</div>
            <div style="font-weight:800;font-size:.93rem;">{plant[1]}</div>
            <div style="font-size:.8rem;margin-top:3px;">{mins} min total studied</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions**")
        if st.button("📚 Open Study Tools",  use_container_width=True, key="d_study"):
            go_to("study")
        if st.button("🗂️ Review Flashcards", use_container_width=True, key="d_fc"):
            go_to("flashcards")
        if st.button("🏅 View Achievements", use_container_width=True, key="d_ach"):
            go_to("achievements")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**📜 Recent Activity**")
        if not st.session_state.history:
            st.info("No activity yet. Generate your first study content!")
        else:
            for h in st.session_state.history:
                st.markdown(f"""<div class="sf-hist">
                    🕐 {h['time']} | <b>{h['tool']}</b><br>
                    📖 {h['chapter']} — {h['subject']}<br>
                    <small>{h['preview']}</small>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**🏅 Badge Snapshot**")
        earned      = get_earned_badges(username)
        earned_list = [b for b in ALL_BADGES if b["id"] in earned][:4]
        if earned_list:
            bc = st.columns(2)
            for i, badge in enumerate(earned_list):
                with bc[i % 2]:
                    st.markdown(f"""<div class="bdg earned">
                        <div class="bi">{badge['icon']}</div>
                        <div class="bn">{badge['name']}</div>
                        <div class="bs">✅ Earned</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Complete daily check-in to earn your first badge!")
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS
# ─────────────────────────────────────────────────────────────────────────────
def show_achievements(username):
    render_back_button()
    render_header("Achievements", "Badges unlock automatically as you learn")
    auto_check_badges(username)

    stats       = get_user_stats(username) or {}
    earned      = get_earned_badges(username)
    earned_list = [b for b in ALL_BADGES if b["id"] in earned]
    locked_list = [b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(f"**✅ {len(earned_list)} / {len(ALL_BADGES)} badges earned**")
    st.progress(len(earned_list) / len(ALL_BADGES) if ALL_BADGES else 0)
    st.markdown("""
    <div style="font-size:.82rem;color:#475569;margin-top:8px;">
        🔥 Streaks — log in every day &nbsp;|&nbsp;
        ⏱️ Study time — use the timer &nbsp;|&nbsp;
        ✨ Content — generate AI material &nbsp;|&nbsp;
        🗂️ Flashcards — create 10 cards &nbsp;|&nbsp;
        🧩 Profile — complete onboarding
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if earned_list:
        st.markdown("## ✅ Earned Badges")
        cols = st.columns(min(4, len(earned_list)))
        for i, b in enumerate(earned_list):
            with cols[i % 4]:
                st.markdown(f"""<div class="bdg earned">
                    <div class="bi">{b['icon']}</div>
                    <div class="bn">{b['name']}</div>
                    <div class="bs">{b['desc']}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("No badges yet — start studying to earn them!")

    if locked_list:
        st.markdown("---")
        st.markdown("## 🔒 Locked Badges")
        hints = {
            "streak_3": "Log in 3 days in a row",
            "streak_7": "Log in 7 days in a row",
            "streak_14": "Log in 14 days in a row",
            "streak_30": "Log in 30 days in a row",
            "first_gen": "Generate any AI content",
            "qp_generated": "Generate a Question Paper",
            "quiz_done": "Generate a Quiz",
            "fc_10": "Create 10 flashcards",
            "study_60": "Study 60 min total",
            "study_300": "Study 300 min total",
            "onboarded": "Complete personalised onboarding",
        }
        cols = st.columns(min(4, len(locked_list)))
        for i, b in enumerate(locked_list):
            with cols[i % 4]:
                st.markdown(f"""<div class="bdg">
                    <div class="bi" style="opacity:.28;">🔒</div>
                    <div class="bn">{b['name']}</div>
                    <div class="bs">{hints.get(b['id'], b['desc'])}</div>
                </div>""", unsafe_allow_html=True)

    streak    = stats.get("streak_days", 0)
    total_min = stats.get("total_study_minutes", 0)
    st.markdown('<div class="sf-card" style="margin-top:14px;">', unsafe_allow_html=True)
    st.markdown("**📈 Progress Towards Next Badge**")
    shown = False
    for b in locked_list:
        bid = b["id"]
        if   bid == "streak_3"  and streak < 3:
            st.caption(f"🔥 Streak: {streak}/3 days");   st.progress(streak / 3);    shown = True
        elif bid == "streak_7"  and streak < 7:
            st.caption(f"🔥 Streak: {streak}/7 days");   st.progress(streak / 7);    shown = True
        elif bid == "streak_14" and streak < 14:
            st.caption(f"🔥 Streak: {streak}/14 days");  st.progress(streak / 14);   shown = True
        elif bid == "streak_30" and streak < 30:
            st.caption(f"🔥 Streak: {streak}/30 days");  st.progress(streak / 30);   shown = True
        elif bid == "study_60"  and total_min < 60:
            st.caption(f"⏱️ Study: {total_min}/60 min"); st.progress(total_min / 60); shown = True
        elif bid == "study_300" and total_min < 300:
            st.caption(f"⏱️ Study: {total_min}/300 min");st.progress(total_min/300);  shown = True
        elif bid == "fc_10":
            conn = sqlite3.connect("users.db"); cc = conn.cursor()
            cc.execute("SELECT COUNT(*) FROM flashcards WHERE username=?", (username,))
            fc = cc.fetchone()[0]; conn.close()
            if fc < 10:
                st.caption(f"🗂️ Flashcards: {fc}/10");  st.progress(fc / 10);        shown = True
    if not shown:
        st.success("🎉 Great work — keep studying to unlock more badges!")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Part 4 - FLASHCARDS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_flashcards(username):
    render_back_button()
    render_header("Flashcards", "Spaced repetition for lasting memory")
    tab1, tab2, tab3 = st.tabs(["📖 Review Due", "➕ Create", "📋 My Library"])

    # ── Tab 1: Review Due Cards ───────────────────────────────────────────
    with tab1:
        due = get_due_flashcards(username)
        if not due:
            st.success("🎉 No flashcards due today — great job!")
            total = len(get_all_flashcards(username))
            if total > 0:
                st.info(f"📚 You have {total} flashcard(s) in your library.")
            else:
                st.info("📭 No flashcards yet. Create some in the ➕ Create tab!")
        else:
            st.markdown(f"**{len(due)} card(s) due for review today**")
            idx = st.session_state.review_idx
            if idx >= len(due):
                st.session_state.review_idx = 0
                idx = 0
            card    = due[idx]
            card_id = card[0]
            front   = card[1]
            back    = card[2]

            st.markdown(f"""
            <div class="fc-front">
                <div style="font-size:.73rem;opacity:.7;margin-bottom:10px;
                    text-transform:uppercase;letter-spacing:.06em;">
                    Card {idx + 1} of {len(due)}
                </div>
                <div style="font-size:1.15rem;font-weight:700;line-height:1.5;">
                    {front}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if not st.session_state.review_show_ans:
                if st.button("👁️ Show Answer", use_container_width=True,
                             key="show_ans_btn"):
                    st.session_state.review_show_ans = True
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="fc-back">
                    <div style="font-size:.73rem;opacity:.8;margin-bottom:8px;">
                        ANSWER
                    </div>
                    <div style="font-size:.98rem;font-weight:700;line-height:1.5;">
                        {back}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown("**How well did you remember?**")
                b1, b2, b3, b4 = st.columns(4)
                for col, lbl, perf, ks in [
                    (b1, "😓 Again", 1, "again"),
                    (b2, "😐 Hard",  2, "hard"),
                    (b3, "🙂 Good",  3, "good"),
                    (b4, "😄 Easy",  4, "easy"),
                ]:
                    with col:
                        if st.button(lbl, use_container_width=True,
                                     key=f"fc_{ks}_{card_id}"):
                            update_flashcard_review(card_id, perf)
                            award_xp(username, 3)
                            st.session_state.review_idx      += 1
                            st.session_state.review_show_ans  = False
                            st.rerun()

    # ── Tab 2: Create Cards ───────────────────────────────────────────────
    with tab2:
        profile = get_user_profile(username) or {}
        p_subj  = profile.get("course", "")
        p_chap  = ""

        cl, cr = st.columns(2)
        with cl:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### ✍️ Manual Card")
            with st.form("manual_fc_form"):
                f_front = st.text_input("Front (Question / Term)")
                f_back  = st.text_area("Back (Answer / Definition)", height=80)
                f_subj  = st.text_input("Subject (optional)", value=p_subj)
                f_chap  = st.text_input("Chapter (optional)")
                if st.form_submit_button("➕ Save Card", use_container_width=True):
                    if f_front.strip() and f_back.strip():
                        save_flashcard(
                            username,
                            f_front.strip(), f_back.strip(),
                            f_subj.strip(),  f_chap.strip()
                        )
                        award_xp(username, 5)
                        auto_check_badges(username)
                        st.success("✅ Card saved! +5 XP")
                        st.rerun()
                    else:
                        st.warning("⚠️ Front and Back are required.")
            st.markdown('</div>', unsafe_allow_html=True)

        with cr:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### 🤖 AI Generate")
            with st.form("ai_fc_form"):
                ai_subj = st.text_input("Subject", value=p_subj)
                ai_chap = st.text_input("Chapter")
                ai_top  = st.text_input("Topic (optional)")
                if st.form_submit_button("⚡ Generate 10 Cards",
                                         use_container_width=True):
                    if ai_subj.strip() and ai_chap.strip():
                        with st.spinner("Generating flashcards..."):
                            raw, mdl = generate_with_fallback(
                                build_flashcard_prompt(
                                    ai_subj.strip(),
                                    ai_chap.strip(),
                                    ai_top.strip()
                                )
                            )
                        if mdl != "None":
                            cards = parse_flashcards(raw)
                            for card in cards:
                                save_flashcard(
                                    username,
                                    card["front"], card["back"],
                                    ai_subj.strip(), ai_chap.strip()
                                )
                            award_xp(username, len(cards) * 5)
                            auto_check_badges(username)
                            st.success(
                                f"✅ {len(cards)} cards saved! "
                                f"+{len(cards) * 5} XP"
                            )
                            st.rerun()
                        else:
                            st.error("❌ AI generation failed. Check API key.")
                    else:
                        st.warning("⚠️ Subject and Chapter are required.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 3: Library ────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        all_cards = get_all_flashcards(username)
        if not all_cards:
            st.markdown("""
            <div style="text-align:center;padding:30px;color:#64748b;">
                📭 No flashcards yet.<br>
                Create your first card in the ➕ Create tab.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption(f"📚 Total: {len(all_cards)} flashcard(s) in your library")
            for row in all_cards:
                c_id, front, back, subj, chap, nrd, rc = row
                with st.expander(
                    f"📌 {front[:60]}{'...' if len(front) > 60 else ''}"
                ):
                    st.markdown(f"**Q:** {front}")
                    st.markdown(f"**A:** {back}")
                    st.caption(
                        f"Subject: {subj or '—'} | Chapter: {chap or '—'} | "
                        f"Next review: {nrd} | Reviews done: {rc}"
                    )
                    if st.button("🗑️ Delete this card",
                                 key=f"del_fc_{c_id}",
                                 use_container_width=True):
                        delete_flashcard(c_id)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def render_custom_upload_section():
    """Renders a custom styled upload section for documents"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        ">
            <span style="font-size: 1.8rem;">📤</span>
            <div>
                <div style="
                    font-weight: 800;
                    font-size: 1rem;
                    color: white;
                ">
                    Upload & Summarize Your Documents
                </div>
                <div style="
                    font-size: 0.85rem;
                    color: rgba(255, 255, 255, 0.85);
                    margin-top: 4px;
                ">
                    PDF or Word files • AI will summarize instantly
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return text


# ─────────────────────────────────────────────────────────────────────────────
# MULTI-TOOL DOCUMENT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_document_output(full_text, filename, action, language="English"):
    """Forces the AI to generate the study material in the target language."""
    
    # We add a CRITICAL instruction about the language here
    base_setup = (
        f"You are an expert academic professor and exam coach.\n"
        f"You have been given the COMPLETE extracted text of a document titled: '{filename}'\n"
        f"🛑 STRICT RULE 1: Base your entire response ONLY on the provided text.\n"
        f"🛑 STRICT RULE 2: You MUST write the ENTIRE response in {language}. "
        f"If the language is not English, ensure the technical terms are explained in {language} "
        f"but you may keep the English term in brackets () for clarity.\n\n"
    )
    
    if action == "📚 Complete Study Guide":
        instructions = (
            "Create a LONG, EXHAUSTIVE, DETAILED study guide.\n"
            "Use this EXACT structure with markdown formatting:\n"
            "# 📚 Complete Exam Study Guide\n"
            "## 📌 1. Executive Overview\n"
            "## 📑 2. Section-by-Section Breakdown (Do not skip any section)\n"
            "## 🔑 3. Key Terms & Definitions\n"
            "## 🎯 4. Exam Questions & Model Answers\n"
        )
    elif action == "⚡ Short & Quick Notes":
        instructions = (
            "Create a highly condensed, quick-reference summary.\n"
            "Include:\n"
            "- A brief 2-paragraph overview.\n"
            "- 10 absolute most important bullet points.\n"
            "- Important formulas, dates, or names mentioned.\n"
            "Make it easy to read in 3 minutes."
        )
    elif action == "🧠 Quiz with Answers":
        instructions = (
            "Create a challenging Quiz based on the document.\n"
            "Include:\n"
            "- 5 Multiple Choice Questions (with 4 options each).\n"
            "- 5 True/False or Short Answer questions.\n"
            "At the VERY END, provide an 'Answer Key' section with the correct answers and a brief explanation for each."
        )
    elif action == "❓ Exam Q&A Bank":
        instructions = (
            "Create a comprehensive Exam Q&A bank based on the document.\n"
            "Generate 8-10 highly probable exam questions (mix of short and long answer).\n"
            "Provide a detailed, step-by-step model answer for EVERY question."
        )
    elif action == "🧪 Mock Question Paper":
        instructions = (
            "Create a formal exam Question Paper based entirely on the document.\n"
            "Structure it professionally:\n"
            "- Section A: 5 MCQs (1 mark each)\n"
            "- Section B: 4 Short Answer Questions (3 marks each)\n"
            "- Section C: 2 Long Answer/Essay Questions (5 marks each)\n"
            "🛑 DO NOT INCLUDE THE ANSWERS. This is just the question paper for the student to practice."
        )

    prompt = f"{base_setup}\nINSTRUCTIONS:\n{instructions}\n\n---\nCOMPLETE DOCUMENT TEXT:\n{full_text}"
    return generate_with_fallback(prompt)





def chunk_text(text, chunk_size=12000, overlap=1000):
    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap

    return chunks


def generate_exam_ready_summary(doc_text):
    chunks = chunk_text(doc_text, chunk_size=12000, overlap=1000)
    chunk_summaries = []

    for i, chunk in enumerate(chunks, start=1):
        prompt = (
            f"You are an expert teacher creating exam-preparation notes.\n"
            f"This is chunk {i} of {len(chunks)} from a study document.\n\n"
            "Instructions:\n"
            "- Write detailed notes for students preparing for exams.\n"
            "- Explain concepts in simple but complete language.\n"
            "- Include important facts, definitions, causes, effects, arguments, dates, formulas, and examples where relevant.\n"
            "- Do not give only headings with 2 bullet points. Write in-depth paragraphs.\n"
            "- Write enough detail so a student can revise from this directly.\n"
            "- End with a short section titled 'Key Exam Points'.\n\n"
            f"TEXT:\n{chunk}\n\n"
            "DETAILED EXAM NOTES:"
        )

        result, model_used = generate_with_fallback(prompt)
        if model_used == "None":
            return "❌ Failed to generate chunk summary.", "None"

        chunk_summaries.append(f"## Part {i}\n\n{result}")

    combined_input = "\n\n".join(chunk_summaries)

    final_prompt = (
        "You are an expert academic tutor.\n"
        "Below are detailed notes generated from different parts of one study document.\n"
        "Merge them into one clean, seamless, exam-ready study guide.\n\n"
        "Instructions:\n"
        "- Organize by topic/chapter logically.\n"
        "- Remove repetition.\n"
        "- Keep the explanation detailed and highly structured.\n"
        "- Make it useful for last-minute revision and exam preparation.\n"
        "- Add a final section called 'Most Important Questions / Topics to Revise'.\n\n"
        f"NOTES:\n{combined_input}\n\n"
        "FINAL EXAM-READY STUDY GUIDE:"
    )

    return generate_with_fallback(final_prompt)

# ═══════════════════════════════════════════════════════════════════════════════
# PART X — AI STUDY ASSISTANT (Profile-Scoped Chat Widget)
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Known course aliases — used for cross-course intent detection
# ─────────────────────────────────────────────────────────────────────────────
_ALL_KNOWN_COURSES = [
    # Undergraduate
    "BA", "B.A", "Bachelor of Arts",
    "BE", "B.E", "Bachelor of Engineering",
    "B.Tech", "BTech", "Bachelor of Technology",
    "BCA", "B.C.A", "Bachelor of Computer Applications",
    "BBA", "B.B.A", "Bachelor of Business Administration",
    "B.Com", "BCom", "Bachelor of Commerce",
    "BSc", "B.Sc", "Bachelor of Science",
    "BDS", "MBBS", "LLB", "B.Arch",
    # Postgraduate
    "MA", "M.A", "Master of Arts",
    "MBA", "M.B.A",
    "MTech", "M.Tech",
    "MSc", "M.Sc",
    "MCA", "M.C.A",
    "LLM", "MDS", "MD",
    # K-12
    "Class 10", "Class 11", "Class 12", "Class 9",
    "Grade 10", "Grade 11", "Grade 12",
    "10th", "11th", "12th",
    # Competitive
    "JEE", "NEET", "UPSC", "CAT", "GMAT", "GRE",
    # Professional
    "CA", "CS", "CMA", "ACCA",
]


def _detect_course_violation(profile: dict, user_question: str) -> bool:
    """
    Uses AI intelligence to determine if a question is actually 
    relevant to the student's specific degree and stream.
    """
    course = profile.get("course", "General")
    stream = profile.get("stream", "General")
    
    # Tiny, fast prompt to act as a judge
    judge_prompt = f"""
    You are an Academic Registrar. Decide if the QUESTION is relevant to the COURSE/STREAM.
    
    STUDENT COURSE: {course}
    STUDENT STREAM: {stream}
    QUESTION: "{user_question}"
    
    CRITERIA:
    - If the student is BA/Arts, BLOCK Science/Medical/Engineering questions (e.g. Photosynthesis, Calculus, Circuit Design).
    - If the student is BSc/Science, BLOCK Literature/Fine Arts/Sociology questions.
    - DO NOT find excuses like 'General Studies' or 'EVS' to allow out-of-scope topics.
    - If it is clearly from another faculty, output 'BLOCKED'.
    - If it belongs to their course, output 'ALLOWED'.

    Output ONLY 'BLOCKED' or 'ALLOWED'.
    """
    
    # We use the existing AI engine to judge
    response, _ = generate_with_fallback(judge_prompt)
    
    return "BLOCKED" in response.upper()





def build_scoped_chat_prompt(
    user_message: str,
    profile: dict,
    chat_history: list[dict],
) -> str:
    """
    Builds the full Gemini prompt, injecting the student's profile as
    the system-level scope guard so the model itself also enforces limits.
    """
    category = profile.get("category", "")
    course   = profile.get("course",   "")
    stream   = profile.get("stream",   "")
    board    = profile.get("board",    "")

    # Build conversation history string (last 6 turns max for context window)
    history_text = ""
    for turn in chat_history[-6:]:
        role    = "Student" if turn["role"] == "user" else "StudyBot"
        content = turn["content"]
        history_text += f"{role}: {content}\n"

        system_scope = f"""
            You are StudyBot, a STRICT academic assistant for {course} ({stream}).

            STRICT SCOPE RULES:
            1. You are NOT a general-purpose AI. You ONLY answer questions within the faculty of {course}.
            2. If a student asks a question from a different faculty (e.g., a BA student asking about Science, or a BSc student asking about Literature), you MUST REJECT IT.
            3. DO NOT use 'General Science', 'Foundation Courses', or 'EVS' as an excuse to answer questions outside the {course} domain.
            4. If a question is out of scope, say: "I am your {course} tutor. This topic belongs to another faculty and I cannot assist with it to keep your studies focused."
            5. Never prioritize being 'helpful' over following these boundary rules.

            STUDENT PROFILE:
            - Course: {course}
            - Stream: {stream}
            - Category: {category}

            Current Question: {user_message}
            """


    return system_scope

def _check_course_scope(question_text: str, student_course: str, profile: dict) -> tuple:
    """
    Validates if the question is within the student's selected course scope.
    Returns: (is_valid: bool, message: str)
    """
    q = question_text.lower().strip()
    
    # Blocked off-topic keywords
    blocked = {
        "cricket", "football", "movie", "actor", "actress", "song", "recipe",
        "cooking", "fashion", "shopping", "celebrity", "instagram", "tiktok",
        "sports", "gaming", "weather", "temperature", "joke", "meme",
        "bitcoin", "stock", "crypto", "trading", "disease", "medicine",
        "hospital", "doctor", "surgery", "vaccine"
    }
    
    for word in blocked:
        if word in q:
            return False, (
                f"❌ **Out of Scope**: Questions about '{word}' are not related to {student_course}. "
                f"Please ask about your course."
            )
    
    # Vague/non-academic questions
    vague = ["hello", "hi", "how are you", "what's up", "hi there", "hey"]
    if any(v in q for v in vague):
        return False, f"⚠️ Please ask a specific academic question about {student_course}."
    
    # Check minimum length
    if len(question_text.strip()) < 8:
        return False, "⚠️ Please ask a more detailed question."
    
    return True, ""


def _build_course_aware_prompt(user_message: str, student_course: str) -> str:
    """
    Builds a prompt that enforces the AI to stay within the student's course.
    """
    return (
        f"STUDENT PROFILE: Enrolled in {student_course}\\n"
        f"STRICT RULE: Only answer questions related to {student_course}.\\n"
        f"If the student asks about a different course/subject, politely redirect them.\\n\\n"
        f"Student Question: {user_message}\\n\\n"
        f"Provide a focused, academic answer about {student_course}."
    )



def get_denial_message(violating_course: str, allowed_course: str) -> str:
    """Returns a friendly but firm access-denial message."""
    return (
        f"🔒 **Access Restricted**\n\n"
        f"I noticed you're asking about **{violating_course}**, but your profile is "
        f"enrolled in **{allowed_course}**.\n\n"
        f"I'm your personal tutor for **{allowed_course}** only — I can't provide "
        f"content for other courses to keep your study experience focused and accurate.\n\n"
        f"💡 *If you'd like to switch courses, please reset your profile from the dashboard.*"
    )


def render_ai_chat_assistant(username):
    """
    🤖 StudyBot Assistant - Fully Fixed & Robust Version
    """
    if "ai_chat_open" not in st.session_state:
        st.session_state.ai_chat_open = False
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []
    if "ai_chat_input_key" not in st.session_state:
        st.session_state.ai_chat_input_key = 0

    profile = get_user_profile(username)
    if not profile:
        return

    u_course = profile.get("course", "General")

    st.markdown("""
        <style>
        div[data-testid="stBaseButton-element"] > button#ai_chat_toggle_btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
            color: white !important;
            font-size: 1.5rem !important;
            border: none !important;
            box-shadow: 0 10px 25px rgba(29,78,216,0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("🤖", key="ai_chat_toggle_btn"):
        st.session_state.ai_chat_open = not st.session_state.ai_chat_open
        st.rerun()

    if st.session_state.ai_chat_open:
        with st.container(border=True):
            h_col1, h_col2 = st.columns([0.9, 0.1])

            with h_col1:
                st.markdown(f"### StudyBot ({u_course})")

            with h_col2:
                if st.button("🗑️", key="clr_chat"):
                    st.session_state.ai_chat_history = []
                    st.rerun()

            chat_container = st.container(height=400)
            with chat_container:
                if not st.session_state.ai_chat_history:
                    st.info(f"Hi! Ask me anything about {u_course}.")

                for msg in st.session_state.ai_chat_history:
                    avatar = "👤" if msg["role"] == "user" else "🤖"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.markdown(msg["content"])

            with st.form(key=f"chat_form_{st.session_state.ai_chat_input_key}", clear_on_submit=True):
                i_col1, i_col2 = st.columns([0.85, 0.15])

                with i_col1:
                    user_input = st.text_input(
                        "Msg",
                        placeholder="Type here...",
                        label_visibility="collapsed"
                    )

                with i_col2:
                    submitted = st.form_submit_button("➤")

                if submitted and user_input.strip():
                    user_input = user_input.strip()

                    st.session_state.ai_chat_history.append({
                        "role": "user",
                        "content": user_input
                    })

                    if _detect_course_violation(profile, user_input):
                        denial_msg = get_denial_message("out-of-scope topic", u_course)
                        st.session_state.ai_chat_history.append({
                            "role": "assistant",
                            "content": denial_msg
                        })
                        st.session_state.ai_chat_input_key += 1
                        st.rerun()

                    with st.spinner("Analyzing..."):
                        full_query = build_scoped_chat_prompt(
                            user_message=user_input,
                            profile=profile,
                            chat_history=st.session_state.ai_chat_history
                        )
                        ans_raw, _ = generate_with_fallback(full_query)

                        import re
                        ans_clean = re.sub(r'[\U00010000-\U0010ffff]', '', str(ans_raw)).strip()

                    st.session_state.ai_chat_history.append({
                        "role": "assistant",
                        "content": ans_clean
                    })

                    st.session_state.ai_chat_input_key += 1
                    st.rerun()





# ─────────────────────────────────────────────────────────────────────────────
# ★ PROFILE-LOCKED STUDY TOOLS
# ─────────────────────────────────────────────────────────────────────────────
def show_study_tools(username, target_lang="English"):

    # ── Language Selector in Sidebar ──────────────────────────────────────
    languages = [
        "English", "Hindi", "Tamil", "Telugu", "Kannada",
        "Malayalam", "Bengali", "Marathi", "Gujarati",
        "Spanish", "French", "German"
    ]
    target_lang = st.sidebar.selectbox(
        "🌐 Select Language",
        languages,
        index=languages.index(target_lang) if target_lang in languages else 0,
        key="language_selector"
    )

    render_back_button()

    profile = get_user_profile(username)
    if not profile:
        st.warning("⚠️ Profile not found. Please complete onboarding first.")
        if st.button("🔄 Go to Onboarding", use_container_width=False):
            reset_profile(username)
            st.rerun()
        return

    p_cat    = profile["category"]
    p_course = profile["course"]
    p_stream = profile["stream"]
    p_board  = profile["board"]
    meta     = CATEGORY_META.get(p_cat, {"icon": "📘", "color": "#3b82f6"})

    render_header(
        "Study Tools",
        f"{meta['icon']} {p_course} · {p_stream} · {p_board}"
    )

    if not STUDY_DATA:
        st.error("❌ No study data loaded. Check data/study_data.json")
        return

    tool = st.radio(
        "🛠️ Select Tool",
        [
            "⚡ Short & Quick", "📝 Summary", "📋 Notes Format",
            "📄 Detailed", "📌 Revision Notes", "❓ Exam Q&A",
            "🧠 Quiz", "🧪 Question Paper", "📤 Upload & Summarize"
        ],
        horizontal=True,
        key="study_tool_radio"
    )

    is_qp = tool == "🧪 Question Paper"
    is_upload = tool == "📤 Upload & Summarize"
    is_exam_qa = tool == "❓ Exam Q&A"

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)


    

    # =========================================================================
    # PART 1: UPLOAD & SUMMARIZE TOOL
    # =========================================================================
    if tool == "📤 Upload & Summarize":
        st.markdown("""
        <style>
        [data-testid="stFileUploadDropzone"]:hover {
            background: linear-gradient(135deg, #bfdbfe 0%, #60a5fa 100%) !important;
            border-color: #1d4ed8 !important;
            transform: translateY(-1px) !important;
        }
        [data-testid="stFileUploadDropzone"] button:hover {
            background: #1d4ed8 !important;
            color: #ffffff !important;
        }
        [data-testid="stFileUploadDropzone"] p,
        [data-testid="stFileUploadDropzone"] span,
        [data-testid="stFileUploadDropzone"] small {
            color: #0f172a !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="color: #1d4ed8; font-weight: 800; margin-bottom: 5px;">
                    📤 Complete Document Analyzer
                </h3>
                <div style="color: #64748b; font-size: 0.9rem;">
                    Upload any PDF or DOCX — AI reads the FULL document and builds a thorough exam study guide
                </div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            uploaded_file = st.file_uploader(
                "Choose your document",
                type=["pdf", "docx"],
                key="doc_uploader",
                label_visibility="collapsed"
            )

        if uploaded_file is not None:
            file_size_kb = round(uploaded_file.size / 1024, 1)
            file_size_mb = round(uploaded_file.size / (1024 * 1024), 2)
            size_display = f"{file_size_mb} MB" if file_size_mb >= 1 else f"{file_size_kb} KB"

            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f0fdf4, #dcfce7); border: 1.5px solid #86efac; border-radius: 12px; padding: 14px; margin-bottom: 16px; text-align: center;">
                    <span style="color: #15803d; font-weight: 700; font-size: 1rem;">✅ {uploaded_file.name}</span>
                    <span style="color: #64748b; font-size: 0.85rem; margin-left: 10px;">({size_display})</span>
                </div>
            """, unsafe_allow_html=True)

            # 🌟 NEW FEATURE: Side-by-Side Action and Language Selectors
            col_action, col_lang = st.columns([2, 1])
            
            with col_action:
                doc_action = st.selectbox(
                    "🎯 What to generate?",
                    [
                        "📚 Complete Study Guide",
                        "⚡ Short & Quick Notes", 
                        "🧠 Quiz with Answers", 
                        "❓ Exam Q&A Bank", 
                        "🧪 Mock Question Paper"
                    ],
                    key="doc_action_sel"
                )
                
            with col_lang:
                languages = [
                    "English", "Hindi", "Tamil", "Telugu", "Kannada", 
                    "Malayalam", "Bengali", "Marathi", "Gujarati", 
                    "Spanish", "French", "German"
                ]
                target_lang = st.selectbox(
                    "🌐 Output Language",
                    languages,
                    index=0,
                    key="doc_lang_sel"
                )


            # Dynamic button text based on selection
            button_text = f"✨ Generate {doc_action.split(' ', 1)[1]}"

            if st.button(button_text, use_container_width=True, key="process_uploaded_doc"):
                
                with st.spinner("📄 Extracting full text from document..."):
                    doc_text = extract_text_from_file(uploaded_file)

                if not doc_text or not doc_text.strip():
                    st.error("❌ Could not extract text. The file may be image-based (scanned PDF) or empty.")
                else:
                    char_count  = len(doc_text)
                    word_count  = len(doc_text.split())
                    page_est    = max(1, round(char_count / 2000))

                    st.info(f"📊 Document Stats: **{word_count:,} words** | ~**{page_est} pages**")

                    with st.spinner(f"🤖 AI is analyzing {page_est} pages to build your {doc_action.split(' ', 1)[1]}..."):
                        
                        # CALL THE NEW FUNCTION AND PASS THE ACTION
                        result, model_used = generate_document_output(doc_text, uploaded_file.name, doc_action, language=target_lang)


                    st.session_state.update({
                        "generated_result":       result,
                        "generated_model":        model_used,
                        "generated_label":        doc_action,  # Saves the chosen action as the title!
                        "generated_tool":         tool,
                        "generated_chapter":      uploaded_file.name,
                        "generated_subject":      "Uploaded Document",
                        "generated_topic":        doc_action,
                        "generated_course":       p_course,
                        "generated_stream":       p_stream,
                        "generated_board":        p_board,
                        "generated_audience":     "Student",
                        "generated_output_style": None,
                    })

                    if model_used != "None":
                        add_to_history(doc_action, uploaded_file.name, "Uploads", result)
                        award_xp(username, 50)
                        auto_check_badges(username)
                        st.rerun() # Refresh to show results immediately
                    else:
                        st.error("❌ Generation failed. Please try again.")



    # =========================================================================
    # PART 2: ALL OTHER NORMAL TOOLS (Subject/Topic/Chapter Selectors)
    # =========================================================================
    else:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)

        # Your beautiful profile-locked UI cards
        i1, i2, i3 = st.columns(3)

        with i1:
            st.markdown(f"""
            <div class="sf-soft-card" style="text-align:center;">
                <div style="font-size:.9rem;color:#64748b;font-weight:800; text-transform:uppercase;letter-spacing:.06em;">
                    📚 Category
                </div>
                <div style="font-weight:500;font-size:.7rem; color:#1d4ed8;margin-top:4px;">
                    {meta['icon']} {p_cat}
                </div>
                <div style="font-size:.65rem;color:#94a3b8;margin-top:3px;">
                    🔒 Locked to profile
                </div>
            </div>
            """, unsafe_allow_html=True)

        with i2:
            st.markdown(f"""
            <div class="sf-soft-card" style="text-align:center;">
                <div style="font-size:.9rem;color:#64748b;font-weight:800; text-transform:uppercase;letter-spacing:.06em;">
                    🎓 Course
                </div>
                <div style="font-weight:500;font-size:.7rem; color:#1d4ed8;margin-top:4px;">
                    {p_course}
                </div>
                <div style="font-size:.65rem;color:#94a3b8;margin-top:3px;">
                    🔒 Locked to profile
                </div>
            </div>
            """, unsafe_allow_html=True)

        with i3:
            st.markdown(f"""
            <div class="sf-soft-card" style="text-align:center;">
                <div style="font-size:.9rem;color:#64748b;font-weight:800; text-transform:uppercase;letter-spacing:.06em;">
                    🔀 Stream · 🏫 Board
                </div>
                <div style="font-weight:500;font-size:.7rem; color:#1d4ed8;margin-top:4px;">
                    {p_stream}
                </div>
                <div style="font-size:.65rem;color:#94a3b8;margin-top:3px;">
                    {p_board}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Subject + Topic + Chapter + Language ─────────────────────────────
        subjects = get_subjects(p_cat, p_course, p_stream)
        if not subjects:
            st.warning(f"⚠️ No subjects found for {p_cat} → {p_course} → {p_stream}. Please check your study_data.json")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        col_s, col_t, col_c, col_l = st.columns([1.7, 1.7, 1.7, 1.2])

        with col_s:
            subject = st.selectbox(
                "🧾 Subject",
                subjects,
                key="sel_subject"
            )

        with col_t:
            topics = get_topics(p_cat, p_course, p_stream, subject)
            topic = st.selectbox(
                "🗂️ Topic",
                topics,
                key="sel_topic"
            )

        # ── Dynamic Chapter List (with initialization fix) ────────────────────
        chapter_key = f"{p_cat}||{p_course}||{p_stream}||{subject}||{topic}"
        if "last_chapter_key" not in st.session_state or st.session_state.last_chapter_key != chapter_key:
            st.session_state.current_chapters = get_chapters(p_cat, p_course, p_stream, subject, topic)
            st.session_state.last_chapter_key = chapter_key

            try:
                reset_generation_state()
            except NameError:
                pass

        with col_c:
            chapter = st.selectbox(
                "📝 Chapter",
                st.session_state.current_chapters,
                key="sel_chapter"
            )

        with col_l:
            languages = [
                "English", "Hindi", "Tamil", "Telugu", "Kannada",
                "Malayalam", "Bengali", "Marathi", "Gujarati"
            ]
            target_lang = st.selectbox(
                "🌐 Language",
                languages,
                index=0,
                key="target_language"
            )

        st.session_state.current_subject_for_timer = subject

        # Keep style explicitly defined
        style = None

        # Audience for prompt
        audience = (
            f"{p_board} {p_course} students"
            if p_cat == "K-12th"
            else f"{p_course} students"
        )

        # ── Generate Button for normal tools ──────────────────────────────────
        eff_label = get_effective_output_name(tool, style)
        btn_label = get_button_label(tool, style)

        if st.button(btn_label, use_container_width=True, key="gen_btn"):
            if not chapter or chapter == "No chapters found":
                st.warning("⚠️ Please select a valid chapter.")
            else:
                prompt = build_prompt(
                    tool,
                    chapter,
                    topic,
                    subject,
                    audience,
                    style,
                    board=p_board,
                    course=p_course,
                    language=target_lang
                )

                with st.spinner(f"⚡ Generating {eff_label}..."):
                    result, model_used = generate_with_fallback(prompt)

                st.session_state.update({
                    "generated_result": result,
                    "generated_model": model_used,
                    "generated_label": eff_label,
                    "generated_tool": tool,
                    "generated_chapter": chapter,
                    "generated_subject": subject,
                    "generated_topic": topic,
                    "generated_course": p_course,
                    "generated_stream": p_stream,
                    "generated_board": p_board,
                    "generated_audience": audience,
                    "generated_output_style": style,
                    "answers_result": None,
                    "answers_model": None,
                    "show_answers": False,
                    "fullpaper_result": None,
                    "fullpaper_model": None,
                    "show_fullpaper": False,
                })

                if model_used != "None":
                    add_to_history(eff_label, chapter, subject, result)
                    award_xp(username, 25)
                    award_badge(username, "first_gen")
                    auto_check_badges(username)

        st.markdown('</div>', unsafe_allow_html=True)



    # ── Display Result ────────────────────────────────────────────────────
    if st.session_state.get("generated_result"):
        result     = st.session_state.generated_result
        g_label    = st.session_state.get("generated_label",    "Study Material")
        g_chapter  = st.session_state.get("generated_chapter",  "Note")
        g_subject  = st.session_state.get("generated_subject",  "General")
        g_topic    = st.session_state.get("generated_topic",    "")
        g_course   = st.session_state.get("generated_course",   "")
        g_stream   = st.session_state.get("generated_stream",   "")
        g_board    = st.session_state.get("generated_board",    "")
        g_audience = st.session_state.get("generated_audience", "Student")

        if st.session_state.get("generated_model") == "None":
            st.error("❌ Generation failed. Check your API key and quota.")
            st.markdown(result)
            return

        is_qp   = (g_label == "Question Paper")
        box_cls = "sf-fullpaper" if is_qp else "sf-output"

        # ── Unique key suffix based on tool name ──────────────────────────
        # This prevents duplicate key errors across tools
        key_suffix = g_label.replace(" ", "_").replace("&", "and").lower()

        st.markdown(f'<div class="{box_cls}">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Non-QP Actions ────────────────────────────────────────────────
        if not is_qp:
            col_fc, col_pdf = st.columns(2)

            with col_fc:
                if st.button(
                    "🗂️ Save as Flashcards",
                    use_container_width=True,
                    key=f"save_fc_btn_{key_suffix}"      # ✅ unique key
                ):
                    with st.spinner("Creating flashcards..."):
                        raw, mdl = generate_with_fallback(
                            build_flashcard_prompt(
                                g_subject, g_chapter, g_topic or ""
                            )
                        )
                    if mdl != "None":
                        cards = parse_flashcards(raw)
                        for card in cards:
                            save_flashcard(
                                username, card["front"], card["back"],
                                g_subject, g_chapter
                            )
                        award_xp(username, len(cards) * 5)
                        auto_check_badges(username)
                        st.success(
                            f"✅ {len(cards)} flashcards saved! "
                            f"+{len(cards) * 5} XP"
                        )
                    else:
                        st.error("❌ Flashcard generation failed.")

            with col_pdf:
                try:
                    pdf = generate_pdf(
                        f"{g_label} — {g_chapter}",
                        f"{g_subject} | {g_topic} | {g_course}",
                        result
                    )
                    safe = (
                        g_chapter.replace(" ", "_")
                                 .replace(":", "")
                                 .replace("/", "-") + ".pdf"
                    )
                    st.download_button(
                        "⬇️ Download PDF",
                        data=pdf, file_name=safe,
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"dl_main_pdf_{key_suffix}"  # ✅ unique key
                    )
                except Exception as e:
                    st.warning(f"⚠️ PDF error: {e}")

        # ── Question Paper Actions ────────────────────────────────────────
        else:
            try:
                qp_pdf = generate_pdf(
                    f"Question Paper — {g_subject}",
                    f"{g_board} | {g_course} | {g_stream}",
                    result
                )
                safe_qp = (
                    g_subject.replace(" ", "_")
                             .replace(":", "")
                             .replace("/", "-") + "_QuestionPaper.pdf"
                )
                st.download_button(
                    "⬇️ Download Question Paper PDF",
                    data=qp_pdf, file_name=safe_qp,
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_qp_pdf_{key_suffix}"        # ✅ unique key
                )
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

            if st.button(
                "📋 Get Questions with Answers",
                use_container_width=True,
                key=f"ans_btn_{key_suffix}"              # ✅ unique key
            ):
                with st.spinner("Generating questions with answers..."):
                    ans_r, ans_m = generate_with_fallback(
                        f"You are an expert educator and examiner.\n"
                        f"Subject: {g_subject} | Board: {g_board}\n\n"
                        f"Below is a question paper. Rewrite the ENTIRE paper and insert a "
                        f"detailed model answer after EVERY question.\n\n"
                        f"🛑 STRICT FORMATTING RULES — FOLLOW EXACTLY:\n"
                        f"1. Keep ALL original section headings.\n"
                        f"2. Copy each question EXACTLY as written.\n"
                        f"3. After EVERY question, add TWO blank lines.\n"
                        f"4. Then write '**✅ Answer:**' on its OWN separate line.\n"
                        f"5. Then write the answer on the NEXT line.\n"
                        f"6. Add a horizontal rule '---' after each answer.\n\n"
                        f"QUESTION PAPER:\n{result}"
                    )
                st.session_state.answers_result = ans_r
                st.session_state.answers_model  = ans_m
                st.session_state.show_answers   = True

            if st.session_state.show_answers and st.session_state.answers_result:
                if st.session_state.answers_model != "None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 📋 Question Paper with Answers — {g_subject}")
                    st.markdown(st.session_state.answers_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        ans_pdf = generate_pdf(
                            f"Questions & Answers — {g_subject}",
                            f"{g_board} | {g_course}",
                            st.session_state.answers_result
                        )
                        safe_a = (
                            g_chapter.replace(" ", "_")
                                     .replace(":", "")
                                     .replace("/", "-") + "_QA.pdf"
                        )
                        st.download_button(
                            "⬇️ Download Q&A PDF",
                            data=ans_pdf, file_name=safe_a,
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"dl_ans_pdf_{key_suffix}"   # ✅ unique key
                        )
                    except Exception as e:
                        st.warning(f"⚠️ PDF error: {e}")

            if st.button(
                f"🗂️ Generate Full {g_subject} Paper",
                use_container_width=True,
                key=f"full_qp_btn_{key_suffix}"              # ✅ unique key
            ):
                with st.spinner("Generating full subject paper..."):
                    full_r, full_m = generate_with_fallback(
                        build_full_qp_prompt(
                            g_board, g_course, g_stream, g_subject, g_audience
                        )
                    )
                st.session_state.fullpaper_result         = full_r
                st.session_state.fullpaper_model          = full_m
                st.session_state.show_fullpaper           = True
                st.session_state.fullpaper_answers_result = None
                st.session_state.fullpaper_answers_model  = None
                st.session_state.show_fullpaper_answers   = False


            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Paper — {g_subject}")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf = generate_pdf(
                            f"Full Paper — {g_subject}",
                            f"{g_board} | {g_course} | {g_stream}",
                            st.session_state.fullpaper_result,
                        )
                        safe_f = f"{g_subject}_{g_board}_FullPaper.pdf".replace(" ", "_")
                        st.download_button(
                            "⬇️ Download Full Paper PDF",
                            data=full_pdf, file_name=safe_f,
                            mime="application/pdf",
                            use_container_width=True, key="dl_full_pdf"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ PDF error: {e}")

                    # ★ FIX 4: Get Answers for Full Paper
                    if st.button("📋 Get Answers for this Full Paper",
                                 use_container_width=True,
                                 key="get_fullpaper_ans_btn"):
                        with st.spinner("Generating answer key for full paper..."):
                            fp_ans_r, fp_ans_m = generate_with_fallback(
                                build_answers_prompt(
                                    st.session_state.fullpaper_result,
                                    g_board, g_course, g_subject,
                                    f"Full {g_subject} Paper"
                                )
                            )
                        st.session_state.fullpaper_answers_result = fp_ans_r
                        st.session_state.fullpaper_answers_model  = fp_ans_m
                        st.session_state.show_fullpaper_answers   = True

                    if (st.session_state.show_fullpaper_answers
                            and st.session_state.fullpaper_answers_result):
                        if st.session_state.fullpaper_answers_model != "None":
                            st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                            st.markdown(f"### 📚 Answer Key — Full {g_subject} Paper")
                            st.markdown(st.session_state.fullpaper_answers_result)
                            st.markdown('</div>', unsafe_allow_html=True)
                            try:
                                fp_ans_pdf = generate_pdf(
                                    f"Answer Key — Full {g_subject} Paper",
                                    f"{g_board} | {g_course} | {g_stream}",
                                    st.session_state.fullpaper_answers_result,
                                )
                                safe_fa = f"{g_subject}_{g_board}_FullPaper_Answers.pdf".replace(" ", "_")
                                st.download_button(
                                    "⬇️ Download Full Paper Answer Key PDF",
                                    data=fp_ans_pdf, file_name=safe_fa,
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key="dl_full_ans_pdf"
                                )
                            except Exception as e:
                                st.warning(f"⚠️ PDF error: {e}")
                        else:
                            st.error("❌ Answer generation failed.")


    # ── ✅ AI CHAT ASSISTANT — Profile-Locked Floating Widget ─────────────
    # Must be the LAST call inside show_study_tools() so it renders on top
    st.markdown("---")
    render_ai_chat_assistant(username)



# ─────────────────────────────────────────────────────────────────────────────
# AUTH UI
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        st.markdown("""
            <div class="sf-header">
                <div class="sf-header-title">StudySmart</div>
                <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
            </div>
            <div class="sf-watermark">POWERED BY AI</div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        # ── LOGIN TAB ─────────────────────────────────────────────────────
        with tab1:
            # st.form allows pressing Enter to submit ✅
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
                    placeholder="Enter your password — press Enter or click Sign In"
                )
                login_submit = st.form_submit_button(
                    "Sign In 🚀",
                    use_container_width=True
                )

            if login_submit:
                if not u.strip() or not p.strip():
                    st.warning("⚠️ Please fill in both fields.")
                else:
                    conn = sqlite3.connect("users.db")
                    c    = conn.cursor()
                    c.execute(
                        "SELECT * FROM users WHERE username=? AND password=?",
                        (u.strip(), hash_p(p))
                    )
                    user_row = c.fetchone()
                    conn.close()

                    if user_row:
                        # Ensure stats row exists
                        conn = sqlite3.connect("users.db")
                        c    = conn.cursor()
                        c.execute(
                            "INSERT OR IGNORE INTO user_stats (username) VALUES (?)",
                            (u.strip(),)
                        )
                        conn.commit()
                        conn.close()
                        st.session_state.logged_in = True
                        st.session_state.username  = u.strip()
                        st.success("✅ Login successful! Loading your dashboard...")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")

        # ── REGISTER TAB ──────────────────────────────────────────────────
        with tab2:
            with st.form("register_form", clear_on_submit=True):
                nu = st.text_input(
                    "👤 New Username",
                    key="reg_u",
                    placeholder="Min 3 characters"
                )
                np_ = st.text_input(
                    "🔑 New Password",
                    type="password",
                    key="reg_p",
                    placeholder="Min 6 characters"
                )
                reg_submit = st.form_submit_button(
                    "Create Account ✨",
                    use_container_width=True
                )

            if reg_submit:
                if not nu.strip():
                    st.error("❌ Username cannot be empty.")
                elif len(nu.strip()) < 3:
                    st.error("❌ Username must be at least 3 characters.")
                elif not np_.strip():
                    st.error("❌ Password cannot be empty.")
                elif len(np_.strip()) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    try:
                        conn = sqlite3.connect("users.db")
                        c    = conn.cursor()
                        c.execute(
                            "INSERT INTO users (username, password) VALUES (?, ?)",
                            (nu.strip(), hash_p(np_))
                        )
                        conn.commit()
                        conn.close()
                        st.success(
                            f"✅ Account created for **{nu.strip()}**! "
                            "Please go to the Login tab."
                        )
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists. Please choose another.")
                    except Exception as e:
                        st.error(f"❌ Registration failed: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

   


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main_app():
    username = st.session_state.username

    # ── ONBOARDING GATE — show wizard if profile not set ─────────────────
    if not is_onboarded(username):
        show_onboarding(username)
        return                        # ← stop here; no sidebar, no dashboard

    # ── Normal app flow ───────────────────────────────────────────────────
    # Call the sidebar and store the selected language
    target_lang = render_sidebar(username)
    
    page = st.session_state.active_page

    if   page == "dashboard":    show_dashboard(username, target_lang)
    elif page == "study":        show_study_tools(username, target_lang)
    elif page == "flashcards":   show_flashcards(username)
    elif page == "achievements": show_achievements(username)
    else:                        show_dashboard(username, target_lang)





# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
init_db()
init_session_state()

# ─────────────────────────────────────────────────────────────────────────────
# MAINTENANCE MODE
# ─────────────────────────────────────────────────────────────────────────────
MAINTENANCE_MODE = False
ALLOWED_USERS_MAINTENANCE = ["Deepak"]   # <- replace with your real username

def show_maintenance_screen():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:5rem;margin-bottom:20px;">🛠️</div>
            <div style="font-size:2.2rem;font-weight:900;
                background:linear-gradient(135deg,#ef4444,#f97316);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
                background-clip:text;">
                Under Maintenance
            </div>
            <div style="font-size:1.05rem;color:#64748b;margin-top:12px;line-height:1.7;">
                StudySmart AI is currently under maintenance.<br><br>
                We are improving the platform and will be back shortly.
            </div>
        </div>
        """, unsafe_allow_html=True)

# If maintenance mode is ON:
if MAINTENANCE_MODE:
    logged_in_user = st.session_state.get("username", "")
    is_logged_in = st.session_state.get("logged_in", False)

    # If already logged in and whitelisted -> allow access
    if is_logged_in and logged_in_user in ALLOWED_USERS_MAINTENANCE:
        main_app()

    # If already logged in but NOT whitelisted -> block
    elif is_logged_in and logged_in_user not in ALLOWED_USERS_MAINTENANCE:
        show_maintenance_screen()

    # If not logged in -> show login screen, but disable public registration
    else:
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown("""
                <div class="sf-header">
                    <div class="sf-header-title">StudySmart</div>
                    <div class="sf-header-subtitle">
                        Maintenance Access
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.info("🛠️ App is in maintenance mode. Only authorised users can log in.")

            u = st.text_input("👤 Username", key="maint_login_u")
            p = st.text_input("🔑 Password", type="password", key="maint_login_p")

            if st.button("Sign In", use_container_width=True, key="maint_login_btn"):
                if not u.strip() or not p.strip():
                    st.warning("⚠️ Please fill in both fields.")
                elif u.strip() not in ALLOWED_USERS_MAINTENANCE:
                    st.error("❌ You are not authorised during maintenance mode.")
                else:
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute(
                        "SELECT * FROM users WHERE username=? AND password=?",
                        (u.strip(), hash_p(p))
                    )
                    user = c.fetchone()
                    conn.close()

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = u.strip()
                        st.success("✅ Login successful!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

            st.markdown('</div>', unsafe_allow_html=True)

# If maintenance mode is OFF:
else:
    if st.session_state.get("logged_in", False):
        main_app()
    else:
        auth_ui()

