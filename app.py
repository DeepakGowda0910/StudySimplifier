import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import io
import re
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="StudySmart AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# PREMIUM ULTRA-MODERN CSS — FULL VERSION
# =========================================================
st.markdown("""
    <style>
    /* ── IMPORT PROFESSIONAL FONTS ── */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Sora:wght@400;500;600;700;800&display=swap');

    /* ── GLOBAL STYLING ── */
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Sora', 'Poppins', sans-serif !important;
        letter-spacing: 0.3px;
    }

    /* ── PREMIUM GRADIENT BACKGROUND ── */
    .stApp {
        background: radial-gradient(circle at top right, #334155, #111827);
        min-height: 100vh;
    }

    /* ── BETTER SCREEN PADDING FOR MOBILE ── */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1300px;
    }

    /* ── HIDE STREAMLIT CHROME ── */
    #MainMenu  { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }

    /* ── STREAMLIT TABS OVERRIDE ── */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
    }

    /* ════════════════════════════════════════════════════════
       PREMIUM HEADER DESIGN WITH GRADIENT TEXT
    ════════════════════════════════════════════════════════ */
    .sf-header {
        text-align: center;
        padding: 40px 0 10px 0;
        position: relative;
    }

    .sf-header-title {
        font-size: 4.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1;
        letter-spacing: -1px;
    }

    .sf-header-subtitle {
        font-size: 1.2rem;
        color: #cbd5e1;
        margin-top: 10px;
        font-weight: 400;
        letter-spacing: 0.5px;
    }

    /* ════════════════════════════════════════════════════════
       THE WATERMARK — CENTERED BETTER FOR DESKTOP + MOBILE
    ════════════════════════════════════════════════════════ */
    .sf-watermark {
        font-size: 4.4rem;
        font-weight: 900;
        color: rgba(255, 255, 255, 0.05);
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

    /* ════════════════════════════════════════════════════════
       PREMIUM GLASS CARD COMPONENT WITH GLASS MORPHISM
    ════════════════════════════════════════════════════════ */
    .sf-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 30px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .sf-card-dark {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(59, 130, 246, 0.2);
    }

    /* ════════════════════════════════════════════════════════
       PREMIUM BUTTONS WITH GRADIENT & SHADOWS
    ════════════════════════════════════════════════════════ */
    .stButton > button {
        width: 100% !important;
        border-radius: 15px !important;
        height: 3.4rem !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
        letter-spacing: 0.5px !important;
    }
    .stButton > button:hover {
        opacity: 0.95 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5) !important;
    }
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }

    /* ── DOWNLOAD BUTTON (GREEN GRADIENT) ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
        transform: translateY(-3px) !important;
    }

    /* ════════════════════════════════════════════════════════
       PREMIUM SELECTBOX & INPUTS
    ════════════════════════════════════════════════════════ */
    div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1.5px solid rgba(59, 130, 246, 0.3) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e0e7ff !important;
    }

    input[type="text"], input[type="password"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e0e7ff !important;
        border: 1.5px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
    }

    input[type="text"]::placeholder, input[type="password"]::placeholder {
        color: #94a3b8 !important;
    }

    /* ── PREMIUM LABELS ── */
    div.stSelectbox label, div.stTextInput label, div.stRadio label {
        font-weight: 700 !important;
        color: #e0e7ff !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.4px !important;
        text-transform: uppercase;
    }

    /* ════════════════════════════════════════════════════════
       PREMIUM SIDEBAR — DARK GRADIENT
    ════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(59, 130, 246, 0.2) !important;
    }

    [data-testid="stSidebar"] * {
        color: #e0e7ff !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: rgba(59, 130, 246, 0.15) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 10px !important;
        color: #60a5fa !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(59, 130, 246, 0.25) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }

    /* ════════════════════════════════════════════════════════
       OUTPUT CONTENT AREA
    ════════════════════════════════════════════════════════ */
    .sf-output {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        margin-top: 10px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        color: #e2e8f0;
    }

    .sf-output h3, .sf-output h2 {
        color: #60a5fa !important;
        margin-top: 0;
    }

    /* ── SUCCESS / INFO / ERROR MESSAGES ── */
    div[data-testid="stSuccessMessage"] {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px !important;
        color: #86efac !important;
    }

    div[data-testid="stErrorMessage"] {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 12px !important;
        color: #fca5a5 !important;
    }

    div[data-testid="stInfoMessage"] {
        background: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        color: #93c5fd !important;
    }

    div[data-testid="stWarningMessage"] {
        background: rgba(251, 146, 60, 0.1) !important;
        border: 1px solid rgba(251, 146, 60, 0.3) !important;
        border-radius: 12px !important;
        color: #fed7aa !important;
    }

    /* ── DIVIDER ── */
    hr {
        border: none;
        border-top: 1px solid rgba(59, 130, 246, 0.2);
        margin: 20px 0;
    }

    /* ── RADIO BUTTONS ── */
    div[data-testid="stHorizontalBlock"] {
        gap: 12px;
    }

    /* ════════════════════════════════════════════════════════
       📱 MOBILE RESPONSIVE STYLES (768px and below)
    ════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .sf-header-title { font-size: 2.8rem !important; }
        .sf-header-subtitle { font-size: 1rem !important; }
        
        .sf-watermark { 
            font-size: 2.4rem !important; 
            letter-spacing: 6px !important; 
            margin-top: 6px !important;
            margin-bottom: -28px !important;
            top: -4px !important;
        }
        
        .sf-header { padding: 20px 0 10px 0 !important; }

        .sf-card { 
            padding: 20px !important; 
            border-radius: 18px !important; 
            margin-bottom: 15px !important;
        }

        .sf-output { padding: 16px !important; }

        .stButton > button { 
            height: 3.6rem !important; 
            font-size: 15px !important; 
        }

        input[type="text"], input[type="password"] {
            font-size: 16px !important; 
            padding: 12px !important;
        }

        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
    }

    /* ════════════════════════════════════════════════════════
       📱 EXTRA SMALL DEVICES (480px and below)
    ════════════════════════════════════════════════════════ */
    @media (max-width: 480px) {
        .sf-header-title { font-size: 2.2rem !important; }
        .sf-header-subtitle { font-size: 0.9rem !important; }
        .sf-watermark { 
            font-size: 1.8rem !important; 
            letter-spacing: 4px !important; 
            margin-bottom: -35px !important;
        }

        .sf-card { padding: 14px !important; }

        .stButton > button { 
            height: 3.8rem !important; 
            font-size: 14px !important; 
        }
    }

    </style>
""", unsafe_allow_html=True)

