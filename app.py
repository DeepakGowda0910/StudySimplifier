# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — APP v2.4
# Fix 1: Session state persistence for Get Answers button
# Fix 2: temperature=0.1 for consistent, trustworthy results
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
# STEP 1: LOAD STUDY DATA FROM JSON
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
# STEP 2: PAGE CONFIG & STYLING
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

    .sf-output {
        background: linear-gradient(135deg,
            rgba(59, 130, 246, 0.05) 0%,
            rgba(37, 99, 235, 0.05) 100%);
        border-radius: 18px;
        padding: 28px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 2px 15px rgba(59, 130, 246, 0.1);
        margin-top: 12px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        color: #1e293b;
    }

    .sf-output h3, .sf-output h2 {
        color: #3b82f6 !important;
        margin-top: 0;
        font-weight: 700;
    }

    /* ✅ Green answer box */
    .sf-answers {
        background: linear-gradient(135deg,
            rgba(34, 197, 94, 0.05) 0%,
            rgba(22, 163, 74, 0.05) 100%);
        border-radius: 18px;
        padding: 28px;
        border-left: 5px solid #22c55e;
        box-shadow: 0 2px 15px rgba(34, 197, 94, 0.1);
        margin-top: 20px;
        border: 1px solid rgba(34, 197, 94, 0.2);
        color: #1e293b;
    }

    .sf-answers h3, .sf-answers h2 {
        color: #16a34a !important;
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
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    .stButton > button:hover {
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
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

    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    div[data-testid="stSuccessMessage"] {
        background: rgba(16, 185, 129, 0.08) !important;
        border: 1.5px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stWarningMessage"] {
        background: rgba(245, 158, 11, 0.08) !important;
        border: 1.5px solid rgba(245, 158, 11, 0.3) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stErrorMessage"] {
        background: rgba(239, 68, 68, 0.08) !important;
        border: 1.5px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 10px !important;
    }

    @media (max-width: 768px) {
        .sf-header-title { font-size: 2.8rem !important; }
        .block-container {
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }
        .sf-card { padding: 16px 14px; }
        .sf-output { padding: 14px 12px; }
        .sf-answers { padding: 14px 12px; }

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
# STEP 4: PROMPT BUILDER
# ═════════════════════════════════════════════════════════════════════════════

def build_prompt(tool, chapter, topic, subject, audience, output_style):
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
        return base_context + """
Create a full exam question paper. Do NOT include answers anywhere.
Format exactly as follows:

## QUESTION PAPER
**Subject:** {subject} | **Chapter:** {chapter}
**Total Marks:** 55 | **Time:** 2 Hours

---
### SECTION A — Multiple Choice Questions (1 mark each)
(List 10 MCQs with 4 options each. Do not mark the answer.)

### SECTION B — Short Answer Questions (3 marks each)
(List 5 short answer questions.)

### SECTION C — Long Answer Questions (5 marks each)
(List 4 long answer questions.)

### SECTION D — Case Study (6 marks)
(1 case study with 3 sub-questions.)

---
Difficulty: 30% easy, 50% medium, 20% hard.
DO NOT provide answers or hints anywhere in this paper.
""".format(subject=subject, chapter=chapter)

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
        return base_context + """
Create a well-structured exam question paper. Do NOT include answers.
Format exactly as follows:

## QUESTION PAPER
**Subject:** {subject} | **Chapter:** {chapter}
**Total Marks:** 55 | **Time:** 2 Hours

---
### SECTION A — Multiple Choice Questions (1 mark each)
(List 10 MCQs with 4 options each. Do not mark the answer.)

### SECTION B — Short Answer Questions (3 marks each)
(List 5 short answer questions.)

### SECTION C — Long Answer Questions (5 marks each)
(List 4 long answer questions.)

### SECTION D — Case Study (6 marks)
(1 case study with 3 sub-questions.)

---
Difficulty: 30% easy, 50% medium, 20% hard.
DO NOT provide answers anywhere.
""".format(subject=subject, chapter=chapter)

    return base_context + "Create comprehensive and exam-ready study material."


def build_answers_prompt(chapter, topic, subject, audience, question_paper_text):
    """
    ✅ FIX: Pass the actual question paper text so AI answers
    exactly those questions — not random new ones.
    """
    return f"""
You are an expert educator. Below is a question paper that was given to students.
Provide COMPLETE and DETAILED answers for EVERY question in this paper.

Subject: {subject} | Topic: {topic} | Chapter: {chapter} | Audience: {audience}

===== QUESTION PAPER =====
{question_paper_text}
===== END OF PAPER =====

Now write the ANSWER KEY:
- For each MCQ: State the correct option letter AND a brief explanation (2-3 lines)
- For each Short Answer: Write a clear 4-6 line answer
- For each Long Answer: Write a detailed answer (200-300 words) with examples
- For Case Study: Provide full analysis and answers to each sub-question

Label each answer clearly matching the question number and section.
Be accurate, educational, and thorough.
"""

# ═════════════════════════════════════════════════════════════════════════════
# STEP 5: AI GENERATION ENGINE
# ✅ FIX: temperature=0.1 for consistent, trustworthy results
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
                    temperature=0.1,      # ✅ FIX: was 0.7 — now 0.1 for consistent results
                    max_output_tokens=4096,
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

def generate_pdf(title, subtitle, content):
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
            fontSize=22,
            textColor=colors.HexColor("#1d4ed8"),
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
            fontSize=11,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName="Helvetica"
        )
    ))

    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=colors.HexColor("#3b82f6"),
        spaceAfter=16
    ))

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10.5,
        textColor=colors.HexColor("#1e293b"),
        leading=16,
        spaceAfter=6,
        fontName="Helvetica"
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1d4ed8"),
        spaceBefore=12,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )

    bullet_style = ParagraphStyle(
        "BulletPoint",
        parent=styles["Normal"],
        fontSize=10.5,
        textColor=colors.HexColor("#334155"),
        leading=15,
        leftIndent=16,
        spaceAfter=4,
        bulletIndent=6,
        fontName="Helvetica"
    )

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2 * cm))
            continue
        if line.startswith("####"):
            story.append(Paragraph(line.lstrip("#").strip(), body_style))
        elif line.startswith("###") or line.startswith("##") or line.startswith("#"):
            story.append(Paragraph(line.lstrip("#").strip(), heading_style))
        elif line.startswith("**") and line.endswith("**"):
            safe = line.replace("**", "")
            story.append(Paragraph(f"<b>{safe}</b>", body_style))
        elif line.startswith(("- ", "• ", "* ")):
            safe = line[2:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"• {safe}", bullet_style))
        elif line and line[0].isdigit() and ". " in line[:5]:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, bullet_style))
        else:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, body_style))

    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#e2e8f0"),
        spaceAfter=6
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
# STEP 7: SESSION STATE INITIALISATION
# ✅ FIX: All session keys declared upfront so nothing is ever lost on re-run
# ═════════════════════════════════════════════════════════════════════════════

