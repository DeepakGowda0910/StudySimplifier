import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib

# --- CONFIG ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result is not None

# --- AI FUNCTIONS ---
def generate_summary(standard, subject, topic):
    prompt = f"""
    You are an expert teacher for Class {standard} students.
    Generate a clear, simple, and well-structured summary for the following:
    - Subject: {subject}
    - Topic: {topic}
    - Standard: Class {standard}

    Include:
    1. Brief Introduction
    2. Key Concepts (bullet points)
    3. Important Points to Remember
    4. One simple real-life example (if applicable)

    Keep the language simple and easy to understand for a Class {standard} student.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_quiz(standard, subject, topic):
    prompt = f"""
    Create 5 multiple choice questions (MCQ) for Class {standard} students on:
    - Subject: {subject}
    - Topic: {topic}

    Format each question as:
    Q1. Question here?
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Answer: A

    Make questions clear and appropriate for Class {standard} level.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_notes(standard, subject, topic):
    prompt = f"""
    Create short revision notes for Class {standard} students on:
    - Subject: {subject}
    - Topic: {topic}

    Format:
    - Use bullet points
    - Keep it concise
    - Highlight key terms in CAPS
    - Add important formulas if applicable
    - Make it exam-ready

    Keep language simple for Class {standard} students.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_qa(standard, subject, topic):
    prompt = f"""
    Generate 5 important exam questions with answers for Class {standard} students on:
    - Subject: {subject}
    - Topic: {topic}

    Format:
    Q1. Question?
    Ans: Answer here (2-3 lines, exam style)

    Make answers crisp and exam-ready for Class {standard} board exams.
    """
    response = model.generate_content(prompt)
    return response.text

# --- PAGE FUNCTIONS ---
def login_page():
    st.title("📚 StudySimplifier")
    st.subheader("Your AI-Powered Exam Preparation Assistant")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}! 🎉")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    with tab2:
        st.subheader("Create a new account")
        new_username = st.text_input("Choose a Username", key="reg_user")
        new_password = st.text_input("Choose a Password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register", use_container_width=True):
            if new_password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif len(new_username) < 3:
                st.error("❌ Username must be at least 3 characters.")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters.")
            elif register_user(new_username, new_password):
                st.success("✅ Account created! Please login.")
            else:
                st.error("❌ Username already exists. Try another.")

def main_app():
    # --- SIDEBAR ---
    with st.sidebar:
        st.title("📚 StudySimplifier")
        st.markdown(f"👋 Hello, **{st.session_state.username}**!")
        st.markdown("---")
        st.markdown("### 🎯 Navigation")
        page = st.radio("Go to:", [
            "🏠 Home",
            "📝 Summary Generator",
            "🧠 Quiz Generator",
            "📌 Revision Notes",
            "❓ Q&A Generator"
        ])
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # --- STANDARD & SUBJECT SELECTION ---
    STANDARDS = [str(i) for i in range(10, 13)]  # Class 10, 11, 12
    SUBJECTS = {
        "10": ["Mathematics", "Science", "Social Science", "English", "Hindi"],
        "11": ["Physics", "Chemistry", "Mathematics", "Biology", "Economics",
               "Accountancy", "Business Studies", "English"],
        "12": ["Physics", "Chemistry", "Mathematics", "Biology", "Economics",
               "Accountancy", "Business Studies", "English"]
    }

    # --- HOME PAGE ---
    if page == "🏠 Home":
        st.title("🏠 Welcome to StudySimplifier!")
        st.markdown(f"### Hello **{st.session_state.username}**! Ready to study smarter? 🚀")
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📝 Summaries", "Instant")
        col2.metric("🧠 Quizzes", "Auto-generated")
        col3.metric("📌 Notes", "Exam-ready")
        col4.metric("❓ Q&A", "Board-style")
        st.markdown("---")
        st.info("👈 Use the sidebar to navigate to any feature!")
        st.markdown("""
        ### What can I do for you?
        - 📝 **Summary Generator** — Get instant topic summaries
        - 🧠 **Quiz Generator** — Test your knowledge with MCQs
        - 📌 **Revision Notes** — Quick bullet-point notes
        - ❓ **Q&A Generator** — Board exam style questions & answers
        """)

    # --- SUMMARY PAGE ---
    elif page == "📝 Summary Generator":
        st.title("📝 Summary Generator")
        st.markdown("Get instant AI-generated summaries for any topic!")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            standard = st.selectbox("Select Your Class", STANDARDS)
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard])
        topic = st.text_input("Enter Topic Name", placeholder="e.g. Photosynthesis, Quadratic Equations...")
        if st.button("Generate Summary ✨", use_container_width=True):
            if topic:
                with st.spinner("Generating your summary..."):
                    result = generate_summary(standard, subject, topic)
                st.success("✅ Summary Ready!")
                st.markdown(result)
            else:
                st.warning("⚠️ Please enter a topic name.")

    # --- QUIZ PAGE ---
    elif page == "🧠 Quiz Generator":
        st.title("🧠 Quiz Generator")
        st.markdown("Test your knowledge with AI-generated MCQs!")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            standard = st.selectbox("Select Your Class", STANDARDS)
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard])
        topic = st.text_input("Enter Topic Name", placeholder="e.g. Newton's Laws, Trigonometry...")
        if st.button("Generate Quiz 🧠", use_container_width=True):
            if topic:
                with st.spinner("Generating your quiz..."):
                    result = generate_quiz(standard, subject, topic)
                st.success("✅ Quiz Ready!")
                st.markdown(result)
            else:
                st.warning("⚠️ Please enter a topic name.")

    # --- NOTES PAGE ---
    elif page == "📌 Revision Notes":
        st.title("📌 Revision Notes")
        st.markdown("Get quick, exam-ready revision notes!")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            standard = st.selectbox("Select Your Class", STANDARDS)
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard])
        topic = st.text_input("Enter Topic Name", placeholder="e.g. French Revolution, Organic Chemistry...")
        if st.button("Generate Notes 📌", use_container_width=True):
            if topic:
                with st.spinner("Generating revision notes..."):
                    result = generate_notes(standard, subject, topic)
                st.success("✅ Notes Ready!")
                st.markdown(result)
            else:
                st.warning("⚠️ Please enter a topic name.")

    # --- Q&A PAGE ---
    elif page == "❓ Q&A Generator":
        st.title("❓ Q&A Generator")
        st.markdown("Get board exam style questions and answers!")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            standard = st.selectbox("Select Your Class", STANDARDS)
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard])
        topic = st.text_input("Enter Topic Name", placeholder="e.g. Democracy, Thermodynamics...")
        if st.button("Generate Q&A ❓", use_container_width=True):
            if topic:
                with st.spinner("Generating questions and answers..."):
                    result = generate_qa(standard, subject, topic)
                st.success("✅ Q&A Ready!")
                st.markdown(result)
            else:
                st.warning("⚠️ Please enter a topic name.")

# --- MAIN ENTRY POINT ---
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.logged_in:
    main_app()
else:
    login_page()
