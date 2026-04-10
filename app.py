import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib

# --- CONFIG ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Preferred models in order
PREFERRED_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

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

# --- AI MODEL HELPERS ---
@st.cache_data(ttl=3600)
def get_available_models():
    available = []
    try:
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods:
                name = getattr(m, "name", "")
                if name.startswith("models/"):
                    name = name.replace("models/", "", 1)
                if name:
                    available.append(name)
    except Exception:
        # If listing models fails, we will still try preferred models directly
        pass
    return available

def extract_response_text(response):
    try:
        if hasattr(response, "text") and response.text:
            return response.text
    except Exception:
        pass

    try:
        parts = []
        if hasattr(response, "candidates"):
            for candidate in response.candidates:
                content = getattr(candidate, "content", None)
                if content and hasattr(content, "parts"):
                    for part in content.parts:
                        text = getattr(part, "text", None)
                        if text:
                            parts.append(text)
        if parts:
            return "\n".join(parts)
    except Exception:
        pass

    return None

def generate_with_fallback(prompt):
    available_models = get_available_models()

    if available_models:
        models_to_try = [m for m in PREFERRED_MODELS if m in available_models]
        extra_models = [m for m in available_models if m not in models_to_try and "gemini" in m.lower()]
        models_to_try.extend(extra_models)
    else:
        models_to_try = PREFERRED_MODELS[:]

    errors = []

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = extract_response_text(response)

            if text and text.strip():
                return text, model_name

            errors.append(f"{model_name}: Empty response received")
        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")

    error_message = "\n".join(errors) if errors else "No model could be used."
    raise RuntimeError(f"All Gemini models failed.\n\nDetails:\n{error_message}")

# --- AI FUNCTIONS ---
def generate_summary(standard, subject, topic):
    prompt = f"""
    You are an expert teacher for Class {standard} students.
    Generate a clear, simple, and well-structured summary for the following:
    Subject: {subject}
    Topic: {topic}
    Standard: Class {standard}

    Include:
    1. Brief Introduction
    2. Key Concepts in bullet points
    3. Important Points to Remember
    4. One simple real-life example if applicable

    Keep the language simple and easy to understand for a Class {standard} student.
    """
    return generate_with_fallback(prompt)

def generate_quiz(standard, subject, topic):
    prompt = f"""
    Create 5 multiple choice questions for Class {standard} students on:
    Subject: {subject}
    Topic: {topic}

    Format each question as:
    Q1. Question here?
    A) Option 1
    B) Option 2
    C) Option 3
    D) Option 4
    Answer: A

    Make questions clear and appropriate for Class {standard} level.
    """
    return generate_with_fallback(prompt)

def generate_notes(standard, subject, topic):
    prompt = f"""
    Create short revision notes for Class {standard} students on:
    Subject: {subject}
    Topic: {topic}

    Format:
    - Use bullet points
    - Keep it concise
    - Highlight key terms in CAPS
    - Add important formulas if applicable
    - Make it exam-ready

    Keep language simple for Class {standard} students.
    """
    return generate_with_fallback(prompt)

def generate_qa(standard, subject, topic):
    prompt = f"""
    Generate 5 important exam questions with answers for Class {standard} students on:
    Subject: {subject}
    Topic: {topic}

    Format:
    Q1. Question?
    Ans: Answer here in 2 to 3 lines, exam style

    Make answers crisp and exam-ready for Class {standard} board exams.
    """
    return generate_with_fallback(prompt)

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
            standard = st.selectbox("Select Your Class", STANDARDS, key="summary_standard")
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard], key="summary_subject")
        topic = st.text_input("Enter Topic Name", placeholder="e.g. Photosynthesis, Quadratic Equations...", key="summary_topic")
        if st.button("Generate Summary ✨", use_container_width=True):
            if topic:
                try:
                    with st.spinner("Generating your summary..."):
                        result, used_model = generate_summary(standard, subject, topic)
                    st.success("✅ Summary Ready!")
                    st.caption(f"Model used: {used_model}")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"❌ Failed to generate summary.\n\n{str(e)}")
            else:
                st.warning("⚠️ Please enter a topic name.")

    # --- QUIZ PAGE ---
    elif page == "🧠 Quiz Generator":
        st.title("🧠 Quiz Generator")
        st.markdown("Test your knowledge with AI-generated MCQs!")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            standard = st.selectbox("Select Your Class", STANDARDS, key="quiz_standard")
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard], key="quiz_subject")
        topic = st.text_input("Enter Topic Name", placeholder="e.g. Newton's Laws, Trigonometry...", key="quiz_topic")
        if st.button("Generate Quiz 🧠", use_container_width=True):
            if topic:
                try:
                    with st.spinner("Generating your quiz..."):
                        result, used_model = generate_quiz(standard, subject, topic)
                    st.success("✅ Quiz Ready!")
                    st.caption(f"Model used: {used_model}")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"❌ Failed to generate quiz.\n\n{str(e)}")
            else:
                st.warning("⚠️ Please enter a topic name.")

    # --- NOTES PAGE ---
    elif page == "📌 Revision Notes":
        st.title("📌 Revision Notes")
        st.markdown("Get quick, exam-ready revision notes!")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            standard = st.selectbox("Select Your Class", STANDARDS, key="notes_standard")
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard], key="notes_subject")
        topic = st.text_input("Enter Topic Name", placeholder="e.g. French Revolution, Organic Chemistry...", key="notes_topic")
        if st.button("Generate Notes 📌", use_container_width=True):
            if topic:
                try:
                    with st.spinner("Generating revision notes..."):
                        result, used_model = generate_notes(standard, subject, topic)
                    st.success("✅ Notes Ready!")
                    st.caption(f"Model used: {used_model}")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"❌ Failed to generate notes.\n\n{str(e)}")
            else:
                st.warning("⚠️ Please enter a topic name.")

    # --- Q&A PAGE ---
    elif page == "❓ Q&A Generator":
        st.title("❓ Q&A Generator")
        st.markdown("Get board exam style questions and answers!")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            standard = st.selectbox("Select Your Class", STANDARDS, key="qa_standard")
        with col2:
            subject = st.selectbox("Select Subject", SUBJECTS[standard], key="qa_subject")
        topic = st.text_input("Enter Topic Name", placeholder="e.g. Democracy, Thermodynamics...", key="qa_topic")
        if st.button("Generate Q&A ❓", use_container_width=True):
            if topic:
                try:
                    with st.spinner("Generating questions and answers..."):
                        result, used_model = generate_qa(standard, subject, topic)
                    st.success("✅ Q&A Ready!")
                    st.caption(f"Model used: {used_model}")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"❌ Failed to generate Q&A.\n\n{str(e)}")
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
