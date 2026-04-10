import streamlit as st
import os
import time
import random
import PyPDF2
from google import genai
from google.genai import errors as genai_errors
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

# 0) Streamlit page config (should be first Streamlit call)
st.set_page_config(page_title="StudySimplifier ✨", layout="centered")

# 1) Header
st.title("📚 StudySimplifier AI")
st.subheader("Transform complex notes into simple summaries!")

# 2) Setup: Get API key with multiple fallbacks
api_key = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
    or os.getenv("GENAI_API_KEY")
    or os.getenv("API_KEY")
)

if not api_key:
    st.error("❌ API Key not found. Please run: export GEMINI_API_KEY=your_key")
    st.info("💡 Or try: GOOGLE_API_KEY, GENAI_API_KEY, or API_KEY")
    st.stop()

# Show masked API key for verification (optional)
st.caption(f"🔐 API key loaded: ****{api_key[-4:]}")

# 3) Initialize Gemini client
client = genai.Client(api_key=api_key)

# 4) Helper Functions (moved to top)
def markdown_to_docx(markdown_text, title="Document"):
    doc = Document()
    h = doc.add_heading(title, level=1)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for line in markdown_text.split("\n"):
        s = line.strip()
        if not s:
            doc.add_paragraph()
        elif s.startswith("# "):
            doc.add_heading(s[2:], level=1)
        elif s.startswith("## "):
            doc.add_heading(s[3:], level=2)
        elif s.startswith("### "):
            doc.add_heading(s[4:], level=3)
        elif s.startswith("- "):
            doc.add_paragraph(s[2:], style="List Bullet")
        else:
            doc.add_paragraph(s)
    return doc

