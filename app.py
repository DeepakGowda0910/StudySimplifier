# ═══════════════════════════════════════════════════════════════════════════════
# STUDYSMART AI — CLEAN APP (UI + AI LOGIC ONLY)
# Auto-detects available Gemini models dynamically
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
    """Load study data from external JSON file"""
    try:
        data_path = Path("data/study_data.json")
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Error: data/study_data.json not found!")
        st.info("📁 Please create the file structure as shown in the setup guide")
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

    .sf-card {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 4px 30px rgba(15, 23, 42, 0.08),
                    inset 0 1px 0 rgba(255, 255, 255, 0.9);
        margin-bottom: 28px;
        border: 1px solid rgba(59, 130, 246, 0.15);
    }

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

    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 20px 0;
    }

    @media (max-width: 768px) {
        .sf-header-title { font-size: 2.8rem !important; }
        .sf-header-subtitle { font-size: 1rem !important; }
        .sf-watermark {
            font-size: 2.4rem !important;
            letter-spacing: 6px !important;
        }

        html, body, .stApp {
            overflow-x: hidden !important;
            overscroll-behavior: none !important;
            scroll-behavior: auto !important;
            position: relative !important;
        }

        div[data-baseweb="select"] input,
        div[data-baseweb="select"] [role="combobox"],
        div[data-baseweb="select"] > div {
            font-size: 16px !important;
            -webkit-text-size-adjust: 100% !important;
        }

        input, textarea, select,
        [contenteditable="true"],
        [role="combobox"] {
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
    """Configure Gemini once if API key exists."""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return False, "GEMINI_API_KEY not found in secrets"
    try:
        genai.configure(api_key=api_key)
        return True, "Configured"
    except Exception as e:
        return False, str(e)

def list_working_gemini_models():
    """
    Dynamically list only Gemini models that support generateContent.
    This avoids hardcoding model names that may not exist for the API key.
    """
    ok, msg = configure_gemini()
    if not ok:
        return [], msg

    try:
        models = genai.list_models()
        working = []

        for m in models:
            name = getattr(m, "name", "")
            display_name = getattr(m, "display_name", name)
            methods = getattr(m, "supported_generation_methods", [])

            if "gemini" in name.lower() and "generateContent" in methods:
                working.append(name)

        return working, None
    except Exception as e:
        return [], str(e)

def get_available_models():
    """Show available models in sidebar."""
    working_models, err = list_working_gemini_models()
    if err:
        return [f"Error: {err}"]
    if not working_models:
        return ["No Gemini models available for this API key"]
    return working_models

# ═════════════════════════════════════════════════════════════════════════════
# STEP 4: PROMPT BUILDER
# ═════════════════════════════════════════════════════════════════════════════

def build_prompt(tool, chapter, topic, subject, audience, output_style):
    """Build detailed prompts for AI"""

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
Create a full exam question paper:
- Section A: 10 MCQs (1 mark each = 10 marks)
- Section B: 5 Short Answer Questions (3 marks each = 15 marks)
- Section C: 4 Long Answer Questions (5 marks each = 20 marks)
- Section D: 1-2 Case Studies (6-8 marks each)
Total: 100 marks | Difficulty: 30% easy, 50% medium, 20% hard
DO NOT provide answers in this question paper.
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

    return base_context + "Create comprehensive and exam-ready study material."

# ═════════════════════════════════════════════════════════════════════════════
# STEP 5: AI GENERATION ENGINE
# ═════════════════════════════════════════════════════════════════════════════

def generate_with_fallback(prompt):
    """
    Automatically uses whatever Gemini model is currently working.
    It discovers the available models dynamically, then tries them one by one.
    """

    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return (
            "⚠️ API key missing! Please add GEMINI_API_KEY to .streamlit/secrets.toml",
            "None"
        )

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return (f"❌ Gemini configuration failed: {str(e)}", "None")

    # First: discover which Gemini models are actually available
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
        return (
            "❌ No Gemini models with generateContent support are available for this API key.\n\n"
            "Fix:\n"
            "- Check that your Gemini API key is valid\n"
            "- Make sure Gemini API is enabled for the key\n"
            "- Verify your quota and billing\n"
            "- Confirm internet access",
            "None"
        )

    # Try every available model until one works
    last_error = "Unknown error"
    for model_name in available_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
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
        f"❌ All AI models failed.\n\nLast error: {last_error}\n\n"
        "Fix:\n"
        "- Check your API key\n"
        "- Check quota and billing\n"
        "- Check internet connection\n"
        "- Try again after a few minutes",
        "None"
    )

# ═════════════════════════════════════════════════════════════════════════════
# STEP 6: PDF GENERATION
# ═════════════════════════════════════════════════════════════════════════════

def generate_pdf(title, subtitle, content):
    """Generate professional PDF"""
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

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#3b82f6"),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    story.append(Paragraph(title, title_style))

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName="Helvetica"
    )
    story.append(Paragraph(subtitle, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 0.5 * cm))

    content_style = ParagraphStyle(
        "CustomContent",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=12,
        leading=14,
        alignment=TA_LEFT
    )

    for line in content.split("\n"):
        line = line.strip()
        if line:
            try:
                story.append(Paragraph(line, content_style))
            except Exception:
                safe_line = line.encode("ascii", "ignore").decode()
                story.append(Paragraph(safe_line, content_style))
        else:
            story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 0.2 * cm))
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
# STEP 7: MAIN APPLICATION UI
# ═════════════════════════════════════════════════════════════════════════════

