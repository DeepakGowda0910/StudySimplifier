# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — APP v3.0
# Fixes included:
# - Dynamic generate button label based on selected output
# - Output Style "Question Paper" now truly generates question paper
# - Board/course specific question paper patterns
# - Get Answers now answers the exact generated paper
# - Full Subject Question Paper retained
# - Stable output with low temperature
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e8f0f7 100%);
}

.block-container {
    max-width: 1250px;
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
}

#MainMenu, footer, header {
    visibility: hidden;
}

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
}

.sf-header-subtitle {
    color: #64748b;
    font-weight: 500;
    margin-top: 8px;
}

.sf-card {
    background: rgba(255,255,255,0.88);
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid rgba(59,130,246,0.14);
    box-shadow: 0 4px 24px rgba(59,130,246,0.07);
    margin-bottom: 18px;
}

.sf-output {
    background: linear-gradient(135deg, rgba(59,130,246,0.05), rgba(37,99,235,0.05));
    border-left: 5px solid #2563eb;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(59,130,246,0.15);
    margin-top: 14px;
}

.sf-output h3, .sf-output h2 {
    color: #1d4ed8 !important;
    margin-top: 0;
}

.sf-answers {
    background: linear-gradient(135deg, rgba(34,197,94,0.05), rgba(22,163,74,0.05));
    border-left: 5px solid #16a34a;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(34,197,94,0.15);
    margin-top: 18px;
}

.sf-answers h3, .sf-answers h2 {
    color: #15803d !important;
    margin-top: 0;
}

.sf-fullpaper {
    background: linear-gradient(135deg, rgba(139,92,246,0.05), rgba(109,40,217,0.05));
    border-left: 5px solid #7c3aed;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(139,92,246,0.15);
    margin-top: 18px;
}

.sf-fullpaper h3, .sf-fullpaper h2 {
    color: #6d28d9 !important;
    margin-top: 0;
}

.sf-preview {
    background: rgba(15, 23, 42, 0.03);
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 14px;
    margin-bottom: 12px;
}

.sf-history-item {
    background: rgba(59,130,246,0.05);
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    font-size: 0.9rem;
}

.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.3rem !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.25) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

div[data-baseweb="select"] > div,
input[type="text"], input[type="password"] {
    border-radius: 10px !important;
}

@media (max-width: 768px) {
    .sf-header-title { font-size: 2.5rem !important; }
    .sf-card, .sf-output, .sf-answers, .sf-fullpaper { padding: 16px; }
}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# STEP 3: BASIC HELPERS
# ═════════════════════════════════════════════════════════════════════════════

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
    if err:
        return [f"Error: {err}"]
    if not working_models:
        return ["No Gemini models available for this API key"]
    return working_models

def get_effective_output_name(tool, output_style):
    """
    This fixes the button text and the actual generation mode.
    If Question Paper is selected in Output Style, it becomes Question Paper.
    """
    if output_style == "🧪 Question Paper":
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
    if tool == "🧪 Question Paper":
        return "Question Paper"
    if tool == "❓ Exam Q&A":
        return "Exam Q&A"
    return "Content"

def get_generate_button_label(tool, output_style):
    name = get_effective_output_name(tool, output_style)
    return f"✨ Generate {name}"
# ═════════════════════════════════════════════════════════════════════════════
# STEP 4: QUESTION PAPER FORMAT DEFINITIONS
# ═════════════════════════════════════════════════════════════════════════════

