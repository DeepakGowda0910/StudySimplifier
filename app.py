# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STUDYSMART AI â€” app.py  (Complete Â· All Features Â· All Fixes Â· Login Page Visible)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

import streamlit as st
import google.generativeai as genai
import sqlite3, hashlib, io, json, time, datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PAGE CONFIG  (MUST be first Streamlit call)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.set_page_config(
    page_title="StudySmart AI",
    page_icon="ðŸŽ“",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# FULL CSS  (original from your uploaded file)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Inter', 'Poppins', sans-serif !important;
        letter-spacing: 0.3px;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e8f0f7 100%);
        min-height: 100vh;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 1300px;
    }

    #MainMenu  { visibility: hidden; }
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

    .sf-header {
        text-align: center;
        padding: 50px 0 15px 0;
        position: relative;
    }
    .sf-header-title {
        font-size: 4.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.1;
        letter-spacing: -1.5px;
    }
    .sf-header-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-top: 12px;
        font-weight: 500;
        letter-spacing: 0.4px;
    }
    .sf-watermark {
        font-size: 4.4rem;
        font-weight: 900;
        color: rgba(59, 130, 246, 0.08);
        text-transform: uppercase;
        letter-spacing: 12px;
        margin-top: 12px;
        margin-bottom: -42px;
        position: relative;
        top: -8px;
        z-index: 10;
        pointer-events: none;
        user-select: none;
        text-align: center;
        width: 100%;
        line-height: 1;
    }

    /* â”€â”€ App hero (inside pages) â”€â”€ */
    .sf-hero { text-align:center; padding:14px 0 8px 0; }
    .sf-hero-title {
        font-size:2rem; font-weight:800;
        background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text; line-height:1.1; margin:0;
    }
    .sf-hero-sub  { color:#475569 !important; font-size:.94rem; font-weight:500; margin-top:4px; }
    .sf-powered   {
        display:inline-block; margin-top:7px; padding:3px 14px;
        border-radius:999px; background:rgba(37,99,235,0.09);
        color:#2563eb !important; font-size:.69rem;
        font-weight:800; letter-spacing:.12em; text-transform:uppercase;
    }

    /* â”€â”€ Cards â”€â”€ */
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

    /* â”€â”€ Metric cards â”€â”€ */
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

    /* â”€â”€ XP bar â”€â”€ */
    .xp-wrap { background:#e2e8f0; border-radius:999px; height:10px; overflow:hidden; }
    .xp-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,#3b82f6,#8b5cf6); }

    /* â”€â”€ History â”€â”€ */
    .sf-hist {
        background:#f8fbff !important; border:1px solid #e2e8f0 !important;
        border-left:4px solid #3b82f6 !important; border-radius:12px !important;
        padding:9px 12px !important; margin-bottom:8px !important;
        font-size:.84rem !important; color:#0f172a !important;
    }
    .sf-hist * { color:#0f172a !important; }
    .sf-hist b { color:#1d4ed8 !important; }
    .sf-hist small { color:#475569 !important; }

    /* â”€â”€ Output boxes â”€â”€ */
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

    /* â”€â”€ Flashcards â”€â”€ */
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

    /* â”€â”€ Badges â”€â”€ */
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

    /* â”€â”€ Selectbox â”€â”€ */
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
        border-radius:12px !important; box-shadow:0 8px 30px rgba(15,23,42,.12) !important;
        z-index:9999 !important;
    }
    div[role="option"] {
        background:#ffffff !important; color:#0f172a !important;
        padding:10px 14px !important;
    }
    div[role="option"]:hover { background:#eff6ff !important; color:#1d4ed8 !important; }

    /* â”€â”€ Inputs â”€â”€ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border:1.5px solid #c7d4e8 !important;
        border-radius:11px !important;
        background:#ffffff !important;
        color:#0f172a !important;
    }

    /* â”€â”€ Buttons â”€â”€ */
    .stButton > button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 3.2rem !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
        letter-spacing: 0.4px !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
    }
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: #ffffff !important;
    }

    /* â”€â”€ Radio â”€â”€ */
    .stRadio > div { gap: 10px !important; }
    .stRadio > div > label {
        background:#f1f5f9 !important; border:1px solid #e2e8f0 !important;
        border-radius:9px !important; padding:8px 14px !important;
        color:#0f172a !important; font-weight:500 !important;
    }
    .stRadio > div > label[data-checked="true"] {
        background:#eff6ff !important; border-color:#3b82f6 !important;
        color:#1d4ed8 !important; font-weight:700 !important;
    }

    /* â”€â”€ Alerts â”€â”€ */
    div[data-testid="stSuccessMessage"] {
        background: rgba(16, 185, 129, 0.08) !important;
        border: 1.5px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stErrorMessage"] {
        background: rgba(239, 68, 68, 0.08) !important;
        border: 1.5px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stInfoMessage"] {
        background: rgba(59, 130, 246, 0.08) !important;
        border: 1.5px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 10px !important;
    }

    hr { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }

    /* â”€â”€ Mobile â”€â”€ */
    @media (max-width: 768px) {
        .sf-header-title { font-size: 2.8rem !important; }
        .sf-header-subtitle { font-size: 1rem !important; }
        .sf-watermark { font-size: 2.4rem !important; letter-spacing: 6px !important; }
        html, body, .stApp {
            overflow-x: hidden !important;
            overscroll-behavior: none !important;
        }
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] [role="combobox"],
        div[data-baseweb="select"] > div {
            font-size: 16px !important;
            -webkit-text-size-adjust: 100% !important;
        }
        input, textarea, select, [contenteditable="true"], [role="combobox"] {
            font-size: 16px !important;
            -webkit-text-size-adjust: 100% !important;
            touch-action: manipulation !important;
        }
        div[role="listbox"] {
            max-height: 38vh !important;
            overflow-y: auto !important;
            -webkit-overflow-scrolling: touch !important;
            position: fixed !important;
            z-index: 9999 !important;
        }
        div[role="option"] {
            min-height: 48px !important;
            padding: 12px 16px !important;
            font-size: 15px !important;
            display: flex !important;
            align-items: center !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# DATA LOADER
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@st.cache_data
def load_study_data():
    try:
        with open(Path("data/study_data.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("âŒ data/study_data.json not found!")
        return {}
    except json.JSONDecodeError:
        st.error("âŒ study_data.json is not valid JSON!")
        return {}

STUDY_DATA = load_study_data()
BOARDS     = ["CBSE", "ICSE", "State Board", "ISC", "IB", "Cambridge"]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# DATABASE (FIXED â€” cursor stays alive for all migrations)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def init_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT NOT NULL)""")

    c.execute("""CREATE TABLE IF NOT EXISTS user_stats (
        username TEXT PRIMARY KEY,
        total_xp INTEGER DEFAULT 0,
        streak_days INTEGER DEFAULT 0,
        last_login TEXT DEFAULT '',
        total_minutes INTEGER DEFAULT 0)""")

    c.execute("""CREATE TABLE IF NOT EXISTS achievements (
        username TEXT, badge_id TEXT, earned_at TEXT,
        PRIMARY KEY (username, badge_id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, front_text TEXT, back_text TEXT,
        subject TEXT DEFAULT '', chapter TEXT DEFAULT '',
        ease_factor REAL DEFAULT 2.5, interval_days INTEGER DEFAULT 1,
        next_review_date TEXT, review_count INTEGER DEFAULT 0, created_date TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, subject TEXT, minutes INTEGER DEFAULT 0, sess_date TEXT)""")

    # safe migration helper â€” cursor stays valid
    def cols(t):
        c.execute(f"PRAGMA table_info({t})")
        return [r[1] for r in c.fetchall()]
    def add(t, col, defn):
        if col not in cols(t):
            c.execute(f"ALTER TABLE {t} ADD COLUMN {col} {defn}")

    add("user_stats","total_xp","INTEGER DEFAULT 0")
    add("user_stats","streak_days","INTEGER DEFAULT 0")
    add("user_stats","last_login","TEXT DEFAULT ''")
    add("user_stats","total_minutes","INTEGER DEFAULT 0")
    add("achievements","earned_at","TEXT")
    add("flashcards","subject","TEXT DEFAULT ''")
    add("flashcards","chapter","TEXT DEFAULT ''")
    add("flashcards","ease_factor","REAL DEFAULT 2.5")
    add("flashcards","interval_days","INTEGER DEFAULT 1")
    add("flashcards","next_review_date","TEXT")
    add("flashcards","review_count","INTEGER DEFAULT 0")
    add("flashcards","created_date","TEXT")

    conn.commit()
    conn.close()

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# HELPERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def hash_p(pw): return hashlib.sha256(pw.encode()).hexdigest()

def get_courses(cat):
    try: return list(STUDY_DATA[cat].keys())
    except: return []
def get_streams(cat,c):
    try: return list(STUDY_DATA[cat][c].keys())
    except: return []
def get_subjects(cat,c,s):
    try: return list(STUDY_DATA[cat][c][s].keys())
    except: return []
def get_topics(cat,c,s,sub):
    try: return list(STUDY_DATA[cat][c][s][sub].keys())
    except: return []
def get_chapters(cat,c,s,sub,top):
    try: return STUDY_DATA[cat][c][s][sub][top]
    except: return ["No chapters found"]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# XP / STREAK / STATS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def award_xp(username, xp):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)",(username,))
    c.execute("UPDATE user_stats SET total_xp=COALESCE(total_xp,0)+? WHERE username=?",(xp,username))
    conn.commit(); conn.close()

def check_daily_login(username):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)",(username,))
    c.execute("SELECT last_login,streak_days FROM user_stats WHERE username=?",(username,))
    row = c.fetchone()
    if row:
        last, streak = row
        if last == today:
            conn.close()
            return {"message":f"âœ… Already checked in today Â· ðŸ”¥ {streak} day streak!","xp":0}
        yesterday = (datetime.date.today()-datetime.timedelta(days=1)).isoformat()
        streak = (streak+1) if last==yesterday else 1
        xp = 20
        c.execute("UPDATE user_stats SET last_login=?,streak_days=?,total_xp=COALESCE(total_xp,0)+? WHERE username=?",
                  (today,streak,xp,username))
        conn.commit(); conn.close()
        return {"message":f"ðŸ”¥ {streak} day streak! +{xp} XP","xp":xp,"streak":streak}
    conn.close()
    return {"message":"Checked in!","xp":0}

def update_streak(username):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)",(username,))
    c.execute("SELECT last_login,streak_days FROM user_stats WHERE username=?",(username,))
    row = c.fetchone()
    if row:
        last, streak = row
        if last == today: conn.close(); return
        yesterday = (datetime.date.today()-datetime.timedelta(days=1)).isoformat()
        streak = (streak+1) if last==yesterday else 1
        c.execute("UPDATE user_stats SET last_login=?,streak_days=? WHERE username=?",(today,streak,username))
    conn.commit(); conn.close()

def get_user_stats(username):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)",(username,))
    c.execute("SELECT COALESCE(total_xp,0),COALESCE(streak_days,0),COALESCE(total_minutes,0) FROM user_stats WHERE username=?",(username,))
    row = c.fetchone()
    total_xp,streak_days,total_minutes = row if row else (0,0,0)

    if total_minutes==0:
        try:
            c.execute("SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE username=?",(username,))
            total_minutes = c.fetchone()[0] or 0
            c.execute("UPDATE user_stats SET total_minutes=? WHERE username=?",(total_minutes,username))
            conn.commit()
        except: pass

    weekly_minutes=0
    try:
        week_ago=(datetime.date.today()-datetime.timedelta(days=7)).isoformat()
        c.execute("SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE username=? AND sess_date>=?",(username,week_ago))
        weekly_minutes=c.fetchone()[0] or 0
    except: pass

    flashcards_due=0
    try:
        today=datetime.date.today().isoformat()
        c.execute("SELECT COUNT(*) FROM flashcards WHERE username=? AND next_review_date<=?",(username,today))
        flashcards_due=c.fetchone()[0] or 0
    except: pass

    conn.commit(); conn.close()
    return {
        "total_xp":total_xp,"streak_days":streak_days,
        "total_minutes":total_minutes,"total_study_minutes":total_minutes,
        "weekly_study_minutes":weekly_minutes,"flashcards_due":flashcards_due,
        "level":(total_xp//500)+1,"level_progress":total_xp%500,
    }

def record_study_session(username, subject, minutes):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("INSERT INTO study_sessions (username,subject,minutes,sess_date) VALUES (?,?,?,?)",
              (username,subject,int(minutes),today))
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)",(username,))
    c.execute("UPDATE user_stats SET total_minutes=COALESCE(total_minutes,0)+? WHERE username=?",(int(minutes),username))
    conn.commit(); conn.close()
    try: auto_check_badges(username)
    except: pass

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# BADGES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ALL_BADGES = [
    {"id":"first_login","name":"First Step",     "icon":"ðŸ‘£","desc":"Logged in for the first time"},
    {"id":"streak_3",   "name":"Heatwave",        "icon":"ðŸ”¥","desc":"3-day study streak"},
    {"id":"streak_7",   "name":"Weekly Warrior",  "icon":"ðŸŽ–ï¸","desc":"7-day study streak"},
    {"id":"streak_14",  "name":"Fortnight Champ", "icon":"ðŸ†","desc":"14-day study streak"},
    {"id":"streak_30",  "name":"Monthly Master",  "icon":"ðŸ‘‘","desc":"30-day study streak"},
    {"id":"first_gen",  "name":"Starter Spark",   "icon":"âœ¨","desc":"Generated first AI content"},
    {"id":"qp_generated","name":"Paper Setter",   "icon":"ðŸ“","desc":"Generated a question paper"},
    {"id":"quiz_done",  "name":"Quiz Taker",       "icon":"ðŸ§ ","desc":"Generated a quiz"},
    {"id":"fc_10",      "name":"Card Collector",  "icon":"ðŸ—‚ï¸","desc":"Created 10 flashcards"},
    {"id":"study_60",   "name":"Hour Hero",        "icon":"â±ï¸","desc":"Studied 60 minutes total"},
    {"id":"study_300",  "name":"Study Champion",  "icon":"ðŸŽ“","desc":"Studied 5 hours total"},
]

def _award_raw(username, badge_id, c):
    try:
        c.execute("INSERT OR IGNORE INTO achievements (username,badge_id,earned_at) VALUES (?,?,?)",
                  (username,badge_id,datetime.datetime.now().isoformat()))
    except: pass

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    try: _award_raw(username, badge_id, c); conn.commit()
    except: pass
    finally: conn.close()

def get_earned_badges(username):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    c.execute("SELECT badge_id FROM achievements WHERE username=?",(username,))
    ids={r[0] for r in c.fetchall()}; conn.close(); return ids

def auto_check_badges(username):
    stats=get_user_stats(username)
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    def aw(bid): _award_raw(username, bid, c)
    try:
        if stats["streak_days"]>=3:  aw("streak_3")
        if stats["streak_days"]>=7:  aw("streak_7")
        if stats["streak_days"]>=14: aw("streak_14")
        if stats["streak_days"]>=30: aw("streak_30")
        if stats["total_minutes"]>=60:  aw("study_60")
        if stats["total_minutes"]>=300: aw("study_300")
        conn.commit()
    except: pass
    finally: conn.close()

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# FLASHCARD HELPERS  (SM-2 algorithm)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def save_flashcard(username, front, back, subject="", chapter=""):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""INSERT INTO flashcards
        (username,front_text,back_text,subject,chapter,ease_factor,interval_days,next_review_date,review_count,created_date)
        VALUES (?,?,?,?,?,2.5,1,?,0,?)""",(username,front,back,subject,chapter,today,today))
    conn.commit(); conn.close()
    conn2=sqlite3.connect("users.db",check_same_thread=False); c2=conn2.cursor()
    c2.execute("SELECT COUNT(*) FROM flashcards WHERE username=?",(username,))
    if (c2.fetchone()[0] or 0)>=10: award_badge(username,"fc_10")
    conn2.close()

def get_due_flashcards(username):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    today=datetime.date.today().isoformat()
    c.execute("""SELECT id,front_text,back_text,subject,chapter,ease_factor,interval_days,review_count
        FROM flashcards WHERE username=? AND next_review_date<=? ORDER BY next_review_date ASC""",(username,today))
    rows=c.fetchall(); conn.close(); return rows

def update_flashcard_review(card_id, performance):
    conn = sqlite3.connect("users.db", check_same_thread=False); c = conn.cursor()
    c.execute("SELECT ease_factor,interval_days,review_count FROM flashcards WHERE id=?",(card_id,))
    row=c.fetchone()
    if not row: conn.close(); return
    ef,interval,rc=row
    if performance==1:   interval=1; ef=max(1.3,ef-0.2)
    elif performance==2: interval=max(1,int(interval*1.2))
    elif performance==3: interval=max(1,int(interval*ef))
    else:                interval=max(1,int(interval*ef*1.3)); ef=min(3.0,ef+0.1)
    next_date=(datetime.date.today()+datetime.timedelta(days=interval)).isoformat()
    c.execute("UPDATE flashcards SET ease_factor=?,interval_days=?,next_review_date=?,review_count=? WHERE id=?",
              (ef,interval,next_date,rc+1,card_id))
    conn.commit(); conn.close()

def delete_flashcard(card_id):
    conn=sqlite3.connect("users.db",check_same_thread=False); c=conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?",(card_id,))
    conn.commit(); conn.close()

def get_all_flashcards(username):
    conn=sqlite3.connect("users.db",check_same_thread=False); c=conn.cursor()
    c.execute("""SELECT id,front_text,back_text,subject,chapter,next_review_date,review_count
        FROM flashcards WHERE username=? ORDER BY created_date DESC""",(username,))
    rows=c.fetchall(); conn.close(); return rows

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# AI ENGINE
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def get_available_models():
    api_key=st.secrets.get("GEMINI_API_KEY","")
    if not api_key: return ["Error: GEMINI_API_KEY not found"]
    try:
        genai.configure(api_key=api_key)
        return [m.name for m in genai.list_models()
                if "gemini" in m.name.lower()
                and "generateContent" in getattr(m,"supported_generation_methods",[])]
    except Exception as e: return [f"Error: {e}"]

def generate_with_fallback(prompt):
    api_key=st.secrets.get("GEMINI_API_KEY","")
    if not api_key: return ("âš ï¸ API key missing in secrets.toml","None")
    try: genai.configure(api_key=api_key)
    except Exception as e: return (f"âŒ Config error: {e}","None")
    try:
        available=[m.name for m in genai.list_models()
                   if "gemini" in m.name.lower()
                   and "generateContent" in getattr(m,"supported_generation_methods",[])]
    except Exception as e: return (f"âŒ Could not list models: {e}","None")
    if not available: return ("âŒ No Gemini models available.","None")
    for model_name in available:
        try:
            model=genai.GenerativeModel(model_name)
            response=model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,max_output_tokens=8192,top_p=0.9))
            if response and getattr(response,"text",None):
                return response.text, model_name
        except: continue
    return ("âŒ All models failed.","None")

def parse_flashcards(raw_text):
    cards=[]
    blocks=raw_text.strip().split("CARD ")
    for block in blocks:
        if not block.strip(): continue
        front=back=""
        for line in block.splitlines():
            l=line.strip()
            if l.upper().startswith("FRONT:"): front=l[6:].strip()
            elif l.upper().startswith("BACK:"): back=l[5:].strip()
        if front and back: cards.append({"front":front,"back":back})
    return cards

def build_prompt(tool, chapter, topic, subject, audience, style, board="", course=""):
    base=(f"You are an expert educator creating study material for {audience}.\n"
          f"Subject: {subject} | Topic: {topic} | Chapter: {chapter} | Board/Syllabus: {board}\n"
          f"Requirements: Accurate, Exam-focused, Well-structured, With examples, Error-free.\n\n")
    if tool=="ðŸ“ Summary":
        if style=="ðŸ§ª Question Paper":
            return (f"You are an expert exam paper setter.\nBoard:{board}|Course:{course}|Subject:{subject}|For:{audience}\n\n"
                    f"Create a complete professional exam paper:\n- Section A: 10 MCQs (1 mark each)\n"
                    f"- Section B: 5 Short Answers (3 marks each)\n- Section C: 4 Long Answers (5 marks each)\n"
                    f"- Section D: 1-2 Case Studies (6-8 marks each)\nTotal: 100 marks. NO answers in this paper.")
        if style=="ðŸ“„ Detailed":
            return base+"Create a detailed chapter summary: overview, key concepts, definitions, formulas, 2 worked examples, common mistakes, exam tips."
        if style=="âš¡ Short & Quick":
            return base+"Create a quick-reference summary: one-liner definition, 5-7 key points, formulas, quick tips. Max 500 words."
        return base+"Create structured notes: clear headings, bullets, definitions, examples, revision points."
    if tool=="ðŸ§  Quiz":
        return base+"Create: 5 MCQs (4 options each, mark answer), 5 short-answer Q&As, 3 long-answer Q&As with model answers."
    if tool=="ðŸ“Œ Revision Notes":
        return base+"Create revision notes: top 10 must-know points, formula sheet, mnemonics, comparisons, exam focus areas."
    if tool=="ðŸ§ª Question Paper":
        return (f"You are an expert exam paper setter.\nBoard:{board}|Course:{course}|Subject:{subject}|For:{audience}\n\n"
                f"Create a complete professional exam paper:\n- Section A: 10 MCQs (1 mark each)\n"
                f"- Section B: 5 Short Answers (3 marks each)\n- Section C: 4 Long Answers (5 marks each)\n"
                f"- Section D: 1-2 Case Studies (6-8 marks each)\nTotal: 100 marks. DO NOT provide answers.")
    if tool=="â“ Exam Q&A":
        return base+"Create exam Q&A bank: 8-10 frequently asked Qs with model answers, conceptual Qs, application Qs."
    return base+"Create complete exam-ready study material."

def build_flashcard_prompt(subject, chapter, topic):
    return (f"Create exactly 10 study flashcards.\nSubject:{subject}|Chapter:{chapter}|Topic:{topic}\n"
            f"Use EXACTLY this format:\nCARD 1\nFRONT: [question or term]\nBACK: [answer or definition]\n"
            f"CARD 2\nFRONT: ...\nBACK: ...\n(Continue for all 10. No extra text.)")

def get_effective_output_name(tool, style):
    if tool=="ðŸ“ Summary":
        if style=="ðŸ§ª Question Paper": return "Question Paper"
        return {"ðŸ“„ Detailed":"Detailed Summary","âš¡ Short & Quick":"Quick Summary","ðŸ“‹ Notes Format":"Study Notes"}.get(style,"Summary")
    return {"ðŸ§  Quiz":"Quiz","ðŸ“Œ Revision Notes":"Revision Notes","ðŸ§ª Question Paper":"Question Paper","â“ Exam Q&A":"Exam Q&A"}.get(tool,"Study Material")

def get_button_label(tool, style):
    return f"âš¡ Generate {get_effective_output_name(tool,style)}"

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PDF GENERATION
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def generate_pdf(title, subtitle, content, color_hex="#1d4ed8"):
    buffer=io.BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,topMargin=2*cm,bottomMargin=2*cm,leftMargin=1.5*cm,rightMargin=1.5*cm)
    styles=getSampleStyleSheet()
    story=[]
    title_style=ParagraphStyle("T2",parent=styles["Normal"],fontSize=20,fontName="Helvetica-Bold",
                               textColor=colors.HexColor(color_hex),alignment=TA_CENTER,spaceAfter=6)
    sub_style=ParagraphStyle("Sub",parent=styles["Normal"],fontSize=11,
                             textColor=colors.HexColor("#64748b"),alignment=TA_CENTER,spaceAfter=4)
    body_style=ParagraphStyle("B2",parent=styles["Normal"],fontSize=11,leading=17,
                              textColor=colors.HexColor("#1e293b"),spaceAfter=8)
    story.append(Paragraph(title,title_style))
    story.append(Paragraph(subtitle,sub_style))
    story.append(HRFlowable(width="100%",thickness=1.5,color=colors.HexColor(color_hex),spaceAfter=12))
    for line in content.split("\n"):
        line=line.strip()
        if not line: story.append(Spacer(1,0.25*cm)); continue
        if line.startswith("## "):
            story.append(Paragraph(f"<b><font size=14>{line[3:]}</font></b>",
                ParagraphStyle("H2",parent=styles["Normal"],fontSize=14,fontName="Helvetica-Bold",
                               textColor=colors.HexColor(color_hex),spaceAfter=6,spaceBefore=10)))
        elif line.startswith("# "):
            story.append(Paragraph(f"<b><font size=16>{line[2:]}</font></b>",
                ParagraphStyle("H1",parent=styles["Normal"],fontSize=16,fontName="Helvetica-Bold",
                               textColor=colors.HexColor(color_hex),spaceAfter=8,spaceBefore=12)))
        elif line.startswith(("- ","* ","â€¢ ")):
            story.append(Paragraph(f"â€¢ {line[2:]}",body_style))
        elif line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(f"<b>{line[2:-2]}</b>",body_style))
        else:
            story.append(Paragraph(line,body_style))
    story.append(Spacer(1,0.2*cm))
    story.append(Paragraph(f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle("Ft",parent=styles["Normal"],fontSize=8,
                       textColor=colors.HexColor("#94a3b8"),alignment=TA_CENTER)))
    doc.build(story)
    buffer.seek(0); return buffer

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# SESSION STATE + NAV
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def init_session_state():
    defaults={
        "logged_in":False,"username":"","active_page":"dashboard",
        "history":[],"current_chapters":[],"last_chapter_key":"",
        "generated_result":None,"generated_model":None,
        "generated_label":None,"generated_tool":None,
        "generated_chapter":None,"generated_subject":None,
        "generated_topic":None,"generated_course":None,
        "generated_stream":None,"generated_board":None,
        "generated_audience":None,"generated_output_style":None,
        "answers_result":None,"answers_model":None,"show_answers":False,
        "fullpaper_result":None,"fullpaper_model":None,"show_fullpaper":False,
        "daily_checkin_done":False,
        "study_timer_active":False,"study_timer_start":None,
        "current_subject_for_timer":"General",
        "review_idx":0,"review_show_ans":False,
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v

def go_to(page):
    st.session_state.active_page=page; st.rerun()

def reset_generation_state():
    for k in ["generated_result","generated_model","generated_label","generated_tool",
              "generated_chapter","generated_subject","generated_topic","generated_course",
              "generated_stream","generated_board","generated_audience","generated_output_style",
              "answers_result","answers_model","fullpaper_result","fullpaper_model"]:
        st.session_state[k]=None
    st.session_state.show_answers=False
    st.session_state.show_fullpaper=False

def add_to_history(tool, chapter, subject, result):
    entry={"time":datetime.datetime.now().strftime("%H:%M"),"tool":tool,
           "chapter":chapter,"subject":subject,
           "preview":result[:80]+"..." if len(result)>80 else result}
    st.session_state.history.insert(0,entry)
    st.session_state.history=st.session_state.history[:10]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# UI HELPERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def render_header(title, subtitle):
    st.markdown(f"""
        <div class="sf-hero">
            <div class="sf-hero-title">{title}</div>
            <div class="sf-hero-sub">{subtitle}</div>
            <div class="sf-powered">âœ¦ POWERED BY AI âœ¦</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

def render_back_button():
    col_btn,_=st.columns([1,3])
    with col_btn:
        if st.button("â† Back to Dashboard",key="back_to_dash",use_container_width=True):
            go_to("dashboard")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# SIDEBAR
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def render_sidebar(username):
    stats=get_user_stats(username) or {}
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:12px 0 10px 0;">
                <div style="font-size:2rem;">ðŸŽ“</div>
                <div style="font-size:1.02rem;font-weight:800;color:#2563eb;">StudySmart AI</div>
                <div style="font-size:.77rem;margin-top:3px;">Hi, {username} ðŸ‘‹</div>
            </div>
        """, unsafe_allow_html=True)

        c1,c2=st.columns(2)
        with c1:
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#ff6b6b,#feca57);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                ðŸ”¥ {stats.get('streak_days',0)}<br>
                <span style="font-size:.62rem;font-weight:500;color:white;">day streak</span>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="text-align:center;padding:7px 3px;
                background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                â­ Lv {stats.get('level',1)}<br>
                <span style="font-size:.62rem;font-weight:500;color:white;">{stats.get('total_xp',0)} XP</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Daily Check-in
        if not st.session_state.daily_checkin_done:
            if st.button("âœ… Daily Check-in (+20 XP)",use_container_width=True,key="sb_checkin"):
                result=check_daily_login(username)
                st.session_state.daily_checkin_done=True
                auto_check_badges(username)
                st.success(result.get("message","Checked in!"))
                st.rerun()
        else:
            st.success(f"âœ… Checked in Â· ðŸ”¥ {stats.get('streak_days',0)} days")

        st.divider()

        # Study Timer
        st.markdown("**â±ï¸ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed=int((datetime.datetime.now()-st.session_state.study_timer_start).total_seconds()//60)
            st.info(f"ðŸŸ¢ Running: {elapsed} min â€” {st.session_state.current_subject_for_timer}")
            if st.button("â¹ï¸ Stop & Save",use_container_width=True,key="sb_stop"):
                st.session_state.study_timer_active=False
                dur=max(1,elapsed)
                subj=st.session_state.get("current_subject_for_timer","General")
                record_study_session(username,subj,dur)
                xp_earned=max(5,(dur//10)*10)
                award_xp(username,xp_earned)
                auto_check_badges(username)
                st.success(f"âœ… {dur} min saved! +{xp_earned} XP")
                st.rerun()
        else:
            if st.button("â–¶ï¸ Start Timer",use_container_width=True,key="sb_start"):
                st.session_state.study_timer_active=True
                st.session_state.study_timer_start=datetime.datetime.now()
                st.rerun()

        st.divider()
        st.markdown("**ðŸ§­ Navigate**")
        pages=[("ðŸ  Dashboard","dashboard"),("ðŸ“š Study Tools","study"),
               ("ðŸ—‚ï¸ Flashcards","flashcards"),("ðŸ… Achievements","achievements")]
        for label,page in pages:
            if st.button(label,use_container_width=True,key=f"nav_{page}"):
                go_to(page)

        st.divider()
        st.markdown("**ðŸ“œ Recent Activity**")
        if st.session_state.history:
            for h in st.session_state.history[:3]:
                st.markdown(f"""<div class="sf-hist">
                    ðŸ• {h['time']} | <b>{h['tool']}</b><br>
                    ðŸ“– {h['chapter']} â€” {h['subject']}<br>
                    <small>{h['preview']}</small>
                </div>""", unsafe_allow_html=True)
        else:
            st.caption("No activity yet.")

        with st.expander("ðŸ¤– AI Status"):
            if st.button("Check Models",use_container_width=True,key="sb_models"):
                with st.spinner("Checking..."):
                    mdls=get_available_models()
                for m in mdls: st.write(f"âœ… {m}")

        st.divider()
        if st.button("ðŸšª Logout",use_container_width=True,key="sb_logout"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# DASHBOARD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def show_dashboard(username):
    render_header("StudySmart","Your Daily Learning Companion")
    stats=get_user_stats(username) or {}

    c1,c2,c3,c4=st.columns(4)
    for col,cls,icon,val,lbl in [
        (c1,"mc-blue",  "ðŸ”¥",stats.get("streak_days",0),"Day Streak"),
        (c2,"mc-green", "â­",f"Level {stats.get('level',1)}","Your Level"),
        (c3,"mc-purple","ðŸ“š",stats.get("flashcards_due",0),"Cards Due"),
        (c4,"mc-amber", "â±ï¸",f"{stats.get('weekly_study_minutes',0)} min","This Week"),
    ]:
        with col:
            st.markdown(f'<div class="mc {cls}"><div class="icon">{icon}</div><div class="val">{val}</div><div class="lbl">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    total_xp=stats.get("total_xp",0); lvl=stats.get("level",1)
    lp=stats.get("level_progress",total_xp%500); pct=min(100,int((lp/500)*100))
    st.markdown(f"""<div style="display:flex;justify-content:space-between;font-size:.85rem;font-weight:700;margin-bottom:5px;">
        <span>â­ Level {lvl}</span><span>{total_xp} XP &nbsp;Â·&nbsp; {500-lp} XP to next level</span>
    </div><div class="xp-wrap"><div class="xp-fill" style="width:{pct}%;"></div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left,right=st.columns([1.1,1])
    with left:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**ðŸŒ± Study Momentum**")
        mins=stats.get("total_study_minutes",0); growth=min(100,mins//10)
        plant=(("ðŸŒ±","Seedling") if growth<20 else ("ðŸŒ¿","Sprout") if growth<40 else
               ("ðŸª´","Growing Plant") if growth<70 else ("ðŸŒ³","Strong Tree") if growth<90 else ("ðŸŒ²","Master Tree"))
        st.markdown(f"""<div class="sf-soft-card" style="text-align:center;margin-bottom:10px;">
            <div style="font-size:2.6rem;">{plant[0]}</div>
            <div style="font-weight:800;font-size:.93rem;">{plant[1]}</div>
            <div style="font-size:.8rem;margin-top:3px;">{mins} min total studied</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**âš¡ Quick Actions**")
        if st.button("ðŸ“š Open Study Tools",  use_container_width=True,key="d_study"):  go_to("study")
        if st.button("ðŸ—‚ï¸ Review Flashcards", use_container_width=True,key="d_fc"):     go_to("flashcards")
        if st.button("ðŸ… View Achievements", use_container_width=True,key="d_ach"):    go_to("achievements")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**ðŸ“œ Recent Activity**")
        if not st.session_state.history:
            st.info("No activity yet. Generate your first study content!")
        else:
            for h in st.session_state.history:
                st.markdown(f"""<div class="sf-hist">
                    ðŸ• {h['time']} | <b>{h['tool']}</b><br>
                    ðŸ“– {h['chapter']} â€” {h['subject']}<br>
                    <small>{h['preview']}</small>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown("**ðŸ… Badge Snapshot**")
        earned=get_earned_badges(username)
        earned_list=[b for b in ALL_BADGES if b["id"] in earned][:4]
        if earned_list:
            bc=st.columns(2)
            for i,badge in enumerate(earned_list):
                with bc[i%2]:
                    st.markdown(f"""<div class="bdg earned">
                        <div class="bi">{badge['icon']}</div>
                        <div class="bn">{badge['name']}</div>
                        <div class="bs">âœ… Earned</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Complete daily check-in to earn your first badge!")
        st.markdown('</div>', unsafe_allow_html=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ACHIEVEMENTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def show_achievements(username):
    render_back_button()
    render_header("Achievements","Badges unlock automatically as you learn")
    auto_check_badges(username)
    stats=get_user_stats(username) or {}
    earned=get_earned_badges(username)
    earned_list=[b for b in ALL_BADGES if b["id"] in earned]
    locked_list=[b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(f"**âœ… {len(earned_list)} / {len(ALL_BADGES)} badges earned**")
    st.progress(len(earned_list)/len(ALL_BADGES) if ALL_BADGES else 0)
    st.markdown("""
    <div style="font-size:.82rem;color:#475569;margin-top:8px;">
    ðŸ”¥ <b>Streaks</b> â€” log in every day &nbsp;|&nbsp;
    â±ï¸ <b>Study time</b> â€” use the Study Timer &nbsp;|&nbsp;
    âœ¨ <b>Content</b> â€” generate with AI &nbsp;|&nbsp;
    ðŸ—‚ï¸ <b>Flashcards</b> â€” create 10 cards
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if earned_list:
        st.markdown("## âœ… Earned Badges")
        cols=st.columns(min(4,len(earned_list)))
        for i,b in enumerate(earned_list):
            with cols[i%4]:
                st.markdown(f"""<div class="bdg earned">
                    <div class="bi">{b['icon']}</div>
                    <div class="bn">{b['name']}</div>
                    <div class="bs">{b['desc']}</div>
                </div>""", unsafe_allow_html=True)

    if locked_list:
        st.markdown("---")
        st.markdown("## ðŸ”’ Locked Badges")
        hints={"streak_3":"Log in 3 days in a row","streak_7":"Log in 7 days in a row",
               "streak_14":"Log in 14 days in a row","streak_30":"Log in 30 days in a row",
               "first_gen":"Generate any AI content","qp_generated":"Generate a Question Paper",
               "quiz_done":"Generate a Quiz","fc_10":"Create 10 flashcards",
               "study_60":"Study 60 min total","study_300":"Study 300 min total"}
        cols=st.columns(min(4,len(locked_list)))
        for i,b in enumerate(locked_list):
            with cols[i%4]:
                hint=hints.get(b["id"],b["desc"])
                st.markdown(f"""<div class="bdg">
                    <div class="bi" style="opacity:.28;">ðŸ”’</div>
                    <div class="bn">{b['name']}</div>
                    <div class="bs">{hint}</div>
                </div>""", unsafe_allow_html=True)

    streak=stats.get("streak_days",0)
    total_min=stats.get("total_study_minutes",0)
    st.markdown('<div class="sf-card" style="margin-top:14px;">', unsafe_allow_html=True)
    st.markdown("**ðŸ“ˆ Your Progress Towards Next Badge**")
    for b in locked_list:
        bid=b["id"]
        if bid=="streak_3"   and streak<3:   st.caption(f"ðŸ”¥ Streak: {streak}/3 days"); st.progress(streak/3)
        elif bid=="streak_7" and streak<7:   st.caption(f"ðŸ”¥ Streak: {streak}/7 days"); st.progress(streak/7)
        elif bid=="streak_14"and streak<14:  st.caption(f"ðŸ”¥ Streak: {streak}/14 days"); st.progress(streak/14)
        elif bid=="streak_30"and streak<30:  st.caption(f"ðŸ”¥ Streak: {streak}/30 days"); st.progress(streak/30)
        elif bid=="study_60" and total_min<60:  st.caption(f"â±ï¸ Study time: {total_min}/60 min"); st.progress(total_min/60)
        elif bid=="study_300"and total_min<300: st.caption(f"â±ï¸ Study time: {total_min}/300 min"); st.progress(total_min/300)
        elif bid=="fc_10":
            conn=sqlite3.connect("users.db"); cc=conn.cursor()
            cc.execute("SELECT COUNT(*) FROM flashcards WHERE username=?",(username,))
            fc=cc.fetchone()[0]; conn.close()
            if fc<10: st.caption(f"ðŸ—‚ï¸ Flashcards: {fc}/10"); st.progress(fc/10)
    st.markdown('</div>', unsafe_allow_html=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# FLASHCARDS PAGE
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def show_flashcards(username):
    render_back_button()
    render_header("Flashcards","Spaced repetition for lasting memory")
    tab1,tab2,tab3=st.tabs(["ðŸ“– Review Due","âž• Create","ðŸ“‹ My Library"])

    with tab1:
        due=get_due_flashcards(username)
        if not due:
            st.success("ðŸŽ‰ No flashcards due today â€” great job!")
            total=len(get_all_flashcards(username))
            if total>0: st.info(f"ðŸ“š You have {total} flashcard(s) in your library.")
            return
        st.markdown(f"**{len(due)} card(s) due for review**")
        idx=st.session_state.review_idx
        if idx>=len(due): st.session_state.review_idx=0; idx=0
        card=due[idx]
        card_id,front,back=card[0],card[1],card[2]

        st.markdown(f"""
        <div class="fc-front">
            <div style="font-size:.73rem;opacity:.7;margin-bottom:10px;text-transform:uppercase;letter-spacing:.06em;">
                Card {idx+1} of {len(due)}
            </div>
            <div style="font-size:1.15rem;font-weight:700;line-height:1.5;">{front}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)

        if not st.session_state.review_show_ans:
            if st.button("ðŸ‘ï¸ Show Answer",use_container_width=True,key="show_ans_btn"):
                st.session_state.review_show_ans=True; st.rerun()
        else:
            st.markdown(f"""
            <div class="fc-back">
                <div style="font-size:.73rem;opacity:.8;margin-bottom:8px;">ANSWER</div>
                <div style="font-size:.98rem;font-weight:700;line-height:1.5;">{back}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
            st.markdown("**How well did you remember?**")
            b1,b2,b3,b4=st.columns(4)
            for col,lbl,perf,ks in [
                (b1,"ðŸ˜“ Again",1,"again"),(b2,"ðŸ˜ Hard",2,"hard"),
                (b3,"ðŸ™‚ Good",3,"good"),(b4,"ðŸ˜„ Easy",4,"easy")
            ]:
                with col:
                    if st.button(lbl,use_container_width=True,key=f"fc_{ks}_{card_id}"):
                        update_flashcard_review(card_id,perf)
                        award_xp(username,3)
                        st.session_state.review_idx+=1
                        st.session_state.review_show_ans=False
                        st.rerun()

    with tab2:
        cl,cr=st.columns(2)
        with cl:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### âœï¸ Manual Card")
            with st.form("manual_fc"):
                f_front=st.text_input("Front (Question)")
                f_back=st.text_area("Back (Answer)",height=75)
                f_subj=st.text_input("Subject (optional)")
                f_chap=st.text_input("Chapter (optional)")
                if st.form_submit_button("âž• Save Card",use_container_width=True):
                    if f_front.strip() and f_back.strip():
                        save_flashcard(username,f_front.strip(),f_back.strip(),f_subj.strip(),f_chap.strip())
                        award_xp(username,5)
                        auto_check_badges(username)
                        st.success("âœ… Card saved! +5 XP"); st.rerun()
                    else: st.warning("âš ï¸ Front and Back required.")
            st.markdown('</div>', unsafe_allow_html=True)

        with cr:
            st.markdown('<div class="sf-card">', unsafe_allow_html=True)
            st.markdown("### ðŸ¤– AI Generate")
            with st.form("ai_fc"):
                ai_subj=st.text_input("Subject")
                ai_chap=st.text_input("Chapter")
                ai_top=st.text_input("Topic (optional)")
                if st.form_submit_button("âš¡ Generate 10 Cards",use_container_width=True):
                    if ai_subj.strip() and ai_chap.strip():
                        with st.spinner("Generating flashcards..."):
                            raw,mdl=generate_with_fallback(build_flashcard_prompt(ai_subj.strip(),ai_chap.strip(),ai_top.strip()))
                        if mdl!="None":
                            cards=parse_flashcards(raw)
                            for card in cards: save_flashcard(username,card["front"],card["back"],ai_subj.strip(),ai_chap.strip())
                            award_xp(username,len(cards)*5)
                            auto_check_badges(username)
                            st.success(f"âœ… {len(cards)} cards saved! +{len(cards)*5} XP"); st.rerun()
                        else: st.error("âŒ Generation failed.")
                    else: st.warning("âš ï¸ Subject and Chapter required.")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        all_cards=get_all_flashcards(username)
        if not all_cards:
            st.markdown("<div style='text-align:center;padding:30px;color:#64748b;'>"
                        "ðŸ“­ No flashcards yet.<br>Create your first card in the âž• Create tab."
                        "</div>", unsafe_allow_html=True)
        else:
            st.caption(f"ðŸ“š Total: {len(all_cards)} flashcards in your library")
            for row in all_cards:
                c_id,front,back,subj,chap,nrd,rc=row
                with st.expander(f"ðŸ“Œ {front[:60]}{'...' if len(front)>60 else ''}"):
                    st.markdown(f"**Q:** {front}")
                    st.markdown(f"**A:** {back}")
                    st.caption(f"Subject: {subj or 'â€”'} | Chapter: {chap or 'â€”'} | Next review: {nrd} | Reviews done: {rc}")
                    if st.button("ðŸ—‘ï¸ Delete this card",key=f"del_fc_{c_id}",use_container_width=True):
                        delete_flashcard(c_id); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# STUDY TOOLS PAGE
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def show_study_tools(username):
    render_back_button()
    render_header("Study Tools","AI-powered exam preparation")

    tool=st.radio("ðŸ› ï¸ Select Tool",
        ["ðŸ“ Summary","ðŸ§  Quiz","ðŸ“Œ Revision Notes","ðŸ§ª Question Paper","â“ Exam Q&A"],
        horizontal=True,key="study_tool_radio")

    if not STUDY_DATA:
        st.error("âŒ No study data loaded. Check data/study_data.json"); return

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    ca,cb=st.columns([1.5,1])
    with ca:
        category=st.selectbox("ðŸ“š Category",list(STUDY_DATA.keys()),key="sel_cat")
    with cb:
        course=st.selectbox("ðŸŽ“ Program / Class",get_courses(category),key="sel_course")
        stream=st.selectbox("ðŸ“– Stream",get_streams(category,course),key="sel_stream")
        subject=st.selectbox("ðŸ§¾ Subject",get_subjects(category,course,stream),key="sel_subject")
        board="University / National Syllabus"
        if category=="K-12th":
            board=st.selectbox("ðŸ« Board",BOARDS,key="sel_board")
        else:
            st.info(f"ðŸ“Œ Syllabus: {board}")

    topic=st.selectbox("ðŸ—‚ï¸ Topic",get_topics(category,course,stream,subject),key="sel_topic")

    chapter_key=f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key!=chapter_key:
        st.session_state.current_chapters=get_chapters(category,course,stream,subject,topic)
        st.session_state.last_chapter_key=chapter_key
        reset_generation_state()

    chapter=st.selectbox("ðŸ“ Chapter",st.session_state.current_chapters,key="sel_chapter")
    st.session_state.current_subject_for_timer=subject
    st.markdown('</div>', unsafe_allow_html=True)

    style=st.radio("âš™ï¸ Output Style",
        ["ðŸ“„ Detailed","âš¡ Short & Quick","ðŸ“‹ Notes Format","ðŸ§ª Question Paper"],
        horizontal=True,key="study_style_radio")

    eff_label=get_effective_output_name(tool,style)
    btn_label=get_button_label(tool,style)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button(btn_label,use_container_width=True,key="gen_btn"):
        if not chapter or chapter=="No chapters found":
            st.warning("âš ï¸ Please select a valid chapter."); return
        audience=(f"{board} {course} students" if category=="K-12th" else f"{course} students")
        prompt=build_prompt(tool,chapter,topic,subject,audience,style,board=board,course=course)
        with st.spinner(f"âš¡ Generating {eff_label}..."):
            result,model_used=generate_with_fallback(prompt)
        st.session_state.update({
            "generated_result":result,"generated_model":model_used,
            "generated_label":eff_label,"generated_tool":tool,
            "generated_chapter":chapter,"generated_subject":subject,
            "generated_topic":topic,"generated_course":course,
            "generated_stream":stream,"generated_board":board,
            "generated_audience":audience,"generated_output_style":style,
            "answers_result":None,"answers_model":None,"show_answers":False,
            "fullpaper_result":None,"fullpaper_model":None,"show_fullpaper":False,
        })
        if model_used!="None":
            add_to_history(eff_label,chapter,subject,result)
            award_xp(username,25)
            award_badge(username,"first_gen")
            if eff_label=="Question Paper": award_badge(username,"qp_generated")
            if eff_label=="Quiz": award_badge(username,"quiz_done")
            auto_check_badges(username)

    if st.session_state.generated_result:
        result=st.session_state.generated_result
        g_label=st.session_state.generated_label
        g_chapter=st.session_state.generated_chapter
        g_subject=st.session_state.generated_subject
        g_topic=st.session_state.generated_topic
        g_course=st.session_state.generated_course
        g_stream=st.session_state.generated_stream
        g_board=st.session_state.generated_board
        g_audience=st.session_state.generated_audience

        if st.session_state.generated_model=="None":
            st.error("âŒ Generation failed."); st.markdown(result); return

        is_qp=(g_label=="Question Paper")
        box_cls="sf-fullpaper" if is_qp else "sf-output"

        st.markdown(f'<div class="{box_cls}">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} â€” {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        if not is_qp:
            if st.button("ðŸ—‚ï¸ Save as Flashcards",use_container_width=True,key="save_fc_btn"):
                with st.spinner("Creating flashcards..."):
                    raw,mdl=generate_with_fallback(build_flashcard_prompt(g_subject,g_chapter,g_topic or ""))
                if mdl!="None":
                    cards=parse_flashcards(raw)
                    for card in cards: save_flashcard(username,card["front"],card["back"],g_subject,g_chapter)
                    award_xp(username,len(cards)*5)
                    auto_check_badges(username)
                    st.success(f"âœ… {len(cards)} flashcards saved! +{len(cards)*5} XP")
                else: st.error("âŒ Flashcard generation failed.")
            try:
                pdf=generate_pdf(f"{g_label} â€” {g_chapter}",f"{g_subject} | {g_topic} | {g_course}",result)
                safe=(g_chapter.replace(" ","_").replace(":","").replace("/","-")+".pdf")
                st.download_button("â¬‡ï¸ Download PDF",data=pdf,file_name=safe,mime="application/pdf",use_container_width=True,key="dl_main_pdf")
            except Exception as e: st.warning(f"âš ï¸ PDF error: {e}")
        else:
            try:
                qp_pdf=generate_pdf(f"Question Paper â€” {g_subject}",f"{g_board} | {g_course} | {g_stream}",result,"#7c3aed")
                safe_qp=(g_subject.replace(" ","_").replace(":","").replace("/","-")+"_QuestionPaper.pdf")
                st.download_button("â¬‡ï¸ Download Question Paper PDF",data=qp_pdf,file_name=safe_qp,mime="application/pdf",use_container_width=True,key="dl_qp_pdf")
            except Exception as e: st.warning(f"âš ï¸ PDF error: {e}")

            if st.button("ðŸ“‹ Generate Answer Key",use_container_width=True,key="ans_btn"):
                with st.spinner("Generating answer key..."):
                    ans_r,ans_m=generate_with_fallback(
                        f"Provide complete model answers for this question paper:\n\n{result}\n\n"
                        f"Subject:{g_subject}|Board:{g_board}|For:{g_audience}")
                st.session_state.answers_result=ans_r
                st.session_state.answers_model=ans_m
                st.session_state.show_answers=True

            if st.session_state.show_answers and st.session_state.answers_result:
                if st.session_state.answers_model!="None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### ðŸ“‹ Answer Key â€” {g_subject}")
                    st.markdown(st.session_state.answers_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        ans_pdf=generate_pdf(f"Answer Key â€” {g_subject}",f"{g_board}|{g_course}",st.session_state.answers_result,"#059669")
                        safe_a=(g_chapter.replace(" ","_").replace(":","").replace("/","-")+"_Answers.pdf")
                        st.download_button("â¬‡ï¸ Download Answer Key PDF",data=ans_pdf,file_name=safe_a,mime="application/pdf",use_container_width=True,key="dl_ans_pdf")
                    except Exception as e: st.warning(f"âš ï¸ PDF error: {e}")

            if st.button(f"ðŸ—‚ï¸ Generate Full {g_subject} Paper",use_container_width=True,key="full_qp_btn"):
                with st.spinner("Generating full subject paper..."):
                    full_r,full_m=generate_with_fallback(build_prompt("ðŸ§ª Question Paper",g_chapter,g_topic,g_subject,g_audience,"ðŸ“„ Detailed",g_board,g_course))
                st.session_state.fullpaper_result=full_r
                st.session_state.fullpaper_model=full_m
                st.session_state.show_fullpaper=True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model!="None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### ðŸ—‚ï¸ Full Subject Paper â€” {g_subject}")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf=generate_pdf(f"Full Paper â€” {g_subject}",f"{g_board}|{g_course}|{g_stream}",st.session_state.fullpaper_result,"#7c3aed")
                        safe_f=f"{g_subject}_{g_board}_FullPaper.pdf".replace(" ","_")
                        st.download_button("â¬‡ï¸ Download Full Paper PDF",data=full_pdf,file_name=safe_f,mime="application/pdf",use_container_width=True,key="dl_full_pdf")
                    except Exception as e: st.warning(f"âš ï¸ PDF error: {e}")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# AUTH UI  (Login page â€” registration CLOSED)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        tab1, tab2 = st.tabs(["ðŸ” Login", "ðŸ“ Register"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input("ðŸ‘¤ Username", key="login_u", placeholder="Enter your username")
                p = st.text_input("ðŸ”‘ Password", type="password", key="login_p", placeholder="Enter your password")
                login_submit = st.form_submit_button("Sign In ðŸš€", use_container_width=True)

            if login_submit:
                if u.strip() and p.strip():
                    conn = sqlite3.connect("users.db", check_same_thread=False)
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username=? AND password=?",
                              (u.strip(), hash_p(p)))
                    user_row = c.fetchone()
                    conn.close()

                    if user_row:
                        conn2 = sqlite3.connect("users.db", check_same_thread=False)
                        c2 = conn2.cursor()
                        c2.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (u.strip(),))
                        conn2.commit(); conn2.close()

                        st.session_state.logged_in = True
                        st.session_state.username  = u.strip()

                        try:
                            update_streak(u.strip())
                            award_badge(u.strip(), "first_login")
                            auto_check_badges(u.strip())
                        except Exception: pass

                        st.success("âœ… Login successful!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("âŒ Invalid username or password.")
                else:
                    st.warning("âš ï¸ Please enter both username and password.")

        with tab2:
            st.info("ðŸ“ Registration is currently closed. Contact admin for access.")
            st.markdown("""
            <div style="padding:16px;background:rgba(59,130,246,0.08);border-radius:10px;margin-top:12px;">
                <strong>â„¹ï¸ Account Access:</strong><br/>
                If you don't have an account, please contact the administrator for registration.
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN ROUTER
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main_app():
    render_sidebar(st.session_state.username)
    page=st.session_state.active_page
    if   page=="dashboard":    show_dashboard(st.session_state.username)
    elif page=="study":        show_study_tools(st.session_state.username)
    elif page=="flashcards":   show_flashcards(st.session_state.username)
    elif page=="achievements": show_achievements(st.session_state.username)
    else:                      show_dashboard(st.session_state.username)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ENTRY POINT
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
init_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
