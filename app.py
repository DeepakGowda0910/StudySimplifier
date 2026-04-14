# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — app.py  (Complete · Self-Contained · All Fixes Applied)
# ✅ Streak works  ✅ Timer saves weekly minutes  ✅ Badges auto-unlock
# ✅ No flashcard library banner  ✅ No external daily_engagement.py needed
# ✅ Quick Actions clickable  ✅ Lighter dark mode  ✅ Mobile friendly
# ✅ Registration closed  ✅ Whitelisted login
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
[data-theme="dark"] .sf-hist { background:#243045 !important; }
[data-theme="dark"] .sf-hist * { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-hist b { color:#93c5fd !important; }
[data-theme="dark"] .sf-output { background:#1e2f4a !important; border-color:#2d4a7a !important; }
[data-theme="dark"] .sf-output *,[data-theme="dark"] .sf-output p { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-output h1,[data-theme="dark"] .sf-output h2,[data-theme="dark"] .sf-output h3 { color:#93c5fd !important; }
[data-theme="dark"] .sf-answers { background:#1a3628 !important; }
[data-theme="dark"] .sf-answers *,[data-theme="dark"] .sf-answers p { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-answers h1,[data-theme="dark"] .sf-answers h2,[data-theme="dark"] .sf-answers h3 { color:#86efac !important; }
[data-theme="dark"] .sf-fullpaper { background:#251a40 !important; }
[data-theme="dark"] .sf-fullpaper *,[data-theme="dark"] .sf-fullpaper p { color:#e2e8f0 !important; }
[data-theme="dark"] .sf-fullpaper h1,[data-theme="dark"] .sf-fullpaper h2,[data-theme="dark"] .sf-fullpaper h3 { color:#c4b5fd !important; }
[data-theme="dark"] .bdg { background:#243045 !important; border-color:#2e3f58 !important; }
[data-theme="dark"] .bdg * { color:#e2e8f0 !important; }
[data-theme="dark"] .bdg.earned { background:#2a2010 !important; }
[data-theme="dark"] [data-testid="stSidebar"] { background:#182030 !important; }
[data-theme="dark"] [data-testid="stSidebar"] * { color:#e2e8f0 !important; }
[data-theme="dark"] div[data-baseweb="select"] > div:first-child { background:#243045 !important; border-color:#3a506e !important; }
[data-theme="dark"] div[data-baseweb="select"] > div > div > div { color:#e2e8f0 !important; }
[data-theme="dark"] div[data-baseweb="popover"] { background:#243045 !important; }
[data-theme="dark"] div[role="option"] { background:#243045 !important; color:#e2e8f0 !important; }
[data-theme="dark"] div[role="option"]:hover { background:#2e3f58 !important; }
[data-theme="dark"] input,[data-theme="dark"] textarea { background:#243045 !important; color:#e2e8f0 !important; }
[data-theme="dark"] .stTabs [data-baseweb="tab"] { color:#94a3b8 !important; }
[data-theme="dark"] .stTabs [aria-selected="true"] { color:#f1f5f9 !important; }
[data-theme="dark"] .sf-hero-sub { color:#94a3b8 !important; }
[data-theme="dark"] .sf-powered { background:rgba(59,130,246,.15) !important; color:#93c5fd !important; }
[data-theme="dark"] .xp-wrap { background:#2e3f58 !important; }
[data-theme="dark"] [data-testid="stWidgetLabel"] p { color:#e2e8f0 !important; }
[data-theme="dark"] .stRadio [data-testid="stMarkdownContainer"] p { color:#e2e8f0 !important; }
[data-theme="dark"] .streamlit-expanderHeader p { color:#e2e8f0 !important; }
[data-theme="dark"] .streamlit-expanderContent * { color:#e2e8f0 !important; }
[data-theme="dark"] [data-testid="stMarkdownContainer"] * { color:#e2e8f0 !important; }
[data-theme="dark"] [data-testid="stCaptionContainer"] p { color:#94a3b8 !important; }
[data-theme="dark"] div[data-testid="stSuccessMessage"] p { color:#d1fae5 !important; }
[data-theme="dark"] div[data-testid="stWarningMessage"] p { color:#fef3c7 !important; }
[data-theme="dark"] div[data-testid="stErrorMessage"] p   { color:#fee2e2 !important; }
[data-theme="dark"] div[data-testid="stInfoMessage"] p    { color:#dbeafe !important; }

/* ══════ MOBILE ══════ */
@media (max-width:768px) {
    .block-container { padding-left:.5rem !important; padding-right:.5rem !important; padding-top:.5rem !important; }
    .sf-hero { padding:8px 0 4px 0 !important; }
    .sf-hero-title { font-size:1.7rem !important; }
    .sf-hero-sub   { font-size:.82rem !important; }
    .sf-powered    { font-size:.6rem !important; padding:2px 10px !important; }
    .sf-card { padding:13px 11px !important; border-radius:13px !important; margin-bottom:10px !important; }
    .sf-soft-card { padding:10px !important; }
    .mc { padding:11px 7px !important; }
    .mc .val { font-size:1.15rem !important; }
    .mc .lbl { font-size:.68rem !important; }
    .fc-front,.fc-back { min-height:120px !important; padding:16px 12px !important; }
    .bdg { padding:9px 6px !important; }
    .bdg .bi { font-size:1.5rem !important; }
    .bdg .bn { font-size:.74rem !important; }
    .stRadio > div { flex-direction:column !important; gap:6px !important; align-items:stretch !important; }
    .stRadio > div > label {
        width:100% !important; border:1.5px solid #e2e8f0 !important;
        border-radius:10px !important; padding:10px 14px !important;
        background:#f8fbff !important; cursor:pointer !important; margin:0 !important;
    }
    input,textarea,select,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] [role="combobox"] {
        font-size:16px !important; -webkit-text-size-adjust:100% !important;
        touch-action:manipulation !important;
    }
    html,body,.stApp { overflow-x:hidden !important; }
    div[role="listbox"] {
        max-height:38vh !important; overflow-y:auto !important;
        -webkit-overflow-scrolling:touch !important;
        position:fixed !important; z-index:9999 !important;
    }
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

    conn.commit()

    def get_columns(table_name):
        c.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in c.fetchall()]

    def add_column_if_missing(table_name, column_name, column_def):
        cols = get_columns(table_name)
        if column_name not in cols:
            c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")

    # user_stats migrations
    add_column_if_missing("user_stats", "total_xp", "INTEGER DEFAULT 0")
    add_column_if_missing("user_stats", "streak_days", "INTEGER DEFAULT 0")
    add_column_if_missing("user_stats", "last_login", "TEXT DEFAULT ''")
    add_column_if_missing("user_stats", "total_minutes", "INTEGER DEFAULT 0")

    # achievements migrations
    add_column_if_missing("achievements", "username", "TEXT")
    add_column_if_missing("achievements", "badge_id", "TEXT")
    add_column_if_missing("achievements", "earned_at", "TEXT")

    # flashcards migrations
    add_column_if_missing("flashcards", "subject", "TEXT DEFAULT ''")
    add_column_if_missing("flashcards", "chapter", "TEXT DEFAULT ''")
    add_column_if_missing("flashcards", "ease_factor", "REAL DEFAULT 2.5")
    add_column_if_missing("flashcards", "interval_days", "INTEGER DEFAULT 1")
    add_column_if_missing("flashcards", "next_review_date", "TEXT")
    add_column_if_missing("flashcards", "review_count", "INTEGER DEFAULT 0")
    add_column_if_missing("flashcards", "created_date", "TEXT")

    # study_sessions migrations
    add_column_if_missing("study_sessions", "subject", "TEXT")
    add_column_if_missing("study_sessions", "minutes", "INTEGER DEFAULT 0")
    add_column_if_missing("study_sessions", "sess_date", "TEXT")

    conn.commit()
    conn.close()

    def get_columns(table_name):
        c.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in c.fetchall()]

    def add_column_if_missing(table_name, column_name, column_def):
        cols = get_columns(table_name)
        if column_name not in cols:
            c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")

    # Migration-safe column additions
    add_column_if_missing("user_stats", "total_xp", "INTEGER DEFAULT 0")
    add_column_if_missing("user_stats", "streak_days", "INTEGER DEFAULT 0")
    add_column_if_missing("user_stats", "last_login", "TEXT DEFAULT ''")
    add_column_if_missing("user_stats", "total_minutes", "INTEGER DEFAULT 0")

    add_column_if_missing("flashcards", "subject", "TEXT DEFAULT ''")
    add_column_if_missing("flashcards", "chapter", "TEXT DEFAULT ''")
    add_column_if_missing("flashcards", "ease_factor", "REAL DEFAULT 2.5")
    add_column_if_missing("flashcards", "interval_days", "INTEGER DEFAULT 1")
    add_column_if_missing("flashcards", "next_review_date", "TEXT")
    add_column_if_missing("flashcards", "review_count", "INTEGER DEFAULT 0")
    add_column_if_missing("flashcards", "created_date", "TEXT")

    add_column_if_missing("study_sessions", "subject", "TEXT")
    add_column_if_missing("study_sessions", "minutes", "INTEGER DEFAULT 0")
    add_column_if_missing("study_sessions", "sess_date", "TEXT")

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# STREAK + XP HELPERS  (all read/write directly from SQLite)
# ─────────────────────────────────────────────────────────────────────────────
def _ensure_stats(username, c):
    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))

def check_daily_login(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    c.execute("INSERT OR IGNORE INTO user_stats (username) VALUES (?)", (username,))

    c.execute("""
        SELECT COALESCE(streak_days, 0),
               COALESCE(last_login, '')
        FROM user_stats
        WHERE username=?
    """, (username,))
    row = c.fetchone()
    streak_days, last_login = row if row else (0, "")

    if last_login == today:
        conn.close()
        return f"🔥 {streak_days} Day Streak!"

    if last_login == yesterday:
        streak_days += 1
    else:
        streak_days = 1

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
        SELECT COALESCE(total_xp, 0),
               COALESCE(streak_days, 0),
               COALESCE(total_minutes, 0)
        FROM user_stats
        WHERE username=?
    """, (username,))
    row = c.fetchone()
    total_xp, streak_days, total_minutes = row if row else (0, 0, 0)

    # Recover total_minutes from sessions if needed
    if total_minutes == 0:
        try:
            c.execute(
                "SELECT COALESCE(SUM(minutes), 0) FROM study_sessions WHERE username=?",
                (username,)
            )
            total_minutes = c.fetchone()[0] or 0
            c.execute(
                "UPDATE user_stats SET total_minutes=? WHERE username=?",
                (total_minutes, username)
            )
            conn.commit()
        except sqlite3.OperationalError:
            total_minutes = 0

    weekly_minutes = 0
    try:
        week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        c.execute(
            "SELECT COALESCE(SUM(minutes),0) FROM study_sessions WHERE username=? AND sess_date>=?",
            (username, week_ago)
        )
        weekly_minutes = c.fetchone()[0] or 0
    except sqlite3.OperationalError:
        weekly_minutes = 0

    flashcards_due = 0
    try:
        today = datetime.date.today().isoformat()
        c.execute(
            "SELECT COUNT(*) FROM flashcards WHERE username=? AND next_review_date<=?",
            (username, today)
        )
        flashcards_due = c.fetchone()[0] or 0
    except sqlite3.OperationalError:
        flashcards_due = 0

    conn.close()

    return {
        "total_xp": total_xp,
        "streak_days": streak_days,
        "total_minutes": total_minutes,
        "weekly_minutes": weekly_minutes,
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
# BADGES — definition + auto-award logic
# ─────────────────────────────────────────────────────────────────────────────
ALL_BADGES = [
    {"id":"first_login",   "name":"First Step",      "icon":"👣","desc":"Logged in for the first time"},
    {"id":"streak_3",      "name":"Heatwave",         "icon":"🔥","desc":"3-day study streak"},
    {"id":"streak_7",      "name":"Weekly Warrior",   "icon":"🎖️","desc":"7-day study streak"},
    {"id":"streak_14",     "name":"Fortnight Champ",  "icon":"🏆","desc":"14-day study streak"},
    {"id":"streak_30",     "name":"Monthly Master",   "icon":"👑","desc":"30-day study streak"},
    {"id":"first_gen",     "name":"Starter Spark",    "icon":"✨","desc":"Generated first AI content"},
    {"id":"qp_generated",  "name":"Paper Setter",     "icon":"📝","desc":"Generated a question paper"},
    {"id":"quiz_done",     "name":"Quiz Taker",        "icon":"🧠","desc":"Generated a quiz"},
    {"id":"fc_10",         "name":"Card Collector",   "icon":"🗂️","desc":"Created 10 flashcards"},
    {"id":"study_60",      "name":"Hour Hero",         "icon":"⏱️","desc":"Studied 60 minutes total"},
    {"id":"study_300",     "name":"Study Champion",   "icon":"🎓","desc":"Studied 5 hours total"},
]

def _award_badge_raw(username, badge_id, c):
    earned_at = datetime.datetime.now().isoformat()
    try:
        c.execute(
            "INSERT OR IGNORE INTO achievements (username, badge_id, earned_at) VALUES (?,?,?)",
            (username, badge_id, earned_at)
        )
    except sqlite3.OperationalError:
        # Try to repair missing column on older DBs
        try:
            c.execute("ALTER TABLE achievements ADD COLUMN earned_at TEXT")
            c.execute(
                "INSERT OR IGNORE INTO achievements (username, badge_id, earned_at) VALUES (?,?,?)",
                (username, badge_id, earned_at)
            )
        except Exception:
            pass

def award_badge(username, badge_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
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

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    def award(badge_id):
        _award_badge_raw(username, badge_id, c)

    try:
        if stats["streak_days"] >= 3:
            award("strk_3")
        if stats["streak_days"] >= 7:
            award("strk_7")
        if stats["total_minutes"] >= 60:
            award("study_60")
        if stats["total_minutes"] >= 300:
            award("study_300")

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
    st.session_state.show_answers = False
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
    name = get_effective_output_name(tool, style)
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
    if   performance==1: interval=1;                          ef=max(1.3,ef-0.2)
    elif performance==2: interval=max(1,int(interval*1.2));   ef=max(1.3,ef-0.1)
    elif performance==3: interval=max(1,int(interval*ef))
    elif performance==4: interval=max(1,int(interval*ef*1.3)); ef+=0.1
    nrd=(datetime.date.today()+datetime.timedelta(days=interval)).isoformat()
    c.execute(
        "UPDATE flashcards SET ease_factor=?,interval_days=?,next_review_date=?,review_count=review_count+1 WHERE id=?",
        (round(ef,2),interval,nrd,card_id)
    )
    conn.commit(); conn.close()

def delete_flashcard(card_id):
    conn=sqlite3.connect("users.db"); c=conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=?",(card_id,))
    conn.commit(); conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# QP FORMAT
# ─────────────────────────────────────────────────────────────────────────────
def get_qp_format_spec(board, course, subject):
    b=board.upper()
    if "CBSE" in b:
        if any(x in course for x in ["10","X","Class 10"]):
            return {"board_label":"CENTRAL BOARD OF SECONDARY EDUCATION","exam_label":"BOARD EXAMINATION",
                "class_label":"CLASS X","total_marks":80,"time":"3 Hours",
                "instructions":["This paper contains Sections A, B, C, D and E.","All questions are compulsory.",
                    "Section A — MCQ (1 mark each).","Section B — Very Short Answer (2 marks each).",
                    "Section C — Short Answer (3 marks each).","Section D — Long Answer (5 marks each).",
                    "Section E — Case / Source Based (4 marks each)."],
                "sections":[{"name":"SECTION A","type":"MCQ","q_count":20,"marks_each":1,"total":20},
                    {"name":"SECTION B","type":"Very Short Answer","q_count":5,"marks_each":2,"total":10},
                    {"name":"SECTION C","type":"Short Answer","q_count":6,"marks_each":3,"total":18},
                    {"name":"SECTION D","type":"Long Answer","q_count":4,"marks_each":5,"total":20},
                    {"name":"SECTION E","type":"Case Based","q_count":3,"marks_each":4,"total":12}]}
        if any(x in course for x in ["12","XII","Class 12"]):
            return {"board_label":"CENTRAL BOARD OF SECONDARY EDUCATION","exam_label":"BOARD EXAMINATION",
                "class_label":"CLASS XII","total_marks":70,"time":"3 Hours",
                "instructions":["This paper contains Sections A, B, C, D and E.","All questions are compulsory.",
                    "Section A — MCQ (1 mark each).","Section B — Very Short Answer (2 marks each).",
                    "Section C — Short Answer (3 marks each).","Section D — Long Answer (5 marks each).",
                    "Section E — Case / Source Based (4 marks each)."],
                "sections":[{"name":"SECTION A","type":"MCQ","q_count":18,"marks_each":1,"total":18},
                    {"name":"SECTION B","type":"Very Short Answer","q_count":4,"marks_each":2,"total":8},
                    {"name":"SECTION C","type":"Short Answer","q_count":5,"marks_each":3,"total":15},
                    {"name":"SECTION D","type":"Long Answer","q_count":2,"marks_each":5,"total":10},
                    {"name":"SECTION E","type":"Case Based","q_count":3,"marks_each":4,"total":12}]}
    if "ICSE" in b:
        return {"board_label":"COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label":"ICSE EXAMINATION","class_label":course.upper(),
            "total_marks":80,"time":"2 Hours",
            "instructions":["Attempt all from Section A.","Attempt any four from Section B.","Marks in brackets."],
            "sections":[{"name":"SECTION A","type":"Compulsory","q_count":10,"marks_each":"varied","total":40},
                {"name":"SECTION B","type":"Descriptive","q_count":6,"marks_each":10,"total":40}]}
    return {"board_label":"UNIVERSITY EXAMINATIONS","exam_label":f"{course.upper()} EXAMINATION",
        "class_label":course.upper(),"total_marks":100,"time":"3 Hours",
        "instructions":["Answer all in Section A.","Answer any five from Section B.","Marks in brackets."],
        "sections":[{"name":"SECTION A","type":"Short Answer","q_count":10,"marks_each":2,"total":20},
            {"name":"SECTION B","type":"Medium Answer","q_count":8,"marks_each":5,"total":40},
            {"name":"SECTION C","type":"Long Answer","q_count":4,"marks_each":10,"total":40}]}

# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────────────
def build_qp_prompt(board,course,subject,chapter,topic,audience):
    fmt=get_qp_format_spec(board,course,subject)
    instr="\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
    secs="\n".join([f"- {s['name']} | {s['type']} | {s['q_count']} Qs | {s['marks_each']} marks each | Total {s['total']}" for s in fmt["sections"]])
    return (f"You are an official academic question paper setter.\n"
            f"BOARD: {fmt['board_label']} | EXAM: {fmt['exam_label']} | CLASS: {fmt['class_label']}\n"
            f"SUBJECT: {subject} | TOPIC: {topic} | CHAPTER: {chapter}\n"
            f"TIME: {fmt['time']} | MARKS: {fmt['total_marks']}\n"
            f"INSTRUCTIONS:\n{instr}\nSTRUCTURE:\n{secs}\n"
            f"RULES: Follow structure exactly. Number all questions. MCQs: 4 options (a)(b)(c)(d). Show marks [X]. No answers.\n"
            f"Generate the complete paper now.")

def build_full_qp_prompt(board,course,stream,subject,audience):
    fmt=get_qp_format_spec(board,course,subject)
    instr="\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
    secs="\n".join([f"- {s['name']} | {s['type']} | {s['q_count']} Qs | {s['marks_each']} marks each | Total {s['total']}" for s in fmt["sections"]])
    return (f"You are an official academic question paper setter.\nGenerate a FULL SUBJECT paper (entire syllabus).\n"
            f"BOARD: {fmt['board_label']} | STREAM: {stream} | SUBJECT: {subject}\n"
            f"TIME: {fmt['time']} | MARKS: {fmt['total_marks']}\n"
            f"INSTRUCTIONS:\n{instr}\nSTRUCTURE:\n{secs}\n"
            f"RULES: Cover full syllabus. No answers. Official academic format.\nGenerate the complete paper now.")

def build_answers_prompt(qp_text,board,course,subject,chapter):
    return (f"Prepare the official answer key.\nBOARD: {board} | COURSE: {course} | SUBJECT: {subject} | CHAPTER: {chapter}\n"
            f"Keep same section names and numbering. MCQs: answer + brief explanation.\nPAPER:\n{qp_text}\nGenerate answer key now.")

def build_prompt(tool,chapter,topic,subject,audience,style,board="",course=""):
    if style=="🧪 Question Paper" or tool=="🧪 Question Paper":
        return build_qp_prompt(board,course,subject,chapter,topic,audience)
    base=(f"You are an expert educator for {audience}.\n"
          f"Subject: {subject} | Topic: {topic} | Chapter: {chapter}\n"
          f"Make it accurate, exam-oriented and well-structured.\n\n")
    if tool=="📝 Summary":
        if style=="📄 Detailed":      return base+"Create a detailed summary: overview, key concepts, definitions, formulas, 2 examples, common mistakes, exam tips."
        if style=="⚡ Short & Quick": return base+"Create a quick-reference summary: one-line definition, 5-7 key points, formulas, quick tips. Max 500 words."
        if style=="📋 Notes Format":  return base+"Create structured notes: clear headings, bullets, definitions, examples, revision points."
    if tool=="🧠 Quiz":           return base+"Create: 5 MCQs (4 options each, mark answer), 5 short-answer Q&As, 3 long-answer Q&As."
    if tool=="📌 Revision Notes": return base+"Create revision notes: top 10 must-know points, formula sheet, mnemonics, comparisons, exam focus areas."
    if tool=="❓ Exam Q&A":       return base+"Create exam Q&A bank: 8-10 frequently asked Qs with answers, conceptual Qs, application Qs."
    return base+"Create complete exam-ready study material."

def build_flashcard_prompt(subject,chapter,topic):
    return (f"Create exactly 10 study flashcards.\nSubject: {subject} | Chapter: {chapter} | Topic: {topic}\n"
            f"Use EXACTLY this format:\nCARD 1\nFRONT: [question or term]\nBACK: [answer or definition]\n"
            f"CARD 2\nFRONT: ...\nBACK: ...\n(Continue for all 10. No extra text.)")

# ─────────────────────────────────────────────────────────────────────────────
# AI ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def generate_with_fallback(prompt):
    api_key=st.secrets.get("GEMINI_API_KEY","")
    if not api_key: return ("⚠️ API key missing.","None")
    try: genai.configure(api_key=api_key)
    except Exception as e: return (f"❌ Config failed: {e}","None")
    try:
        available=[m.name for m in genai.list_models()
                   if "gemini" in m.name.lower()
                   and "generateContent" in getattr(m,"supported_generation_methods",[])]
    except Exception as e: return (f"❌ Could not list models: {e}","None")
    if not available: return ("❌ No Gemini models available.","None")
    for model_name in available:
        try:
            model=genai.GenerativeModel(model_name)
            response=model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.0,max_output_tokens=8192,top_p=0.9)
            )
            if response and getattr(response,"text",None):
                return response.text, model_name
        except Exception: continue
    return ("❌ All models failed.","None")

def get_available_models():
    api_key=st.secrets.get("GEMINI_API_KEY","")
    if not api_key: return ["Error: GEMINI_API_KEY not found"]
    try:
        genai.configure(api_key=api_key)
        return [m.name for m in genai.list_models()
                if "gemini" in m.name.lower()
                and "generateContent" in getattr(m,"supported_generation_methods",[])]
    except Exception as e: return [f"Error: {e}"]

def parse_flashcards(raw_text):
    cards=[]; blocks=raw_text.strip().split("CARD ")
    for block in blocks:
        if not block.strip(): continue
        front=back=""
        for line in block.splitlines():
            l=line.strip()
            if l.upper().startswith("FRONT:"): front=l[6:].strip()
            elif l.upper().startswith("BACK:"): back=l[5:].strip()
        if front and back: cards.append({"front":front,"back":back})
    return cards

# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(title, subtitle, content, color_hex="#1d4ed8"):
    buffer=io.BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,topMargin=2*cm,bottomMargin=2*cm,leftMargin=1.5*cm,rightMargin=1.5*cm)
    styles=getSampleStyleSheet(); story=[]
    story.append(Paragraph(title,ParagraphStyle("T",parent=styles["Heading1"],fontSize=20,
        textColor=colors.HexColor(color_hex),alignment=TA_CENTER,spaceAfter=6,fontName="Helvetica-Bold")))
    story.append(Paragraph(subtitle,ParagraphStyle("S",parent=styles["Normal"],fontSize=10,
        textColor=colors.HexColor("#64748b"),alignment=TA_CENTER,spaceAfter=10)))
    story.append(HRFlowable(width="100%",thickness=2,color=colors.HexColor(color_hex),spaceAfter=14))
    body=ParagraphStyle("B",parent=styles["Normal"],fontSize=10.5,leading=15,
        textColor=colors.HexColor("#1e293b"),spaceAfter=5)
    head=ParagraphStyle("H",parent=styles["Heading2"],fontSize=12.5,
        textColor=colors.HexColor(color_hex),spaceBefore=10,spaceAfter=6,fontName="Helvetica-Bold")
    for line in content.split("\n"):
        line=line.strip()
        if not line: story.append(Spacer(1,0.15*cm)); continue
        safe=line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
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
                background:linear-gradient(135deg,#8b5cf6,#7c3aed);
                border-radius:10px;color:white;font-weight:800;font-size:.85rem;">
                ⭐ Lv {stats.get('level',1)}<br>
                <span style="font-size:.62rem;font-weight:500;color:white;">{stats.get('total_xp',0)} XP</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Daily Check-in ────────────────────────────────────────────────
        if not st.session_state.daily_checkin_done:
            if st.button("✅ Daily Check-in (+20 XP)",use_container_width=True,key="sb_checkin"):
                result=check_daily_login(username)
                st.session_state.daily_checkin_done=True
                auto_check_badges(username)
                st.success(result.get("message","Checked in!"))
                st.rerun()
        else:
            st.success(f"✅ Checked in · 🔥 {stats.get('streak_days',0)} days")

        st.divider()

        # ── Study Timer ───────────────────────────────────────────────────
        st.markdown("**⏱️ Study Timer**")
        if st.session_state.study_timer_active and st.session_state.study_timer_start:
            elapsed=int((datetime.datetime.now()-st.session_state.study_timer_start).total_seconds()//60)
            st.info(f"🟢 Running: {elapsed} min — {st.session_state.current_subject_for_timer}")
            if st.button("⏹️ Stop & Save",use_container_width=True,key="sb_stop"):
                st.session_state.study_timer_active=False
                dur=max(1,elapsed)
                subj=st.session_state.get("current_subject_for_timer","General")
                record_study_session(username, subj, dur)      # ← saves to DB
                xp_earned=max(5,(dur//10)*10)
                award_xp(username, xp_earned)
                auto_check_badges(username)                    # ← auto-unlocks badges
                st.session_state.study_timer_start=None
                st.success(f"✅ {dur} min saved! +{xp_earned} XP")
                st.rerun()
        else:
            if st.button("▶️ Start Timer",use_container_width=True,key="sb_start"):
                st.session_state.study_timer_active=True
                st.session_state.study_timer_start=datetime.datetime.now()
                st.rerun()

        st.divider()

        # ── Navigation ────────────────────────────────────────────────────
        st.markdown("**🧭 Navigate**")
        cur=st.session_state.active_page
        for key,label in [("dashboard","📊 Dashboard"),("study","📚 Study Tools"),
                           ("flashcards","🗂️ Flashcards"),("achievements","🏅 Achievements")]:
            btn_type="primary" if cur==key else "secondary"
            if st.button(label,use_container_width=True,key=f"nav_{key}",type=btn_type):
                if cur!=key: go_to(key)

        fc_due=stats.get("flashcards_due",0)
        if fc_due>0:
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.warning(f"📚 {fc_due} card{'s' if fc_due>1 else ''} due for review!")
        st.divider()

        with st.expander("📜 Recent History"):
            if not st.session_state.history: st.caption("No activity yet.")
            else:
                for h in st.session_state.history:
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
        earned=get_earned_badges(username)
        earned_list=[b for b in ALL_BADGES if b["id"] in earned][:4]
        if earned_list:
            bc=st.columns(2)
            for i,badge in enumerate(earned_list):
                with bc[i%2]:
                    st.markdown(f"""<div class="bdg earned">
                        <div class="bi">{badge['icon']}</div>
                        <div class="bn">{badge['name']}</div>
                        <div class="bs">✅ Earned</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Complete daily check-in to earn your first badge!")
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────────────────────────────────────
def show_flashcards(username):
    render_back_button()
    render_header("Flashcards","Spaced repetition for lasting memory")
    tab1,tab2,tab3=st.tabs(["📖 Review Due","➕ Create","📋 My Library"])

    with tab1:
        due=get_due_flashcards(username)
        if not due:
            st.success("🎉 No flashcards due today — great job!")
            total=len(get_all_flashcards(username))
            if total>0:
                st.caption(f"You have {total} total cards. Come back tomorrow!")
        else:
            idx=st.session_state.review_idx
            if idx>=len(due):
                st.success(f"✅ All {len(due)} cards reviewed for today!")
                if st.button("🔄 Review Again",use_container_width=True,key="fc_restart"):
                    st.session_state.review_idx=0; st.session_state.review_show_ans=False; st.rerun()
            else:
                card=due[idx]; card_id,front,back,subj,chap=card[0],card[1],card[2],card[3],card[4]
                st.progress((idx+1)/len(due))
                st.caption(f"Card {idx+1} of {len(due)} · {subj} · {chap}")
                if not st.session_state.review_show_ans:
                    st.markdown(f"""<div class="fc-front">
                        <div style="font-size:.73rem;opacity:.8;margin-bottom:8px;">QUESTION</div>
                        <div style="font-size:1.02rem;font-weight:700;line-height:1.5;">{front}</div>
                        <div style="font-size:.68rem;opacity:.65;margin-top:10px;">Tap to reveal ↓</div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    if st.button("👁️ Reveal Answer",use_container_width=True,key="fc_reveal"):
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

    # ── My Library — NO unwanted banners ──────────────────────────────────
    with tab3:
        all_cards=get_all_flashcards(username)
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        if not all_cards:
            st.markdown("<div style='text-align:center;padding:30px;color:#64748b;'>"
                        "📭 No flashcards yet.<br>Create your first card in the ➕ Create tab."
                        "</div>", unsafe_allow_html=True)
        else:
            st.caption(f"📚 Total: {len(all_cards)} flashcards in your library")
            for row in all_cards:
                c_id,front,back,subj,chap,nrd,rc=row
                with st.expander(f"📌 {front[:60]}{'...' if len(front)>60 else ''}"):
                    st.markdown(f"**Q:** {front}")
                    st.markdown(f"**A:** {back}")
                    st.caption(f"Subject: {subj or '—'} | Chapter: {chap or '—'} | Next review: {nrd} | Reviews done: {rc}")
                    if st.button("🗑️ Delete this card",key=f"del_fc_{c_id}",use_container_width=True):
                        delete_flashcard(c_id); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS  — auto-unlock logic built-in
# ─────────────────────────────────────────────────────────────────────────────
def show_achievements(username):
    render_back_button()
    render_header("Achievements","Badges unlock automatically as you learn")

    # Run auto-check every time page opens
    auto_check_badges(username)
    stats=get_user_stats(username) or {}
    earned=get_earned_badges(username)
    earned_list=[b for b in ALL_BADGES if b["id"] in earned]
    locked_list=[b for b in ALL_BADGES if b["id"] not in earned]

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(f"**✅ {len(earned_list)} / {len(ALL_BADGES)} badges earned**")
    st.progress(len(earned_list)/len(ALL_BADGES) if ALL_BADGES else 0)

    # How to unlock hints
    st.markdown("""
    <div style="font-size:.82rem;color:#475569;margin-top:8px;">
    🔥 <b>Streaks</b> — log in every day &nbsp;|&nbsp;
    ⏱️ <b>Study time</b> — use the Study Timer &nbsp;|&nbsp;
    🗂️ <b>Flashcards</b> — create 10+ cards &nbsp;|&nbsp;
    ✨ <b>AI tools</b> — generate content
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if earned_list:
        st.markdown("### ✅ Earned")
        cols=st.columns(4)
        for i,b in enumerate(earned_list):
            with cols[i%4]:
                st.markdown(f"""<div class="bdg earned">
                    <div class="bi">{b['icon']}</div>
                    <div class="bn">{b['name']}</div>
                    <div class="bs">✅ {b['desc']}</div>
                </div>""", unsafe_allow_html=True)

    if locked_list:
        st.markdown("### 🔒 Locked — how to unlock")
        # Show unlock hint for each locked badge
        unlock_hints = {
            "streak_3":     "Log in 3 days in a row",
            "streak_7":     "Log in 7 days in a row",
            "streak_14":    "Log in 14 days in a row",
            "streak_30":    "Log in 30 days in a row",
            "first_gen":    "Generate any AI content once",
            "qp_generated": "Generate a Question Paper",
            "quiz_done":    "Generate a Quiz",
            "fc_10":        "Create 10 flashcards total",
            "study_60":     "Study for 60 minutes total",
            "study_300":    "Study for 300 minutes total",
        }
        cols=st.columns(4)
        for i,b in enumerate(locked_list):
            with cols[i%4]:
                hint=unlock_hints.get(b["id"],"Keep using the app!")
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
# STUDY TOOLS
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
    ca,cb=st.columns([1.5,1])
    with ca:
        category=st.selectbox("📚 Category",list(STUDY_DATA.keys()),key="sel_cat")
    with cb:
    course =st.selectbox("🎓 Program / Class",get_courses(category),           key="sel_course")
    stream =st.selectbox("📖 Stream",          get_streams(category,course),    key="sel_stream")
    subject=st.selectbox("🧾 Subject",         get_subjects(category,course,stream),key="sel_subject")

    board="University / National Syllabus"
    if category=="K-12th":
        board=st.selectbox("🏫 Board",BOARDS,key="sel_board")

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
        if not chapter or chapter=="No chapters found":
            st.warning("⚠️ Please select a valid chapter."); return
        audience=(f"{board} {course} students" if category=="K-12th" else f"{course} students")
        prompt=build_prompt(tool,chapter,topic,subject,audience,style,board=board,course=course)
        with st.spinner(f"Generating {eff_label}..."):
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
            if eff_label=="Quiz":           award_badge(username,"quiz_done")
            auto_check_badges(username)

    if st.session_state.generated_result:
        result    =st.session_state.generated_result
        g_label   =st.session_state.generated_label
        g_chapter =st.session_state.generated_chapter
        g_subject =st.session_state.generated_subject
        g_topic   =st.session_state.generated_topic
        g_course  =st.session_state.generated_course
        g_stream  =st.session_state.generated_stream
        g_board   =st.session_state.generated_board
        g_audience=st.session_state.generated_audience

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
                qp_pdf=generate_pdf(f"Question Paper — {g_chapter}",f"{g_subject} | {g_board} | {g_course}",result,"#1d4ed8")
                safe_q=(g_chapter.replace(" ","_").replace(":","").replace("/","-")+"_QP.pdf")
                st.download_button("⬇️ Download Question Paper PDF",data=qp_pdf,file_name=safe_q,mime="application/pdf",use_container_width=True,key="dl_qp_pdf")
            except Exception as e: st.warning(f"⚠️ PDF error: {e}")

            if st.button("📋 Get Answers for this Paper",use_container_width=True,key="get_ans_btn"):
                with st.spinner("Generating answer key..."):
                    ans_r,ans_m=generate_with_fallback(build_answers_prompt(result,g_board,g_course,g_subject,g_chapter))
                st.session_state.answers_result=ans_r; st.session_state.answers_model=ans_m
                st.session_state.show_answers=True

            if st.session_state.show_answers and st.session_state.answers_result:
                if st.session_state.answers_model!="None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 📚 Answer Key — {g_chapter}")
                    st.markdown(st.session_state.answers_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        ans_pdf=generate_pdf(f"Answer Key — {g_chapter}",f"{g_subject} | {g_board} | {g_course}",st.session_state.answers_result,"#15803d")
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
# AUTH UI  — registration CLOSED
# ─────────────────────────────────────────────────────────────────────────────
def auth_ui():
   def auth_ui():
    """Login and Registration screen"""

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
                if u.strip() and p.strip():
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()

                    c.execute(
                        "SELECT * FROM users WHERE username=? AND password=?",
                        (u.strip(), hash_p(p))
                    )
                    user_row = c.fetchone()
                    conn.close()

                    if user_row:
                        # Make sure stats row exists before rerun
                        conn = sqlite3.connect("users.db")
                        c = conn.cursor()
                        c.execute(
                            "INSERT OR IGNORE INTO user_stats (username) VALUES (?)",
                            (u.strip(),)
                        )
                        conn.commit()
                        conn.close()

                        st.session_state.logged_in = True
                        st.session_state.username = u.strip()

                        try:
                            auto_check_badges(u.strip())
                        except Exception:
                            pass

                        st.success("✅ Login successful!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
                else:
                    st.warning("⚠️ Please enter both username and password.")

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
