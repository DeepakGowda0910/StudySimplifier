import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib

# --- PAGE CONFIG ---
st.set_page_config(page_title="StudyFiesta AI", page_icon="🎓", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #007bff; color: white; border: none; font-weight: bold;
    }
    .stButton>button:hover { background-color: #0056b3; color: white; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e3b4e,#2e3b4e); color: white; }
    div.stSelectbox label, div.stTextInput label { font-weight: bold; color: #1f1f1f; }
    .card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    h1, h2, h3 { color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIG & AI ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]

def generate_with_fallback(prompt):
    for m in MODELS:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(prompt)
            return response.text, m
        except: continue
    return "Service temporarily unavailable.", "None"

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()

def hash_p(p): return hashlib.sha256(p.encode()).hexdigest()

# --- COURSE ARCHITECTURE ---
DATA_MAP = {
    "Competitive Exams 🏆": {
        "UPSC (Civil Services)": ["General Studies 1", "General Studies 2 (CSAT)", "History Optional", "Geography Optional", "Public Admin", "Ethics"],
        "JEE (Mains/Adv)": ["Physics", "Chemistry", "Mathematics"],
        "NEET": ["Biology", "Physics", "Chemistry"],
        "GATE": ["Computer Science", "Mechanical", "Electrical", "Civil", "Electronics"],
        "Banking/SSC": ["Quantitative Aptitude", "Reasoning", "English", "General Awareness"]
    },
    "Engineering & Tech 💻": {
        "B.Tech / M.Tech": ["Computer Science (CSE)", "Information Technology (IT)", "Electronics (ECE)", "Mechanical (ME)", "Civil (CE)", "AI & Data Science"],
        "Polytechnic Diploma": ["Mechanical", "Electrical", "Civil", "Computer"],
        "BCA / MCA": ["Programming in C/C++", "Java & Python", "Database Management", "Software Engineering", "Web Development"]
    },
    "School (K-12) 🏫": {
        "Class 10": ["Mathematics", "Science", "Social Science", "English", "Hindi"],
        "Class 11 & 12": ["Physics", "Chemistry", "Mathematics", "Biology", "Accountancy", "Business Studies", "Economics", "History", "Psychology"]
    },
    "Degree & Masters 🎓": {
        "Commerce (B.Com/M.Com)": ["Financial Accounting", "Corporate Tax", "Auditing", "Costing", "Management Accounting"],
        "Science (B.Sc/M.Sc)": ["Physics", "Chemistry", "Maths", "Zoology", "Botany", "Biotechnology"],
        "Management (BBA/MBA)": ["Marketing", "Finance", "HR", "Operations", "Strategy"],
        "Arts (B.A/M.A)": ["English Literature", "Political Science", "Economics", "History", "Psychology"]
    }
}

BOARDS = ["CBSE", "ICSE", "IGCSE", "State Board (Maharashtra)", "State Board (Karnataka)", "State Board (UP)", "State Board (Others)"]

# --- APP LOGIC ---
def get_chapters(category, course, subject):
    prompt = f"Act as a top professor for {course}. List only the official chapter names for {subject}. Format: Comma-separated list only. No numbers, no intro."
    res, _ = generate_with_fallback(prompt)
    return [c.strip() for c in res.split(",") if len(c.strip()) > 2]

def main_app():
    # Sidebar
    with st.sidebar:
        st.title("🎓 StudyFiesta")
        st.markdown(f"**Welcome, {st.session_state.username}**")
        st.divider()
        tool = st.radio("SELECT TOOL", ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "❓ Exam Q&A"])
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # Header
    st.markdown(f"# {tool}")
    st.write("Streamlining your preparation with AI precision.")
    
    # Selectors
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            cat = st.selectbox("Category", list(DATA_MAP.keys()))
        with c2:
            course = st.selectbox("Exam / Course", list(DATA_MAP[cat].keys()))
        with c3:
            # Add Board selection for School category
            if "School" in cat:
                board = st.selectbox("Education Board", BOARDS)
            else:
                board = "University/National Syllabus"

        c4, c5 = st.columns(2)
        with c4:
            sub = st.selectbox("Subject", DATA_MAP[cat][course])
        
        # Chapter Fetching
        if "last_sub_key" not in st.session_state or st.session_state.last_sub_key != f"{course}_{sub}":
            with st.spinner("AI Fetching Syllabus..."):
                st.session_state.current_chapters = get_chapters(cat, course, sub)
                st.session_state.last_sub_key = f"{course}_{sub}"
        
        with c5:
            chap = st.selectbox("Chapter / Topic", st.session_state.current_chapters)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Execution
    if st.button(f"Generate {tool} ✨"):
        with st.spinner(f"Analyzing {chap} for {course}..."):
            prompt_map = {
                "📝 Summary": f"Generate a professional, structured academic summary for {chap} in {sub} for {course} students. Use headings and bullet points.",
                "🧠 Quiz": f"Generate 5 high-quality MCQs for {chap} ({sub} - {course}). Include options A-D and the correct Answer with a brief explanation.",
                "📌 Revision Notes": f"Create concise revision notes for {chap} ({sub} - {course}). Highlight key terms, formulas, and critical concepts in CAPS.",
                "❓ Exam Q&A": f"List 5 highly probable exam questions and detailed professional answers for {chap} ({sub} - {course})."
            }
            
            final_prompt = f"{prompt_map[tool]} Important: If there are mathematical formulas, use LaTeX format $$...$$. Use clear formatting."
            result, model_name = generate_with_fallback(final_prompt)
            
            st.markdown("---")
            st.success(f"Preparation Material Ready! (Powered by {model_name})")
            
            # Display result in a nice box
            st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)

# --- AUTH UI ---
def auth_ui():
    st.title("📚 AI StudyFiesta")
    st.subheader("Professional Exam Preparation Platform")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login"):
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_p(p)))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Invalid Credentials")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            try:
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("INSERT INTO users VALUES (?, ?)", (nu, hash_p(np)))
                conn.commit()
                st.success("Account Created! Go to Login tab.")
            except: st.error("Username already exists.")

# --- START ---
init_db()
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if st.session_state.logged_in: main_app()
else: auth_ui()
