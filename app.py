import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib

# --- PAGE CONFIG ---
st.set_page_config(page_title="StudyFiesta AI", page_icon="🎓", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    div.stSelectbox label, div.stTextInput label {
        font-weight: bold;
        color: #1f1f1f;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #0e1117;
    }
    </style>
""", unsafe_allow_html=True)

# --- AI CONFIG ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash-exp"
]

def generate_with_fallback(prompt):
    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and hasattr(response, "text") and response.text:
                return response.text.strip(), model_name
        except Exception:
            continue
    return "Service temporarily unavailable. Please try again in a moment.", "None"

# --- DATABASE ---
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

# --- COURSE / SUBJECT MAP ---
DATA_MAP = {
    "Competitive Exams 🏆": {
        "UPSC (Civil Services)": [
            "General Studies 1",
            "General Studies 2 (CSAT)",
            "History Optional",
            "Geography Optional",
            "Public Admin",
            "Ethics"
        ],
        "JEE (Mains/Adv)": ["Physics", "Chemistry", "Mathematics"],
        "NEET": ["Biology", "Physics", "Chemistry"],
        "GATE": ["Computer Science", "Mechanical", "Electrical", "Civil", "Electronics"],
        "Banking/SSC": ["Quantitative Aptitude", "Reasoning", "English", "General Awareness"]
    },
    "Engineering & Tech 💻": {
        "B.Tech / M.Tech": [
            "Computer Science (CSE)",
            "Information Technology (IT)",
            "Electronics (ECE)",
            "Mechanical (ME)",
            "Civil (CE)",
            "AI & Data Science"
        ],
        "Polytechnic Diploma": ["Mechanical", "Electrical", "Civil", "Computer"],
        "BCA / MCA": [
            "Programming in C/C++",
            "Java & Python",
            "Database Management",
            "Software Engineering",
            "Web Development"
        ]
    },
    "School (K-12) 🏫": {
        "Class 10": ["Mathematics", "Science", "Social Science", "English", "Hindi"],
        "Class 11 & 12": [
            "Physics",
            "Chemistry",
            "Mathematics",
            "Biology",
            "Accountancy",
            "Business Studies",
            "Economics",
            "History",
            "Psychology"
        ]
    },
    "Degree & Masters 🎓": {
        "Commerce (B.Com/M.Com)": [
            "Financial Accounting",
            "Corporate Tax",
            "Auditing",
            "Costing",
            "Management Accounting"
        ],
        "Science (B.Sc/M.Sc)": [
            "Physics",
            "Chemistry",
            "Maths",
            "Zoology",
            "Botany",
            "Biotechnology"
        ],
        "Management (BBA/MBA)": [
            "Marketing",
            "Finance",
            "HR",
            "Operations",
            "Strategy"
        ],
        "Arts (B.A/M.A)": [
            "English Literature",
            "Political Science",
            "Economics",
            "History",
            "Psychology"
        ]
    }
}

BOARDS = [
    "CBSE",
    "ICSE",
    "IGCSE",
    "State Board (Maharashtra)",
    "State Board (Karnataka)",
    "State Board (UP)",
    "State Board (Others)"
]

# --- LOCAL CHAPTER BANK ---
CHAPTER_MAP = {
    "Competitive Exams 🏆": {
        "UPSC (Civil Services)": {
            "General Studies 1": [
                "Indian Heritage and Culture",
                "Modern Indian History",
                "World History",
                "Indian Society",
                "Geography of India",
                "World Geography"
            ],
            "General Studies 2 (CSAT)": [
                "Reading Comprehension",
                "Logical Reasoning",
                "Analytical Ability",
                "Decision Making",
                "Basic Numeracy",
                "Data Interpretation"
            ],
            "History Optional": [
                "Ancient India",
                "Medieval India",
                "Modern India",
                "World History",
                "Historical Thought",
                "Indian National Movement"
            ],
            "Geography Optional": [
                "Geomorphology",
                "Climatology",
                "Oceanography",
                "Human Geography",
                "Indian Geography",
                "Models and Theories"
            ],
            "Public Admin": [
                "Administrative Thought",
                "Organizations",
                "Accountability and Control",
                "Comparative Public Administration",
                "Development Dynamics",
                "Indian Administration"
            ],
            "Ethics": [
                "Ethics and Human Interface",
                "Attitude",
                "Aptitude and Foundational Values",
                "Emotional Intelligence",
                "Moral Thinkers",
                "Probity in Governance"
            ]
        },
        "JEE (Mains/Adv)": {
            "Physics": [
                "Kinematics",
                "Laws of Motion",
                "Work Power Energy",
                "Rotational Motion",
                "Gravitation",
                "Thermodynamics",
                "Oscillations and Waves",
                "Electrostatics",
                "Current Electricity",
                "Magnetism",
                "Optics",
                "Modern Physics"
            ],
            "Chemistry": [
                "Atomic Structure",
                "Chemical Bonding",
                "Thermodynamics",
                "Equilibrium",
                "Electrochemistry",
                "Organic Chemistry Basics",
                "Hydrocarbons",
                "Coordination Compounds",
                "d and f Block Elements",
                "Biomolecules"
            ],
            "Mathematics": [
                "Sets and Relations",
                "Quadratic Equations",
                "Sequences and Series",
                "Permutations and Combinations",
                "Binomial Theorem",
                "Trigonometry",
                "Limits and Derivatives",
                "Integral Calculus",
                "Coordinate Geometry",
                "Vectors and 3D Geometry",
                "Probability"
            ]
        },
        "NEET": {
            "Biology": [
                "Cell Structure",
                "Plant Physiology",
                "Human Physiology",
                "Genetics",
                "Evolution",
                "Biotechnology",
                "Ecology",
                "Reproduction"
            ],
            "Physics": [
                "Motion",
                "Work Energy Power",
                "Thermodynamics",
                "Electrostatics",
                "Current Electricity",
                "Magnetic Effects",
                "Optics",
                "Modern Physics"
            ],
            "Chemistry": [
                "Structure of Atom",
                "Chemical Bonding",
                "States of Matter",
                "Thermodynamics",
                "Equilibrium",
                "p Block Elements",
                "Organic Chemistry",
                "Biomolecules"
            ]
        },
        "GATE": {
            "Computer Science": [
                "Programming and Data Structures",
                "Algorithms",
                "Theory of Computation",
                "Compiler Design",
                "Operating Systems",
                "Databases",
                "Computer Networks",
                "Digital Logic",
                "Computer Organization",
                "Engineering Mathematics"
            ],
            "Mechanical": [
                "Engineering Mechanics",
                "Strength of Materials",
                "Theory of Machines",
                "Thermodynamics",
                "Fluid Mechanics",
                "Heat Transfer",
                "Manufacturing Engineering",
                "Industrial Engineering"
            ],
            "Electrical": [
                "Network Theory",
                "Electrical Machines",
                "Power Systems",
                "Control Systems",
                "Signals and Systems",
                "Power Electronics"
            ],
            "Civil": [
                "Engineering Mechanics",
                "Structural Analysis",
                "Geotechnical Engineering",
                "Fluid Mechanics",
                "Transportation Engineering",
                "Environmental Engineering"
            ],
            "Electronics": [
                "Network Theory",
                "Electronic Devices",
                "Analog Circuits",
                "Digital Circuits",
                "Signals and Systems",
                "Communication Systems",
                "Control Systems"
            ]
        },
        "Banking/SSC": {
            "Quantitative Aptitude": [
                "Number System",
                "Simplification",
                "Percentage",
                "Ratio and Proportion",
                "Profit and Loss",
                "Time and Work",
                "Time Speed Distance",
                "Simple and Compound Interest",
                "Mensuration",
                "Data Interpretation"
            ],
            "Reasoning": [
                "Analogy",
                "Classification",
                "Coding Decoding",
                "Blood Relations",
                "Syllogism",
                "Seating Arrangement",
                "Puzzles",
                "Direction Sense"
            ],
            "English": [
                "Reading Comprehension",
                "Error Spotting",
                "Fill in the Blanks",
                "Cloze Test",
                "Para Jumbles",
                "Vocabulary",
                "Sentence Improvement"
            ],
            "General Awareness": [
                "Current Affairs",
                "Indian History",
                "Indian Geography",
                "Indian Polity",
                "Economics",
                "Science",
                "Static GK",
                "Banking Awareness"
            ]
        }
    },
    "Engineering & Tech 💻": {
        "B.Tech / M.Tech": {
            "Computer Science (CSE)": [
                "Programming Fundamentals",
                "Data Structures",
                "Algorithms",
                "Database Management Systems",
                "Operating Systems",
                "Computer Networks",
                "Software Engineering",
                "Object Oriented Programming",
                "Theory of Computation",
                "Compiler Design",
                "Artificial Intelligence",
                "Machine Learning"
            ],
            "Information Technology (IT)": [
                "Programming Basics",
                "Database Systems",
                "Web Technologies",
                "Networking",
                "Cloud Computing",
                "Cybersecurity",
                "Software Engineering",
                "Data Analytics"
            ],
            "Electronics (ECE)": [
                "Network Theory",
                "Electronic Devices",
                "Analog Electronics",
                "Digital Electronics",
                "Signals and Systems",
                "Communication Systems",
                "Microprocessors",
                "Control Systems",
                "VLSI Basics"
            ],
            "Mechanical (ME)": [
                "Engineering Mechanics",
                "Thermodynamics",
                "Fluid Mechanics",
                "Strength of Materials",
                "Theory of Machines",
                "Machine Design",
                "Manufacturing Processes",
                "Heat Transfer"
            ],
            "Civil (CE)": [
                "Engineering Mechanics",
                "Surveying",
                "Strength of Materials",
                "Structural Analysis",
                "Concrete Technology",
                "Soil Mechanics",
                "Transportation Engineering",
                "Environmental Engineering"
            ],
            "AI & Data Science": [
                "Python for Data Science",
                "Statistics",
                "Linear Algebra",
                "Data Preprocessing",
                "Machine Learning",
                "Deep Learning",
                "Natural Language Processing",
                "Computer Vision",
                "Model Evaluation"
            ]
        },
        "Polytechnic Diploma": {
            "Mechanical": [
                "Engineering Drawing",
                "Workshop Technology",
                "Thermal Engineering",
                "Machine Tools",
                "Strength of Materials"
            ],
            "Electrical": [
                "Basic Electrical Engineering",
                "Electrical Machines",
                "Power Systems",
                "Wiring and Estimation",
                "Control Systems"
            ],
            "Civil": [
                "Building Materials",
                "Surveying",
                "Construction Technology",
                "Concrete Technology",
                "Estimating and Costing"
            ],
            "Computer": [
                "Computer Fundamentals",
                "Programming in C",
                "DBMS",
                "Operating Systems",
                "Computer Networks"
            ]
        },
        "BCA / MCA": {
            "Programming in C/C++": [
                "Variables and Data Types",
                "Operators",
                "Control Statements",
                "Functions",
                "Arrays",
                "Pointers",
                "Structures",
                "File Handling",
                "OOP in C++"
            ],
            "Java & Python": [
                "Basics of Java",
                "OOP Concepts",
                "Exception Handling",
                "Collections",
                "Python Basics",
                "Functions in Python",
                "OOP in Python",
                "Modules and Packages"
            ],
            "Database Management": [
                "Introduction to DBMS",
                "ER Model",
                "Relational Model",
                "Normalization",
                "SQL Queries",
                "Transactions",
                "Indexing"
            ],
            "Software Engineering": [
                "SDLC",
                "Requirement Analysis",
                "Design Models",
                "Testing",
                "Maintenance",
                "Agile Methodology"
            ],
            "Web Development": [
                "HTML",
                "CSS",
                "JavaScript",
                "Responsive Design",
                "Frontend Framework Basics",
                "Backend Basics",
                "APIs"
            ]
        }
    },
    "School (K-12) 🏫": {
        "Class 10": {
            "Mathematics": [
                "Real Numbers",
                "Polynomials",
                "Pair of Linear Equations in Two Variables",
                "Quadratic Equations",
                "Arithmetic Progressions",
                "Triangles",
                "Coordinate Geometry",
                "Introduction to Trigonometry",
                "Applications of Trigonometry",
                "Circles",
                "Constructions",
                "Areas Related to Circles",
                "Surface Areas and Volumes",
                "Statistics",
                "Probability"
            ],
            "Science": [
                "Chemical Reactions and Equations",
                "Acids Bases and Salts",
                "Metals and Non-metals",
                "Carbon and Its Compounds",
                "Periodic Classification of Elements",
                "Life Processes",
                "Control and Coordination",
                "How do Organisms Reproduce",
                "Heredity and Evolution",
                "Light Reflection and Refraction",
                "Human Eye and the Colourful World",
                "Electricity",
                "Magnetic Effects of Electric Current",
                "Sources of Energy",
                "Our Environment"
            ],
            "Social Science": [
                "The Rise of Nationalism in Europe",
                "Nationalism in India",
                "Power Sharing",
                "Federalism",
                "Political Parties",
                "Outcomes of Democracy",
                "Development",
                "Sectors of the Indian Economy",
                "Money and Credit",
                "Globalisation and the Indian Economy",
                "Resources and Development",
                "Forest and Wildlife Resources",
                "Water Resources",
                "Agriculture",
                "Minerals and Energy Resources"
            ],
            "English": [
                "Reading Comprehension",
                "Grammar",
                "Writing Skills",
                "First Flight Prose",
                "First Flight Poetry",
                "Footprints Without Feet"
            ],
            "Hindi": [
                "गद्य भाग",
                "पद्य भाग",
                "व्याकरण",
                "लेखन कौशल",
                "अपठित बोध"
            ]
        },
        "Class 11 & 12": {
            "Physics": [
                "Units and Measurements",
                "Motion in a Straight Line",
                "Laws of Motion",
                "Work Energy and Power",
                "Gravitation",
                "Thermodynamics",
                "Oscillations",
                "Waves",
                "Electrostatics",
                "Current Electricity",
                "Magnetism",
                "Electromagnetic Induction",
                "Optics",
                "Atoms and Nuclei",
                "Semiconductors"
            ],
            "Chemistry": [
                "Some Basic Concepts of Chemistry",
                "Structure of Atom",
                "Chemical Bonding",
                "Thermodynamics",
                "Equilibrium",
                "Redox Reactions",
                "Organic Chemistry Basics",
                "Hydrocarbons",
                "Solutions",
                "Electrochemistry",
                "Chemical Kinetics",
                "Coordination Compounds",
                "Haloalkanes and Haloarenes",
                "Alcohols Phenols and Ethers",
                "Biomolecules"
            ],
            "Mathematics": [
                "Sets",
                "Relations and Functions",
                "Trigonometric Functions",
                "Complex Numbers",
                "Permutations and Combinations",
                "Binomial Theorem",
                "Sequences and Series",
                "Straight Lines",
                "Conic Sections",
                "Limits and Derivatives",
                "Matrices",
                "Determinants",
                "Continuity and Differentiability",
                "Integrals",
                "Probability",
                "Vectors",
                "3D Geometry"
            ],
            "Biology": [
                "The Living World",
                "Biological Classification",
                "Cell Structure and Function",
                "Plant Physiology",
                "Human Physiology",
                "Reproduction",
                "Genetics",
                "Evolution",
                "Biotechnology",
                "Ecology"
            ],
            "Accountancy": [
                "Accounting Principles",
                "Journal",
                "Ledger",
                "Trial Balance",
                "Final Accounts",
                "Depreciation",
                "Bills of Exchange",
                "Cash Flow Statement",
                "Partnership Accounts",
                "Company Accounts"
            ],
            "Business Studies": [
                "Nature and Purpose of Business",
                "Forms of Business Organisation",
                "Business Services",
                "Emerging Modes of Business",
                "Social Responsibility of Business",
                "Management Principles",
                "Planning",
                "Organising",
                "Staffing",
                "Directing",
                "Controlling",
                "Marketing Management"
            ],
            "Economics": [
                "Introduction to Microeconomics",
                "Consumer Equilibrium",
                "Demand",
                "Production Function",
                "Cost",
                "Market Structures",
                "National Income",
                "Money and Banking",
                "Government Budget",
                "Balance of Payments"
            ],
            "History": [
                "Writing and City Life",
                "An Empire Across Three Continents",
                "Changing Cultural Traditions",
                "The Industrial Revolution",
                "Colonialism and Rural Society",
                "Mahatma Gandhi and the Nationalist Movement",
                "Framing the Constitution"
            ],
            "Psychology": [
                "Introduction to Psychology",
                "Methods of Enquiry",
                "Human Development",
                "Learning",
                "Memory",
                "Motivation and Emotion",
                "Personality",
                "Psychological Disorders",
                "Therapeutic Approaches"
            ]
        }
    },
    "Degree & Masters 🎓": {
        "Commerce (B.Com/M.Com)": {
            "Financial Accounting": [
                "Accounting Principles",
                "Journal and Ledger",
                "Trial Balance",
                "Final Accounts",
                "Depreciation",
                "Bills of Exchange",
                "Partnership Accounts",
                "Company Accounts"
            ],
            "Corporate Tax": [
                "Introduction to Corporate Tax",
                "Residential Status",
                "Taxable Income",
                "Deductions",
                "MAT",
                "Assessment Procedures"
            ],
            "Auditing": [
                "Introduction to Auditing",
                "Internal Control",
                "Vouching",
                "Verification and Valuation",
                "Audit Report",
                "Company Audit"
            ],
            "Costing": [
                "Cost Concepts",
                "Material Cost",
                "Labour Cost",
                "Overheads",
                "Process Costing",
                "Marginal Costing"
            ],
            "Management Accounting": [
                "Financial Statement Analysis",
                "Ratio Analysis",
                "Cash Flow Analysis",
                "Budgetary Control",
                "Standard Costing",
                "Decision Making"
            ]
        },
        "Science (B.Sc/M.Sc)": {
            "Physics": [
                "Classical Mechanics",
                "Electromagnetism",
                "Quantum Mechanics",
                "Thermodynamics",
                "Statistical Mechanics",
                "Optics",
                "Nuclear Physics",
                "Solid State Physics"
            ],
            "Chemistry": [
                "Physical Chemistry",
                "Organic Reaction Mechanisms",
                "Inorganic Chemistry",
                "Coordination Chemistry",
                "Spectroscopy",
                "Quantum Chemistry"
            ],
            "Maths": [
                "Real Analysis",
                "Complex Analysis",
                "Linear Algebra",
                "Abstract Algebra",
                "Differential Equations",
                "Topology",
                "Numerical Analysis"
            ],
            "Zoology": [
                "Animal Diversity",
                "Cell Biology",
                "Genetics",
                "Physiology",
                "Developmental Biology",
                "Ecology"
            ],
            "Botany": [
                "Plant Diversity",
                "Cell Biology",
                "Genetics",
                "Plant Physiology",
                "Ecology",
                "Plant Pathology"
            ],
            "Biotechnology": [
                "Cell Biology",
                "Molecular Biology",
                "Genetic Engineering",
                "Immunology",
                "Bioprocess Engineering",
                "Bioinformatics"
            ]
        },
        "Management (BBA/MBA)": {
            "Marketing": [
                "Introduction to Marketing",
                "Consumer Behaviour",
                "Segmentation Targeting Positioning",
                "Product Strategy",
                "Pricing Strategy",
                "Promotion Strategy",
                "Digital Marketing"
            ],
            "Finance": [
                "Financial Management",
                "Time Value of Money",
                "Capital Budgeting",
                "Cost of Capital",
                "Working Capital Management",
                "Risk and Return"
            ],
            "HR": [
                "Human Resource Management",
                "Recruitment and Selection",
                "Training and Development",
                "Performance Appraisal",
                "Compensation Management",
                "Employee Relations"
            ],
            "Operations": [
                "Operations Management",
                "Process Design",
                "Capacity Planning",
                "Inventory Management",
                "Quality Management",
                "Supply Chain Management"
            ],
            "Strategy": [
                "Strategic Management",
                "SWOT Analysis",
                "Competitive Advantage",
                "Industry Analysis",
                "Business Level Strategy",
                "Corporate Level Strategy"
            ]
        },
        "Arts (B.A/M.A)": {
            "English Literature": [
                "Poetry",
                "Drama",
                "Prose",
                "Novel",
                "Literary Criticism",
                "Literary Theory"
            ],
            "Political Science": [
                "Political Theory",
                "Indian Government and Politics",
                "Comparative Politics",
                "International Relations",
                "Public Administration"
            ],
            "Economics": [
                "Microeconomics",
                "Macroeconomics",
                "Public Finance",
                "Indian Economy",
                "Statistics for Economics",
                "Development Economics"
            ],
            "History": [
                "Ancient History",
                "Medieval History",
                "Modern History",
                "World History",
                "Historiography"
            ],
            "Psychology": [
                "Cognitive Psychology",
                "Social Psychology",
                "Developmental Psychology",
                "Abnormal Psychology",
                "Research Methods",
                "Counselling Psychology"
            ]
        }
    }
}

# --- CHAPTER FETCHING ---
def get_chapters(category, course, subject, board=None):
    local_chapters = (
        CHAPTER_MAP.get(category, {})
        .get(course, {})
        .get(subject, [])
    )

    if local_chapters:
        return local_chapters

    board_text = f" for {board}" if board else ""
    prompt = (
        f"Act as an expert academic syllabus planner. "
        f"List only important standard chapter names for {subject} in {course}{board_text}. "
        f"Return only a comma-separated list. No numbering. No explanation."
    )
    result, _ = generate_with_fallback(prompt)

    if "Service temporarily unavailable" in result or result.strip() == "":
        return ["Topic 1", "Topic 2", "Topic 3"]

    chapters = [c.strip() for c in result.split(",") if c.strip()]
    return chapters if chapters else ["Topic 1", "Topic 2", "Topic 3"]

# --- MAIN APP ---
def main_app():
    with st.sidebar:
        st.title("🎓 StudyFiesta")
        st.markdown(f"**Welcome, {st.session_state.username}**")
        st.divider()

        tool = st.radio(
            "SELECT TOOL",
            ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "❓ Exam Q&A"]
        )

        st.divider()

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.markdown(f"# {tool}")
    st.write("Streamlining your preparation with AI precision.")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        cat = st.selectbox("Category", list(DATA_MAP.keys()))

    with c2:
        course = st.selectbox("Exam / Course", list(DATA_MAP[cat].keys()))

    with c3:
        if "School" in cat:
            board = st.selectbox("Education Board", BOARDS)
        else:
            board = "University/National Syllabus"

    c4, c5 = st.columns(2)

    with c4:
        sub = st.selectbox("Subject", DATA_MAP[cat][course])

    selection_key = f"{cat}||{course}||{sub}||{board}"

    if "last_selection_key" not in st.session_state:
        st.session_state.last_selection_key = ""

    if "current_chapters" not in st.session_state:
        st.session_state.current_chapters = []

    if st.session_state.last_selection_key != selection_key:
        with st.spinner("Loading chapters..."):
            st.session_state.current_chapters = get_chapters(cat, course, sub, board)
            st.session_state.last_selection_key = selection_key

    with c5:
        chap = st.selectbox("Chapter / Topic", st.session_state.current_chapters)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button(f"Generate {tool} ✨"):
        with st.spinner(f"Analyzing {chap} for {course}..."):
            audience_text = f"{course} students"
            if "School" in cat:
                audience_text = f"{board} {course} students"

            prompt_map = {
                "📝 Summary": (
                    f"Generate a clear, professional, student-friendly summary for '{chap}' "
                    f"in '{sub}' for {audience_text}. "
                    f"Use headings, bullet points, key concepts, and simple explanations."
                ),
                "🧠 Quiz": (
                    f"Generate 5 high-quality MCQs for '{chap}' in '{sub}' for {audience_text}. "
                    f"Include options A-D, correct answer, and a brief explanation for each."
                ),
                "📌 Revision Notes": (
                    f"Create concise revision notes for '{chap}' in '{sub}' for {audience_text}. "
                    f"Highlight important definitions, formulas, concepts, and quick memory points."
                ),
                "❓ Exam Q&A": (
                    f"List 5 probable exam questions and detailed answers for '{chap}' in '{sub}' "
                    f"for {audience_text}. Make them exam-oriented and easy to revise."
                )
            }

            final_prompt = (
                f"{prompt_map[tool]} "
                f"If mathematical expressions are needed, write them in proper LaTeX format. "
                f"Keep the answer accurate, structured, and easy for students to understand."
            )

            result, model_name = generate_with_fallback(final_prompt)

            st.markdown("---")
            if model_name != "None":
                st.success(f"Preparation Material Ready! (Powered by {model_name})")
            else:
                st.warning("The AI service is currently unavailable. Please try again.")

            st.markdown("### Output")
            st.markdown(result)

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
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (u, hash_p(p))
            )
            user = c.fetchone()
            conn.close()

            if user:
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid Credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")

        if st.button("Sign Up"):
            if not nu.strip() or not np.strip():
                st.error("Username and password cannot be empty.")
            else:
                try:
                    conn = sqlite3.connect("users.db")
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO users VALUES (?, ?)",
                        (nu.strip(), hash_p(np))
                    )
                    conn.commit()
                    conn.close()
                    st.success("Account Created! Go to Login tab.")
                except sqlite3.IntegrityError:
                    st.error("Username already exists.")

# --- START ---
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
