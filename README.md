# 🎓 StudyFiesta AI

StudyFiesta AI is a universal, AI-powered EdTech platform designed to simplify exam preparation for students across all levels—from Middle School (Class 8+) to PhD researchers, including competitive exams like UPSC, JEE, and NEET.

## ✨ Features
- **Universal Curriculum Support:** Covers School Boards, Undergrad/Postgrad Degrees, Engineering, and Competitive Exams.
- **Dynamic AI Syllabus Fetching:** Automatically retrieves chapter lists for selected subjects.
- **Multi-Tool Arsenal:**
  - 📝 **Summary:** Generates structured academic summaries.
  - 🧠 **Quiz:** Creates 5-question MCQs with explanations.
  - 📌 **Revision Notes:** Highlights key terms, formulas, and concepts.
  - ❓ **Exam Q&A:** Predicts highly probable exam questions with detailed answers.
- **Mathematical Support:** Fully renders complex equations using LaTeX formatting.
- **Professional UI:** Card-based, responsive design built with Streamlit custom CSS.

## 🚀 Installation & Setup

1. **Clone the repository:**
   `git clone https://github.com/yourusername/studyfiesta-ai.git`
   `cd studyfiesta-ai`

2. **Install dependencies:**
   `pip install streamlit google-generativeai pysqlite3`

3. **Set up API Keys:**
   Create a `.streamlit/secrets.toml` file in the root directory and add your Gemini API key:
   `GEMINI_API_KEY = "your_google_gemini_api_key_here"`

4. **Run the application:**
   `streamlit run app.py`

## 🛠️ Tech Stack
- **Frontend/Backend:** Python, Streamlit
- **AI Engine:** Google Gemini (1.5 Pro / Flash)
- **Database:** SQLite (Local User Authentication)

## 🔮 Future Roadmap
- [ ] Export generated notes to PDF and DOCX.
- [ ] User dashboard to save previous study materials.
- [ ] PDF upload support for custom PhD/Masters study material analysis.
- [ ] Migration to PostgreSQL for scalable user management.
