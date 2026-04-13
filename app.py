# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — APP v3.5
# FIXES:
# ✅ Enter key submits login — st.form() used correctly
# ✅ Dropdown arrow visible — CSS fixed to not override arrow container
# ✅ Dark mode via [data-theme="dark"]
# ✅ Single generate button with dynamic label
# ✅ All features retained
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
# STEP 2: PAGE CONFIG & CSS
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

/* ── Global ── */
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

/* ══════════════════════════
   LIGHT MODE
══════════════════════════ */
.stApp { background: #f0f4f8 !important; }

.sf-header { text-align: center; padding: 28px 0 8px 0; }
.sf-header-title {
    font-size: 3.2rem; font-weight: 800;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1;
}
.sf-header-subtitle {
    color: #64748b; font-weight: 500; margin-top: 6px; font-size: 1rem;
}

.sf-card {
    background: #ffffff !important; border-radius: 14px;
    padding: 22px 26px; border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05); margin-bottom: 16px;
}

/* Output boxes */
.sf-output {
    background: #eff6ff !important; border-left: 4px solid #2563eb !important;
    border-radius: 14px; padding: 22px 24px;
    border: 1px solid #bfdbfe !important; margin-top: 14px;
}
.sf-output h1,.sf-output h2,.sf-output h3 { color: #1d4ed8 !important; margin-top:0; }
.sf-output p,.sf-output li,.sf-output span,.sf-output strong { color: #1e293b !important; }

.sf-answers {
    background: #f0fdf4 !important; border-left: 4px solid #16a34a !important;
    border-radius: 14px; padding: 22px 24px;
    border: 1px solid #bbf7d0 !important; margin-top: 16px;
}
.sf-answers h1,.sf-answers h2,.sf-answers h3 { color: #15803d !important; margin-top:0; }
.sf-answers p,.sf-answers li,.sf-answers span,.sf-answers strong { color: #1e293b !important; }

.sf-fullpaper {
    background: #faf5ff !important; border-left: 4px solid #7c3aed !important;
    border-radius: 14px; padding: 22px 24px;
    border: 1px solid #ddd6fe !important; margin-top: 16px;
}
.sf-fullpaper h1,.sf-fullpaper h2,.sf-fullpaper h3 { color: #6d28d9 !important; margin-top:0; }
.sf-fullpaper p,.sf-fullpaper li,.sf-fullpaper span,.sf-fullpaper strong { color: #1e293b !important; }

.sf-history-item {
    background: #eff6ff; border-left: 3px solid #3b82f6;
    border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; font-size: 0.88rem;
}
.sf-history-item { color: #334155 !important; }
.sf-history-item b { color: #1d4ed8 !important; }
.sf-history-item small { color: #64748b !important; }

/* ── Radio labels ── */
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] > div > label > div > p {
    color: #1e293b !important; font-weight: 500 !important;
}

/* ── Widget labels ── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
div.stSelectbox > label,
div.stTextInput > label,
div.stRadio > label,
label[data-testid="stWidgetLabel"] {
    color: #1e293b !important; font-weight: 600 !important; font-size: 0.88rem !important;
}

/* ═══════════════════════════════════════════════════════
   DROPDOWN FIX — KEY CHANGE:
   Target only [data-baseweb="select"] VALUE container,
   NOT the outer wrapper. This preserves the arrow icon.
═══════════════════════════════════════════════════════ */

/* Outer select wrapper — only border/radius, NO background override */
div[data-baseweb="select"] {
    border-radius: 10px !important;
}

/* The visible selected-value box only */
div[data-baseweb="select"] > div:first-child {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
}

/* Selected text color */
div[data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="select"] > div > div > div {
    color: #1e293b !important;
}

/* Dropdown arrow SVG — ensure it stays visible */
div[data-baseweb="select"] svg {
    fill: #64748b !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Dropdown list */
div[data-baseweb="popover"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
}
div[role="listbox"] { background: #ffffff !important; }
div[role="option"]  { color: #1e293b !important; background: #ffffff !important; }
div[role="option"]:hover { background: #eff6ff !important; color: #1d4ed8 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important; border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * { color: #1e293b !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #e2e8f0 !important; }
.stTabs [data-baseweb="tab"] { color: #64748b !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { color: #1e293b !important; border-bottom: 3px solid #3b82f6 !important; }

/* ── Expanders ── */
details { background: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 10px !important; }
details summary { color: #1e293b !important; font-weight: 600 !important; }

/* ── Markdown ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span { color: #1e293b !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 11px !important; font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important; font-size: 0.95rem !important;
    box-shadow: 0 3px 12px rgba(59,130,246,0.22) !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(59,130,246,0.35) !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 11px !important; font-weight: 600 !important;
    box-shadow: 0 3px 12px rgba(16,185,129,0.22) !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 6px 20px rgba(16,185,129,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Form submit button — same style as regular button ── */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 11px !important; font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important; font-size: 0.95rem !important;
    box-shadow: 0 3px 12px rgba(59,130,246,0.22) !important;
    width: 100% !important; transition: all 0.18s ease !important;
}
.stFormSubmitButton > button:hover {
    box-shadow: 0 6px 20px rgba(59,130,246,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Alerts ── */
div[data-testid="stSuccessMessage"] {
    background: rgba(16,185,129,0.08) !important;
    border: 1.5px solid rgba(16,185,129,0.3) !important; border-radius: 10px !important;
}
div[data-testid="stWarningMessage"] {
    background: rgba(245,158,11,0.08) !important;
    border: 1.5px solid rgba(245,158,11,0.3) !important; border-radius: 10px !important;
}
div[data-testid="stErrorMessage"] {
    background: rgba(239,68,68,0.08) !important;
    border: 1.5px solid rgba(239,68,68,0.3) !important; border-radius: 10px !important;
}

hr { border-color: #e2e8f0 !important; }

/* ══════════════════════════════════════════════════════
   DARK MODE — [data-theme="dark"] ONLY correct selector
══════════════════════════════════════════════════════ */

[data-theme="dark"] .stApp { background: #0f172a !important; }
[data-theme="dark"] .sf-card { background: #1e293b !important; border-color: #334155 !important; }

[data-theme="dark"] .sf-output  { background: rgba(37,99,235,0.13) !important; border-color: #3b82f6 !important; }
[data-theme="dark"] .sf-output h1,[data-theme="dark"] .sf-output h2,[data-theme="dark"] .sf-output h3 { color: #93c5fd !important; }
[data-theme="dark"] .sf-output p,[data-theme="dark"] .sf-output li,[data-theme="dark"] .sf-output span,[data-theme="dark"] .sf-output strong { color: #dbeafe !important; }

[data-theme="dark"] .sf-answers { background: rgba(22,163,74,0.13) !important; border-color: #16a34a !important; }
[data-theme="dark"] .sf-answers h1,[data-theme="dark"] .sf-answers h2,[data-theme="dark"] .sf-answers h3 { color: #86efac !important; }
[data-theme="dark"] .sf-answers p,[data-theme="dark"] .sf-answers li,[data-theme="dark"] .sf-answers span,[data-theme="dark"] .sf-answers strong { color: #dcfce7 !important; }

[data-theme="dark"] .sf-fullpaper { background: rgba(109,40,217,0.13) !important; border-color: #7c3aed !important; }
[data-theme="dark"] .sf-fullpaper h1,[data-theme="dark"] .sf-fullpaper h2,[data-theme="dark"] .sf-fullpaper h3 { color: #c4b5fd !important; }
[data-theme="dark"] .sf-fullpaper p,[data-theme="dark"] .sf-fullpaper li,[data-theme="dark"] .sf-fullpaper span,[data-theme="dark"] .sf-fullpaper strong { color: #ede9fe !important; }

[data-theme="dark"] .sf-history-item { background: rgba(37,99,235,0.15) !important; border-left-color: #60a5fa !important; color: #cbd5e1 !important; }
[data-theme="dark"] .sf-history-item b { color: #93c5fd !important; }
[data-theme="dark"] .sf-history-item small { color: #94a3b8 !important; }

/* Radio dark */
[data-theme="dark"] div[data-testid="stRadio"] label p,
[data-theme="dark"] div[data-testid="stRadio"] label span,
[data-theme="dark"] div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p,
[data-theme="dark"] div[data-testid="stRadio"] > div > label > div > p { color: #e2e8f0 !important; }

/* Widget labels dark */
[data-theme="dark"] [data-testid="stWidgetLabel"] p,
[data-theme="dark"] [data-testid="stWidgetLabel"] label,
[data-theme="dark"] div.stSelectbox > label,
[data-theme="dark"] div.stTextInput > label,
[data-theme="dark"] div.stRadio > label,
[data-theme="dark"] label[data-testid="stWidgetLabel"] { color: #e2e8f0 !important; }

/* Dropdown dark — same targeted approach */
[data-theme="dark"] div[data-baseweb="select"] > div:first-child {
    border-color: #475569 !important;
    background: #1e293b !important;
}
[data-theme="dark"] div[data-baseweb="select"] > div > div > div { color: #e2e8f0 !important; }
[data-theme="dark"] div[data-baseweb="select"] svg { fill: #94a3b8 !important; }
[data-theme="dark"] div[data-baseweb="popover"] {
    background: #1e293b !important; border-color: #334155 !important;
}
[data-theme="dark"] div[role="listbox"] { background: #1e293b !important; }
[data-theme="dark"] div[role="option"] { color: #e2e8f0 !important; background: #1e293b !important; }
[data-theme="dark"] div[role="option"]:hover { background: #334155 !important; color: #f1f5f9 !important; }

/* Sidebar dark */
[data-theme="dark"] [data-testid="stSidebar"] { background: #0f172a !important; border-right-color: #334155 !important; }
[data-theme="dark"] [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Tabs dark */
[data-theme="dark"] .stTabs [data-baseweb="tab-list"] { border-bottom-color: #334155 !important; }
[data-theme="dark"] .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
[data-theme="dark"] .stTabs [aria-selected="true"] { color: #f1f5f9 !important; border-bottom-color: #60a5fa !important; }

/* Expanders dark */
[data-theme="dark"] details { background: #1e293b !important; border-color: #334155 !important; }
[data-theme="dark"] details summary { color: #e2e8f0 !important; }

/* Markdown dark */
[data-theme="dark"] [data-testid="stMarkdownContainer"] p,
[data-theme="dark"] [data-testid="stMarkdownContainer"] li,
[data-theme="dark"] [data-testid="stMarkdownContainer"] span,
[data-theme="dark"] [data-testid="stMarkdownContainer"] h1,
[data-theme="dark"] [data-testid="stMarkdownContainer"] h2,
[data-theme="dark"] [data-testid="stMarkdownContainer"] h3 { color: #e2e8f0 !important; }

/* Alerts dark */
[data-theme="dark"] div[data-testid="stSuccessMessage"] { background: rgba(16,185,129,0.15) !important; border-color: rgba(16,185,129,0.4) !important; }
[data-theme="dark"] div[data-testid="stWarningMessage"] { background: rgba(245,158,11,0.15) !important; border-color: rgba(245,158,11,0.4) !important; }
[data-theme="dark"] div[data-testid="stErrorMessage"]   { background: rgba(239,68,68,0.15) !important;  border-color: rgba(239,68,68,0.4) !important; }

[data-theme="dark"] hr { border-color: #334155 !important; }

/* Form submit dark */
[data-theme="dark"] .stFormSubmitButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: #ffffff !important;
}

@media (max-width: 768px) {
    .sf-header-title { font-size: 2.3rem !important; }
    .sf-card,.sf-output,.sf-answers,.sf-fullpaper { padding: 14px 16px; }
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
}
</style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: HELPERS
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

def do_login(username, password):
    """Shared login logic used by both button click and Enter key."""
    username = username.strip()
    password = password.strip()
    if not username or not password:
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

def get_available_models():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ["Error: GEMINI_API_KEY not found"]
    try:
        genai.configure(api_key=api_key)
        models  = genai.list_models()
        working = []
        for m in models:
            name    = getattr(m, "name", "")
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
        if output_style == "📋 Notes Format":  return "Notes"
        if output_style == "📄 Detailed":       return "Detailed Summary"
        if output_style == "⚡ Short & Quick":  return "Quick Summary"
        return "Summary"
    if tool == "🧠 Quiz":           return "Quiz"
    if tool == "📌 Revision Notes": return "Revision Notes"
    if tool == "❓ Exam Q&A":       return "Exam Q&A"
    return "Content"

def get_button_label(tool, output_style):
    name  = get_effective_output_name(tool, output_style)
    icons = {
        "Question Paper":   "🧪",
        "Notes":            "📋",
        "Detailed Summary": "📄",
        "Quick Summary":    "⚡",
        "Summary":          "📝",
        "Quiz":             "🧠",
        "Revision Notes":   "📌",
        "Exam Q&A":         "❓",
    }
    return f"{icons.get(name, '✨')} Generate {name}"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: QP FORMAT SPECS
# ─────────────────────────────────────────────────────────────────────────────

def get_qp_format_spec(board, course, subject):
    b = board.upper()

    if "CBSE" in b:
        if any(x in course for x in ["10","X","Class 10"]):
            return {
                "board_label":"CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label":"BOARD EXAMINATION","class_label":"CLASS X",
                "total_marks":80,"time":"3 Hours",
                "instructions":[
                    "This paper contains Sections A, B, C, D and E.",
                    "All questions are compulsory.",
                    "Section A — MCQ (1 mark each).",
                    "Section B — Very Short Answer (2 marks each).",
                    "Section C — Short Answer (3 marks each).",
                    "Section D — Long Answer (5 marks each).",
                    "Section E — Case / Source Based (4 marks each).",
                    "Internal choices are provided in some questions.",
                ],
                "sections":[
                    {"name":"SECTION A","type":"MCQ / Objective","q_count":20,"marks_each":1,"total":20},
                    {"name":"SECTION B","type":"Very Short Answer","q_count":5,"marks_each":2,"total":10},
                    {"name":"SECTION C","type":"Short Answer","q_count":6,"marks_each":3,"total":18},
                    {"name":"SECTION D","type":"Long Answer","q_count":4,"marks_each":5,"total":20},
                    {"name":"SECTION E","type":"Case / Source Based","q_count":3,"marks_each":4,"total":12},
                ]
            }
        if any(x in course for x in ["12","XII","Class 12"]):
            return {
                "board_label":"CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label":"BOARD EXAMINATION","class_label":"CLASS XII",
                "total_marks":70,"time":"3 Hours",
                "instructions":[
                    "This paper contains Sections A, B, C, D and E.",
                    "All questions are compulsory.",
                    "Section A — MCQ (1 mark each).",
                    "Section B — Very Short Answer (2 marks each).",
                    "Section C — Short Answer (3 marks each).",
                    "Section D — Long Answer (5 marks each).",
                    "Section E — Case / Source Based (4 marks each).",
                    "Internal choices in Sections B, C and D.",
                ],
                "sections":[
                    {"name":"SECTION A","type":"MCQ / Objective","q_count":18,"marks_each":1,"total":18},
                    {"name":"SECTION B","type":"Very Short Answer","q_count":4,"marks_each":2,"total":8},
                    {"name":"SECTION C","type":"Short Answer","q_count":5,"marks_each":3,"total":15},
                    {"name":"SECTION D","type":"Long Answer","q_count":2,"marks_each":5,"total":10},
                    {"name":"SECTION E","type":"Case / Source Based","q_count":3,"marks_each":4,"total":12},
                ]
            }
        return {
            "board_label":"CENTRAL BOARD OF SECONDARY EDUCATION",
            "exam_label":"ANNUAL EXAMINATION","class_label":course.upper(),
            "total_marks":80,"time":"3 Hours",
            "instructions":["All questions are compulsory.","Read each section carefully."],
            "sections":[
                {"name":"SECTION A","type":"Objective","q_count":20,"marks_each":1,"total":20},
                {"name":"SECTION B","type":"Short Answer I","q_count":6,"marks_each":2,"total":12},
                {"name":"SECTION C","type":"Short Answer II","q_count":6,"marks_each":3,"total":18},
                {"name":"SECTION D","type":"Long Answer","q_count":4,"marks_each":5,"total":20},
            ]
        }

    if "ICSE" in b:
        return {
            "board_label":"COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label":"ICSE EXAMINATION","class_label":course.upper(),
            "total_marks":80,"time":"2 Hours",
            "instructions":["Attempt all from Section A.","Attempt any four from Section B.","Marks in brackets [ ]."],
            "sections":[
                {"name":"SECTION A","type":"Compulsory Objective / Short Answer","q_count":10,"marks_each":"varied","total":40},
                {"name":"SECTION B","type":"Descriptive (Attempt 4 of 6)","q_count":6,"marks_each":10,"total":40},
            ]
        }

    if "ISC" in b:
        return {
            "board_label":"COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label":"ISC EXAMINATION","class_label":course.upper(),
            "total_marks":70,"time":"3 Hours",
            "instructions":["Attempt all from Section A.","Attempt any four from Section B.","Marks in brackets [ ].","Draw neat labelled diagrams where necessary."],
            "sections":[
                {"name":"SECTION A","type":"Compulsory","q_count":10,"marks_each":"varied","total":30},
                {"name":"SECTION B","type":"Descriptive (4 of 6)","q_count":6,"marks_each":10,"total":40},
            ]
        }

    if "IB" in b:
        return {
            "board_label":"INTERNATIONAL BACCALAUREATE",
            "exam_label":"FINAL EXAMINATION","class_label":course.upper(),
            "total_marks":100,"time":"2 Hours 30 Minutes",
            "instructions":["Answer required questions.","Show all reasoning where necessary."],
            "sections":[
                {"name":"SECTION A","type":"Structured / Objective","q_count":20,"marks_each":"varied","total":40},
                {"name":"SECTION B","type":"Extended Response","q_count":4,"marks_each":15,"total":60},
            ]
        }

    if "CAMBRIDGE" in b:
        return {
            "board_label":"CAMBRIDGE ASSESSMENT INTERNATIONAL EDUCATION",
            "exam_label":"INTERNATIONAL EXAMINATION","class_label":course.upper(),
            "total_marks":80,"time":"2 Hours",
            "instructions":["Answer all questions as instructed.","Show all working where required."],
            "sections":[
                {"name":"SECTION A","type":"Structured Questions","q_count":10,"marks_each":4,"total":40},
                {"name":"SECTION B","type":"Extended Response","q_count":4,"marks_each":10,"total":40},
            ]
        }

    if any(k in course.upper() for k in ["MBBS","BDS","MD","MEDICAL"]):
        return {
            "board_label":"UNIVERSITY EXAMINATIONS",
            "exam_label":f"{course.upper()} PROFESSIONAL EXAMINATION","class_label":course.upper(),
            "total_marks":100,"time":"3 Hours",
            "instructions":["Answer all in Part A.","Answer any five from Part B.","Draw neat labelled diagrams where necessary."],
            "sections":[
                {"name":"PART A","type":"Short Notes","q_count":10,"marks_each":5,"total":50},
                {"name":"PART B","type":"Long Essays","q_count":8,"marks_each":10,"total":50},
            ]
        }

    return {
        "board_label":"UNIVERSITY EXAMINATIONS",
        "exam_label":f"{course.upper()} SEMESTER EXAMINATION","class_label":course.upper(),
        "total_marks":100,"time":"3 Hours",
        "instructions":["Answer all in Section A.","Answer any five from Section B.","Figures in brackets indicate marks."],
        "sections":[
            {"name":"SECTION A","type":"Short Answer","q_count":10,"marks_each":2,"total":20},
            {"name":"SECTION B","type":"Medium Answer","q_count":8,"marks_each":5,"total":40},
            {"name":"SECTION C","type":"Long Answer","q_count":4,"marks_each":10,"total":40},
        ]
    }

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

def build_question_paper_prompt(board, course, subject, chapter, topic, audience):
    fmt   = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
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
SUBJECT: {subject} | TOPIC: {topic} | CHAPTER: {chapter}
TIME: {fmt['time']} | MAXIMUM MARKS: {fmt['total_marks']}

GENERAL INSTRUCTIONS (print in paper):
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
9. Academic tone only.

Generate the complete question paper now.
"""

def build_full_subject_qp_prompt(board, course, stream, subject, audience):
    fmt   = get_qp_format_spec(board, course, subject)
    instr = "\n".join([f"{i+1}. {x}" for i,x in enumerate(fmt["instructions"])])
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
STREAM: {stream} | SUBJECT: {subject}
TIME: {fmt['time']} | MAXIMUM MARKS: {fmt['total_marks']}

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

BOARD: {board} | COURSE: {course} | SUBJECT: {subject} | CHAPTER: {chapter}

CRITICAL RULES:
1. Answer ONLY the questions in the paper below.
2. Keep EXACT same section names and question numbers.
3. For each: question number → brief restatement → answer.
4. MCQs: correct option letter + 2-3 line explanation.
5. Very Short: 2-3 lines.
6. Short: 4-6 lines with key points.
7. Long: 150-250 words with examples.
8. Case-Based: full analysis + all sub-question answers.
9. If OR choices exist, answer BOTH.
10. DO NOT create a new paper — only answer the one below.

===== QUESTION PAPER =====
{question_paper_text}
===== END =====

Generate the answer key now, same section and question order.
"""

def build_prompt(tool, chapter, topic, subject, audience, output_style, board="", course=""):
    if output_style == "🧪 Question Paper" or tool == "🧪 Question Paper":
        return build_question_paper_prompt(board, course, subject, chapter, topic, audience)
    base = f"""
You are an expert educator creating study material for {audience}.
Subject: {subject} | Topic: {topic} | Chapter: {chapter}
Requirements: Accurate, exam-focused, well-structured, with examples, and error-free.
"""
    if tool == "📝 Summary":
        if output_style == "📄 Detailed":
            return base + "\nCreate a detailed summary with: chapter overview (150-200 words), key concepts (300-400 words), important definitions and formulas, 2-3 worked examples, common mistakes to avoid, exam tips."
        elif output_style == "⚡ Short & Quick":
            return base + "\nCreate a concise quick-reference guide (max 500 words): one-line definition, 5-7 key points, important formulas/facts, quick revision tips."
        elif output_style == "📋 Notes Format":
            return base + "\nCreate structured study notes: clear headings and subheadings, bullet points per concept, definitions highlighted, important facts and examples, revision points."
    if tool == "🧠 Quiz":
        return base + "\nCreate a quiz: 5 MCQs with 4 options (mark correct answer), 5 short answer questions with answers, 3 long answer questions with answers."
    if tool == "📌 Revision Notes":
        return base + "\nCreate revision notes: top 10 must-know points, formula/fact sheet, mnemonics and memory tricks, key comparisons/tables, exam focus areas."
    if tool == "❓ Exam Q&A":
        return base + "\nCreate an exam Q&A bank: 8-10 frequently asked questions with answers, 5 conceptual questions with answers, 5 application questions with answers, 5 why/how questions with answers."
    return base + "Create comprehensive exam-ready study material."

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: AI ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return ("⚠️ API key missing! Add GEMINI_API_KEY to `.streamlit/secrets.toml`","None")
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Gemini configuration failed: {str(e)}","None")
    available = []
    try:
        for m in genai.list_models():
            name    = getattr(m,"name","")
            methods = getattr(m,"supported_generation_methods",[])
            if "gemini" in name.lower() and "generateContent" in methods:
                available.append(name)
    except Exception as e:
        return (f"❌ Could not list models: {str(e)}","None")
    if not available:
        return ("❌ No Gemini models available.","None")
    last_error = ""
    for model_name in available:
        try:
            model    = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0, max_output_tokens=8192, top_p=0.9
                ),
            )
            if response and getattr(response,"text",None):
                return response.text, model_name
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            continue
    return (f"❌ All models failed. Last error: {last_error}","None")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: PDF GENERATION
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
    body_sty = ParagraphStyle("B", parent=styles["Normal"], fontSize=10.5, leading=15,
        textColor=colors.HexColor("#1e293b"), spaceAfter=5, fontName="Helvetica")
    head_sty = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12.5,
        textColor=colors.HexColor(color_hex), spaceBefore=10, spaceAfter=6, fontName="Helvetica-Bold")
    bull_sty = ParagraphStyle("BL", parent=styles["Normal"], fontSize=10.5, leading=15,
        leftIndent=16, bulletIndent=6, textColor=colors.HexColor("#334155"),
        spaceAfter=4, fontName="Helvetica")
    for line in content.split("\n"):
        line = line.strip()
        if not line: story.append(Spacer(1, 0.18*cm)); continue
        safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if line.startswith(("###","##","#")):
            story.append(Paragraph(line.lstrip("#").strip(), head_sty))
        elif line.startswith(("- ","• ","* ")):
            story.append(Paragraph(f"• {safe[2:]}", bull_sty))
        else:
            story.append(Paragraph(safe, body_sty))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1,
        color=colors.HexColor("#e2e8f0"), spaceAfter=5))
    story.append(Paragraph(
        f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle("F", parent=styles["Normal"], fontSize=8,
            textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)))
    doc.build(story)
    buffer.seek(0)
    return buffer
# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "logged_in":False,"username":"","history":[],
        "current_chapters":[],"last_chapter_key":"",
        "generated_result":None,"generated_model":None,
        "generated_label":None,"generated_tool":None,
        "generated_chapter":None,"generated_subject":None,
        "generated_topic":None,"generated_course":None,
        "generated_stream":None,"generated_board":None,
        "generated_audience":None,"generated_output_style":None,
        "answers_result":None,"answers_model":None,"show_answers":False,
        "fullpaper_result":None,"fullpaper_model":None,"show_fullpaper":False,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_generation_state():
    for k in [
        "generated_result","generated_model","generated_label","generated_tool",
        "generated_chapter","generated_subject","generated_topic","generated_course",
        "generated_stream","generated_board","generated_audience","generated_output_style",
        "answers_result","answers_model","fullpaper_result","fullpaper_model",
    ]:
        st.session_state[k] = None
    st.session_state.show_answers   = False
    st.session_state.show_fullpaper = False

# ─────────────────────────────────────────────────────────────────────────────
# STEP 9: MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

def main_app():
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center;padding:18px 0 14px 0;">
                <div style="font-size:2.6rem;">🎓</div>
                <div style="font-size:1.2rem;font-weight:800;color:#2563eb;">StudySmart</div>
                <div style="font-size:0.85rem;color:#64748b;margin-top:4px;">
                    Welcome, {st.session_state.username} 👋
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.divider()
        tool = st.radio("SELECT TOOL",[
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

    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">StudySmart</div>
            <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    if not STUDY_DATA:
        st.error("No study data found.")
        st.stop()

    category = st.selectbox("📚 Category",       list(STUDY_DATA.keys()))
    course   = st.selectbox("🎓 Program / Class", get_courses(category))
    stream   = st.selectbox("📖 Stream",          get_streams(category, course))
    subject  = st.selectbox("🧾 Subject",         get_subjects(category, course, stream))
    board    = st.selectbox("🏫 Board", BOARDS) if category == "K-12th" else "University / National Syllabus"
    topic    = st.selectbox("🗂️ Topic",           get_topics(category, course, stream, subject))

    chapter_key = f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key
        reset_generation_state()

    chapter = st.selectbox("📝 Chapter", st.session_state.current_chapters)
    st.markdown('</div>', unsafe_allow_html=True)

    output_style    = st.radio(
        "⚙️ Output Style",
        ["📄 Detailed","⚡ Short & Quick","📋 Notes Format","🧪 Question Paper"],
        horizontal=True
    )
    effective_label = get_effective_output_name(tool, output_style)
    btn_label       = get_button_label(tool, output_style)

    st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)

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
            "generated_result":result,"generated_model":model_used,
            "generated_label":effective_label,"generated_tool":tool,
            "generated_chapter":chapter,"generated_subject":subject,
            "generated_topic":topic,"generated_course":course,
            "generated_stream":stream,"generated_board":board,
            "generated_audience":audience,"generated_output_style":output_style,
            "answers_result":None,"answers_model":None,"show_answers":False,
            "fullpaper_result":None,"fullpaper_model":None,"show_fullpaper":False,
        })
        if model_used != "None":
            add_to_history(effective_label, chapter, subject, result)

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

        if g_label == "Question Paper":
            st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
            try:
                qp_pdf  = generate_pdf(f"Question Paper — {g_chapter}",
                    f"{g_subject} | {g_board} | {g_course}", result, "#1d4ed8")
                safe_qp = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_QP.pdf"
                st.download_button("⬇️ Download Question Paper as PDF",
                    data=qp_pdf, file_name=safe_qp, mime="application/pdf",
                    use_container_width=True, key="dl_qp")
            except Exception as e:
                st.warning(f"⚠️ PDF error: {e}")

            st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True)
            if st.button("📋 Get Answers for this Paper", use_container_width=True, key="get_answers_btn"):
                with st.spinner("Generating answer key for the exact paper above... ⏳"):
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
                        st.download_button("⬇️ Download Answer Key as PDF",
                            data=ans_pdf, file_name=safe_ans, mime="application/pdf",
                            use_container_width=True, key="dl_ans")
                    except Exception as e:
                        st.warning(f"⚠️ Answer PDF error: {e}")
                else:
                    st.error("❌ Failed to generate answers.")

            st.markdown("---")
            st.info(f"💡 Need a complete **{g_subject}** paper covering the full syllabus in **{g_board}** format?")
            if st.button(f"🗂️ Generate Full {g_subject} Question Paper ({g_board})",
                         use_container_width=True, key="full_qp_btn"):
                with st.spinner(f"Generating full {g_subject} question paper... ⏳"):
                    full_r, full_m = generate_with_fallback(
                        build_full_subject_qp_prompt(g_board, g_course, g_stream, g_subject, g_audience))
                st.session_state.fullpaper_result = full_r
                st.session_state.fullpaper_model  = full_m
                st.session_state.show_fullpaper   = True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                if st.session_state.fullpaper_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Paper — {g_subject} ({g_board} · {g_course})")
                    st.markdown(st.session_state.fullpaper_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf = generate_pdf(f"Full Question Paper — {g_subject}",
                            f"{g_board} | {g_course} | {g_stream}",
                            st.session_state.fullpaper_result, "#6d28d9")
                        safe_f = f"{g_subject}_{g_board}_{g_course}_FullPaper.pdf".replace(" ","_")
                        st.download_button("⬇️ Download Full Subject Paper as PDF",
                            data=full_pdf, file_name=safe_f, mime="application/pdf",
                            use_container_width=True, key="dl_full")
                    except Exception as e:
                        st.warning(f"⚠️ Full PDF error: {e}")
                else:
                    st.error("❌ Failed to generate full subject paper.")
        else:
            st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
            try:
                pdf  = generate_pdf(f"{g_label} — {g_chapter}",
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
# KEY FIX: st.form() captures Enter key on any field inside it.
# do_login() is called from both the form submit AND on Enter.
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

        # ── LOGIN TAB — wrapped in st.form so Enter key triggers submit ────────
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                u = st.text_input(
                    "👤 Username",
                    placeholder="Enter your username",
                    key="login_u"
                )
                p = st.text_input(
                    "🔑 Password",
                    type="password",
                    placeholder="Enter your password — press Enter to sign in",
                    key="login_p"
                )
                # form_submit_button fires on Enter key AND on click
                submitted = st.form_submit_button(
                    "Sign In 🚀",
                    use_container_width=True
                )

            if submitted:
                success, result = do_login(u, p)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username  = result
                    st.success("✅ Login successful!")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.error(result)

        # ── REGISTER TAB — also wrapped in st.form ─────────────────────────────
        with tab2:
            with st.form("register_form", clear_on_submit=True):
                nu = st.text_input(
                    "👤 New Username",
                    placeholder="Minimum 3 characters",
                    key="reg_u"
                )
                np = st.text_input(
                    "🔑 New Password",
                    type="password",
                    placeholder="Minimum 6 characters",
                    key="reg_p"
                )
                cp = st.text_input(
                    "🔑 Confirm Password",
                    type="password",
                    placeholder="Re-enter your password — press Enter to register",
                    key="reg_cp"
                )
                reg_submitted = st.form_submit_button(
                    "Create Account ✨",
                    use_container_width=True
                )

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
                        c    = conn.cursor()
                        c.execute(
                            "INSERT INTO users (username, password) VALUES (?, ?)",
                            (nu.strip(), hash_p(np))
                        )
                        conn.commit()
                        conn.close()
                        st.success("✅ Account created! Logging you in...")
                        time.sleep(0.8)
                        st.session_state.logged_in = True
                        st.session_state.username  = nu.strip()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists. Please choose another.")

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