def init_session_state():
    defaults = {
        "logged_in": False,
        "username": "",
        "current_chapters": [],
        "history": [],
        "last_chapter_key": "",
        # ✅ These persist the generated content across button clicks
        "generated_result": None,
        "generated_model": None,
        "generated_tool": None,
        "generated_chapter": None,
        "generated_subject": None,
        "generated_topic": None,
        "generated_course": None,
        "generated_audience": None,
        "generated_output_style": None,
        # ✅ These persist the answers
        "answers_result": None,
        "answers_model": None,
        "show_answers": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ═════════════════════════════════════════════════════════════════════════════
# STEP 8: MAIN APPLICATION UI
# ═════════════════════════════════════════════════════════════════════════════

def main_app():

    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center; padding: 20px 0 15px 0;">
                <div style="font-size:3rem; margin-bottom: 8px;">🎓</div>
                <div style="font-size:1.4rem; font-weight:800;
                     background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                     -webkit-background-clip: text;
                     -webkit-text-fill-color: transparent;
                     background-clip: text;">StudySmart</div>
                <div style="font-size:0.9rem; color:#64748b; margin-top:6px;">
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
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.history = []
            st.session_state.generated_result = None
            st.session_state.answers_result = None
            st.session_state.show_answers = False
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">StudySmart</div>
            <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
        </div>
        <div class="sf-watermark">POWERED BY AI</div>
    """, unsafe_allow_html=True)

    # ── Selection Card ─────────────────────────────────────────────────────────
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
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key
        # ✅ Clear previous results when selection changes
        st.session_state.generated_result = None
        st.session_state.answers_result   = None
        st.session_state.show_answers     = False

    chapter = st.selectbox("📝 Chapter", st.session_state.get("current_chapters", ["No chapters found"]))

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Output Style ───────────────────────────────────────────────────────────
    output_style = st.radio(
        "⚙️ Output Style",
        ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format", "🧪 Question Paper"],
        horizontal=True
    )

    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)

    # ── Generate Button ────────────────────────────────────────────────────────
    if st.button(f"✨ Generate {tool}", use_container_width=True):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter before generating.")
            return

        audience = f"{board} {course} students" if category == "K-12th" else f"{course} students"
        final_prompt = build_prompt(tool, chapter, topic, subject, audience, output_style)

        with st.spinner(f"🧠 Generating {tool}... please wait ⏳"):
            result, model_used = generate_with_fallback(final_prompt)

        # ✅ FIX: Store everything in session_state so it survives "Get Answers" click
        st.session_state.generated_result       = result
        st.session_state.generated_model        = model_used
        st.session_state.generated_tool         = tool
        st.session_state.generated_chapter      = chapter
        st.session_state.generated_subject      = subject
        st.session_state.generated_topic        = topic
        st.session_state.generated_course       = course
        st.session_state.generated_audience     = audience
        st.session_state.generated_output_style = output_style
        # Reset answers whenever a new paper is generated
        st.session_state.answers_result         = None
        st.session_state.show_answers           = False

        if model_used != "None":
            add_to_history(tool, chapter, subject, result)

    # ── Display Previously Generated Result (persists across re-runs) ──────────
    if st.session_state.generated_result and st.session_state.generated_model != "None":

        result       = st.session_state.generated_result
        model_used   = st.session_state.generated_model
        g_tool       = st.session_state.generated_tool
        g_chapter    = st.session_state.generated_chapter
        g_subject    = st.session_state.generated_subject
        g_topic      = st.session_state.generated_topic
        g_course     = st.session_state.generated_course
        g_audience   = st.session_state.generated_audience
        g_style      = st.session_state.generated_output_style

        st.markdown("---")

        word_count = count_words(result)
        col_a, col_b = st.columns(2)
        col_a.metric("🤖 Model Used", model_used.split("/")[-1] if "/" in model_used else model_used)
        col_b.metric("📝 Word Count", f"{word_count:,}")

        st.markdown('<div class="sf-output">', unsafe_allow_html=True)
        st.markdown(f"### {g_tool} — {g_chapter}")
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Question Paper PDF + Get Answers ──────────────────────────────────
        is_question_paper = (
            g_tool  == "🧪 Question Paper" or
            g_style == "🧪 Question Paper"
        )

        if is_question_paper:

            # Download question paper PDF
            st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
            try:
                qp_pdf = generate_pdf(
                    f"Question Paper — {g_chapter}",
                    f"{g_subject} | {g_topic} | {g_course}",
                    result
                )
                safe_qp = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + "_QuestionPaper.pdf"
                st.download_button(
                    label="⬇️ Download Question Paper as PDF",
                    data=qp_pdf,
                    file_name=safe_qp,
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_qp"
                )
            except Exception as e:
                st.warning(f"⚠️ PDF generation failed: {str(e)}")

            st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)

            # ✅ FIX: "Get Answers" button — uses session_state, never loses context
            if st.button("📋 Get Answers", use_container_width=True, key="get_answers_btn"):
                with st.spinner("📚 Generating detailed answers... please wait ⏳"):
                    ans_prompt = build_answers_prompt(
                        g_chapter, g_topic, g_subject, g_audience,
                        result   # ✅ Pass the actual question paper text
                    )
                    ans_result, ans_model = generate_with_fallback(ans_prompt)
                st.session_state.answers_result = ans_result
                st.session_state.answers_model  = ans_model
                st.session_state.show_answers   = True

            # ── Display Answers (also persisted in session_state) ──────────────
            if st.session_state.show_answers and st.session_state.answers_result:
                ans_result = st.session_state.answers_result
                ans_model  = st.session_state.answers_model

                if ans_model != "None":
                    st.markdown('<div class="sf-answers">', unsafe_allow_html=True)
                    st.markdown(f"### 📚 Answer Key — {g_chapter}")
                    st.markdown(ans_result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Download answers PDF
                    try:
                        ans_pdf = generate_pdf(
                            f"Answer Key — {g_chapter}",
                            f"{g_subject} | {g_topic} | {g_course}",
                            ans_result
                        )
                        safe_ans = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + "_Answers.pdf"
                        st.download_button(
                            label="⬇️ Download Answer Key as PDF",
                            data=ans_pdf,
                            file_name=safe_ans,
                            mime="application/pdf",
                            use_container_width=True,
                            key="dl_ans"
                        )
                        st.info("✅ Answer Key PDF ready — click above to download.")
                    except Exception as e:
                        st.warning(f"⚠️ Answer PDF failed: {str(e)}")
                else:
                    st.error("❌ Failed to generate answers. Please try again.")
                    st.markdown(ans_result)

        else:
            # ── Non-question-paper: standard PDF download ──────────────────────
            st.markdown("---")
            try:
                pdf_buffer = generate_pdf(
                    f"{g_tool} — {g_chapter}",
                    f"{g_subject} | {g_topic} | {g_course}",
                    result
                )
                safe_name = g_chapter.replace(" ", "_").replace(":", "").replace("/", "-") + ".pdf"
                st.download_button(
                    label="⬇️ Download as PDF",
                    data=pdf_buffer,
                    file_name=safe_name,
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_main"
                )
                st.info("✅ PDF ready — click above to download.")
            except Exception as pdf_err:
                st.warning(f"⚠️ PDF generation failed: {str(pdf_err)}")

    elif st.session_state.generated_result and st.session_state.generated_model == "None":
        st.markdown("---")
        st.error("❌ AI Generation Failed")
        st.markdown(st.session_state.generated_result)

# ═════════════════════════════════════════════════════════════════════════════
# STEP 9: AUTHENTICATION UI
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
                    c.execute(
                        "SELECT * FROM users WHERE username=? AND password=?",
                        (u.strip(), hash_p(p))
                    )
                    user = c.fetchone()
                    conn.close()

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = u.strip()
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