def markdown_to_html(markdown_text, title="Document"):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
body{{font-family:Arial,sans-serif;margin:40px;line-height:1.8;color:#333}}
h1{{color:#1f77b4;text-align:center;border-bottom:3px solid #1f77b4;padding-bottom:12px}}
h2{{color:#2ca02c;margin-top:25px;border-left:5px solid #2ca02c;padding-left:12px}}
h3{{color:#d62728;margin-top:15px}}
ul,ol{{margin:10px 0;padding-left:30px}}
li{{margin:5px 0}}
.summary{{background-color:#f0f8ff;padding:15px;border-radius:5px}}
.question{{background-color:#fffacd;padding:10px;margin:10px 0;border-left:4px solid #ff7f0e}}
</style></head><body>
<h1>{title}</h1>
<div class="summary">
{markdown_text.replace(chr(10), "<br>")}
</div>
</body></html>"""

def show_download_buttons(content, filename_base, title="Document"):
    """Show 3 download buttons for content in different formats"""
    if not content:  # Safety check
        st.warning("No content to download")
        return
        
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "📄 Markdown",
            data=content.encode("utf-8"),
            file_name=f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            key=f"md_{filename_base}_{id(content)}"  # Unique key
        )
    with c2:
        doc = markdown_to_docx(content, title)
        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button(
            "📘 Word (.docx)",
            data=buf.getvalue(),
            file_name=f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"docx_{filename_base}_{id(content)}"  # Unique key
        )
    with c3:
        html = markdown_to_html(content, title)
        st.download_button(
            "🌐 HTML (Print to PDF)",
            data=html.encode("utf-8"),
            file_name=f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            key=f"html_{filename_base}_{id(content)}"  # Unique key
        )

# 5) Retry + Fallback helper
def generate_with_retry(client, prompt, primary_model, max_retries=4, fallbacks=None):
    models_to_try = [primary_model]
    default_fallbacks = [
        "models/gemini-2.5-flash-lite",
        "models/gemini-flash-latest", 
        "models/gemini-2.0-flash",
    ]
    if fallbacks and isinstance(fallbacks, list):
        models_to_try.extend(fallbacks)
    else:
        models_to_try.extend(default_fallbacks)

    last_err = None
    for model in models_to_try:
        for attempt in range(max_retries):
            try:
                resp = client.models.generate_content(model=model, contents=prompt)
                return resp.text
            except genai_errors.ServerError as e:
                if getattr(e, "status_code", None) == 503 or "UNAVAILABLE" in str(e):
                    if attempt < max_retries - 1:
                        delay = (2 ** attempt) + random.uniform(0, 0.5)
                        st.warning(f"⏳ {model.split('/')[-1]} busy, retrying in {delay:.1f}s...")
                        time.sleep(delay)
                        continue
                last_err = e
                break
            except Exception as e:
                last_err = e
                break

    raise last_err if last_err else Exception("All models failed")

# Initialize session state variables
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'quiz' not in st.session_state:
    st.session_state.quiz = None
if 'qp_markdown' not in st.session_state:
    st.session_state.qp_markdown = None

# 6) PDF Upload
uploaded_file = st.file_uploader("Upload your study notes (PDF)", type="pdf")

if uploaded_file is not None:
    # Extract text from PDF safely
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text
    except Exception as e:
        st.error(f"❌ Failed to read PDF: {e}")
        st.stop()

    if not text.strip():
        st.error("❌ No text extracted from PDF. Try a different file.")
        st.stop()

    st.success("✅ PDF Uploaded Successfully!")
    st.caption(f"Extracted ~{len(text)} characters")

    # Primary model
    model_name = "models/gemini-2.5-flash"

    # Actions - UNIQUE KEYS FOR ALL BUTTONS
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 Summarize Notes", key="summarize_btn"):
            with st.spinner("Simplifying..."):
                prompt = (
                    "Please summarize the following study notes into concise, "
                    "easy-to-understand bullet points for a student:\n\n" + text
                )
                try:
                    summary = generate_with_retry(client, prompt, model_name)
                    # Store in session state to persist
                    st.session_state.summary = summary
                    st.rerun()  # Refresh to show new content
                    
                except Exception as e:
                    st.error(f"❌ Failed after retries/fallbacks: {e}")

    with col2:
        if st.button("❓ Generate Quiz", key="quiz_btn"):
            with st.spinner("Creating questions..."):
                prompt = (
                    "Based on this text, create 5 multiple-choice questions with 4 options "
                    "(A-D) and show the correct answer after each question.\n\n" + text
                )
                try:
                    quiz = generate_with_retry(client, prompt, model_name)
                    # Store in session state
                    st.session_state.quiz = quiz
                    st.rerun()  # Refresh to show new content
                    
                except Exception as e:
                    st.error(f"❌ Failed after retries/fallbacks: {e}")

    # Display generated content from session state
    if st.session_state.summary:
        st.markdown("---")
        st.markdown("### 📖 Study Summary")
        st.write(st.session_state.summary)
        st.markdown("#### 📥 Download Summary")
        show_download_buttons(st.session_state.summary, "study_summary", "Study Summary")

    if st.session_state.quiz:
        st.markdown("---")
        st.markdown("### 🧠 Study Quiz")
        st.write(st.session_state.quiz)
        st.markdown("#### 📥 Download Quiz")
        show_download_buttons(st.session_state.quiz, "study_quiz", "Study Quiz")

    # ==== Question Paper Generator ====
    st.markdown("---")
    st.markdown("## 🧪 Create Question Paper")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Question Paper Settings")
        subject = st.text_input("Subject (optional)", "")
        level = st.selectbox("Level", ["High School", "Undergraduate", "Graduate"], index=0)
        duration = st.text_input("Duration", "3 hours")
        total_marks = st.number_input("Total Marks", min_value=10, max_value=300, value=100, step=10)
        num_mcq = st.number_input("MCQs (1 mark each)", min_value=0, max_value=100, value=10, step=1)
        num_short = st.number_input("Short Answer (3-5 marks)", min_value=0, max_value=100, value=5, step=1)
        num_long = st.number_input("Long Answer (10-15 marks)", min_value=0, max_value=100, value=3, step=1)
        answer_placement = st.selectbox("Answer placement", ["After each question", "Separate Answer Key"], index=0)

    if st.button("🧪 Generate Question Paper", key="qp_btn"):
        with st.spinner("Designing question paper..."):
            prompt = f"""Create a complete question paper with these specifications:
- Level: {level}
- Subject: {subject if subject.strip() else "General"}
- Duration: {duration}
- Total Marks: {total_marks}
- MCQs: {num_mcq} (1 mark each)
- Short Answer: {num_short} (3-5 marks each)
- Long Answer: {num_long} (10-15 marks each)
- Answer placement: {answer_placement}

Format with clear sections. Base ONLY on this material:
-----
{text}
-----"""
            try:
                qp_markdown = generate_with_retry(client, prompt, model_name)
                # Store in session state
                st.session_state.qp_markdown = qp_markdown
                st.rerun()  # Refresh to show new content

            except Exception as e:
                st.error(f"❌ Failed to generate question paper: {e}")

    # Display question paper from session state
    if st.session_state.qp_markdown:
        st.markdown("---")
        st.markdown("### 📝 Question Paper")
        st.markdown(st.session_state.qp_markdown)
        st.markdown("#### 📥 Download Question Paper")
        show_download_buttons(st.session_state.qp_markdown, "question_paper", "Question Paper")

else:
    st.info("👈 Upload a PDF to get started.")

# 7) Footer
st.divider()
st.caption("Powered by AI Fiesta & Gemini 2.5 Flash ✨")
