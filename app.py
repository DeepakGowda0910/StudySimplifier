# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — APP v3.1
# Fix: Full dark mode compatibility for all UI elements
# ═══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import io
import json
import time
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: LOAD STUDY DATA
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
# STEP 2: PAGE CONFIG & CSS (Dark Mode Safe)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ═══════════════════════════════════════════
   BASE — applies in BOTH light and dark mode
   ═══════════════════════════════════════════ */
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }

.sf-header {
    text-align: center;
    padding: 32px 0 10px 0;
}
.sf-header-title {
    font-size: 3.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}
.sf-header-subtitle {
    color: #64748b;
    font-weight: 500;
    margin-top: 8px;
    font-size: 1.05rem;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
}

/* ═══════════════════════════════════════════
   LIGHT MODE STYLES
   ═══════════════════════════════════════════ */

/* App background */
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e8f0f7 100%) !important;
}

/* Cards */
.sf-card {
    background: rgba(255,255,255,0.9) !important;
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid rgba(59,130,246,0.14);
    box-shadow: 0 4px 24px rgba(59,130,246,0.07);
    margin-bottom: 18px;
}

/* Output boxes */
.sf-output {
    background: rgba(239,246,255,0.7) !important;
    border-left: 5px solid #2563eb;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(59,130,246,0.2);
    margin-top: 14px;
    color: #1e293b !important;
}
.sf-output h3, .sf-output h2 { color: #1d4ed8 !important; margin-top: 0; }

.sf-answers {
    background: rgba(240,253,244,0.7) !important;
    border-left: 5px solid #16a34a;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(34,197,94,0.2);
    margin-top: 18px;
    color: #1e293b !important;
}
.sf-answers h3, .sf-answers h2 { color: #15803d !important; margin-top: 0; }

.sf-fullpaper {
    background: rgba(245,243,255,0.7) !important;
    border-left: 5px solid #7c3aed;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(139,92,246,0.2);
    margin-top: 18px;
    color: #1e293b !important;
}
.sf-fullpaper h3, .sf-fullpaper h2 { color: #6d28d9 !important; margin-top: 0; }

.sf-preview {
    background: rgba(248,250,252,0.9) !important;
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 14px;
    margin-bottom: 12px;
    color: #1e293b !important;
}

.sf-history-item {
    background: rgba(239,246,255,0.7);
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    font-size: 0.9rem;
    color: #1e293b !important;
}

/* ─── Radio buttons — LIGHT MODE ─── */
div[data-testid="stRadio"] label {
    color: #1e293b !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
}
div[data-testid="stRadio"] > label {
    color: #1e293b !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
}
div[data-testid="stRadio"] p {
    color: #1e293b !important;
    font-weight: 500 !important;
}

/* ─── All widget labels — LIGHT MODE ─── */
div.stSelectbox > label,
div.stTextInput > label,
div.stRadio > label,
[data-testid="stWidgetLabel"] {
    color: #1e293b !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

/* ─── Selectbox / dropdown — LIGHT MODE ─── */
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 1.5px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #1e293b !important;
}
div[data-baseweb="select"] span {
    color: #1e293b !important;
}
div[role="listbox"] li {
    color: #1e293b !important;
    background: #ffffff !important;
}

/* ─── Text inputs — LIGHT MODE ─── */
input[type="text"],
input[type="password"] {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
}
input::placeholder { color: #94a3b8 !important; }

/* ─── Sidebar — LIGHT MODE ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * { color: #1e293b !important; }
[data-testid="stSidebar"] .sf-history-item { color: #1e293b !important; }

/* ─── Metrics — LIGHT MODE ─── */
[data-testid="metric-container"] label,
[data-testid="metric-container"] div {
    color: #1e293b !important;
}

/* ─── Tabs — LIGHT MODE ─── */
.stTabs [data-baseweb="tab"] { color: #64748b !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { color: #0f172a !important; border-bottom: 3px solid #3b82f6 !important; }

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.3rem !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.25) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    box-shadow: 0 8px 25px rgba(59,130,246,0.4) !important;
    transform: translateY(-2px) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(16,185,129,0.25) !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 8px 25px rgba(16,185,129,0.4) !important;
    transform: translateY(-2px) !important;
}

/* ─── Alert banners ─── */
div[data-testid="stSuccessMessage"] {
    background: rgba(16,185,129,0.1) !important;
    border: 1.5px solid rgba(16,185,129,0.35) !important;
    border-radius: 10px !important;
}
div[data-testid="stWarningMessage"] {
    background: rgba(245,158,11,0.1) !important;
    border: 1.5px solid rgba(245,158,11,0.35) !important;
    border-radius: 10px !important;
}
div[data-testid="stErrorMessage"] {
    background: rgba(239,68,68,0.1) !important;
    border: 1.5px solid rgba(239,68,68,0.35) !important;
    border-radius: 10px !important;
}

/* ═══════════════════════════════════════════════════════════════════
   DARK MODE OVERRIDES
   These fire when the OS / browser is in dark mode.
   Every color that was hardcoded for light is now flipped here.
   ═══════════════════════════════════════════════════════════════════ */
@media (prefers-color-scheme: dark) {

    /* App background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%) !important;
    }

    /* Main body text */
    .stApp, .stApp p, .stApp span, .stApp div {
        color: #e2e8f0 !important;
    }

    /* Cards */
    .sf-card {
        background: rgba(30,41,59,0.95) !important;
        border: 1px solid rgba(99,179,237,0.18) !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35) !important;
    }

    /* Output boxes */
    .sf-output {
        background: rgba(30,58,138,0.18) !important;
        border: 1px solid rgba(96,165,250,0.25) !important;
        color: #e2e8f0 !important;
    }
    .sf-output h3, .sf-output h2, .sf-output h1 { color: #93c5fd !important; }
    .sf-output p, .sf-output li, .sf-output span { color: #e2e8f0 !important; }

    .sf-answers {
        background: rgba(20,83,45,0.2) !important;
        border: 1px solid rgba(74,222,128,0.25) !important;
        color: #e2e8f0 !important;
    }
    .sf-answers h3, .sf-answers h2, .sf-answers h1 { color: #86efac !important; }
    .sf-answers p, .sf-answers li, .sf-answers span { color: #e2e8f0 !important; }

    .sf-fullpaper {
        background: rgba(76,29,149,0.18) !important;
        border: 1px solid rgba(196,181,253,0.25) !important;
        color: #e2e8f0 !important;
    }
    .sf-fullpaper h3, .sf-fullpaper h2, .sf-fullpaper h1 { color: #c4b5fd !important; }
    .sf-fullpaper p, .sf-fullpaper li, .sf-fullpaper span { color: #e2e8f0 !important; }

    .sf-preview {
        background: rgba(30,41,59,0.85) !important;
        border: 1px solid rgba(148,163,184,0.2) !important;
        color: #e2e8f0 !important;
    }
    .sf-preview p, .sf-preview span, .sf-preview li { color: #e2e8f0 !important; }
    .sf-preview strong { color: #93c5fd !important; }

    .sf-history-item {
        background: rgba(30,58,138,0.2) !important;
        border-left: 4px solid #60a5fa !important;
        color: #cbd5e1 !important;
    }
    .sf-history-item b { color: #93c5fd !important; }
    .sf-history-item small { color: #94a3b8 !important; }

    /* ─── Radio buttons — DARK MODE (THE MAIN FIX) ─── */
    div[data-testid="stRadio"] label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stRadio"] > label {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stRadio"] p {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    /* The actual option text nodes */
    [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        color: #e2e8f0 !important;
    }
    /* Radio circle */
    [data-testid="stRadio"] input[type="radio"] + div {
        border-color: #60a5fa !important;
    }
    [data-testid="stRadio"] input[type="radio"]:checked + div {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
    }

    /* ─── All widget labels — DARK MODE ─── */
    div.stSelectbox > label,
    div.stTextInput > label,
    div.stRadio > label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }

    /* ─── Selectbox / dropdown — DARK MODE ─── */
    div[data-baseweb="select"] > div {
        background: #1e293b !important;
        border: 1.5px solid #334155 !important;
        color: #e2e8f0 !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #e2e8f0 !important;
    }
    div[role="listbox"] {
        background: #1e293b !important;
    }
    div[role="listbox"] li,
    div[role="option"] {
        color: #e2e8f0 !important;
        background: #1e293b !important;
    }
    div[role="option"]:hover {
        background: #334155 !important;
    }

    /* ─── Text inputs — DARK MODE ─── */
    input[type="text"],
    input[type="password"] {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1.5px solid #334155 !important;
    }
    input::placeholder { color: #64748b !important; }

    /* ─── Sidebar — DARK MODE ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid #334155 !important;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .sf-history-item { color: #cbd5e1 !important; }

    /* ─── Metrics — DARK MODE ─── */
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] div {
        color: #e2e8f0 !important;
    }
    [data-testid="metric-container"] {
        background: rgba(30,41,59,0.7) !important;
        border-radius: 10px;
    }

    /* ─── Tabs — DARK MODE ─── */
    .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #f1f5f9 !important; border-bottom: 3px solid #60a5fa !important; }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #334155 !important; }

    /* ─── General markdown text — DARK MODE ─── */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #e2e8f0 !important;
    }

    /* ─── Alert banners — DARK MODE ─── */
    div[data-testid="stSuccessMessage"] {
        background: rgba(16,185,129,0.15) !important;
        color: #d1fae5 !important;
    }
    div[data-testid="stWarningMessage"] {
        background: rgba(245,158,11,0.15) !important;
        color: #fef3c7 !important;
    }
    div[data-testid="stErrorMessage"] {
        background: rgba(239,68,68,0.15) !important;
        color: #fee2e2 !important;
    }

    /* ─── Expanders — DARK MODE ─── */
    details {
        background: rgba(30,41,59,0.6) !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }
    details summary { color: #e2e8f0 !important; }

    /* ─── Divider ─── */
    hr { border-color: #334155 !important; }

    /* ─── Spinner text ─── */
    [data-testid="stSpinner"] p { color: #94a3b8 !important; }

    /* ─── Caption / small text ─── */
    .stCaption, small { color: #94a3b8 !important; }
}

/* ─── Mobile responsive ─── */
@media (max-width: 768px) {
    .sf-header-title { font-size: 2.5rem !important; }
    .sf-card, .sf-output, .sf-answers, .sf-fullpaper, .sf-preview { padding: 16px; }
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
}
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: BASIC HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_courses(category):
    try: return list(STUDY_DATA[category].keys())
    except KeyError: return []

def get_streams(category, course):
    try: return list(STUDY_DATA[category][course].keys())
    except KeyError: return []

def get_subjects(category, course, stream):
    try: return list(STUDY_DATA[category][course][stream].keys())
    except KeyError: return []

def get_topics(category, course, stream, subject):
    try: return list(STUDY_DATA[category][course][stream][subject].keys())
    except KeyError: return []

def get_chapters(category, course, stream, subject, topic):
    try: return STUDY_DATA[category][course][stream][subject][topic]
    except KeyError: return ["No chapters found"]

def hash_p(password):
    return hashlib.sha256(password.encode()).hexdigest()

def count_words(text):
    return len(text.split()) if text else 0

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
    st.session_state.history = st.session_state.history[:5]

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

def configure_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return False, "GEMINI_API_KEY not found in secrets"
    try:
        genai.configure(api_key=api_key)
        return True, "Configured"
    except Exception as e:
        return False, str(e)

def list_working_gemini_models():
    ok, msg = configure_gemini()
    if not ok:
        return [], msg
    try:
        models = genai.list_models()
        working = []
        for m in models:
            name = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "gemini" in name.lower() and "generateContent" in methods:
                working.append(name)
        return working, None
    except Exception as e:
        return [], str(e)

def get_available_models():
    working_models, err = list_working_gemini_models()
    if err: return [f"Error: {err}"]
    if not working_models: return ["No Gemini models available for this API key"]
    return working_models

def get_effective_output_name(tool, output_style):
    if output_style == "🧪 Question Paper":
        return "Question Paper"
    if tool == "📝 Summary":
        if output_style == "📋 Notes Format": return "Notes"
        if output_style == "📄 Detailed":     return "Detailed Summary"
        if output_style == "⚡ Short & Quick": return "Quick Summary"
        return "Summary"
    if tool == "🧠 Quiz":           return "Quiz"
    if tool == "📌 Revision Notes": return "Revision Notes"
    if tool == "🧪 Question Paper": return "Question Paper"
    if tool == "❓ Exam Q&A":       return "Exam Q&A"
    return "Content"

def get_generate_button_label(tool, output_style):
    return f"✨ Generate {get_effective_output_name(tool, output_style)}"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: QUESTION PAPER FORMAT SPECS
# ─────────────────────────────────────────────────────────────────────────────

def get_qp_format_spec(board, course, subject):
    b = board.upper()

    if "CBSE" in b:
        if any(x in course for x in ["10", "X", "Class 10"]):
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "BOARD EXAMINATION",
                "class_label": "CLASS X",
                "total_marks": 80, "time": "3 Hours",
                "instructions": [
                    "This paper has Sections A, B, C, D and E. All questions are compulsory.",
                    "Section A — MCQ/Objective (1 mark each).",
                    "Section B — Very Short Answer (2 marks each).",
                    "Section C — Short Answer (3 marks each).",
                    "Section D — Long Answer (5 marks each).",
                    "Section E — Case/Source Based (4 marks each).",
                    "Internal choices are provided in some questions.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ / Objective",   "q_count": 20, "marks_each": 1, "total": 20},
                    {"name": "SECTION B", "type": "Very Short Answer",  "q_count": 5,  "marks_each": 2, "total": 10},
                    {"name": "SECTION C", "type": "Short Answer",       "q_count": 6,  "marks_each": 3, "total": 18},
                    {"name": "SECTION D", "type": "Long Answer",        "q_count": 4,  "marks_each": 5, "total": 20},
                    {"name": "SECTION E", "type": "Case / Source Based","q_count": 3,  "marks_each": 4, "total": 12},
                ]
            }
        if any(x in course for x in ["12", "XII", "Class 12"]):
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "BOARD EXAMINATION",
                "class_label": "CLASS XII",
                "total_marks": 70, "time": "3 Hours",
                "instructions": [
                    "This paper has Sections A, B, C, D and E. All questions are compulsory.",
                    "Section A — MCQ/Objective (1 mark each).",
                    "Section B — Very Short Answer (2 marks each).",
                    "Section C — Short Answer (3 marks each).",
                    "Section D — Long Answer (5 marks each).",
                    "Section E — Case/Source Based (4 marks each).",
                    "Internal choices are provided in Sections B, C and D.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ / Objective",   "q_count": 18, "marks_each": 1, "total": 18},
                    {"name": "SECTION B", "type": "Very Short Answer",  "q_count": 4,  "marks_each": 2, "total": 8},
                    {"name": "SECTION C", "type": "Short Answer",       "q_count": 5,  "marks_each": 3, "total": 15},
                    {"name": "SECTION D", "type": "Long Answer",        "q_count": 2,  "marks_each": 5, "total": 10},
                    {"name": "SECTION E", "type": "Case / Source Based","q_count": 3,  "marks_each": 4, "total": 12},
                ]
            }
        return {
            "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
            "exam_label": "ANNUAL EXAMINATION", "class_label": course.upper(),
            "total_marks": 80, "time": "3 Hours",
            "instructions": ["All questions are compulsory.", "Read instructions on each section carefully."],
            "sections": [
                {"name": "SECTION A", "type": "Objective",       "q_count": 20, "marks_each": 1, "total": 20},
                {"name": "SECTION B", "type": "Short Answer I",  "q_count": 6,  "marks_each": 2, "total": 12},
                {"name": "SECTION C", "type": "Short Answer II", "q_count": 6,  "marks_each": 3, "total": 18},
                {"name": "SECTION D", "type": "Long Answer",     "q_count": 4,  "marks_each": 5, "total": 20},
            ]
        }

    if "ICSE" in b:
        return {
            "board_label": "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label": "ICSE EXAMINATION", "class_label": course.upper(),
            "total_marks": 80, "time": "2 Hours",
            "instructions": [
                "Attempt all questions from Section A.",
                "Attempt any four from Section B.",
                "Marks are in brackets [ ].",
            ],
            "sections": [
                {"name": "SECTION A", "type": "Compulsory Objective / Short Answer", "q_count": 10, "marks_each": "varied", "total": 40},
                {"name": "SECTION B", "type": "Descriptive (Attempt 4 of 6)",        "q_count": 6,  "marks_each": 10,       "total": 40},
            ]
        }

    if "ISC" in b:
        return {
            "board_label": "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label": "ISC EXAMINATION", "class_label": course.upper(),
            "total_marks": 70, "time": "3 Hours",
            "instructions": [
                "Attempt all questions from Section A.",
                "Attempt any four from Section B.",
                "Marks are in brackets [ ].",
                "Draw neat labelled diagrams wherever necessary.",
            ],
            "sections": [
                {"name": "SECTION A", "type": "Compulsory",              "q_count": 10, "marks_each": "varied", "total": 30},
                {"name": "SECTION B", "type": "Descriptive (4 of 6)",    "q_count": 6,  "marks_each": 10,       "total": 40},
            ]
        }

    if "IB" in b:
        return {
            "board_label": "INTERNATIONAL BACCALAUREATE",
            "exam_label": "FINAL EXAMINATION", "class_label": course.upper(),
            "total_marks": 100, "time": "2 Hours 30 Minutes",
            "instructions": ["Answer required questions.", "Show all reasoning where necessary."],
            "sections": [
                {"name": "SECTION A", "type": "Structured / Objective",  "q_count": 20, "marks_each": "varied", "total": 40},
                {"name": "SECTION B", "type": "Extended Response",       "q_count": 4,  "marks_each": 15,       "total": 60},
            ]
        }

    if "CAMBRIDGE" in b:
        return {
            "board_label": "CAMBRIDGE ASSESSMENT INTERNATIONAL EDUCATION",
            "exam_label": "INTERNATIONAL EXAMINATION", "class_label": course.upper(),
            "total_marks": 80, "time": "2 Hours",
            "instructions": ["Answer all questions as instructed.", "Show all working where required."],
            "sections": [
                {"name": "SECTION A", "type": "Structured Questions",   "q_count": 10, "marks_each": 4,  "total": 40},
                {"name": "SECTION B", "type": "Extended Response",      "q_count": 4,  "marks_each": 10, "total": 40},
            ]
        }

    if any(k in course.upper() for k in ["MBBS","BDS","MD","MEDICAL"]):
        return {
            "board_label": "UNIVERSITY EXAMINATIONS",
            "exam_label": f"{course.upper()} PROFESSIONAL EXAMINATION", "class_label": course.upper(),
            "total_marks": 100, "time": "3 Hours",
            "instructions": [
                "Answer all questions in Part A.",
                "Answer any five from Part B.",
                "Draw neat labelled diagrams wherever necessary.",
            ],
            "sections": [
                {"name": "PART A", "type": "Short Notes",   "q_count": 10, "marks_each": 5,  "total": 50},
                {"name": "PART B", "type": "Long Essays",   "q_count": 8,  "marks_each": 10, "total": 50},
            ]
        }

    return {
        "board_label": "UNIVERSITY EXAMINATIONS",
        "exam_label": f"{course.upper()} SEMESTER EXAMINATION", "class_label": course.upper(),
        "total_marks": 100, "time": "3 Hours",
        "instructions": [
            "Answer all questions in Section A.",
            "Answer any five from Section B.",
            "Marks are in brackets.",
        ],
        "sections": [
            {"name": "SECTION A", "type": "Short Answer",  "q_count": 10, "marks_each": 2,  "total": 20},
            {"name": "SECTION B", "type": "Medium Answer", "q_count": 8,  "marks_each": 5,  "total": 40},
            {"name": "SECTION C", "type": "Long Answer",   "q_count": 4,  "marks_each": 10, "total": 40},
        ]
    }


def render_qp_preview(board, course, subject):
    fmt = get_qp_format_spec(board, course, subject)
    lines = [
        f"**Board / Pattern:** {fmt['board_label']}",
        f"**Exam:** {fmt['exam_label']}",
        f"**Class / Course:** {fmt['class_label']}",
        f"**Time Allowed:** {fmt['time']}",
        f"**Maximum Marks:** {fmt['total_marks']}",
        "", "**Sections:**"
    ]
    for s in fmt["sections"]:
        lines.append(f"- **{s['name']}** — {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}")
    lines += ["", "**Instructions:**"]
    for ins in fmt["instructions"]:
        lines.append(f"- {ins}")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

def build_question_paper_prompt(board, course, subject, chapter, topic, audience):
    fmt = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i, x in enumerate(fmt["instructions"])])
    secs  = "\n".join([
        f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}"
        for s in fmt["sections"]
    ])
    return f"""
You are an official academic question paper setter.

Generate a CHAPTER-LEVEL question paper using the EXACT format below.

BOARD: {fmt['board_label']}
EXAM: {fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
SUBJECT: {subject}
TOPIC: {topic}
CHAPTER: {chapter}
TIME: {fmt['time']}
MAXIMUM MARKS: {fmt['total_marks']}

GENERAL INSTRUCTIONS (print in paper):
{instr}

SECTION STRUCTURE (follow exactly):
{secs}

RULES:
1. Follow the structure exactly — section names, question counts, mark distribution.
2. Print a proper academic header at the top.
3. Number all questions (Q1, Q2 ...).
4. MCQs must have exactly (a) (b) (c) (d). DO NOT mark the answer.
5. Show marks in square brackets [X marks].
6. Cover the chapter comprehensively.
7. Difficulty: 30% easy, 50% medium, 20% hard.
8. DO NOT include answers or hints.
9. Academic tone only.

Generate the complete question paper now.
"""

def build_full_subject_qp_prompt(board, course, stream, subject, audience):
    fmt = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i, x in enumerate(fmt["instructions"])])
    secs  = "\n".join([
        f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}"
        for s in fmt["sections"]
    ])
    return f"""
You are an official academic question paper setter.

Generate a FULL SUBJECT question paper covering the complete syllabus.

BOARD: {fmt['board_label']}
EXAM: {fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
STREAM: {stream}
SUBJECT: {subject}
TIME: {fmt['time']}
MAXIMUM MARKS: {fmt['total_marks']}

INSTRUCTIONS (print in paper):
{instr}

STRUCTURE (follow exactly):
{secs}

RULES:
1. Cover the FULL syllabus — not just one chapter.
2. Distribute questions across all major units.
3. Follow official format exactly.
4. Number all questions.
5. MCQs have 4 options (a)(b)(c)(d). No answers.
6. Show marks [X marks].
7. DO NOT include answers or hints.

Generate the complete full subject question paper now.
"""

def build_answers_prompt(question_paper_text, board, course, subject, chapter):
    return f"""
You are preparing the OFFICIAL ANSWER KEY for the EXACT question paper below.

BOARD: {board}   COURSE: {course}
SUBJECT: {subject}   CHAPTER: {chapter}

CRITICAL RULES:
1. Answer ONLY the questions in the paper below — do not invent new ones.
2. Keep the EXACT same section names and question numbers.
3. For each question write: question number → brief restatement → answer.
4. MCQs: state the correct option letter and explain briefly (2-3 lines).
5. Very Short Answer: 2-3 concise lines.
6. Short Answer: 4-6 lines with key points.
7. Long Answer: 150-250 words with examples.
8. Case-Based: full analysis with answers to each sub-question.
9. If OR choices exist, answer BOTH alternatives.
10. DO NOT generate a new question paper — only answer the one given below.

===== QUESTION PAPER (answer these exact questions) =====
{question_paper_text}
===== END OF PAPER =====

Generate the answer key now, following the same section and question order.
"""

def build_prompt(tool, chapter, topic, subject, audience, output_style, board="", course=""):
    """Output Style Question Paper always takes priority over tool selection."""
    base = f"""
You are an expert educator creating study material for {audience}.
Subject: {subject} | Topic: {topic} | Chapter: {chapter}
Requirements: Accurate, exam-focused, well-structured, with examples, and error-free.
"""
    if output_style == "🧪 Question Paper" or tool == "🧪 Question Paper":
        return build_question_paper_prompt(board, course, subject, chapter, topic, audience)

    if tool == "📝 Summary":
        if output_style == "📄 Detailed":
            return base + """
Create a detailed summary with:
- Chapter overview (150-200 words)
- Key concepts (300-400 words)
- Important definitions
- Worked examples
- Common mistakes to avoid
- Exam tips
"""
        elif output_style == "⚡ Short & Quick":
            return base + """
Create a concise quick-reference guide (max 500 words):
- One-line definition
- 5-7 key points
- Important formulas / facts
- Quick revision tips
"""
        elif output_style == "📋 Notes Format":
            return base + """
Create structured study notes:
- Headings and subheadings
- Bullet points
- Definitions highlighted
- Important facts boxed
- Examples
- Revision points
"""

    if tool == "🧠 Quiz":
        return base + """
Create a quiz:
- 5 MCQs with 4 options each (mark correct answer)
- 5 short questions with answers
- 3 long questions with answers
"""

    if tool == "📌 Revision Notes":
        return base + """
Create revision notes:
- Top 10 must-know points
- Formula / fact sheet
- Mnemonics
- Key comparisons
- Exam focus areas
"""

    if tool == "❓ Exam Q&A":
        return base + """
Create an exam Q&A bank:
- 8-10 frequently asked questions with answers
- Conceptual questions with answers
- Application questions with answers
- Why / How questions with answers
"""

    return base + "Create comprehensive exam-ready study material."

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: AI GENERATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ("⚠️ API key missing! Add GEMINI_API_KEY to `.streamlit/secrets.toml`", "None")
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Gemini configuration failed: {str(e)}", "None")

    available_models = []
    try:
        models = genai.list_models()
        for m in models:
            name    = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "gemini" in name.lower() and "generateContent" in methods:
                available_models.append(name)
    except Exception as e:
        return (f"❌ Could not list Gemini models: {str(e)}", "None")

    if not available_models:
        return ("❌ No Gemini models available.", "None")

    last_error = "Unknown error"
    for model_name in available_models:
        try:
            model    = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=8192,
                    top_p=0.9,
                ),
            )
            if response and getattr(response, "text", None):
                return response.text, model_name
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            continue

    return (f"❌ All AI models failed.\n\nLast error: {last_error}", "None")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: PDF GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(title, subtitle, content, color_hex="#1d4ed8"):
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm
    )
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph(title, ParagraphStyle(
        "T", parent=styles["Heading1"], fontSize=21,
        textColor=colors.HexColor(color_hex), spaceAfter=6,
        alignment=TA_CENTER, fontName="Helvetica-Bold"
    )))
    story.append(Paragraph(subtitle, ParagraphStyle(
        "S", parent=styles["Normal"], fontSize=10.5,
        textColor=colors.HexColor("#64748b"), spaceAfter=10,
        alignment=TA_CENTER, fontName="Helvetica"
    )))
    story.append(HRFlowable(width="100%", thickness=2,
        color=colors.HexColor(color_hex), spaceAfter=14))

    body_style    = ParagraphStyle("B", parent=styles["Normal"], fontSize=10.5,
        leading=15, textColor=colors.HexColor("#1e293b"), spaceAfter=5, fontName="Helvetica")
    heading_style = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12.5,
        textColor=colors.HexColor(color_hex), spaceBefore=10, spaceAfter=6, fontName="Helvetica-Bold")
    bullet_style  = ParagraphStyle("BL", parent=styles["Normal"], fontSize=10.5,
        leading=15, leftIndent=16, bulletIndent=6,
        textColor=colors.HexColor("#334155"), spaceAfter=4, fontName="Helvetica")

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.18*cm)); continue
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if line.startswith(("###","##","#")):
            story.append(Paragraph(line.lstrip("#").strip(), heading_style))
        elif line.startswith(("- ","• ","* ")):
            story.append(Paragraph(f"• {safe[2:]}", bullet_style))
        else:
            story.append(Paragraph(safe, body_style))

    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1,
        color=colors.HexColor("#e2e8f0"), spaceAfter=5))
    story.append(Paragraph(
        f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle("F", parent=styles["Normal"], fontSize=8,
            textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer
# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "logged_in": False, "username": "",
        "history": [], "current_chapters": [], "last_chapter_key": "",
        "generated_result": None, "generated_model": None,
        "generated_label": None,  "generated_tool": None,
        "generated_chapter": None,"generated_subject": None,
        "generated_topic": None,  "generated_course": None,
        "generated_stream": None, "generated_board": None,
        "generated_audience": None,"generated_output_style": None,
        "answers_result": None,   "answers_model": None,  "show_answers": False,
        "fullpaper_result": None, "fullpaper_model": None,"show_fullpaper": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_generation_state():
    for k in [
        "generated_result","generated_model","generated_label","generated_tool",
        "generated_chapter","generated_subject","generated_topic","generated_course",
        "generated_stream","generated_board","generated_audience","generated_output_style",
        "answers_result","answers_model","show_answers",
        "fullpaper_result","fullpaper_model","show_fullpaper",
    ]:
        st.session_state[k] = None if k not in ("show_answers","show_fullpaper") else False

# ─────────────────────────────────────────────────────────────────────────────
# STEP 9: MAIN APP UI
# ─────────────────────────────────────────────────────────────────────────────

def main_app():

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:18px 0 12px 0;">
                <div style="font-size:2.8rem;">🎓</div>
                <div style="font-size:1.3rem;font-weight:800;color:#2563eb;">StudySmart</div>
                <div style="font-size:0.9rem;color:#64748b;margin-top:4px;">
                    Welcome, {st.session_state.username} 👋
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        tool = st.radio("SELECT TOOL", [
            "📝 Summary","🧠 Quiz","📌 Revision Notes","🧪 Question Paper","❓ Exam Q&A"
        ])
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

        st.divider()
        with st.expander("🤖 AI Model Status"):
            if st.button("Check Models", use_container_width=True):
                with st.spinner("Checking..."):
                    mdls = get_available_models()
                for m in mdls:
                    st.write(f"✅ {m}")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.history   = []
            reset_generation_state()
            st.rerun()

    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">StudySmart</div>
            <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
        </div>
    """, unsafe_allow_html=True)

    # ── Selection Card ──────────────────────────────────────────────────────────
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)

    if not STUDY_DATA:
        st.error("No study data found.")
        st.stop()

    category = st.selectbox("📚 Category", list(STUDY_DATA.keys()))
    course   = st.selectbox("🎓 Program / Class", get_courses(category))
    stream   = st.selectbox("📖 Stream", get_streams(category, course))
    subject  = st.selectbox("🧾 Subject", get_subjects(category, course, stream))

    board = st.selectbox("🏫 Board", BOARDS) if category == "K-12th" else "University / National Syllabus"

    topic = st.selectbox("🗂️ Topic", get_topics(category, course, stream, subject))

    chapter_key = f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key
        reset_generation_state()

    chapter = st.selectbox("📝 Chapter", st.session_state.current_chapters)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Output Style ────────────────────────────────────────────────────────────
    output_style = st.radio(
        "⚙️ Output Style",
        ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format", "🧪 Question Paper"],
        horizontal=True
    )

    effective_label  = get_effective_output_name(tool, output_style)
    btn_label        = get_generate_button_label(tool, output_style)

    # QP format preview
    if effective_label == "Question Paper":
        st.markdown('<div class="sf-preview">', unsafe_allow_html=True)
        st.markdown("#### 📄 Question Paper Pattern Preview")
        st.markdown(render_qp_preview(board, course, subject))
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Dynamic Generate Button ─────────────────────────────────────────────────
    if st.button(btn_label, use_container_width=True):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter first.")
            return

        audience = f"{board} {course} students" if category == "K-12th" else f"{course} students"
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
            "answers_result":         None,
            "answers_model":          None,
            "show_answers":           False,
            "fullpaper_result":       None,
            "fullpaper_model":        None,
            "show_fullpaper":         False,
        })

        if model_used != "None":
            add_to_history(effective_label, chapter, subject, result)

    # ── Display Output ──────────────────────────────────────────────────────────
    if st.session_state.generated_result and st.session_state.generated_model != "None":
        result     = st.session_state.generated_result
        g_label    = st.session_state.generated_label
        g_chapter  = st.session_state.generated_chapter
        g_subject  = st.session_state.generated_subject
        g_topic    = st.session_state.generated_topic
        g_course   = st.session_state.generated_course
        g_stream   = st.session_state.generated_stream
        g_board    = st.session_state.generated_board
        g_audience = st.session_state.generated_audience
        model_used = st.session_state.generated_model

        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("🤖 Model Used", model_used.split("/")[-1] if "/" in model_used else model_used)
        c2.metric("📝 Word Count", f"{count_words(result):,}")

        st.markdown('<div class="sf-output">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        is_qp = g_label == "Question Paper"

        if is_qp:
            st.markdown("---")

            # Download QP PDF
            try:
                qp_pdf  = generate_pdf(f"Question Paper — {g_chapter}",
                                       f"{g_subject} | {g_board} | {g_course}",
                                       result, color_hex="#1d4ed8")
                safe_qp = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_QP.pdf"
                st.download_button("⬇️ Download Question Paper as PDF",
                    data=qp_pdf, file_name=safe_qp,
                    mime="application/pdf", use_container_width=True, key="dl_qp")
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

            # Get Answers button
            if st.button("📋 Get Answers", use_container_width=True, key="get_answers_btn"):
                with st.spinner("Generating answer key for the exact paper above... ⏳"):
                    ans_prompt  = build_answers_prompt(
                        st.session_state.generated_result,
                        g_board, g_course, g_subject, g_chapter
                    )
                    ans_result, ans_model = generate_with_fallback(ans_prompt)
                st.session_state.answers_result = ans_result
                st.session_state.answers_model  = ans_model
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
                                               st.session_state.answers_result, color_hex="#15803d")
                        safe_ans = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_Answers.pdf"
                        st.download_button("⬇️ Download Answer Key as PDF",
                            data=ans_pdf, file_name=safe_ans,
                            mime="application/pdf", use_container_width=True, key="dl_ans")
                    except Exception as e:
                        st.warning(f"⚠️ Answer PDF error: {e}")
                else:
                    st.error("❌ Failed to generate answers.")
                    st.markdown(st.session_state.answers_result)

            # Full Subject QP
            st.markdown("---")
            st.markdown(f"""
                <div class="sf-preview">
                    <strong>🗂️ Generate Full Subject Question Paper</strong><br/>
                    A complete <strong>{g_subject}</strong> paper covering the full syllabus,
                    following the official <strong>{g_board}</strong> / <strong>{g_course}</strong> format.
                </div>
            """, unsafe_allow_html=True)

            if st.button(f"🗂️ Generate Full {g_subject} Question Paper",
                         use_container_width=True, key="full_qp_btn"):
                with st.spinner(f"Generating full {g_subject} question paper... ⏳"):
                    full_prompt  = build_full_subject_qp_prompt(
                        g_board, g_course, g_stream, g_subject, g_audience)
                    full_result, full_model = generate_with_fallback(full_prompt)
                st.session_state.fullpaper_result = full_result
                st.session_state.fullpaper_model  = full_model
                st.session_state.show_fullpaper   = True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Paper — {g_subject} ({g_board} {g_course})")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf  = generate_pdf(f"Full Question Paper — {g_subject}",
                                                f"{g_board} | {g_course} | {g_stream}",
                                                st.session_state.fullpaper_result, color_hex="#6d28d9")
                        safe_full = f"{g_subject}_{g_board}_{g_course}_FullPaper.pdf".replace(" ","_")
                        st.download_button("⬇️ Download Full Subject Paper as PDF",
                            data=full_pdf, file_name=safe_full,
                            mime="application/pdf", use_container_width=True, key="dl_full")
                    except Exception as e:
                        st.warning(f"⚠️ Full paper PDF error: {e}")
                else:
                    st.error("❌ Failed to generate full subject paper.")
                    st.markdown(st.session_state.fullpaper_result)

        else:
            # Non-QP PDF download
            st.markdown("---")
            try:
                pdf = generate_pdf(f"{g_label} — {g_chapter}",
                                   f"{g_subject} | {g_topic} | {g_course}", result)
                safe = g_chapter.replace(" ","_").replace(":","").replace("/","-") + ".pdf"
                st.download_button("⬇️ Download as PDF", data=pdf, file_name=safe,
                    mime="application/pdf", use_container_width=True, key="dl_main")
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

    elif st.session_state.generated_result and st.session_state.generated_model == "None":
        st.markdown("---")
        st.error("❌ AI generation failed")
        st.markdown(st.session_state.generated_result)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 10: AUTH UI
# ─────────────────────────────────────────────────────────────────────────────

def auth_ui():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
            <div class="sf-header">
                <div class="sf-header-title">StudySmart</div>
                <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        with tab1:
            u = st.text_input("👤 Username", key="login_u", placeholder="Enter username")
            p = st.text_input("🔑 Password", type="password", key="login_p", placeholder="Enter password")
            if st.button("Sign In 🚀", use_container_width=True):
                if u.strip() and p.strip():
                    conn = sqlite3.connect("users.db")
                    c    = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username=? AND password=?",
                              (u.strip(), hash_p(p)))
                    user = c.fetchone(); conn.close()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username  = u.strip()
                        st.success("✅ Login successful!")
                        time.sleep(1); st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
                else:
                    st.warning("⚠️ Please fill in both fields.")

        with tab2:
            nu = st.text_input("👤 New Username",  key="reg_u",  placeholder="Min 3 characters")
            np = st.text_input("🔑 New Password",  type="password", key="reg_p", placeholder="Min 6 characters")
            cp = st.text_input("🔑 Confirm Password", type="password", key="reg_cp", placeholder="Re-enter password")
            if st.button("Create Account ✨", use_container_width=True):
                if not nu.strip():          st.error("❌ Username cannot be empty")
                elif len(nu.strip()) < 3:   st.error("❌ Username min 3 characters")
                elif len(np.strip()) < 6:   st.error("❌ Password min 6 characters")
                elif np != cp:              st.error("❌ Passwords do not match")
                else:
                    try:
                        conn = sqlite3.connect("users.db"); c = conn.cursor()
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                  (nu.strip(), hash_p(np)))
                        conn.commit(); conn.close()
                        st.success("✅ Account created!")
                        time.sleep(1)
                        st.session_state.logged_in = True
                        st.session_state.username  = nu.strip()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists")

        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 11: ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

init_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