def get_qp_format_spec(board, course, subject):
    board_up = board.upper()

    if "CBSE" in board_up:
        if any(x in course for x in ["10", "X", "Class 10"]):
            return {
                "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
                "exam_label": "BOARD EXAMINATION",
                "class_label": "CLASS X",
                "total_marks": 80,
                "time": "3 Hours",
                "instructions": [
                    "This question paper contains Sections A, B, C, D and E.",
                    "All questions are compulsory.",
                    "Section A consists of objective type questions.",
                    "Internal choices are provided in some questions.",
                    "Use neat and clear presentation.",
                    "Do not write anything in the question paper except where instructed."
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ / Objective", "q_count": 20, "marks_each": 1, "total": 20},
                    {"name": "SECTION B", "type": "Very Short Answer", "q_count": 5, "marks_each": 2, "total": 10},
                    {"name": "SECTION C", "type": "Short Answer", "q_count": 6, "marks_each": 3, "total": 18},
                    {"name": "SECTION D", "type": "Long Answer", "q_count": 4, "marks_each": 5, "total": 20},
                    {"name": "SECTION E", "type": "Case / Source Based", "q_count": 3, "marks_each": 4, "total": 12},
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
                    "This question paper contains Sections A, B, C, D and E.",
                    "All questions are compulsory.",
                    "Section A consists of objective type questions.",
                    "Internal choices are provided in some questions.",
                    "Use neat and clear presentation."
                ],
                "sections": [
                    {"name": "SECTION A", "type": "MCQ / Objective", "q_count": 18, "marks_each": 1, "total": 18},
                    {"name": "SECTION B", "type": "Very Short Answer", "q_count": 4, "marks_each": 2, "total": 8},
                    {"name": "SECTION C", "type": "Short Answer", "q_count": 5, "marks_each": 3, "total": 15},
                    {"name": "SECTION D", "type": "Long Answer", "q_count": 2, "marks_each": 5, "total": 10},
                    {"name": "SECTION E", "type": "Case / Source Based", "q_count": 3, "marks_each": 4, "total": 12},
                ]
            }

        return {
            "board_label": "CENTRAL BOARD OF SECONDARY EDUCATION",
            "exam_label": "ANNUAL EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 80,
            "time": "3 Hours",
            "instructions": [
                "All questions are compulsory.",
                "Read all questions carefully before answering.",
                "Use proper numbering and show all workings where necessary."
            ],
            "sections": [
                {"name": "SECTION A", "type": "Objective", "q_count": 20, "marks_each": 1, "total": 20},
                {"name": "SECTION B", "type": "Short Answer I", "q_count": 6, "marks_each": 2, "total": 12},
                {"name": "SECTION C", "type": "Short Answer II", "q_count": 6, "marks_each": 3, "total": 18},
                {"name": "SECTION D", "type": "Long Answer", "q_count": 4, "marks_each": 5, "total": 20},
            ]
        }

    if "ICSE" in board_up:
        return {
            "board_label": "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label": "ICSE EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 80,
            "time": "2 Hours",
            "instructions": [
                "Attempt all questions from Section A.",
                "Attempt any four questions from Section B unless otherwise specified.",
                "The intended marks for questions are given in brackets [ ].",
                "Neatness and proper presentation will be rewarded."
            ],
            "sections": [
                {"name": "SECTION A", "type": "Compulsory Objective / Short Answer", "q_count": 10, "marks_each": "varied", "total": 40},
                {"name": "SECTION B", "type": "Descriptive", "q_count": 6, "marks_each": 10, "total": 40},
            ]
        }

    if "ISC" in board_up:
        return {
            "board_label": "COUNCIL FOR THE INDIAN SCHOOL CERTIFICATE EXAMINATIONS",
            "exam_label": "ISC EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 70,
            "time": "3 Hours",
            "instructions": [
                "Attempt all questions from Section A.",
                "Attempt any four questions from Section B unless otherwise specified.",
                "The intended marks for questions are given in brackets [ ].",
                "Neat diagrams should be drawn wherever necessary."
            ],
            "sections": [
                {"name": "SECTION A", "type": "Compulsory", "q_count": 10, "marks_each": "varied", "total": 30},
                {"name": "SECTION B", "type": "Descriptive", "q_count": 6, "marks_each": 10, "total": 40},
            ]
        }

    if "IB" in board_up:
        return {
            "board_label": "INTERNATIONAL BACCALAUREATE",
            "exam_label": "FINAL EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 100,
            "time": "2 Hours 30 Minutes",
            "instructions": [
                "Answer all required questions.",
                "Use precise terminology and structured responses.",
                "Show reasoning wherever required."
            ],
            "sections": [
                {"name": "SECTION A", "type": "Structured / Objective", "q_count": 20, "marks_each": "varied", "total": 40},
                {"name": "SECTION B", "type": "Extended Response", "q_count": 4, "marks_each": 15, "total": 60},
            ]
        }

    if "CAMBRIDGE" in board_up:
        return {
            "board_label": "CAMBRIDGE ASSESSMENT INTERNATIONAL EDUCATION",
            "exam_label": "INTERNATIONAL EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 80,
            "time": "2 Hours",
            "instructions": [
                "Answer all questions as instructed.",
                "Write clearly and use correct numbering.",
                "Show all working where required."
            ],
            "sections": [
                {"name": "SECTION A", "type": "Structured Questions", "q_count": 10, "marks_each": 4, "total": 40},
                {"name": "SECTION B", "type": "Extended Response", "q_count": 4, "marks_each": 10, "total": 40},
            ]
        }

    # University / professional fallback
    if any(k in course.upper() for k in ["MBBS", "BDS", "MD", "MEDICAL"]):
        return {
            "board_label": "UNIVERSITY EXAMINATIONS",
            "exam_label": f"{course.upper()} PROFESSIONAL EXAMINATION",
            "class_label": course.upper(),
            "total_marks": 100,
            "time": "3 Hours",
            "instructions": [
                "Answer all questions in Part A.",
                "Answer any five questions from Part B unless otherwise specified.",
                "Draw neat labelled diagrams wherever necessary.",
                "Clinical relevance will be given due credit."
            ],
            "sections": [
                {"name": "PART A", "type": "Short Notes", "q_count": 10, "marks_each": 5, "total": 50},
                {"name": "PART B", "type": "Long Essays", "q_count": 8, "marks_each": 10, "total": 50},
            ]
        }

    return {
        "board_label": "UNIVERSITY EXAMINATIONS",
        "exam_label": f"{course.upper()} SEMESTER EXAMINATION",
        "class_label": course.upper(),
        "total_marks": 100,
        "time": "3 Hours",
        "instructions": [
            "Answer all questions in Section A.",
            "Answer any five questions from Section B unless otherwise specified.",
            "Figures in brackets indicate marks."
        ],
        "sections": [
            {"name": "SECTION A", "type": "Short Answer", "q_count": 10, "marks_each": 2, "total": 20},
            {"name": "SECTION B", "type": "Medium Answer", "q_count": 8, "marks_each": 5, "total": 40},
            {"name": "SECTION C", "type": "Long Answer", "q_count": 4, "marks_each": 10, "total": 40},
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
        "",
        "**Sections:**"
    ]
    for sec in fmt["sections"]:
        lines.append(
            f"- **{sec['name']}** — {sec['type']} | {sec['q_count']} questions | {sec['marks_each']} marks each | Total {sec['total']}"
        )
    lines.append("")
    lines.append("**Instructions Preview:**")
    for ins in fmt["instructions"]:
        lines.append(f"- {ins}")
    return "\n".join(lines)

# ═════════════════════════════════════════════════════════════════════════════
# STEP 5: PROMPTS
# ═════════════════════════════════════════════════════════════════════════════

def build_question_paper_prompt(board, course, subject, chapter, topic, audience):
    fmt = get_qp_format_spec(board, course, subject)
    instructions_text = "\n".join([f"{i+1}. {x}" for i, x in enumerate(fmt["instructions"])])
    sections_text = "\n".join([
        f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}"
        for s in fmt["sections"]
    ])

    return f"""
You are an official academic paper setter.

Generate a CHAPTER-LEVEL question paper using the EXACT academic pattern below.

BOARD: {fmt['board_label']}
EXAM: {fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
SUBJECT: {subject}
TOPIC: {topic}
CHAPTER: {chapter}
TIME ALLOWED: {fmt['time']}
MAXIMUM MARKS: {fmt['total_marks']}
AUDIENCE: {audience}

GENERAL INSTRUCTIONS TO PRINT IN THE PAPER:
{instructions_text}

REQUIRED SECTION STRUCTURE:
{sections_text}

VERY IMPORTANT RULES:
1. Follow this format strictly.
2. Use a proper academic header.
3. Show sections clearly, such as SECTION A, SECTION B, PART A, PART B, depending on the pattern.
4. Number questions properly.
5. For MCQs, give exactly 4 options: (a), (b), (c), (d).
6. Show marks in square brackets like [3 marks].
7. Cover the selected chapter only, but do it comprehensively.
8. Difficulty split must be 30% easy, 50% medium, 20% hard.
9. DO NOT include answers.
10. DO NOT include hints.
11. DO NOT produce a summary or notes.
12. Output must look like a real examination paper.

Generate only the final question paper.
"""