def main_app():
    """Main application UI + AI Logic"""

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
            st.rerun()

    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">StudySmart</div>
            <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
        </div>
        <div class="sf-watermark">POWERED BY AI</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)

    c1, c2 = st.columns([1.5, 1.5])
    with c1:
        if not STUDY_DATA:
            st.error("No study data found.")
            st.stop()
        category = st.selectbox("📚 Category", list(STUDY_DATA.keys()))
    with c2:
        st.info("📌 Select your options below")

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
    if st.session_state.get("last_chapter_key") != chapter_key:
        st.session_state.current_chapters = get_chapters(category, course, stream, subject, topic)
        st.session_state.last_chapter_key = chapter_key

    chapter = st.selectbox("📝 Chapter", st.session_state.get("current_chapters", ["No chapters found"]))

    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        output_style = st.radio(
            "⚙️ Output Style",
            ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format"]
        )
    with col2:
        

    st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)

    if st.button(f"✨ Generate {tool}", use_container_width=True):
        if not chapter or chapter == "No chapters found":
            st.warning("⚠️ Please select a valid chapter before generating.")
            return

        audience = f"{board} {course} students" if category == "K-12th" else f"{course} students"
        final_prompt = build_prompt(tool, chapter, topic, subject, audience, output_style)

        with st.spinner(f"🧠 Generating {tool}... please wait ⏳"):
            result, model_used = generate_with_fallback(final_prompt)

        st.markdown("---")

        if model_used != "None":
            st.success(f"✅ Generated using **{model_used}**")

            st.markdown('<div class="sf-output">', unsafe_allow_html=True)
            st.markdown(f"### {tool} — {chapter}")
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("---")

            try:
                pdf_buffer = generate_pdf(
                    f"{tool} — {chapter}",
                    f"{subject} | {topic} | {course}",
                    result
                )
                safe_name = chapter.replace(" ", "_").replace(":", "").replace("/", "-") + ".pdf"
                st.download_button(
                    label="⬇️ Download as PDF",
                    data=pdf_buffer,
                    file_name=safe_name,
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.info("✅ PDF ready — click above to download.")
            except Exception as pdf_err:
                st.warning(f"⚠️ PDF generation failed: {str(pdf_err)}")
        else:
            st.error("❌ AI Generation Failed")
            st.markdown(result)

# ═════════════════════════════════════════════════════════════════════════════
# STEP 8: AUTHENTICATION UI
# ═════════════════════════════════════════════════════════════════════════════

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
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please fill in both fields")

        with tab2:
            nu = st.text_input("👤 New Username", key="reg_u", placeholder="Min 3 characters")
            np = st.text_input("🔑 New Password", type="password", key="reg_p", placeholder="Min 6 characters")

            if st.button("Create Account ✨", use_container_width=True):
                if not nu.strip():
                    st.error("❌ Username cannot be empty")
                elif len(nu.strip()) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif not np.strip():
                    st.error("❌ Password cannot be empty")
                elif len(np.strip()) < 6:
                    st.error("❌ Password must be at least 6 characters")
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
                        st.error("❌ Username already taken. Choose another.")

        st.markdown('</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# STEP 9: ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "current_chapters" not in st.session_state:
    st.session_state.current_chapters = []

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
