# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — APP v2.5
# ✅ Academic-format question papers per board/class
# ✅ Full Subject Question Paper generator
# ✅ Get Answers (session_state fixed)
# ✅ temperature=0.1 for consistent results
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
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ═════════════════════════════════════════════════════════════════════════════
# STEP 1: LOAD STUDY DATA
# ═════════════════════════════════════════════════════════════════════════════

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

# ═════════════════════════════════════════════════════════════════════════════
# STEP 2: PAGE CONFIG
# ═════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        font-size: 0.7rem;
        color: #cbd5e1;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 8px;
        text-align: center !important;
        width: 100% !important;
        display: block !important;
    }

    .sf-card {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 28px 32px;
        border: 1px solid rgba(59,130,246,0.15);
        margin-bottom: 20px;
        box-shadow: 0 4px 24px rgba(59,130,246,0.07);
    }

    /* Blue output box */
    .sf-output {
        background: linear-gradient(135deg,
            rgba(59,130,246,0.05) 0%,
            rgba(37,99,235,0.05) 100%);
        border-radius: 18px;
        padding: 28px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 2px 15px rgba(59,130,246,0.1);
        margin-top: 12px;
        border: 1px solid rgba(59,130,246,0.2);
        color: #1e293b;
    }
    .sf-output h3, .sf-output h2 {
        color: #3b82f6 !important;
        margin-top: 0;
        font-weight: 700;
    }

    /* Green answers box */
    .sf-answers {
        background: linear-gradient(135deg,
            rgba(34,197,94,0.05) 0%,
            rgba(22,163,74,0.05) 100%);
        border-radius: 18px;
        padding: 28px;
        border-left: 5px solid #22c55e;
        box-shadow: 0 2px 15px rgba(34,197,94,0.1);
        margin-top: 20px;
        border: 1px solid rgba(34,197,94,0.2);
        color: #1e293b;
    }
    .sf-answers h3, .sf-answers h2 {
        color: #16a34a !important;
        margin-top: 0;
        font-weight: 700;
    }

    /* Purple full-subject box */
    .sf-fullpaper {
        background: linear-gradient(135deg,
            rgba(139,92,246,0.05) 0%,
            rgba(109,40,217,0.05) 100%);
        border-radius: 18px;
        padding: 28px;
        border-left: 5px solid #8b5cf6;
        box-shadow: 0 2px 15px rgba(139,92,246,0.1);
        margin-top: 20px;
        border: 1px solid rgba(139,92,246,0.2);
        color: #1e293b;
    }
    .sf-fullpaper h3, .sf-fullpaper h2 {
        color: #7c3aed !important;
        margin-top: 0;
        font-weight: 700;
    }

    .sf-history-item {
        background: rgba(59,130,246,0.05);
        border-radius: 10px;
        padding: 12px 16px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 10px;
        font-size: 0.9rem;
        color: #475569;
    }

    /* Primary blue button */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.8rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.4px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(59,130,246,0.3) !important;
    }
    .stButton > button:hover {
        box-shadow: 0 8px 25px rgba(59,130,246,0.4) !important;
        transform: translateY(-2px) !important;
    }

    /* Green download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(16,185,129,0.3) !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 25px rgba(16,185,129,0.4) !important;
        transform: translateY(-2px) !important;
    }

    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        background: #ffffff !important;
        color: #1e293b !important;
    }
    input[type="text"], input[type="password"] {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    input[type="text"]::placeholder, input[type="password"]::placeholder {
        color: #cbd5e1 !important;
    }
    div.stSelectbox label, div.stTextInput label, div.stRadio label {
        font-weight: 600 !important;
        color: #1e293b !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.3px !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] * { color: #1e293b !important; }

    div[data-testid="stSuccessMessage"] {
        background: rgba(16,185,129,0.08) !important;
        border: 1.5px solid rgba(16,185,129,0.3) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stWarningMessage"] {
        background: rgba(245,158,11,0.08) !important;
        border: 1.5px solid rgba(245,158,11,0.3) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stErrorMessage"] {
        background: rgba(239,68,68,0.08) !important;
        border: 1.5px solid rgba(239,68,68,0.3) !important;
        border-radius: 10px !important;
    }

    @media (max-width: 768px) {
        .sf-header-title { font-size: 2.8rem !important; }
        .block-container {
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }
        .sf-card    { padding: 16px 14px; }
        .sf-output  { padding: 14px 12px; }
        .sf-answers { padding: 14px 12px; }
        .sf-fullpaper { padding: 14px 12px; }

        .stSelectbox > div > div {
            min-height: 48px !important;
            font-size: 15px !important;
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
        .sf-watermark {
            text-align: center !important;
            width: 100% !important;
            display: block !important;
        }
    }
    </style>
""", unsafe_allow_html=True)
# ═════════════════════════════════════════════════════════════════════════════
# STEP 3: HELPER FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

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

def count_words(text):
    return len(text.split())

def add_to_history(tool, chapter, subject, result_preview):
    if "history" not in st.session_state:
        st.session_state.history = []
    entry = {
        "time": time.strftime("%H:%M"),
        "tool": tool,
        "chapter": chapter,
        "subject": subject,
        "preview": result_preview[:120] + "..." if len(result_preview) > 120 else result_preview
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:5]


# ═════════════════════════════════════════════════════════════════════════════
# STEP 4A: BOARD-AWARE QUESTION PAPER FORMAT BUILDER
# Returns the exact academic format spec for any board/class/level
# ═════════════════════════════════════════════════════════════════════════════

def get_qp_format_spec(board, course, subject):
    """
    Returns a structured dict describing the OFFICIAL question paper format
    for the given board + course + subject combination.
    No web fetch needed — the AI is instructed to use its own knowledge of
    official formats, and we supply the structural skeleton it must follow.
    """
    board_up = board.upper()

    # ── K-12 CBSE ────────────────────────────────────────────────────────────
    if "CBSE" in board_up:
        if any(c in course for c in ["10", "X", "Class 10"]):
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "SUMMATIVE ASSESSMENT / BOARD EXAMINATION",
                "class_label": "CLASS X",
                "total_marks": 80,
                "time": "3 Hours",
                "instructions": [
                    "This question paper contains 5 Sections — A, B, C, D and E.",
                    "Section A has 20 MCQs carrying 1 mark each.",
                    "Section B has 5 Very Short Answer questions carrying 2 marks each.",
                    "Section C has 6 Short Answer questions carrying 3 marks each.",
                    "Section D has 4 Long Answer questions carrying 5 marks each.",
                    "Section E has 3 Source/Case-Based questions carrying 4 marks each.",
                    "There is no overall choice. However, internal choices are provided.",
                    "Use of calculator is NOT allowed.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ", "q_count": 20, "marks_each": 1, "total": 20},
                    {"name": "SECTION B", "type": "Very Short Answer (VSA)", "q_count": 5, "marks_each": 2, "total": 10},
                    {"name": "SECTION C", "type": "Short Answer (SA)", "q_count": 6, "marks_each": 3, "total": 18},
                    {"name": "SECTION D", "type": "Long Answer (LA)", "q_count": 4, "marks_each": 5, "total": 20},
                    {"name": "SECTION E", "type": "Case/Source-Based", "q_count": 3, "marks_each": 4, "total": 12},
                ],
            }
        elif any(c in course for c in ["12", "XII", "Class 12"]):
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "BOARD EXAMINATION",
                "class_label": "CLASS XII",
                "total_marks": 70,
                "time": "3 Hours",
                "instructions": [
                    "This question paper contains 5 Sections — A, B, C, D and E.",
                    "Section A has 18 MCQs carrying 1 mark each.",
                    "Section B has 4 Very Short Answer questions carrying 2 marks each.",
                    "Section C has 5 Short Answer questions carrying 3 marks each.",
                    "Section D has 2 Long Answer questions carrying 5 marks each.",
                    "Section E has 3 Case/Source-Based questions carrying 4 marks each.",
                    "Internal choices are provided in Sections B, C and D.",
                    "Use of calculator is NOT allowed.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ", "q_count": 18, "marks_each": 1, "total": 18},
                    {"name": "SECTION B", "type": "Very Short Answer (VSA)", "q_count": 4, "marks_each": 2, "total": 8},
                    {"name": "SECTION C", "type": "Short Answer (SA)", "q_count": 5, "marks_each": 3, "total": 15},
                    {"name": "SECTION D", "type": "Long Answer (LA)", "q_count": 2, "marks_each": 5, "total": 10},
                    {"name": "SECTION E", "type": "Case/Source-Based", "q_count": 3, "marks_each": 4, "total": 12},
                ],
            }
        else:
            # CBSE generic (Classes 6-9, 11)
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "ANNUAL EXAMINATION",
                "class_label": course.upper(),
                "total_marks": 80,
                "time": "3 Hours",
                "instructions": [
                    "This question paper has 4 Sections — A, B, C and D.",
                    "Section A: 20 MCQs (1 mark each).",
                    "Section B: 6 Short Answer questions (2 marks each).",
                    "Section C: 6 Short Answer questions (3 marks each).",
                    "Section D: 4 Long Answer questions (5 marks each).",
                    "All questions are compulsory.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ", "q_count": 20, "marks_each": 1, "total": 20},
                    {"name": "SECTION B", "type": "Short Answer I (SA-I)", "q_count": 6, "marks_each": 2, "total": 12},
                    {"name": "SECTION C", "type": "Short Answer II (SA-II)", "q_count": 6, "marks_each": 3, "total": 18},
                    {"name": "SECTION D", "type": "Long Answer (LA)", "q_count": 4, "marks_each": 5, "total": 20},
                ],
            }

    # ── K-12 ICSE / ISC ──────────────────────────────────────────────────────
    elif "ICSE" in board_up or "ISC" in board_up:
        if any(c in course for c in ["12", "XII"]) or "ISC" in board_up:
            return {
                "board_label": "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
                "exam_label": "INDIAN SCHOOL CERTIFICATE EXAMINATION (ISC)",
                "class_label": "CLASS XII",
                "total_marks": 70,
                "time": "3 Hours",
                "instructions": [
                    "Attempt ALL questions in Section A and any FOUR from Section B.",
                    "Section A is compulsory and contains MCQs and short answers.",
                    "Section B contains structured/essay-type questions.",
                    "The intended marks for questions are given in brackets [ ].",
                    "Neat diagrams must be drawn wherever necessary.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ + Assertion-Reason + Short Answer", "q_count": 15, "marks_each": "varies", "total": 30},
                    {"name": "SECTION B", "type": "Structured / Essay-Type (Attempt any 4 of 6)", "q_count": 6, "marks_each": 10, "total": 40},
                ],
            }
        else:
            return {
                "board_label": "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
                "exam_label": "INDIAN CERTIFICATE OF SECONDARY EDUCATION (ICSE)",
                "class_label": "CLASS X",
                "total_marks": 80,
                "time": "2 Hours",
                "instructions": [
                    "Attempt ALL questions from Section A and any FOUR from Section B.",
                    "All working, including rough work, must be shown clearly.",
                    "The intended marks for questions are given in brackets [ ].",
                    "Mathematical tables are provided.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ + Short Answer (Compulsory)", "q_count": 10, "marks_each": "varies", "total": 40},
                    {"name": "SECTION B", "type": "Long Answer (Attempt any 4 of 6)", "q_count": 6, "marks_each": 10, "total": 40},
                ],
            }

    # ── IB ────────────────────────────────────────────────────────────────────
    elif "IB" in board_up:
        return {
            "board_label": "INTERNATIONAL BACCALAUREATE ORGANIZATION",
            "exam_label": "IB DIPLOMA PROGRAMME — FINAL EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 100,
            "time": "2 Hours 30 Minutes",
            "instructions": [
                "Do NOT open this examination paper until instructed.",
                "Answer ALL questions in Paper 1 (Section A).",
                "Answer TWO questions from Paper 2 (Section B).",
                "Show all working. Where not asked, a correct answer alone will not earn marks.",
                "Diagrams and graphs must be drawn in pencil.",
            ],
            "sections": [
                {"name": "PAPER 1 / SECTION A", "type": "Structured (Data-based / MCQ)", "q_count": 30, "marks_each": 1, "total": 30},
                {"name": "PAPER 2 / SECTION B", "type": "Extended Response (Choose 2 of 4)", "q_count": 4, "marks_each": 25, "total": 50},
                {"name": "PAPER 3 / SECTION C", "type": "Option / Case Study", "q_count": 2, "marks_each": 10, "total": 20},
            ],
        }

    # ── Cambridge IGCSE / A-Level ─────────────────────────────────────────────
    elif "CAMBRIDGE" in board_up:
        return {
            "board_label": "CAMBRIDGE ASSESSMENT INTERNATIONAL EDUCATION",
            "exam_label": "CAMBRIDGE IGCSE / A LEVEL EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 80,
            "time": "2 Hours",
            "instructions": [
                "Write your name, centre number and candidate number on your answer booklet.",
                "Answer ALL questions in Section A.",
                "Answer any THREE questions from Section B.",
                "Write in dark blue or black pen.",
                "Do not use staples, paper clips, glue or correction fluid.",
            ],
            "sections": [
                {"name": "SECTION A", "type": "Structured Questions (Compulsory)", "q_count": 10, "marks_each": 4, "total": 40},
                {"name": "SECTION B", "type": "Essay / Extended Response (Choose 3 of 5)", "q_count": 5, "marks_each": 12, "total": 36},
            ],
        }

    # ── University / Medical / Engineering / UG-PG ────────────────────────────
    else:
        if any(k in course.upper() for k in ["MBBS", "BDS", "MD", "MEDICAL"]):
            return {
                "board_label": "UNIVERSITY EXAMINATIONS",
                "exam_label": f"{course.upper()} PROFESSIONAL EXAMINATION",
                "class_label": course.upper(),
                "total_marks": 100,
                "time": "3 Hours",
                "instructions": [
                    "Answer ALL questions in Part A.",
                    "Answer any FIVE questions from Part B.",
                    "Diagrams must be neat, labelled and relevant.",
                    "Clinical relevance and applied aspects will be given due credit.",
                    "Write legibly; illegible answers will not be evaluated.",
                ],
                "sections": [
                    {"name": "PART A — SHORT NOTES", "type": "Short Notes (2–3 paragraphs each)", "q_count": 10, "marks_each": 5, "total": 50},
                    {"name": "PART B — LONG ESSAYS", "type": "Long Essays (Attempt any 5 of 8)", "q_count": 8, "marks_each": 10, "total": 50},
                ],
            }
        elif any(k in course.upper() for k in ["B.TECH", "B.E", "ENGINEERING"]):
            return {
                "board_label": "UNIVERSITY EXAMINATIONS",
                "exam_label": f"{course.upper()} END SEMESTER EXAMINATION",
                "class_label": course.upper(),
                "total_marks": 100,
                "time": "3 Hours",
                "instructions": [
                    "Answer any FIVE full questions, choosing one from each module.",
                    "Missing data if any may be suitably assumed.",
                    "Use of scientific calculator is permitted.",
                    "Draw neat circuit/block diagrams wherever required.",
                ],
                "sections": [
                    {"name": "MODULE 1", "type": "Q1 OR Q2 (10 marks each)", "q_count": 2, "marks_each": 10, "total": 10},
                    {"name": "MODULE 2", "type": "Q3 OR Q4 (10 marks each)", "q_count": 2, "marks_each": 10, "total": 10},
                    {"name": "MODULE 3", "type": "Q5 OR Q6 (10 marks each)", "q_count": 2, "marks_each": 10, "total": 10},
                    {"name": "MODULE 4", "type": "Q7 OR Q8 (10 marks each)", "q_count": 2, "marks_each": 10, "total": 10},
                    {"name": "MODULE 5", "type": "Q9 OR Q10 (10 marks each)", "q_count": 2, "marks_each": 10, "total": 10},
                ],
            }
        else:
            # Generic university
            return {
                "board_label": "UNIVERSITY EXAMINATIONS",
                "exam_label": f"{course.upper()} SEMESTER EXAMINATION",
                "class_label": course.upper(),
                "total_marks": 100,
                "time": "3 Hours",
                "instructions": [
                    "Answer ALL questions in Section A.",
                    "Answer any FIVE questions from Section B.",
                    "Answer any TWO questions from Section C.",
                    "Figures in brackets indicate marks.",
                ],
                "sections": [
                    {"name": "SECTION A", "type": "Short Answer (Compulsory)", "q_count": 10, "marks_each": 2, "total": 20},
                    {"name": "SECTION B", "type": "Medium Answer (Attempt 5 of 8)", "q_count": 8, "marks_each": 5, "total": 40},
                    {"name": "SECTION C", "type": "Long Essay (Attempt 2 of 4)", "q_count": 4, "marks_each": 10, "total": 40},
                ],
            }


# ═════════════════════════════════════════════════════════════════════════════
# STEP 4B: PROMPT BUILDER
# ═════════════════════════════════════════════════════════════════════════════

def build_prompt(tool, chapter, topic, subject, audience, output_style, board="", course=""):
    base_context = f"""
You are an expert educator creating study material for {audience}.
Subject: {subject} | Topic: {topic} | Chapter: {chapter}
Requirements: Accurate, Exam-focused, Well-structured, With examples, Error-free.
"""

    if tool == "📝 Summary":
        if output_style == "📄 Detailed":
            return base_context + """
Create a comprehensive summary with:
- Chapter Overview (150-200 words)
- Key Concepts (300-400 words)
- Formulas and Definitions
- 2-3 Worked Examples
- Real-world Applications
- Common Mistakes to Avoid
- Quick Revision Points (100 words)
- Exam Important Points
"""
        elif output_style == "⚡ Short & Quick":
            return base_context + """
Create a quick reference guide (500 words max) with:
- One-line Definition
- 5-7 Key Points
- 3 Important Formulas
- 2 Quick Examples
- Exam Tips
"""
        else:
            return base_context + """
Create notebook-style notes with:
- Title and Date
- Main Ideas
- Sub-topics with bullet points
- Formulas boxed separately
- Examples
- Quick Facts
"""

    elif tool == "🧠 Quiz":
        return base_context + """
Create a complete quiz with:
- Section A: 5 MCQs with 4 options each (mark correct answer)
- Section B: 5 Short Answer Questions (50-100 words each)
- Section C: 3 Long Answer Questions (200+ words each)
- Full Answer Key with detailed explanations
"""

    elif tool == "📌 Revision Notes":
        return base_context + """
Create revision notes with:
- Top 10 Must-Know Points
- Mind Map in text format
- Formula Sheet
- Diagram Descriptions
- Important Definitions
- Comparison Tables
- Exam Pattern Focus Areas
- Memory Tricks and Mnemonics
"""

    elif tool == "🧪 Question Paper":
        # ── Academic-format chapter-level question paper ──────────────────────
        fmt = get_qp_format_spec(board, course, subject)
        instructions_text = "\n".join([f"  {i+1}. {ins}" for i, ins in enumerate(fmt["instructions"])])
        sections_text = "\n".join([
            f"  • {s['name']} — {s['type']} | {s['q_count']} questions × {s['marks_each']} marks = {s['total']} marks"
            for s in fmt["sections"]
        ])

        return f"""
You are a {fmt['board_label']} official question paper setter.
Create a CHAPTER-LEVEL question paper STRICTLY following the format below.

═══════════════════════════════════════════════════════
{fmt['board_label']}
{fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
Subject: {subject}   Chapter: {chapter}
Maximum Marks: {fmt['total_marks']}     Time Allowed: {fmt['time']}
═══════════════════════════════════════════════════════

GENERAL INSTRUCTIONS (print these at the top):
{instructions_text}

PAPER STRUCTURE YOU MUST FOLLOW EXACTLY:
{sections_text}
Total: {fmt['total_marks']} marks

RULES FOR QUESTION GENERATION:
1. Number every question clearly (Q1, Q2 … within each section).
2. For MCQs: provide exactly 4 options labelled (a) (b) (c) (d). Do NOT mark the answer.
3. For Short/Long Answer: write the question and show marks in brackets e.g. [3 marks].
4. Include internal choices where appropriate (e.g., "OR") as per the board pattern.
5. Cover all major sub-topics of Chapter: {chapter}.
6. Difficulty split: 30% easy, 50% medium, 20% hard.
7. DO NOT provide answers or hints anywhere in this paper.
8. Maintain the official tone — no casual language.

Now generate the complete question paper.
"""

    elif tool == "❓ Exam Q&A":
        return base_context + """
Create a complete Q&A bank with:
- 8-10 Frequently Asked Questions
- 5 Conceptual Questions with answers
- 5 Application-Based Questions with answers
- 3 Comparison Questions with answers
- 5 'Why/How' Questions with answers
- 3-5 Solved Numerical/Practical Problems
Each answer: 150-300 words minimum with examples
"""

    elif output_style == "🧪 Question Paper":
        fmt = get_qp_format_spec(board, course, subject)
        instructions_text = "\n".join([f"  {i+1}. {ins}" for i, ins in enumerate(fmt["instructions"])])
        sections_text = "\n".join([
            f"  • {s['name']} — {s['type']} | {s['q_count']} questions × {s['marks_each']} marks = {s['total']} marks"
            for s in fmt["sections"]
        ])
        return f"""
You are a {fmt['board_label']} official question paper setter.
Create a question paper for Chapter: {chapter} strictly following the official format below.

{fmt['board_label']}
{fmt['exam_label']} | {fmt['class_label']}
Subject: {subject} | Maximum Marks: {fmt['total_marks']} | Time: {fmt['time']}

INSTRUCTIONS:
{instructions_text}

STRUCTURE:
{sections_text}

Rules: Number all questions. MCQs must have (a)(b)(c)(d). Show marks in brackets.
DO NOT include answers. Maintain official board tone.
"""

    return base_context + "Create comprehensive and exam-ready study material."


def build_answers_prompt(chapter, topic, subject, audience, question_paper_text):
    """Generate answers strictly matching the provided question paper."""
    return f"""
You are an expert educator. Below is a question paper given to students.
Provide COMPLETE and DETAILED answers for EVERY question in this paper.

Subject: {subject} | Topic: {topic} | Chapter: {chapter} | Audience: {audience}

===== QUESTION PAPER =====
{question_paper_text}
===== END OF PAPER =====

Write the ANSWER KEY:
- MCQs: State the correct option letter AND a brief explanation (2-3 lines).
- Very Short Answer: 2-4 concise lines.
- Short Answer: 4-6 lines with examples.
- Long Answer: Detailed 200-300 words with diagrams described in text, examples, key points.
- Case/Source-Based: Full analysis and all sub-question answers.

Label each answer clearly matching the question number and section.
Be accurate, educational, and thorough. Maintain academic tone.
"""


def build_full_subject_qp_prompt(board, course, stream, subject, category):
    """
    Build a prompt for a FULL SUBJECT question paper covering the complete syllabus.
    """
    fmt = get_qp_format_spec(board, course, subject)
    instructions_text = "\n".join([f"  {i+1}. {ins}" for i, ins in enumerate(fmt["instructions"])])
    sections_text = "\n".join([
        f"  • {s['name']} — {s['type']} | {s['q_count']} questions × {s['marks_each']} marks = {s['total']} marks"
        for s in fmt["sections"]
    ])

    return f"""
You are an official question paper setter for {fmt['board_label']}.
Generate a COMPLETE FULL-SYLLABUS question paper for the subject below.

═══════════════════════════════════════════════════════════════════
{fmt['board_label']}
{fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
Subject: {subject}   Stream/Branch: {stream}
Maximum Marks: {fmt['total_marks']}     Time Allowed: {fmt['time']}
═══════════════════════════════════════════════════════════════════

GENERAL INSTRUCTIONS (print verbatim at the top of the paper):
{instructions_text}

OFFICIAL PAPER STRUCTURE (follow this EXACTLY):
{sections_text}
Total: {fmt['total_marks']} marks

SYLLABUS COVERAGE RULES:
1. This is a FULL SUBJECT paper — cover ALL major chapters/units of {subject} for {course}.
2. Questions must be spread across the entire syllabus proportionally.
3. Do NOT focus on one chapter — distribute questions across all units.
4. Number questions continuously within each section (Q1, Q2, Q3 ...).
5. MCQs must have exactly 4 options labelled (a) (b) (c) (d). Do NOT mark correct answers.
6. Show marks in square brackets [X marks] after every question.
7. Provide internal choices (OR) where the board format requires it.
8. Difficulty: 30% easy (recall), 50% medium (application), 20% hard (analysis/evaluation).
9. Maintain STRICT official academic language — no casual phrasing.
10. DO NOT include answers or hints anywhere in this paper.
11. Include diagrams as "Draw a neat labelled diagram of X" type instructions.

Generate the full question paper now — complete, exam-ready, and properly formatted.
"""


# ═════════════════════════════════════════════════════════════════════════════
# STEP 5: AI GENERATION ENGINE  (temperature=0.1 for consistency)
# ═════════════════════════════════════════════════════════════════════════════

def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return (
            "⚠️ API key missing!\n\n"
            "1. Create `.streamlit/secrets.toml`\n"
            "2. Add: `GEMINI_API_KEY = \"your_key_here\"`\n"
            "3. Get your free key at https://aistudio.google.com/app/apikey",
            "None"
        )
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Gemini configuration failed: {str(e)}", "None")

    available_models = []
    try:
        models = genai.list_models()
        for m in models:
            name = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "gemini" in name.lower() and "generateContent" in methods:
                available_models.append(name)
    except Exception as e:
        return (f"❌ Could not list Gemini models: {str(e)}", "None")

    if not available_models:
        return ("❌ No Gemini models available for this API key.", "None")

    last_error = "Unknown error"
    for model_name in available_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,        # ✅ Consistent results
                    max_output_tokens=8192, # ✅ Full-subject papers need more tokens
                    top_p=0.95,
                ),
            )
            if response and getattr(response, "text", None):
                return response.text, model_name
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            continue

    return (
        f"❌ All AI models failed.\n\n**Last error:** {last_error}\n\n"
        "- Check your API key is active\n"
        "- Check internet connection\n"
        "- Try again after a few minutes",
        "None"
    )


# ═════════════════════════════════════════════════════════════════════════════
# STEP 6: PDF GENERATION
# ═════════════════════════════════════════════════════════════════════════════

def generate_pdf(title, subtitle, content, header_color="#1d4ed8"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm
    )
    styles = getSampleStyleSheet()
    story  = []

    story.append(Paragraph(title, ParagraphStyle(
        "T", parent=styles["Heading1"], fontSize=22,
        textColor=colors.HexColor(header_color),
        spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold"
    )))
    story.append(Paragraph(subtitle, ParagraphStyle(
        "S", parent=styles["Normal"], fontSize=11,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=10, alignment=TA_CENTER, fontName="Helvetica"
    )))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=colors.HexColor(header_color), spaceAfter=16
    ))

    body_style = ParagraphStyle(
        "B", parent=styles["Normal"], fontSize=10.5,
        textColor=colors.HexColor("#1e293b"),
        leading=16, spaceAfter=6, fontName="Helvetica"
    )
    heading_style = ParagraphStyle(
        "H", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor(header_color),
        spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"
    )
    bullet_style = ParagraphStyle(
        "BL", parent=styles["Normal"], fontSize=10.5,
        textColor=colors.HexColor("#334155"),
        leading=15, leftIndent=16, spaceAfter=4,
        bulletIndent=6, fontName="Helvetica"
    )

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2*cm)); continue
        if line.startswith("####"):
            story.append(Paragraph(line.lstrip("#").strip(), body_style))
        elif line.startswith(("###", "##", "#")):
            story.append(Paragraph(line.lstrip("#").strip(), heading_style))
        elif line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(f"<b>{line.replace('**','')}</b>", body_style))
        elif line.startswith(("- ", "• ", "* ")):
            safe = line[2:].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(f"• {safe}", bullet_style))
        elif line and line[0].isdigit() and ". " in line[:5]:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, bullet_style))
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, body_style))

    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1,
        color=colors.HexColor("#e2e8f0"), spaceAfter=6))
    story.append(Paragraph(
        f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle("F", parent=styles["Normal"], fontSize=8,
            textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer
# ═════════════════════════════════════════════════════════════════════════════
# STEP 7: SESSION STATE INIT
# ═════════════════════════════════════════════════════════════════════════════

def init_session_state():
    defaults = {
        "logged_in": False,
        "username": "",
        "current_chapters": [],
        "history": [],
        "last_chapter_key": "",
        # Generated content
        "generated_result": None,
        "generated_model": None,
        "generated_tool": None,
        "generated_chapter": None,
        "generated_subject": None,
        "generated_topic": None,
        "generated_course": None,
        "generated_stream": None,
        "generated_board": None,
        "generated_audience": None,
        "generated_output_style": None,
        # Answers
        "answers_result": None,
        "answers_model": None,
        "show_answers": False,
        # Full subject paper
        "fullpaper_result": None,
        "fullpaper_model": None,
        "show_fullpaper": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ═════════════════════════════════════════════════════════════════════════════
# STEP 8: MAIN APP UI
# ═════════════════════════════════════════════════════════════════════════════

def main_app():

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center; padding:20px 0 15px 0;">
                <div style="font-size:3rem; margin-bottom:8px;">🎓</div>
                <div style="font-size:1.4rem; font-weight:800;
                     background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     background-clip:text;">StudySmart</div>
                <div style="font-size:0.9rem;color:#64748b;margin-top:6px;">
                    Welcome, {st.session_state.username} 👋
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        tool = st.radio("SELECT TOOL", [
            "📝 Summary", "🧠 Quiz", "📌 Revision Notes",
            "🧪 Question Paper", "❓ Exam Q&A"
        ])
        st.divider()

        with st.expander("📜 Recent History"):
            history = st.session_state.get("history", [])
            if not history:
                st.caption("No history yet. Generate something first!")
            else:
                for h in history:
                    st.markdown(f"""
                        <div class="sf-history-item">
                            🕐 {h['time']} &nbsp;|&nbsp; <b>{h['tool']}</b><br/>
                            📖 {h['chapter']} — {h['subject']}<br/>
                            <small style="opacity:0.7">{h['preview']}</small>
                        </div>
                    """, unsafe_allow_html=True)

        st.divider()
        with st.expander("🤖 AI Model Status"):
            if st.button("Check Models", use_container_width=True):
                with st.spinner("Checking..."):
                    models = get_available_models()
                for m in models:
                    st.write(f"✅ {m}")
        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in","username","history","generated_result",
                      "answers_result","show_answers","fullpaper_result","show_fullpaper"]:
                st.session_state[k] = False if k == "logged_in" else (
                    "" if k == "username" else ([] if k == "history" else None))
            st.session_state.show_answers   = False
            st.session_state.show_fullpaper = False
            st.rerun()

    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">StudySmart</div>
            <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
        </div>
        <div class="sf-watermark">POWERED BY AI</div>
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

    if category == "K-12th":
        board = st.selectbox("🏫 Board", BOARDS)
    else:
        board = "University / National Syllabus"

    topic = st.selectbox("🗂️ Topic", get_topics(category, course, stream, subject))

    chapter_key = f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.get("last_chapter_key") != chapter_key:
        st.session_state.current_chapters   = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key   = chapter_key
        st.session_state.generated_result   = None
        st.session_state.answers_result     = None
        st.session_state.show_answers       = False
        st.session_state.fullpaper_result   = None
        st.session_state.show_fullpaper     = False

    chapter = st.selectbox("📝 Chapter", st.session_state.get("current_chapters", ["No chapters found"]))
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Output Style ────────────────────────────────────────────────────────────
    output_style = st.radio(
        "⚙️ Output Style",
        ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format", "🧪 Question Paper"],
        horizontal=True
    )
    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)

    # ── Generate Button ─────────────────────────────────────────────────────────
    if st.button(f"✨ Generate {tool}", use_container_width=True):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter before generating.")
            return

        audience     = f"{board} {course} students" if category == "K-12th" else f"{course} students"
        final_prompt = build_prompt(tool, chapter, topic, subject, audience,
                                    output_style, board=board, course=course)

        with st.spinner(f"🧠 Generating {tool}... please wait ⏳"):
            result, model_used = generate_with_fallback(final_prompt)

        st.session_state.generated_result       = result
        st.session_state.generated_model        = model_used
        st.session_state.generated_tool         = tool
        st.session_state.generated_chapter      = chapter
        st.session_state.generated_subject      = subject
        st.session_state.generated_topic        = topic
        st.session_state.generated_course       = course
        st.session_state.generated_stream       = stream
        st.session_state.generated_board        = board
        st.session_state.generated_audience     = audience
        st.session_state.generated_output_style = output_style
        st.session_state.answers_result         = None
        st.session_state.show_answers           = False
        st.session_state.fullpaper_result       = None
        st.session_state.show_fullpaper         = False

        if model_used != "None":
            add_to_history(tool, chapter, subject, result)

    # ── Display Generated Content ───────────────────────────────────────────────
    if st.session_state.generated_result and st.session_state.generated_model != "None":

        result     = st.session_state.generated_result
        model_used = st.session_state.generated_model
        g_tool     = st.session_state.generated_tool
        g_chapter  = st.session_state.generated_chapter
        g_subject  = st.session_state.generated_subject
        g_topic    = st.session_state.generated_topic
        g_course   = st.session_state.generated_course
        g_stream   = st.session_state.generated_stream
        g_board    = st.session_state.generated_board
        g_audience = st.session_state.generated_audience
        g_style    = st.session_state.generated_output_style

        st.markdown("---")
        col_a, col_b = st.columns(2)
        col_a.metric("🤖 Model Used",
            model_used.split("/")[-1] if "/" in model_used else model_used)
        col_b.metric("📝 Word Count", f"{count_words(result):,}")

        st.markdown('<div class="sf-output">', unsafe_allow_html=True)
        st.markdown(f"### {g_tool} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        is_question_paper = (
            g_tool  == "🧪 Question Paper" or
            g_style == "🧪 Question Paper"
        )

        # ── Question Paper specific buttons ──────────────────────────────────
        if is_question_paper:
            st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)

            # Download chapter question paper
            try:
                qp_pdf = generate_pdf(
                    f"Question Paper — {g_chapter}",
                    f"{g_subject} | {g_board} | {g_course}",
                    result, header_color="#1d4ed8"
                )
                safe_qp = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_QP.pdf"
                st.download_button(
                    "⬇️ Download Question Paper as PDF",
                    data=qp_pdf, file_name=safe_qp,
                    mime="application/pdf",
                    use_container_width=True, key="dl_qp"
                )
            except Exception as e:
                st.warning(f"⚠️ PDF failed: {e}")

            st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)

            # ── GET ANSWERS button ────────────────────────────────────────────
            if st.button("📋 Get Answers", use_container_width=True, key="get_answers_btn"):
                with st.spinner("📚 Generating detailed answer key... please wait ⏳"):
                    ans_prompt = build_answers_prompt(
                        g_chapter, g_topic, g_subject, g_audience, result
                    )
                    ans_result, ans_model = generate_with_fallback(ans_prompt)
                st.session_state.answers_result = ans_result
                st.session_state.answers_model  = ans_model
                st.session_state.show_answers   = True

            # Display answers
            if st.session_state.show_answers and st.session_state.answers_result:
                ans_result = st.session_state.answers_result
                ans_model  = st.session_state.answers_model
                if ans_model != "None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 📚 Answer Key — {g_chapter}")
                    st.markdown(ans_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        ans_pdf = generate_pdf(
                            f"Answer Key — {g_chapter}",
                            f"{g_subject} | {g_board} | {g_course}",
                            ans_result, header_color="#16a34a"
                        )
                        safe_ans = g_chapter.replace(" ","_").replace(":","").replace("/","-") + "_Answers.pdf"
                        st.download_button(
                            "⬇️ Download Answer Key as PDF",
                            data=ans_pdf, file_name=safe_ans,
                            mime="application/pdf",
                            use_container_width=True, key="dl_ans"
                        )
                        st.info("✅ Answer Key PDF ready — click above to download.")
                    except Exception as e:
                        st.warning(f"⚠️ Answer PDF failed: {e}")
                else:
                    st.error("❌ Failed to generate answers. Please try again.")
                    st.markdown(ans_result)

            # ─────────────────────────────────────────────────────────────────
            # ✅ NEW: GENERATE FULL SUBJECT QUESTION PAPER
            # ─────────────────────────────────────────────────────────────────
            st.markdown("---")
            st.markdown("""
                <div style="background:linear-gradient(135deg,rgba(139,92,246,0.08),rgba(109,40,217,0.08));
                     border-radius:14px;padding:20px 24px;border:1px solid rgba(139,92,246,0.2);
                     margin-bottom:12px;">
                    <div style="font-size:1.1rem;font-weight:700;color:#7c3aed;margin-bottom:6px;">
                        📋 Generate Full Subject Question Paper
                    </div>
                    <div style="font-size:0.88rem;color:#64748b;">
                        Generate a <strong>complete exam paper covering the entire syllabus</strong>
                        of <strong>{subject}</strong> — strictly following the official
                        <strong>{board}</strong> format for <strong>{course}</strong>.
                    </div>
                </div>
            """.format(
                subject=g_subject, board=g_board, course=g_course
            ), unsafe_allow_html=True)

            if st.button(
                f"🗂️ Generate Full {g_subject} Question Paper ({g_board})",
                use_container_width=True, key="full_qp_btn"
            ):
                with st.spinner(
                    f"📄 Generating full {g_subject} question paper for {g_board} {g_course}... ⏳"
                ):
                    full_prompt = build_full_subject_qp_prompt(
                        g_board, g_course, g_stream, g_subject, g_subject
                    )
                    full_result, full_model = generate_with_fallback(full_prompt)
                st.session_state.fullpaper_result = full_result
                st.session_state.fullpaper_model  = full_model
                st.session_state.show_fullpaper   = True

            # Display full subject paper
            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                full_result = st.session_state.fullpaper_result
                full_model  = st.session_state.fullpaper_model
                if full_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Question Paper — {g_subject} ({g_board} {g_course})")
                    st.markdown(full_result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    try:
                        full_pdf = generate_pdf(
                            f"Full Question Paper — {g_subject}",
                            f"{g_board} | {g_course} | {g_stream}",
                            full_result, header_color="#7c3aed"
                        )
                        safe_full = f"{g_subject}_{g_board}_{g_course}_FullPaper.pdf".replace(" ","_")
                        st.download_button(
                            "⬇️ Download Full Subject Question Paper as PDF",
                            data=full_pdf, file_name=safe_full,
                            mime="application/pdf",
                            use_container_width=True, key="dl_full"
                        )
                        st.info("✅ Full Subject Question Paper PDF ready — click above to download.")
                    except Exception as e:
                        st.warning(f"⚠️ PDF generation failed: {e}")
                else:
                    st.error("❌ Failed to generate full subject question paper.")
                    st.markdown(full_result)

        # ── Non-question-paper PDF download ────────────────────────────────────
        else:
            st.markdown("---")
            try:
                pdf_buffer = generate_pdf(
                    f"{g_tool} — {g_chapter}",
                    f"{g_subject} | {g_topic} | {g_course}",
                    result
                )
                safe_name = g_chapter.replace(" ","_").replace(":","").replace("/","-") + ".pdf"
                st.download_button(
                    "⬇️ Download as PDF",
                    data=pdf_buffer, file_name=safe_name,
                    mime="application/pdf",
                    use_container_width=True, key="dl_main"
                )
                st.info("✅ PDF ready — click above to download.")
            except Exception as e:
                st.warning(f"⚠️ PDF generation failed: {e}")

    elif st.session_state.generated_result and st.session_state.generated_model == "None":
        st.markdown("---")
        st.error("❌ AI Generation Failed")
        st.markdown(st.session_state.generated_result)


# ═════════════════════════════════════════════════════════════════════════════
# STEP 9: AUTH UI
# ═════════════════════════════════════════════════════════════════════════════

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

        with tab1:
            u = st.text_input("👤 Username", key="login_u", placeholder="Enter your username")
            p = st.text_input("🔑 Password", type="password", key="login_p", placeholder="Enter your password")
            if st.button("Sign In 🚀", use_container_width=True):
                if u.strip() and p.strip():
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username=? AND password=?",
                              (u.strip(), hash_p(p)))
                    user = c.fetchone()
                    conn.close()
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username  = u.strip()
                        st.success("✅ Login successful! Loading app...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
                else:
                    st.warning("⚠️ Please fill in both fields")

        with tab2:
            nu = st.text_input("👤 New Username", key="reg_u", placeholder="Min 3 characters")
            np = st.text_input("🔑 New Password", type="password", key="reg_p", placeholder="Min 6 characters")
            cp = st.text_input("🔑 Confirm Password", type="password", key="reg_cp", placeholder="Re-enter password")
            if st.button("Create Account ✨", use_container_width=True):
                if not nu.strip():
                    st.error("❌ Username cannot be empty")
                elif len(nu.strip()) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif not np.strip():
                    st.error("❌ Password cannot be empty")
                elif len(np.strip()) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif np != cp:
                    st.error("❌ Passwords do not match.")
                else:
                    try:
                        conn = sqlite3.connect("users.db")
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                  (nu.strip(), hash_p(np)))
                        conn.commit()
                        conn.close()
                        st.success("✅ Account created! Logging you in...")
                        time.sleep(1)
                        st.session_state.logged_in = True
                        st.session_state.username  = nu.strip()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already taken.")
        st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# STEP 10: ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

init_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