def build_full_subject_qp_prompt(board, course, stream, subject, audience):
    fmt = get_qp_format_spec(board, course, subject)
    instructions_text = "\n".join([f"{i+1}. {x}" for i, x in enumerate(fmt["instructions"])])
    sections_text = "\n".join([
        f"- {s['name']} | {s['type']} | {s['q_count']} questions | {s['marks_each']} marks each | Total {s['total']}"
        for s in fmt["sections"]
    ])

    return f"""
You are an official academic paper setter.

Generate a FULL SUBJECT question paper covering the complete syllabus.

BOARD: {fmt['board_label']}
EXAM: {fmt['exam_label']}
CLASS / COURSE: {fmt['class_label']}
STREAM: {stream}
SUBJECT: {subject}
TIME ALLOWED: {fmt['time']}
MAXIMUM MARKS: {fmt['total_marks']}
AUDIENCE: {audience}

GENERAL INSTRUCTIONS TO PRINT IN THE PAPER:
{instructions_text}

REQUIRED SECTION STRUCTURE:
{sections_text}

STRICT RULES:
1. This must cover the FULL subject syllabus, not just one chapter.
2. Distribute questions across the syllabus.
3. Follow the academic format exactly.
4. Number questions properly.
5. MCQs must have 4 options: (a), (b), (c), (d).
6. Show marks like [5 marks].
7. Add internal choices if appropriate for the pattern.
8. DO NOT include answers.
9. DO NOT include hints.
10. Output must look like a proper standard exam paper.

Generate only the final full subject question paper.
"""