# =========================================================
# AI CONFIG — DYNAMIC MULTI-MODEL FALLBACK
# =========================================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

PREFERRED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]

@st.cache_data(ttl=1800, show_spinner=False)
def get_available_models():
    try:
        available = []
        for m in genai.list_models():
            name    = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods and "gemini" in name:
                available.append(name.replace("models/", ""))
        ordered = [m for m in PREFERRED_MODELS if m in available]
        others  = [m for m in available if m not in ordered]
        return ordered + others
    except Exception:
        return PREFERRED_MODELS

def generate_with_fallback(prompt):
    models_to_try = get_available_models()
    errors = []
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 4096,
                },
            )
            response = model.generate_content(prompt)
            if response and hasattr(response, "text") and response.text and response.text.strip():
                return response.text.strip(), model_name
            errors.append(f"{model_name}: empty response")
        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")
            continue
    return "AI generation failed.\n" + "\n".join(errors[-3:]), "None"

# =========================================================
# PDF GENERATOR
# =========================================================
def generate_pdf(title, subtitle, content_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()

    s_title = ParagraphStyle(
        "T", parent=styles["Title"],
        fontSize=22, textColor=colors.HexColor("#1e3c72"),
        spaceAfter=8, alignment=TA_CENTER, fontName="Helvetica-Bold",
    )
    s_sub = ParagraphStyle(
        "S", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#555555"),
        spaceAfter=16, alignment=TA_CENTER,
    )
    s_head = ParagraphStyle(
        "H", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2a5298"),
        spaceBefore=14, spaceAfter=5, fontName="Helvetica-Bold",
    )
    s_body = ParagraphStyle(
        "B", parent=styles["Normal"],
        fontSize=10, leading=16,
        textColor=colors.HexColor("#1a1a1a"), spaceAfter=4,
    )
    s_bullet = ParagraphStyle(
        "Bu", parent=styles["Normal"],
        fontSize=10, leading=16,
        textColor=colors.HexColor("#1a1a1a"),
        leftIndent=16, bulletIndent=6, spaceAfter=3,
    )
    s_footer = ParagraphStyle(
        "F", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#aaaaaa"),
        alignment=TA_CENTER,
    )

    story = [
        Paragraph(title, s_title),
        Paragraph(subtitle, s_sub),
        HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#1e3c72")),
        Spacer(1, 0.4*cm),
    ]

    for line in content_text.split("\n"):
        s = line.strip()
        if not s:
            story.append(Spacer(1, 0.2*cm))
            continue
        s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
        s = re.sub(r"\*(.+?)\*",     r"\1", s)
        s = re.sub(r"\$$\$$(.+?)\$$\$$", r"[\1]", s)
        s = re.sub(r"\\$$(.+?)\\$$", r"[\1]", s)
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if s.startswith("## ") or s.startswith("### "):
            story.append(Paragraph(s.lstrip("#").strip(), s_head))
        elif re.match(r"^\d+\.\s+[A-Z0-9 ()\-]{4,}$", s):
            story.append(Paragraph(s, s_head))
        elif s.startswith("- ") or s.startswith("• ") or s.startswith("* "):
            story.append(Paragraph(f"• {s[2:].strip()}", s_bullet))
        elif re.match(r"^\d+\.\s", s) and len(s) < 120:
            story.append(Paragraph(s, s_bullet))
        else:
            story.append(Paragraph(s, s_body))

    story.extend([
        Spacer(1, 0.6*cm),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")),
        Spacer(1, 0.2*cm),
        Paragraph("Generated by StudyFiesta AI 🎓 | Your Smart Exam Preparation Platform", s_footer),
    ])

    doc.build(story)
    buffer.seek(0)
    return buffer

# =========================================================
# DATABASE
# =========================================================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_p(password):
    return hashlib.sha256(password.encode()).hexdigest()
# =========================================================
# DATA MAP
# =========================================================
DATA_MAP = {
    "Competitive Exams 🏆": {
        "UPSC (Civil Services)": [
            "General Studies 1", "General Studies 2 (CSAT)",
            "History Optional", "Geography Optional",
            "Public Administration", "Ethics"
        ],
        "JEE (Mains/Adv)":  ["Physics", "Chemistry", "Mathematics"],
        "NEET":              ["Biology", "Physics", "Chemistry"],
        "GATE":              ["Computer Science", "Mechanical", "Electrical", "Civil", "Electronics"],
        "Banking/SSC":       ["Quantitative Aptitude", "Reasoning", "English", "General Awareness"],
    },
    "Engineering & Tech 💻": {
        "B.Tech / M.Tech": [
            "Computer Science (CSE)", "Information Technology (IT)",
            "Electronics (ECE)", "Mechanical (ME)", "Civil (CE)", "AI & Data Science"
        ],
        "Polytechnic Diploma": ["Mechanical", "Electrical", "Civil", "Computer"],
        "BCA / MCA": [
            "Programming in C/C++", "Java & Python",
            "Database Management", "Software Engineering", "Web Development"
        ],
    },
    "School (K-12) 🏫": {
        "Class 10": [
            "Mathematics", "Science",
            "Social Science — History", "Social Science — Geography",
            "Social Science — Civics (Political Science)", "Social Science — Economics",
            "English", "Hindi"
        ],
        "Class 11 & 12": [
            "Physics", "Chemistry", "Mathematics", "Biology",
            "Accountancy", "Business Studies", "Economics", "History", "Psychology"
        ],
    },
    "Degree & Masters 🎓": {
        "Commerce (B.Com/M.Com)": [
            "Financial Accounting", "Corporate Tax", "Auditing", "Costing", "Management Accounting"
        ],
        "Science (B.Sc/M.Sc)": [
            "Physics", "Chemistry", "Maths", "Zoology", "Botany", "Biotechnology"
        ],
        "Management (BBA/MBA)": ["Marketing", "Finance", "HR", "Operations", "Strategy"],
        "Arts (B.A/M.A)": [
            "English Literature", "Political Science", "Economics", "History", "Psychology"
        ],
    }
}

BOARDS = [
    "CBSE", "ICSE", "IGCSE",
    "State Board (Maharashtra)", "State Board (Karnataka)",
    "State Board (UP)", "State Board (Others)"
]

# =========================================================
# TOPIC MAP
# =========================================================
TOPIC_MAP = {
    "School (K-12) 🏫": {
        "Class 10": {
            "Mathematics": [
                "Number Systems & Algebra", "Geometry", "Trigonometry",
                "Coordinate Geometry", "Mensuration", "Statistics & Probability"
            ],
            "Science": ["Chemistry", "Biology", "Physics"],
            "Social Science — History": [
                "Events and Processes",
                "Livelihoods Economies and Societies",
                "Everyday Life Culture and Politics"
            ],
            "Social Science — Geography": [
                "Resources", "Agriculture and Industries", "Transport and Communication"
            ],
            "Social Science — Civics (Political Science)": [
                "Power Sharing and Democracy", "Political Institutions", "Outcomes of Democracy"
            ],
            "Social Science — Economics": [
                "Development and Sectors", "Money Banking and Trade", "Consumer Awareness"
            ],
            "English": [
                "Literature — Prose", "Literature — Poetry", "Grammar", "Writing Skills"
            ],
            "Hindi": [
                "गद्य (Prose)", "पद्य (Poetry)", "व्याकरण (Grammar)", "लेखन (Writing)"
            ],
        },
        "Class 11 & 12": {
            "Physics": [
                "Mechanics", "Thermodynamics & Waves",
                "Electromagnetism", "Optics & Modern Physics"
            ],
            "Chemistry": ["Physical Chemistry", "Inorganic Chemistry", "Organic Chemistry"],
            "Mathematics": [
                "Algebra", "Calculus", "Coordinate Geometry",
                "Vectors & 3D", "Statistics & Probability"
            ],
            "Biology": [
                "Cell Biology & Diversity", "Plant Physiology", "Human Physiology",
                "Genetics & Evolution", "Ecology & Environment"
            ],
            "Accountancy": [
                "Basic Accounting", "Partnership Accounts",
                "Company Accounts", "Analysis of Financial Statements"
            ],
            "Business Studies": [
                "Nature and Forms of Business", "Management Principles",
                "Business Finance and Marketing"
            ],
            "Economics": ["Microeconomics", "Macroeconomics", "Indian Economic Development"],
            "History":   ["Themes in Indian History", "World History"],
            "Psychology": [
                "Foundations of Psychology", "Human Behaviour and Processes", "Applied Psychology"
            ],
        },
    },
    "Competitive Exams 🏆": {
        "JEE (Mains/Adv)": {
            "Physics":     ["Mechanics", "Thermodynamics", "Electrodynamics", "Optics & Modern Physics"],
            "Chemistry":   ["Physical Chemistry", "Inorganic Chemistry", "Organic Chemistry"],
            "Mathematics": ["Algebra", "Calculus", "Coordinate Geometry", "Trigonometry", "Probability"],
        },
        "NEET": {
            "Biology":   ["Cell Biology", "Plant Biology", "Human Physiology", "Genetics & Evolution", "Ecology"],
            "Physics":   ["Mechanics", "Thermodynamics", "Electrodynamics", "Optics"],
            "Chemistry": ["Physical Chemistry", "Inorganic Chemistry", "Organic Chemistry"],
        },
        "GATE": {
            "Computer Science": [
                "Programming & Data Structures", "Theory of Computation",
                "Systems (OS & Networks)", "Databases & Engineering Math"
            ],
            "Mechanical": ["Mechanics & Design", "Thermal Sciences", "Manufacturing"],
            "Electrical": ["Circuits & Machines", "Power Systems", "Signals & Control"],
            "Civil":      ["Structures & Geotechnical", "Fluid & Environmental", "Transportation"],
            "Electronics":["Circuits & Devices", "Signals & Control", "Communications"],
        },
        "Banking/SSC": {
            "Quantitative Aptitude": ["Arithmetic", "Algebra & Geometry", "Data Interpretation"],
            "Reasoning":             ["Verbal Reasoning", "Non-Verbal Reasoning", "Puzzles"],
            "English":               ["Comprehension & Vocabulary", "Grammar", "Writing"],
            "General Awareness":     ["Current Affairs", "Static GK", "Banking & Finance"],
        },
        "UPSC (Civil Services)": {
            "General Studies 1":        ["History", "Geography", "Society"],
            "General Studies 2 (CSAT)": ["Comprehension", "Reasoning", "Numeracy"],
            "History Optional":         ["Ancient India", "Medieval India", "Modern India", "World History"],
            "Geography Optional":       ["Physical Geography", "Human Geography", "Indian Geography"],
            "Public Administration":    ["Administrative Theory", "Indian Administration"],
            "Ethics":                   ["Ethics & Integrity", "Attitude & Aptitude", "Case Studies"],
        },
    },
    "Engineering & Tech 💻": {
        "B.Tech / M.Tech": {
            "Computer Science (CSE)": [
                "Programming Fundamentals", "Core CS (OS, Networks, DBMS)",
                "Algorithms & Theory", "AI & Machine Learning"
            ],
            "Information Technology (IT)": ["Networking & Security", "Web & Cloud", "Data & Analytics"],
            "Electronics (ECE)":           ["Circuits & Devices", "Communication Systems", "Embedded Systems"],
            "Mechanical (ME)":             ["Mechanics & Design", "Thermal Sciences", "Manufacturing"],
            "Civil (CE)":                  ["Structures", "Geotechnical & Environmental", "Transportation"],
            "AI & Data Science":           ["Statistics & Math", "Machine Learning", "Deep Learning & NLP", "Data Engineering"],
        },
        "Polytechnic Diploma": {
            "Mechanical": ["Mechanics", "Thermal", "Manufacturing"],
            "Electrical":  ["Circuits", "Machines", "Power"],
            "Civil":       ["Structures", "Construction", "Surveying"],
            "Computer":    ["Programming", "Networking", "DBMS"],
        },
        "BCA / MCA": {
            "Programming in C/C++": ["Basics", "Functions & Arrays", "OOP Concepts"],
            "Java & Python":        ["Core Java", "Python Basics", "OOP & Libraries"],
            "Database Management":  ["ER Model & SQL", "Normalization", "Transactions"],
            "Software Engineering": ["SDLC Models", "Testing", "Agile"],
            "Web Development":      ["Frontend", "Backend", "Deployment"],
        },
    },
    "Degree & Masters 🎓": {
        "Commerce (B.Com/M.Com)": {
            "Financial Accounting":    ["Basic Accounts", "Partnership", "Company Accounts"],
            "Corporate Tax":           ["Income Tax Basics", "Corporate Tax Planning"],
            "Auditing":                ["Audit Basics", "Types of Audit", "Audit Report"],
            "Costing":                 ["Material & Labour", "Process Costing", "Marginal Costing"],
            "Management Accounting":   ["Ratio Analysis", "Budgeting", "Standard Costing"],
        },
        "Science (B.Sc/M.Sc)": {
            "Physics":       ["Classical Mechanics", "Electromagnetism", "Quantum Mechanics", "Modern Physics"],
            "Chemistry":     ["Physical", "Organic", "Inorganic", "Analytical"],
            "Maths":         ["Analysis", "Algebra", "Differential Equations", "Topology"],
            "Zoology":       ["Animal Diversity", "Physiology", "Genetics", "Ecology"],
            "Botany":        ["Plant Diversity", "Physiology", "Genetics", "Ecology"],
            "Biotechnology": ["Molecular Biology", "Genetic Engineering", "Bioprocess", "Bioinformatics"],
        },
        "Management (BBA/MBA)": {
            "Marketing":  ["Basics & Consumer Behaviour", "Strategy & Mix", "Digital Marketing"],
            "Finance":    ["Financial Management", "Investments", "Risk"],
            "HR":         ["Recruitment & Training", "Performance & Compensation", "Employee Relations"],
            "Operations": ["Process & Capacity", "Quality & Supply Chain"],
            "Strategy":   ["Analysis & Positioning", "Corporate Strategy"],
        },
        "Arts (B.A/M.A)": {
            "English Literature": ["Poetry", "Drama", "Novel & Prose", "Literary Theory"],
            "Political Science":  ["Political Theory", "Indian Politics", "International Relations"],
            "Economics":          ["Micro & Macro", "Indian Economy", "Development Economics"],
            "History":            ["Ancient", "Medieval", "Modern", "World History"],
            "Psychology":         ["Cognitive & Social", "Developmental & Abnormal", "Research Methods"],
        },
    },
}

# =========================================================
# CHAPTER MAP — FULL NCERT VERIFIED
# =========================================================
CHAPTER_MAP = {
    "School (K-12) 🏫": {
        "Class 10": {
            "Mathematics": {
                "Number Systems & Algebra": [
                    "Ch 1: Real Numbers",
                    "Ch 2: Polynomials",
                    "Ch 3: Pair of Linear Equations in Two Variables",
                    "Ch 4: Quadratic Equations",
                    "Ch 5: Arithmetic Progressions",
                ],
                "Geometry": [
                    "Ch 6: Triangles",
                    "Ch 10: Circles",
                    "Ch 11: Constructions",
                ],
                "Trigonometry": [
                    "Ch 8: Introduction to Trigonometry",
                    "Ch 9: Some Applications of Trigonometry",
                ],
                "Coordinate Geometry": ["Ch 7: Coordinate Geometry"],
                "Mensuration": [
                    "Ch 12: Areas Related to Circles",
                    "Ch 13: Surface Areas and Volumes",
                ],
                "Statistics & Probability": [
                    "Ch 14: Statistics",
                    "Ch 15: Probability",
                ],
            },
            "Science": {
                "Chemistry": [
                    "Ch 1: Chemical Reactions and Equations",
                    "Ch 2: Acids, Bases and Salts",
                    "Ch 3: Metals and Non-metals",
                    "Ch 4: Carbon and Its Compounds",
                    "Ch 5: Periodic Classification of Elements",
                ],
                "Biology": [
                    "Ch 6: Life Processes",
                    "Ch 7: Control and Coordination",
                    "Ch 8: How do Organisms Reproduce?",
                    "Ch 9: Heredity and Evolution",
                    "Ch 15: Our Environment",
                ],
                "Physics": [
                    "Ch 10: Light - Reflection and Refraction",
                    "Ch 11: Human Eye and the Colourful World",
                    "Ch 12: Electricity",
                    "Ch 13: Magnetic Effects of Electric Current",
                    "Ch 14: Sources of Energy",
                ],
            },
            "Social Science — History": {
                "Events and Processes": [
                    "Ch 1: The Rise of Nationalism in Europe",
                    "Ch 2: Nationalism in India",
                ],
                "Livelihoods Economies and Societies": [
                    "Ch 3: The Making of a Global World",
                    "Ch 4: The Age of Industrialisation",
                ],
                "Everyday Life Culture and Politics": [
                    "Ch 5: Print Culture and the Modern World",
                ],
            },
            "Social Science — Geography": {
                "Resources": [
                    "Ch 1: Resources and Development",
                    "Ch 2: Forest and Wildlife Resources",
                    "Ch 3: Water Resources",
                ],
                "Agriculture and Industries": [
                    "Ch 4: Agriculture",
                    "Ch 5: Minerals and Energy Resources",
                    "Ch 6: Manufacturing Industries",
                ],
                "Transport and Communication": [
                    "Ch 7: Lifelines of the National Economy",
                ],
            },
            "Social Science — Civics (Political Science)": {
                "Power Sharing and Democracy": [
                    "Ch 1: Power Sharing",
                    "Ch 2: Federalism",
                    "Ch 3: Gender, Religion and Caste",
                ],
                "Political Institutions": ["Ch 4: Political Parties"],
                "Outcomes of Democracy":  ["Ch 5: Outcomes of Democracy"],
            },
            "Social Science — Economics": {
                "Development and Sectors": [
                    "Ch 1: Development",
                    "Ch 2: Sectors of the Indian Economy",
                ],
                "Money Banking and Trade": [
                    "Ch 3: Money and Credit",
                    "Ch 4: Globalisation and the Indian Economy",
                ],
                "Consumer Awareness": ["Ch 5: Consumer Rights"],
            },
            "English": {
                "Literature — Prose": [
                    "A Letter to God",
                    "Nelson Mandela: Long Walk to Freedom",
                    "Two Stories About Flying",
                    "From the Diary of Anne Frank",
                    "Glimpses of India",
                    "Mijbil the Otter",
                    "Madam Rides the Bus",
                    "The Sermon at Benares",
                    "The Proposal",
                ],
                "Literature — Poetry": [
                    "Dust of Snow", "Fire and Ice",
                    "A Tiger in the Zoo", "How to Tell Wild Animals",
                    "The Ball Poem", "Amanda", "Animals",
                    "The Trees", "Fog",
                    "The Tale of Custard the Dragon", "For Anne Gregory",
                ],
                "Grammar": [
                    "Tenses", "Modals", "Subject-Verb Agreement",
                    "Reported Speech", "Active and Passive Voice",
                    "Determiners", "Clauses",
                ],
                "Writing Skills": [
                    "Formal Letter Writing", "Informal Letter Writing",
                    "Notice Writing", "Paragraph Writing", "Essay Writing",
                ],
            },
            "Hindi": {
                "गद्य (Prose)": [
                    "नेताजी का चश्मा", "बालगोबिन भगत", "लखनवी अंदाज़",
                    "एही ठैयाँ झुलनी हेरानी हो रामा", "मानवीय करुणा की दिव्य चमक",
                    "एक कहानी यह भी", "स्त्री शिक्षा के विरोधी कुतर्कों का खण्डन",
                    "नौबतखाने में इबादत", "संस्कृति",
                ],
                "पद्य (Poetry)": [
                    "सूर के पद", "राम-लक्ष्मण-परशुराम संवाद",
                    "देव के सवैये और कवित्त", "आत्मकथ्य",
                    "उत्साह और अट नहीं रही", "यह दंतुरहित मुस्कान और फसल",
                    "छाया मत छूना", "कन्यादान", "संगतकार",
                ],
                "व्याकरण (Grammar)": [
                    "पद परिचय", "रस", "अलंकार", "समास", "वाच्य", "वाक्य भेद", "मुहावरे",
                ],
                "लेखन (Writing)": [
                    "पत्र लेखन", "निबंध लेखन", "सूचना लेखन", "विज्ञापन लेखन",
                ],
            },
        },
        "Class 11 & 12": {
            "Physics": {
                "Mechanics": [
                    "Ch 1: Physical World",
                    "Ch 2: Units and Measurements",
                    "Ch 3: Motion in a Straight Line",
                    "Ch 4: Motion in a Plane",
                    "Ch 5: Laws of Motion",
                    "Ch 6: Work, Energy and Power",
                    "Ch 7: Systems of Particles and Rotational Motion",
                    "Ch 8: Gravitation",
                ],
                "Thermodynamics & Waves": [
                    "Ch 9: Mechanical Properties of Solids",
                    "Ch 10: Mechanical Properties of Fluids",
                    "Ch 11: Thermal Properties of Matter",
                    "Ch 12: Thermodynamics",
                    "Ch 13: Kinetic Theory",
                    "Ch 14: Oscillations",
                    "Ch 15: Waves",
                ],
                "Electromagnetism": [
                    "Ch 1 (XII): Electric Charges and Fields",
                    "Ch 2 (XII): Electrostatic Potential and Capacitance",
                    "Ch 3 (XII): Current Electricity",
                    "Ch 4 (XII): Moving Charges and Magnetism",
                    "Ch 5 (XII): Magnetism and Matter",
                    "Ch 6 (XII): Electromagnetic Induction",
                    "Ch 7 (XII): Alternating Current",
                    "Ch 8 (XII): Electromagnetic Waves",
                ],
                "Optics & Modern Physics": [
                    "Ch 9 (XII): Ray Optics and Optical Instruments",
                    "Ch 10 (XII): Wave Optics",
                    "Ch 11 (XII): Dual Nature of Radiation and Matter",
                    "Ch 12 (XII): Atoms",
                    "Ch 13 (XII): Nuclei",
                    "Ch 14 (XII): Semiconductor Electronics",
                ],
            },
            "Chemistry": {
                "Physical Chemistry": [
                    "Ch 1: Some Basic Concepts of Chemistry",
                    "Ch 2: Structure of Atom",
                    "Ch 5: States of Matter",
                    "Ch 6: Thermodynamics",
                    "Ch 7: Equilibrium",
                    "Ch 8: Redox Reactions",
                    "Ch 1 (XII): The Solid State",
                    "Ch 2 (XII): Solutions",
                    "Ch 3 (XII): Electrochemistry",
                    "Ch 4 (XII): Chemical Kinetics",
                ],
                "Inorganic Chemistry": [
                    "Ch 3: Classification of Elements and Periodicity",
                    "Ch 4: Chemical Bonding and Molecular Structure",
                    "Ch 9: Hydrogen",
                    "Ch 10: The s-Block Elements",
                    "Ch 11: The p-Block Elements",
                    "Ch 6 (XII): The p-Block Elements (continued)",
                    "Ch 7 (XII): The d and f-Block Elements",
                    "Ch 8 (XII): Coordination Compounds",
                ],
                "Organic Chemistry": [
                    "Ch 12: Organic Chemistry - Some Basic Principles",
                    "Ch 13: Hydrocarbons",
                    "Ch 14: Environmental Chemistry",
                    "Ch 9 (XII): Haloalkanes and Haloarenes",
                    "Ch 10 (XII): Alcohols, Phenols and Ethers",
                    "Ch 11 (XII): Aldehydes, Ketones and Carboxylic Acids",
                    "Ch 12 (XII): Amines",
                    "Ch 13 (XII): Biomolecules",
                    "Ch 14 (XII): Polymers",
                    "Ch 15 (XII): Chemistry in Everyday Life",
                ],
            },
            "Mathematics": {
                "Algebra": [
                    "Ch 1: Sets",
                    "Ch 2: Relations and Functions",
                    "Ch 5: Complex Numbers and Quadratic Equations",
                    "Ch 6: Linear Inequalities",
                    "Ch 7: Permutations and Combinations",
                    "Ch 8: Binomial Theorem",
                    "Ch 9: Sequences and Series",
                    "Ch 1 (XII): Relations and Functions",
                    "Ch 3 (XII): Matrices",
                    "Ch 4 (XII): Determinants",
                ],
                "Calculus": [
                    "Ch 13: Limits and Derivatives",
                    "Ch 5 (XII): Continuity and Differentiability",
                    "Ch 6 (XII): Application of Derivatives",
                    "Ch 7 (XII): Integrals",
                    "Ch 8 (XII): Application of Integrals",
                    "Ch 9 (XII): Differential Equations",
                ],
                "Coordinate Geometry": [
                    "Ch 10: Straight Lines",
                    "Ch 11: Conic Sections",
                    "Ch 12: Introduction to 3D Geometry",
                ],
                "Vectors & 3D": [
                    "Ch 10 (XII): Vector Algebra",
                    "Ch 11 (XII): Three-Dimensional Geometry",
                ],
                "Statistics & Probability": [
                    "Ch 15: Statistics",
                    "Ch 16: Probability",
                    "Ch 13 (XII): Probability",
                ],
            },
            "Biology": {
                "Cell Biology & Diversity": [
                    "Ch 1: The Living World",
                    "Ch 2: Biological Classification",
                    "Ch 3: Plant Kingdom",
                    "Ch 4: Animal Kingdom",
                    "Ch 8: Cell - The Unit of Life",
                    "Ch 9: Biomolecules",
                    "Ch 10: Cell Cycle and Cell Division",
                ],
                "Plant Physiology": [
                    "Ch 5: Morphology of Flowering Plants",
                    "Ch 6: Anatomy of Flowering Plants",
                    "Ch 11: Transport in Plants",
                    "Ch 12: Mineral Nutrition",
                    "Ch 13: Photosynthesis in Higher Plants",
                    "Ch 14: Respiration in Plants",
                    "Ch 15: Plant Growth and Development",
                ],
                "Human Physiology": [
                    "Ch 7: Structural Organisation in Animals",
                    "Ch 16: Digestion and Absorption",
                    "Ch 17: Breathing and Exchange of Gases",
                    "Ch 18: Body Fluids and Circulation",
                    "Ch 19: Excretory Products and Elimination",
                    "Ch 20: Locomotion and Movement",
                    "Ch 21: Neural Control and Coordination",
                    "Ch 22: Chemical Coordination and Integration",
                ],
                "Genetics & Evolution": [
                    "Ch 1 (XII): Reproduction in Organisms",
                    "Ch 2 (XII): Sexual Reproduction in Flowering Plants",
                    "Ch 3 (XII): Human Reproduction",
                    "Ch 4 (XII): Reproductive Health",
                    "Ch 5 (XII): Principles of Inheritance and Variation",
                    "Ch 6 (XII): Molecular Basis of Inheritance",
                    "Ch 7 (XII): Evolution",
                ],
                "Ecology & Environment": [
                    "Ch 13 (XII): Organisms and Populations",
                    "Ch 14 (XII): Ecosystem",
                    "Ch 15 (XII): Biodiversity and Conservation",
                    "Ch 16 (XII): Environmental Issues",
                ],
            },
            "Accountancy": {
                "Basic Accounting": [
                    "Ch 1: Introduction to Accounting",
                    "Ch 2: Theory Base of Accounting",
                    "Ch 3: Recording of Transactions",
                    "Ch 4: Bank Reconciliation Statement",
                    "Ch 5: Ledger",
                    "Ch 6: Trial Balance and Rectification",
                    "Ch 7: Depreciation, Provisions and Reserves",
                    "Ch 8: Bills of Exchange",
                ],
                "Partnership Accounts": [
                    "Ch 1 (XII): Accounting for Partnership - Basic Concepts",
                    "Ch 2 (XII): Change in Profit-Sharing Ratio",
                    "Ch 3 (XII): Admission of a Partner",
                    "Ch 4 (XII): Retirement and Death of a Partner",
                    "Ch 5 (XII): Dissolution of Partnership Firm",
                ],
                "Company Accounts": [
                    "Ch 6 (XII): Accounting for Share Capital",
                    "Ch 7 (XII): Issue and Redemption of Debentures",
                ],
                "Analysis of Financial Statements": [
                    "Ch 8 (XII): Financial Statements of a Company",
                    "Ch 9 (XII): Analysis of Financial Statements",
                    "Ch 10 (XII): Accounting Ratios",
                    "Ch 11 (XII): Cash Flow Statement",
                ],
            },
            "Business Studies": {
                "Nature and Forms of Business": [
                    "Ch 1: Nature and Purpose of Business",
                    "Ch 2: Forms of Business Organisation",
                    "Ch 3: Private, Public and Global Enterprises",
                    "Ch 4: Business Services",
                    "Ch 5: Emerging Modes of Business",
                    "Ch 6: Social Responsibility of Business",
                ],
                "Management Principles": [
                    "Ch 1 (XII): Nature and Significance of Management",
                    "Ch 2 (XII): Principles of Management",
                    "Ch 3 (XII): Business Environment",
                    "Ch 4 (XII): Planning",
                    "Ch 5 (XII): Organising",
                    "Ch 6 (XII): Staffing",
                    "Ch 7 (XII): Directing",
                    "Ch 8 (XII): Controlling",
                ],
                "Business Finance and Marketing": [
                    "Ch 9 (XII): Financial Management",
                    "Ch 10 (XII): Financial Markets",
                    "Ch 11 (XII): Marketing Management",
                    "Ch 12 (XII): Consumer Protection",
                ],
            },
            "Economics": {
                "Microeconomics": [
                    "Ch 1: Introduction to Microeconomics",
                    "Ch 2: Theory of Consumer Behaviour",
                    "Ch 3: Production and Costs",
                    "Ch 4: Theory of the Firm under Perfect Competition",
                    "Ch 5: Market Equilibrium",
                    "Ch 6: Non-Competitive Markets",
                ],
                "Macroeconomics": [
                    "Ch 1 (XII): Introduction to Macroeconomics",
                    "Ch 2 (XII): National Income Accounting",
                    "Ch 3 (XII): Money and Banking",
                    "Ch 4 (XII): Determination of Income and Employment",
                    "Ch 5 (XII): Government Budget and the Economy",
                    "Ch 6 (XII): Balance of Payments",
                ],
                "Indian Economic Development": [
                    "Ch 1: Indian Economy on the Eve of Independence",
                    "Ch 2: Indian Economy 1950-1990",
                    "Ch 3: Liberalisation, Privatisation and Globalisation",
                    "Ch 4: Poverty",
                    "Ch 5: Human Capital Formation",
                    "Ch 6: Rural Development",
                    "Ch 7: Employment",
                    "Ch 8: Infrastructure",
                    "Ch 9: Environment and Sustainable Development",
                    "Ch 10: Comparative Development Experiences",
                ],
            },
            "History": {
                "Themes in Indian History": [
                    "Ch 1: Bricks, Beads and Bones (Harappan Civilisation)",
                    "Ch 2: Kings, Farmers and Towns",
                    "Ch 3: Kinship, Caste and Class",
                    "Ch 4: Thinkers, Beliefs and Buildings",
                    "Ch 5: Through the Eyes of Travellers",
                    "Ch 6: Bhakti-Sufi Traditions",
                    "Ch 7: An Imperial Capital - Vijayanagara",
                    "Ch 8: Peasants, Zamindars and the State",
                    "Ch 9: Kings and Chronicles",
                    "Ch 10: Colonialism and the Countryside",
                    "Ch 11: Rebels and the Raj",
                    "Ch 12: Colonial Cities",
                    "Ch 13: Mahatma Gandhi and the Nationalist Movement",
                    "Ch 14: Understanding Partition",
                    "Ch 15: Framing the Constitution",
                ],
                "World History": [
                    "Ch 1: From the Beginning of Time",
                    "Ch 2: Writing and City Life",
                    "Ch 3: An Empire Across Three Continents",
                    "Ch 4: The Central Islamic Lands",
                    "Ch 5: Nomadic Empires",
                    "Ch 6: The Three Orders",
                    "Ch 7: Changing Cultural Traditions",
                    "Ch 8: Confrontation of Cultures",
                    "Ch 9: The Industrial Revolution",
                    "Ch 10: Displacing Indigenous Peoples",
                    "Ch 11: Paths to Modernisation",
                ],
            },
            "Psychology": {
                "Foundations of Psychology": [
                    "Ch 1: What is Psychology?",
                    "Ch 2: Methods of Enquiry in Psychology",
                    "Ch 3: The Bases of Human Behaviour",
                ],
                "Human Behaviour and Processes": [
                    "Ch 4: Human Development",
                    "Ch 5: Sensory, Attentional and Perceptual Processes",
                    "Ch 6: Learning",
                    "Ch 7: Human Memory",
                    "Ch 8: Thinking",
                    "Ch 9: Motivation and Emotion",
                ],
                "Applied Psychology": [
                    "Ch 1 (XII): Variations in Psychological Attributes",
                    "Ch 2 (XII): Self and Personality",
                    "Ch 3 (XII): Meeting Life Challenges",
                    "Ch 4 (XII): Psychological Disorders",
                    "Ch 5 (XII): Therapeutic Approaches",
                    "Ch 6 (XII): Attitude and Social Cognition",
                    "Ch 7 (XII): Social Influence and Group Processes",
                    "Ch 8 (XII): Psychology and Life",
                    "Ch 9 (XII): Developing Psychological Skills",
                ],
            },
        },
    },
}

# =========================================================
# HELPERS
# =========================================================
def get_topics(category, course, subject):
    course_data = TOPIC_MAP.get(category, {}).get(course, {})
    if isinstance(course_data, dict):
        return course_data.get(subject, ["General Topics"])
    return ["General Topics"]

def get_chapters(category, course, subject, topic):
    chapters = (
        CHAPTER_MAP
        .get(category, {})
        .get(course, {})
        .get(subject, {})
        .get(topic, [])
    )
    if chapters:
        return chapters
    prompt = (
        f"You are an academic syllabus expert. "
        f"List the standard chapter names for the topic '{topic}' "
        f"in '{subject}' for {course}. "
        f"Return ONLY a comma-separated list. No numbers, no explanation."
    )
    result, _ = generate_with_fallback(prompt)
    if "failed" in result.lower() or not result.strip():
        return [f"Introduction to {topic}", f"Core Concepts of {topic}", f"Advanced {topic}"]
    chapters = [c.strip() for c in result.split(",") if c.strip() and len(c.strip()) > 2]
    return chapters if chapters else [f"Introduction to {topic}"]

def build_prompt(tool, chap, topic, sub, audience, output_style):
    style_map = {
        "📄 Detailed":      "Write thoroughly. Every section needs at least 3-5 bullets or 3-4 sentences.",
        "⚡ Short & Quick": "Keep concise. Minimum 2 bullets per section. No empty sections.",
        "📋 Notes Format":  "Use bullet points throughout. At least 2-3 bullets per section.",
    }
    si = style_map[output_style]

    if tool == "📝 Summary":
        return f"""Act as a professional teacher for {audience}.
STYLE: {si}
Create a COMPLETE summary for chapter '{chap}' (topic: '{topic}') in '{sub}'.
Include ALL 5 sections:
1. OVERVIEW — what this chapter is about
2. KEY CONCEPTS — all important definitions
3. IMPORTANT POINTS — facts, formulas, dates
4. EXAM FOCUS — what to study for exams
5. QUICK REVISION NOTES — 5-6 short bullets
Use LaTeX for math. Keep language student-friendly."""

    if tool == "🧠 Quiz":
        return f"""Act as an expert for {audience}.
STYLE: {si}
Generate exactly 5 MCQs for '{chap}' (topic: {topic}) in '{sub}'.
Each question: Question, Options A-D, Correct Answer, Explanation.
Use LaTeX for math."""

    if tool == "📌 Revision Notes":
        return f"""Act as a revision coach for {audience}.
STYLE: {si}
Create detailed revision notes for '{chap}' (topic: {topic}) in '{sub}'.
Include: headings, definitions, formulas, memory tips. No empty sections.
Use LaTeX for math."""

    if tool == "❓ Exam Q&A":
        return f"""Act as an exam coach for {audience}.
STYLE: {si}
Generate exactly 5 exam questions with complete model answers for '{chap}' (topic: {topic}) in '{sub}'.
Every answer must be complete. Use LaTeX for math."""

    return ""
# =========================================================
# MAIN APPLICATION
# =========================================================
def main_app():
    # ── SIDEBAR ──────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align:center; padding: 20px 0 15px 0;">
                <div style="font-size:3rem; margin-bottom: 8px;">🎓</div>
                <div style="font-size:1.4rem; font-weight:800; background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">StudySmart</div>
                <div style="font-size:0.9rem; opacity:0.8; margin-top: 6px;">Welcome, {st.session_state.username}</div>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

        tool = st.radio(
            "SELECT TOOL",
            ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "❓ Exam Q&A"]
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

    # ── PREMIUM HEADER WITH WATERMARK ───────────────────────────────
    st.markdown("""
        <div class="sf-header">
            <div class="sf-header-title">StudySmart</div>
            <div class="sf-header-subtitle">Your Smart Exam Preparation Platform</div>
        </div>
        <div class="sf-watermark">POWERED BY AI</div>
    """, unsafe_allow_html=True)

    # ── SELECTION CARD ────────────────────────────────────
    st.markdown('<div class="sf-card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.2, 1.2, 1])
    with c1:
        cat = st.selectbox("📚 Category", list(DATA_MAP.keys()))
    with c2:
        course = st.selectbox("🎓 Exam / Course", list(DATA_MAP[cat].keys()))
    with c3:
        if "School" in cat:
            board = st.selectbox("🏫 Board", BOARDS)
        else:
            board = "University / National Syllabus"
            st.info(f"📌 {board}")

    c4, c5 = st.columns(2)
    with c4:
        sub = st.selectbox("📖 Subject", DATA_MAP[cat][course])

    topics_list = get_topics(cat, course, sub)
    with c5:
        topic = st.selectbox("🗂️ Topic / Unit", topics_list)

    # Chapter auto-load with caching
    chapter_key = f"{cat}||{course}||{sub}||{topic}"
    if "last_chapter_key" not in st.session_state:
        st.session_state.last_chapter_key = ""
    if "current_chapters" not in st.session_state:
        st.session_state.current_chapters = []
    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters = get_chapters(cat, course, sub, topic)
        st.session_state.last_chapter_key = chapter_key

    chap = st.selectbox("📝 Chapter", st.session_state.current_chapters)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── OUTPUT STYLE ──────────────────────────────────────
    output_style = st.radio(
        "⚙️ Output Style",
        ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format"],
        horizontal=True
    )

    # ── GENERATE BUTTON ───────────────────────────────────
    if st.button(f"✨ Generate {tool}", use_container_width=True):
        audience = (
            f"{board} {course} students"
            if "School" in cat
            else f"{course} students"
        )
        final_prompt = build_prompt(tool, chap, topic, sub, audience, output_style)

        with st.spinner(f"🧠 Generating {tool} for '{chap}'... please wait ⏳"):
            try:
                result, model_used = generate_with_fallback(final_prompt)
            except Exception as e:
                result, model_used = f"Unexpected error: {e}", "None"

        st.markdown("---")

        if model_used != "None":
            st.success(f"✅ Generated using **{model_used}**")

            # Output card
            st.markdown(f'<div class="sf-output">', unsafe_allow_html=True)
            st.markdown(f"### 📄 {tool} — {chap}")
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)

            # PDF Download
            st.markdown("---")
            pdf_title = f"{tool.replace('📝','').replace('🧠','').replace('📌','').replace('❓','').strip()} — {chap}"
            pdf_subtitle = f"{sub} | {topic} | {course} | {board}"

            try:
                pdf_buffer = generate_pdf(pdf_title, pdf_subtitle, result)
                safe_filename = (
                    chap.replace(" ", "_")
                        .replace(":", "")
                        .replace("/", "-")
                        .replace("—", "-")
                ) + ".pdf"

                st.download_button(
                    label="⬇️ Download as PDF",
                    data=pdf_buffer,
                    file_name=safe_filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as pdf_err:
                st.warning(f"PDF generation issue: {pdf_err}")
        else:
            st.error("⚠️ AI service unavailable. Please try again.")
            with st.expander("🔍 Debug Info"):
                st.code(result)


# =========================================================
# AUTH UI — PREMIUM DESIGN
# =========================================================
def auth_ui():
    col_l, col_c, col_r = st.columns([1, 2, 1])
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
            u = st.text_input("Username", key="login_u", placeholder="Enter your username")
            p = st.text_input("Password", type="password", key="login_p", placeholder="Enter your password")
            if st.button("Sign In 🚀", use_container_width=True):
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_p(p)))
                user = c.fetchone()
                conn.close()

                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        with tab2:
            nu = st.text_input("Choose Username", key="reg_u", placeholder="Pick a unique username")
            np = st.text_input("Choose Password", type="password", key="reg_p", placeholder="Create a strong password")
            if st.button("Create Account ✨", use_container_width=True):
                if not nu.strip() or not np.strip():
                    st.error("Username and password cannot be empty.")
                else:
                    try:
                        conn = sqlite3.connect("users.db")
                        c = conn.cursor()
                        c.execute("INSERT INTO users VALUES (?, ?)", (nu.strip(), hash_p(np)))
                        conn.commit()
                        conn.close()

                        # 🚀 AUTO LOGIN AFTER REGISTRATION
                        st.success("✅ Account created! Logging you in...")
                        time.sleep(1)
                        st.session_state.logged_in = True
                        st.session_state.username = nu.strip()
                        st.rerun()

                    except sqlite3.IntegrityError:
                        st.error("❌ Username already exists. Try a different one.")

        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# RUN
# =========================================================
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