def build_answers_prompt(question_paper_text, board, course, subject, chapter):
    """
    This is the main mismatch fix:
    the model is forced to answer the EXACT generated paper text.
    """
    return f"""
You are preparing the OFFICIAL ANSWER KEY for the exact question paper below.

BOARD / COURSE: {board} | {course}
SUBJECT: {subject}
CHAPTER: {chapter}

IMPORTANT INSTRUCTIONS:
1. Answer ONLY the questions present in the paper below.
2. DO NOT invent new questions.
3. DO NOT change question numbering.
4. DO NOT create a new paper.
5. Preserve the same section names and question numbers.
6. For each question, write:
   - the exact question number
   - a short restatement of the question
   - the answer
7. For MCQs:
   - give the correct option
   - briefly explain why
8. For descriptive questions:
   - provide accurate academic answers
   - keep them aligned to the asked marks
9. If the paper contains internal choice OR questions, answer both alternatives clearly.
10. The answer key must match the given paper exactly.

===== EXACT QUESTION PAPER START =====
{question_paper_text}
===== EXACT QUESTION PAPER END =====

Now generate the answer key for the EXACT SAME paper above.
"""

def build_prompt(tool, chapter, topic, subject, audience, output_style, board="", course=""):
    """
    IMPORTANT:
    Output Style Question Paper gets priority over tool.
    This fixes the issue where Summary was still being generated.
    """
    base_context = f"""
You are an expert educator creating study material for {audience}.
Subject: {subject} | Topic: {topic} | Chapter: {chapter}
Requirements: Accurate, exam-focused, well-structured, with examples, and error-free.
"""

    # Highest priority
    if output_style == "🧪 Question Paper":
        return build_question_paper_prompt(board, course, subject, chapter, topic, audience)

    if tool == "🧪 Question Paper":
        return build_question_paper_prompt(board, course, subject, chapter, topic, audience)

    if tool == "📝 Summary":
        if output_style == "📄 Detailed":
            return base_context + """
Create a detailed summary with:
- Chapter overview
- Key concepts
- Important definitions
- Worked examples
- Exam tips
- Common mistakes
"""
        elif output_style == "⚡ Short & Quick":
            return base_context + """
Create a quick summary with:
- One-line definition
- 5-7 key points
- Important formulas / facts
- Quick revision tips
"""
        elif output_style == "📋 Notes Format":
            return base_context + """
Create structured study notes with:
- Headings and subheadings
- Bullet points
- Definitions
- Important facts
- Examples
- Revision points
"""

    if tool == "🧠 Quiz":
        return base_context + """
Create a quiz with:
- 5 MCQs
- 5 short questions
- 3 long questions
- Answer key
"""

    if tool == "📌 Revision Notes":
        return base_context + """
Create revision notes with:
- Top 10 must-know points
- Formula sheet / facts list
- Mnemonics
- Key comparisons
- Exam focus areas
"""

    if tool == "❓ Exam Q&A":
        return base_context + """
Create an exam Q&A bank with:
- Frequently asked questions
- Conceptual questions with answers
- Application questions with answers
- Why/how questions with answers
"""

    return base_context + "Create comprehensive study material."

# ═════════════════════════════════════════════════════════════════════════════
# STEP 6: AI GENERATION
# ═════════════════════════════════════════════════════════════════════════════

def generate_with_fallback(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return (
            "⚠️ API key missing!\n\n"
            "Add GEMINI_API_KEY to `.streamlit/secrets.toml`",
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

# ═════════════════════════════════════════════════════════════════════════════
# STEP 7: PDF GENERATION
# ═════════════════════════════════════════════════════════════════════════════

def generate_pdf(title, subtitle, content, color_hex="#1d4ed8"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(
        title,
        ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=21,
            textColor=colors.HexColor(color_hex),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold"
        )
    ))

    story.append(Paragraph(
        subtitle,
        ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Normal"],
            fontSize=10.5,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName="Helvetica"
        )
    ))

    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=colors.HexColor(color_hex),
        spaceAfter=14
    ))

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5,
        fontName="Helvetica"
    )

    heading_style = ParagraphStyle(
        "Head",
        parent=styles["Heading2"],
        fontSize=12.5,
        textColor=colors.HexColor(color_hex),
        spaceBefore=10,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=15,
        leftIndent=16,
        bulletIndent=6,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4,
        fontName="Helvetica"
    )

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.18 * cm))
            continue

        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if line.startswith(("###", "##", "#")):
            story.append(Paragraph(line.lstrip("#").strip(), heading_style))
        elif line.startswith(("- ", "• ", "* ")):
            story.append(Paragraph(f"• {safe[2:]}", bullet_style))
        else:
            story.append(Paragraph(safe, body_style))

    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#e2e8f0"),
        spaceAfter=5
    ))

    story.append(Paragraph(
        f"<i>Generated by StudySmart AI | {time.strftime('%Y-%m-%d %H:%M')}</i>",
        ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#94a3b8"),
            alignment=TA_CENTER
        )
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
# ═════════════════════════════════════════════════════════════════════════════
# STEP 8: SESSION STATE
# ═════════════════════════════════════════════════════════════════════════════

def init_session_state():
    defaults = {
        "logged_in": False,
        "username": "",
        "history": [],
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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_generation_state():
    st.session_state.generated_result = None
    st.session_state.generated_model = None
    st.session_state.generated_label = None
    st.session_state.generated_tool = None
    st.session_state.generated_chapter = None
    st.session_state.generated_subject = None
    st.session_state.generated_topic = None
    st.session_state.generated_course = None
    st.session_state.generated_stream = None
    st.session_state.generated_board = None
    st.session_state.generated_audience = None
    st.session_state.generated_output_style = None
    st.session_state.answers_result = None
    st.session_state.answers_model = None
    st.session_state.show_answers = False
    st.session_state.fullpaper_result = None
    st.session_state.fullpaper_model = None
    st.session_state.show_fullpaper = False

# ═════════════════════════════════════════════════════════════════════════════
# STEP 9: MAIN APP
# ═════════════════════════════════════════════════════════════════════════════

def main_app():
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center; padding:18px 0 12px 0;">
                <div style="font-size:2.8rem;">🎓</div>
                <div style="font-size:1.3rem; font-weight:800; color:#2563eb;">StudySmart</div>
                <div style="font-size:0.9rem; color:#64748b; margin-top:4px;">
                    Welcome, {st.session_state.username} 👋
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        tool = st.radio(
            "SELECT TOOL",
            ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "🧪 Question Paper", "❓ Exam Q&A"]
        )

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
                    models = get_available_models()
                for m in models:
                    st.write(f"✅ {m}")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.history = []
            reset_generation_state()
            st.rerun()

    # Header
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">StudySmart</div>
            <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
        </div>
    """, unsafe_allow_html=True)

    # Selection card
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)

    if not STUDY_DATA:
        st.error("No study data found.")
        st.stop()

    category = st.selectbox("📚 Category", list(STUDY_DATA.keys()))
    course = st.selectbox("🎓 Program / Class", get_courses(category))
    stream = st.selectbox("📖 Stream", get_streams(category, course))
    subject = st.selectbox("🧾 Subject", get_subjects(category, course, stream))

    if category == "K-12th":
        board = st.selectbox("🏫 Board", BOARDS)
    else:
        board = "University / National Syllabus"

    topic = st.selectbox("🗂️ Topic", get_topics(category, course, stream, subject))

    chapter_key = f"{category}||{course}||{stream}||{subject}||{topic}"
    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key
        reset_generation_state()

    chapter = st.selectbox("📝 Chapter", st.session_state.current_chapters)

    st.markdown('</div>', unsafe_allow_html=True)

    output_style = st.radio(
        "⚙️ Output Style",
        ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format", "🧪 Question Paper"],
        horizontal=True
    )

    effective_label = get_effective_output_name(tool, output_style)
    generate_button_label = get_generate_button_label(tool, output_style)

    # Show format preview whenever question paper mode is selected
    if effective_label == "Question Paper":
        st.markdown('<div class="sf-preview">', unsafe_allow_html=True)
        st.markdown("### 📄 Question Paper Pattern Preview")
        st.markdown(render_qp_preview(board, course, subject))
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button(generate_button_label, use_container_width=True):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter before generating.")
            return

        audience = f"{board} {course} students" if category == "K-12th" else f"{course} students"

        prompt = build_prompt(
            tool=tool,
            chapter=chapter,
            topic=topic,
            subject=subject,
            audience=audience,
            output_style=output_style,
            board=board,
            course=course
        )

        with st.spinner(f"Generating {effective_label}... please wait ⏳"):
            result, model_used = generate_with_fallback(prompt)

        st.session_state.generated_result = result
        st.session_state.generated_model = model_used
        st.session_state.generated_label = effective_label
        st.session_state.generated_tool = tool
        st.session_state.generated_chapter = chapter
        st.session_state.generated_subject = subject
        st.session_state.generated_topic = topic
        st.session_state.generated_course = course
        st.session_state.generated_stream = stream
        st.session_state.generated_board = board
        st.session_state.generated_audience = audience
        st.session_state.generated_output_style = output_style

        st.session_state.answers_result = None
        st.session_state.answers_model = None
        st.session_state.show_answers = False

        st.session_state.fullpaper_result = None
        st.session_state.fullpaper_model = None
        st.session_state.show_fullpaper = False

        if model_used != "None":
            add_to_history(effective_label, chapter, subject, result)

    # Display generated content
    if st.session_state.generated_result and st.session_state.generated_model != "None":
        result = st.session_state.generated_result
        model_used = st.session_state.generated_model
        g_label = st.session_state.generated_label
        g_chapter = st.session_state.generated_chapter
        g_subject = st.session_state.generated_subject
        g_topic = st.session_state.generated_topic
        g_course = st.session_state.generated_course
        g_stream = st.session_state.generated_stream
        g_board = st.session_state.generated_board
        g_audience = st.session_state.generated_audience

        st.markdown("---")

        c1, c2 = st.columns(2)
        c1.metric("🤖 Model Used", model_used.split("/")[-1] if "/" in model_used else model_used)
        c2.metric("📝 Word Count", f"{count_words(result):,}")

        st.markdown('<div class="sf-output">', unsafe_allow_html=True)
        st.markdown(f"### {g_label} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        is_question_paper = g_label == "Question Paper"

        if is_question_paper:
            st.markdown("---")

            try:
                qp_pdf = generate_pdf(
                    f"Question Paper — {g_chapter}",
                    f"{g_subject} | {g_board} | {g_course}",
                    result,
                    color_hex="#1d4ed8"
                )
                safe_qp = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + "_QuestionPaper.pdf"
                st.download_button(
                    "⬇️ Download Question Paper as PDF",
                    data=qp_pdf,
                    file_name=safe_qp,
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_qp"
                )
            except Exception as e:
                st.warning(f"⚠️ Question paper PDF generation failed: {str(e)}")

            # Get answers button
            if st.button("📋 Get Answers", use_container_width=True, key="get_answers_btn"):
                exact_question_paper = st.session_state.generated_result

                with st.spinner("Generating answers for the exact question paper... ⏳"):
                    answers_prompt = build_answers_prompt(
                        question_paper_text=exact_question_paper,
                        board=g_board,
                        course=g_course,
                        subject=g_subject,
                        chapter=g_chapter
                    )
                    answers_result, answers_model = generate_with_fallback(answers_prompt)

                st.session_state.answers_result = answers_result
                st.session_state.answers_model = answers_model
                st.session_state.show_answers = True

            if st.session_state.show_answers and st.session_state.answers_result:
                ans_result = st.session_state.answers_result
                ans_model = st.session_state.answers_model

                if ans_model != "None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 📚 Answer Key — {g_chapter}")
                    st.markdown(ans_result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    try:
                        ans_pdf = generate_pdf(
                            f"Answer Key — {g_chapter}",
                            f"{g_subject} | {g_board} | {g_course}",
                            ans_result,
                            color_hex="#15803d"
                        )
                        safe_ans = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + "_Answers.pdf"
                        st.download_button(
                            "⬇️ Download Answer Key as PDF",
                            data=ans_pdf,
                            file_name=safe_ans,
                            mime="application/pdf",
                            use_container_width=True,
                            key="dl_answers"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Answer key PDF generation failed: {str(e)}")
                else:
                    st.error("❌ Failed to generate answer key.")
                    st.markdown(ans_result)

            # Full subject paper
            st.markdown("---")
            st.markdown(f"""
                <div class="sf-preview">
                    <strong>🗂️ Full Subject Question Paper</strong><br/>
                    Generate a complete <strong>{g_subject}</strong> paper for <strong>{g_board}</strong> / <strong>{g_course}</strong> following the standard academic structure.
                </div>
            """, unsafe_allow_html=True)

            if st.button(
                f"🗂️ Generate Full {g_subject} Question Paper",
                use_container_width=True,
                key="full_subject_qp_btn"
            ):
                with st.spinner(f"Generating full subject question paper for {g_subject}... ⏳"):
                    full_prompt = build_full_subject_qp_prompt(
                        board=g_board,
                        course=g_course,
                        stream=g_stream,
                        subject=g_subject,
                        audience=g_audience
                    )
                    full_result, full_model = generate_with_fallback(full_prompt)

                st.session_state.fullpaper_result = full_result
                st.session_state.fullpaper_model = full_model
                st.session_state.show_fullpaper = True

            if st.session_state.show_fullpaper and st.session_state.fullpaper_result:
                full_result = st.session_state.fullpaper_result
                full_model = st.session_state.fullpaper_model

                if full_model != "None":
                    st.markdown('<div class="sf-fullpaper">', unsafe_allow_html=True)
                    st.markdown(f"### 🗂️ Full Subject Question Paper — {g_subject}")
                    st.markdown(full_result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    try:
                        full_pdf = generate_pdf(
                            f"Full Subject Question Paper — {g_subject}",
                            f"{g_board} | {g_course} | {g_stream}",
                            full_result,
                            color_hex="#6d28d9"
                        )
                        safe_full = f"{g_subject}_{g_board}_{g_course}_FullPaper.pdf".replace(" ", "_")
                        st.download_button(
                            "⬇️ Download Full Subject Question Paper as PDF",
                            data=full_pdf,
                            file_name=safe_full,
                            mime="application/pdf",
                            use_container_width=True,
                            key="dl_fullpaper"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Full paper PDF generation failed: {str(e)}")
                else:
                    st.error("❌ Failed to generate full subject question paper.")
                    st.markdown(full_result)

        else:
            st.markdown("---")
            try:
                pdf_buffer = generate_pdf(
                    f"{g_label} — {g_chapter}",
                    f"{g_subject} | {g_topic} | {g_course}",
                    result
                )
                safe_name = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + ".pdf"
                st.download_button(
                    "⬇️ Download as PDF",
                    data=pdf_buffer,
                    file_name=safe_name,
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_main"
                )
            except Exception as e:
                st.warning(f"⚠️ PDF generation failed: {str(e)}")

    elif st.session_state.generated_result and st.session_state.generated_model == "None":
        st.markdown("---")
        st.error("❌ AI generation failed")
        st.markdown(st.session_state.generated_result)

# ═════════════════════════════════════════════════════════════════════════════
# STEP 10: AUTH UI
# ═════════════════════════════════════════════════════════════════════════════

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
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
                else:
                    st.warning("⚠️ Please fill in both fields.")

        with tab2:
            nu = st.text_input("👤 New Username", key="reg_u", placeholder="Minimum 3 characters")
            np = st.text_input("🔑 New Password", type="password", key="reg_p", placeholder="Minimum 6 characters")
            cp = st.text_input("🔑 Confirm Password", type="password", key="reg_cp", placeholder="Re-enter password")

            if st.button("Create Account ✨", use_container_width=True):
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

                        st.success("✅ Account created! Logging you in...")
                        time.sleep(1)
                        st.session_state.logged_in = True
                        st.session_state.username = nu.strip()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists")

        st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# STEP 11: ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

init_db()
init_session_state()

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
