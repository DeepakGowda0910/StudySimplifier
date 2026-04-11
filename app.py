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
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #007bff; color: white; border: none; font-weight: bold;
    }
    .stButton>button:hover { background-color: #0056b3; color: white; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    div.stSelectbox label, div.stTextInput label { font-weight: bold; color: #1f1f1f; }
    .card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    h1, h2, h3 { color: #0e1117; }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# AI CONFIG  —  Step 3 improved: stable model order + generation config
# =====================================================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

PRIMARY_MODEL  = "gemini-2.0-flash"
BACKUP_MODELS  = ["gemini-2.5-flash", "gemini-1.5-flash"]

def generate_with_fallback(prompt):
    model_list = [PRIMARY_MODEL] + BACKUP_MODELS
    last_error  = None

    for model_name in model_list:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={
                    "temperature":      0.4,
                    "top_p":            0.9,
                    "top_k":            40,
                    "max_output_tokens": 2048,
                },
            )
            response = model.generate_content(prompt)
            if response and hasattr(response, "text") and response.text and response.text.strip():
                return response.text.strip(), model_name
        except Exception as e:
            last_error = str(e)
            continue

    return f"AI generation failed. Last error: {last_error}", "None"

# =====================================================================
# DATABASE
# =====================================================================
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

# =====================================================================
# COURSE / SUBJECT MAP   Category → Course → [Subjects]
# =====================================================================
DATA_MAP = {
    "Competitive Exams 🏆": {
        "UPSC (Civil Services)": [
            "General Studies 1",
            "General Studies 2 (CSAT)",
            "History Optional",
            "Geography Optional",
            "Public Administration",
            "Ethics"
        ],
        "JEE (Mains/Adv)":  ["Physics", "Chemistry", "Mathematics"],
        "NEET":              ["Biology", "Physics", "Chemistry"],
        "GATE":              ["Computer Science", "Mechanical", "Electrical", "Civil", "Electronics"],
        "Banking/SSC":       ["Quantitative Aptitude", "Reasoning", "English", "General Awareness"]
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
        ]
    },
    "School (K-12) 🏫": {
        "Class 10": [
            "Mathematics", "Science",
            "Social Science — History",
            "Social Science — Geography",
            "Social Science — Civics (Political Science)",
            "Social Science — Economics",
            "English", "Hindi"
        ],
        "Class 11 & 12": [
            "Physics", "Chemistry", "Mathematics", "Biology",
            "Accountancy", "Business Studies", "Economics", "History", "Psychology"
        ]
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
        ]
    }
}

BOARDS = [
    "CBSE", "ICSE", "IGCSE",
    "State Board (Maharashtra)", "State Board (Karnataka)",
    "State Board (UP)", "State Board (Others)"
]

# =====================================================================
# TOPIC MAP   Category → Course → Subject → [Topics / Units]
# =====================================================================
TOPIC_MAP = {
    "School (K-12) 🏫": {
        "Class 10": {
            "Mathematics": [
                "Number Systems & Algebra", "Geometry",
                "Trigonometry", "Coordinate Geometry",
                "Mensuration", "Statistics & Probability"
            ],
            "Science": ["Chemistry", "Biology", "Physics"],
            "Social Science — History": [
                "Events and Processes",
                "Livelihoods Economies and Societies",
                "Everyday Life Culture and Politics"
            ],
            "Social Science — Geography": [
                "Resources",
                "Agriculture and Industries",
                "Transport and Communication"
            ],
            "Social Science — Civics (Political Science)": [
                "Power Sharing and Democracy",
                "Political Institutions",
                "Outcomes of Democracy"
            ],
            "Social Science — Economics": [
                "Development and Sectors",
                "Money Banking and Trade",
                "Consumer Awareness"
            ],
            "English": [
                "Literature — Prose", "Literature — Poetry",
                "Grammar", "Writing Skills"
            ],
            "Hindi": [
                "गद्य (Prose)", "पद्य (Poetry)",
                "व्याकरण (Grammar)", "लेखन (Writing)"
            ]
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
                "Cell Biology & Diversity", "Plant Physiology",
                "Human Physiology", "Genetics & Evolution", "Ecology & Environment"
            ],
            "Accountancy": [
                "Basic Accounting", "Partnership Accounts",
                "Company Accounts", "Analysis of Financial Statements"
            ],
            "Business Studies": [
                "Nature and Forms of Business",
                "Management Principles",
                "Business Finance and Marketing"
            ],
            "Economics": ["Microeconomics", "Macroeconomics", "Indian Economic Development"],
            "History": ["Themes in Indian History", "World History"],
            "Psychology": [
                "Foundations of Psychology",
                "Human Behaviour and Processes",
                "Applied Psychology"
            ]
        }
    },
    "Competitive Exams 🏆": {
        "JEE (Mains/Adv)": {
            "Physics":     ["Mechanics", "Thermodynamics", "Electrodynamics", "Optics & Modern Physics"],
            "Chemistry":   ["Physical Chemistry", "Inorganic Chemistry", "Organic Chemistry"],
            "Mathematics": ["Algebra", "Calculus", "Coordinate Geometry", "Trigonometry", "Probability"]
        },
        "NEET": {
            "Biology":   ["Cell Biology", "Plant Biology", "Human Physiology", "Genetics & Evolution", "Ecology"],
            "Physics":   ["Mechanics", "Thermodynamics", "Electrodynamics", "Optics"],
            "Chemistry": ["Physical Chemistry", "Inorganic Chemistry", "Organic Chemistry"]
        },
        "GATE": {
            "Computer Science": [
                "Programming & Data Structures", "Theory of Computation",
                "Systems (OS & Networks)", "Databases & Engineering Math"
            ],
            "Mechanical":  ["Mechanics & Design", "Thermal Sciences", "Manufacturing"],
            "Electrical":  ["Circuits & Machines", "Power Systems", "Signals & Control"],
            "Civil":       ["Structures & Geotechnical", "Fluid & Environmental", "Transportation"],
            "Electronics": ["Circuits & Devices", "Signals & Control", "Communications"]
        },
        "Banking/SSC": {
            "Quantitative Aptitude": ["Arithmetic", "Algebra & Geometry", "Data Interpretation"],
            "Reasoning":             ["Verbal Reasoning", "Non-Verbal Reasoning", "Puzzles"],
            "English":               ["Comprehension & Vocabulary", "Grammar", "Writing"],
            "General Awareness":     ["Current Affairs", "Static GK", "Banking & Finance"]
        },
        "UPSC (Civil Services)": {
            "General Studies 1":        ["History", "Geography", "Society"],
            "General Studies 2 (CSAT)": ["Comprehension", "Reasoning", "Numeracy"],
            "History Optional":         ["Ancient India", "Medieval India", "Modern India", "World History"],
            "Geography Optional":       ["Physical Geography", "Human Geography", "Indian Geography"],
            "Public Administration":    ["Administrative Theory", "Indian Administration"],
            "Ethics":                   ["Ethics & Integrity", "Attitude & Aptitude", "Case Studies"]
        }
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
            "AI & Data Science":           ["Statistics & Math", "Machine Learning", "Deep Learning & NLP", "Data Engineering"]
        },
        "Polytechnic Diploma": {
            "Mechanical": ["Mechanics", "Thermal", "Manufacturing"],
            "Electrical":  ["Circuits", "Machines", "Power"],
            "Civil":       ["Structures", "Construction", "Surveying"],
            "Computer":    ["Programming", "Networking", "DBMS"]
        },
        "BCA / MCA": {
            "Programming in C/C++": ["Basics", "Functions & Arrays", "OOP Concepts"],
            "Java & Python":        ["Core Java", "Python Basics", "OOP & Libraries"],
            "Database Management":  ["ER Model & SQL", "Normalization", "Transactions"],
            "Software Engineering": ["SDLC Models", "Testing", "Agile"],
            "Web Development":      ["Frontend", "Backend", "Deployment"]
        }
    },
    "Degree & Masters 🎓": {
        "Commerce (B.Com/M.Com)": {
            "Financial Accounting":  ["Basic Accounts", "Partnership", "Company Accounts"],
            "Corporate Tax":         ["Income Tax Basics", "Corporate Tax Planning"],
            "Auditing":              ["Audit Basics", "Types of Audit", "Audit Report"],
            "Costing":               ["Material & Labour", "Process Costing", "Marginal Costing"],
            "Management Accounting": ["Ratio Analysis", "Budgeting", "Standard Costing"]
        },
        "Science (B.Sc/M.Sc)": {
            "Physics":       ["Classical Mechanics", "Electromagnetism", "Quantum Mechanics", "Modern Physics"],
            "Chemistry":     ["Physical", "Organic", "Inorganic", "Analytical"],
            "Maths":         ["Analysis", "Algebra", "Differential Equations", "Topology"],
            "Zoology":       ["Animal Diversity", "Physiology", "Genetics", "Ecology"],
            "Botany":        ["Plant Diversity", "Physiology", "Genetics", "Ecology"],
            "Biotechnology": ["Molecular Biology", "Genetic Engineering", "Bioprocess", "Bioinformatics"]
        },
        "Management (BBA/MBA)": {
            "Marketing":  ["Basics & Consumer Behaviour", "Strategy & Mix", "Digital Marketing"],
            "Finance":    ["Financial Management", "Investments", "Risk"],
            "HR":         ["Recruitment & Training", "Performance & Compensation", "Employee Relations"],
            "Operations": ["Process & Capacity", "Quality & Supply Chain"],
            "Strategy":   ["Analysis & Positioning", "Corporate Strategy"]
        },
        "Arts (B.A/M.A)": {
            "English Literature":  ["Poetry", "Drama", "Novel & Prose", "Literary Theory"],
            "Political Science":   ["Political Theory", "Indian Politics", "International Relations"],
            "Economics":           ["Micro & Macro", "Indian Economy", "Development Economics"],
            "History":             ["Ancient", "Medieval", "Modern", "World History"],
            "Psychology":          ["Cognitive & Social", "Developmental & Abnormal", "Research Methods"]
        }
    }
}

# =====================================================================
# CHAPTER MAP   Category → Course → Subject → Topic → [Chapters]
# All NCERT Class 10 chapters verified against 2025-26 syllabus
# =====================================================================
CHAPTER_MAP = {
    "School (K-12) 🏫": {
        "Class 10": {
            "Mathematics": {
                "Number Systems & Algebra": [
                    "Ch 1: Real Numbers",
                    "Ch 2: Polynomials",
                    "Ch 3: Pair of Linear Equations in Two Variables",
                    "Ch 4: Quadratic Equations",
                    "Ch 5: Arithmetic Progressions"
                ],
                "Geometry": [
                    "Ch 6: Triangles",
                    "Ch 10: Circles",
                    "Ch 11: Constructions"
                ],
                "Trigonometry": [
                    "Ch 8: Introduction to Trigonometry",
                    "Ch 9: Some Applications of Trigonometry"
                ],
                "Coordinate Geometry": ["Ch 7: Coordinate Geometry"],
                "Mensuration": [
                    "Ch 12: Areas Related to Circles",
                    "Ch 13: Surface Areas and Volumes"
                ],
                "Statistics & Probability": [
                    "Ch 14: Statistics",
                    "Ch 15: Probability"
                ]
            },
            "Science": {
                "Chemistry": [
                    "Ch 1: Chemical Reactions and Equations",
                    "Ch 2: Acids, Bases and Salts",
                    "Ch 3: Metals and Non-metals",
                    "Ch 4: Carbon and Its Compounds",
                    "Ch 5: Periodic Classification of Elements"
                ],
                "Biology": [
                    "Ch 6: Life Processes",
                    "Ch 7: Control and Coordination",
                    "Ch 8: How do Organisms Reproduce?",
                    "Ch 9: Heredity and Evolution",
                    "Ch 15: Our Environment"
                ],
                "Physics": [
                    "Ch 10: Light — Reflection and Refraction",
                    "Ch 11: Human Eye and the Colourful World",
                    "Ch 12: Electricity",
                    "Ch 13: Magnetic Effects of Electric Current",
                    "Ch 14: Sources of Energy"
                ]
            },
            "Social Science — History": {
                "Events and Processes": [
                    "Ch 1: The Rise of Nationalism in Europe",
                    "Ch 2: Nationalism in India"
                ],
                "Livelihoods Economies and Societies": [
                    "Ch 3: The Making of a Global World",
                    "Ch 4: The Age of Industrialisation"
                ],
                "Everyday Life Culture and Politics": [
                    "Ch 5: Print Culture and the Modern World"
                ]
            },
            "Social Science — Geography": {
                "Resources": [
                    "Ch 1: Resources and Development",
                    "Ch 2: Forest and Wildlife Resources",
                    "Ch 3: Water Resources"
                ],
                "Agriculture and Industries": [
                    "Ch 4: Agriculture",
                    "Ch 5: Minerals and Energy Resources",
                    "Ch 6: Manufacturing Industries"
                ],
                "Transport and Communication": [
                    "Ch 7: Lifelines of the National Economy"
                ]
            },
            "Social Science — Civics (Political Science)": {
                "Power Sharing and Democracy": [
                    "Ch 1: Power Sharing",
                    "Ch 2: Federalism",
                    "Ch 3: Gender, Religion and Caste"
                ],
                "Political Institutions": [
                    "Ch 4: Political Parties"
                ],
                "Outcomes of Democracy": [
                    "Ch 5: Outcomes of Democracy"
                ]
            },
            "Social Science — Economics": {
                "Development and Sectors": [
                    "Ch 1: Development",
                    "Ch 2: Sectors of the Indian Economy"
                ],
                "Money Banking and Trade": [
                    "Ch 3: Money and Credit",
                    "Ch 4: Globalisation and the Indian Economy"
                ],
                "Consumer Awareness": [
                    "Ch 5: Consumer Rights"
                ]
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
                    "The Proposal"
                ],
                "Literature — Poetry": [
                    "Dust of Snow",
                    "Fire and Ice",
                    "A Tiger in the Zoo",
                    "How to Tell Wild Animals",
                    "The Ball Poem",
                    "Amanda",
                    "Animals",
                    "The Trees",
                    "Fog",
                    "The Tale of Custard the Dragon",
                    "For Anne Gregory"
                ],
                "Grammar": [
                    "Tenses",
                    "Modals",
                    "Subject-Verb Agreement",
                    "Reported Speech",
                    "Active and Passive Voice",
                    "Determiners",
                    "Clauses"
                ],
                "Writing Skills": [
                    "Formal Letter Writing",
                    "Informal Letter Writing",
                    "Notice Writing",
                    "Paragraph Writing",
                    "Essay Writing"
                ]
            },
            "Hindi": {
                "गद्य (Prose)": [
                    "नेताजी का चश्मा",
                    "बालगोबिन भगत",
                    "लखनवी अंदाज़",
                    "एही ठैयाँ झुलनी हेरानी हो रामा",
                    "मानवीय करुणा की दिव्य चमक",
                    "एक कहानी यह भी",
                    "स्त्री शिक्षा के विरोधी कुतर्कों का खण्डन",
                    "नौबतखाने में इबादत",
                    "संस्कृति"
                ],
                "पद्य (Poetry)": [
                    "सूर के पद",
                    "राम-लक्ष्मण-परशुराम संवाद",
                    "देव के सवैये और कवित्त",
                    "आत्मकथ्य",
                    "उत्साह और अट नहीं रही",
                    "यह दंतुरहित मुस्कान और फसल",
                    "छाया मत छूना",
                    "कन्यादान",
                    "संगतकार"
                ],
                "व्याकरण (Grammar)": [
                    "पद परिचय", "रस", "अलंकार",
                    "समास", "वाच्य", "वाक्य भेद", "मुहावरे"
                ],
                "लेखन (Writing)": [
                    "पत्र लेखन", "निबंध लेखन",
                    "सूचना लेखन", "विज्ञापन लेखन"
                ]
            }
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
                    "Ch 8: Gravitation"
                ],
                "Thermodynamics & Waves": [
                    "Ch 9: Mechanical Properties of Solids",
                    "Ch 10: Mechanical Properties of Fluids",
                    "Ch 11: Thermal Properties of Matter",
                    "Ch 12: Thermodynamics",
                    "Ch 13: Kinetic Theory",
                    "Ch 14: Oscillations",
                    "Ch 15: Waves"
                ],
                "Electromagnetism": [
                    "Ch 1 (XII): Electric Charges and Fields",
                    "Ch 2 (XII): Electrostatic Potential and Capacitance",
                    "Ch 3 (XII): Current Electricity",
                    "Ch 4 (XII): Moving Charges and Magnetism",
                    "Ch 5 (XII): Magnetism and Matter",
                    "Ch 6 (XII): Electromagnetic Induction",
                    "Ch 7 (XII): Alternating Current",
                    "Ch 8 (XII): Electromagnetic Waves"
                ],
                "Optics & Modern Physics": [
                    "Ch 9 (XII): Ray Optics and Optical Instruments",
                    "Ch 10 (XII): Wave Optics",
                    "Ch 11 (XII): Dual Nature of Radiation and Matter",
                    "Ch 12 (XII): Atoms",
                    "Ch 13 (XII): Nuclei",
                    "Ch 14 (XII): Semiconductor Electronics"
                ]
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
                    "Ch 4 (XII): Chemical Kinetics"
                ],
                "Inorganic Chemistry": [
                    "Ch 3: Classification of Elements and Periodicity",
                    "Ch 4: Chemical Bonding and Molecular Structure",
                    "Ch 9: Hydrogen",
                    "Ch 10: The s-Block Elements",
                    "Ch 11: The p-Block Elements",
                    "Ch 6 (XII): The p-Block Elements (continued)",
                    "Ch 7 (XII): The d and f-Block Elements",
                    "Ch 8 (XII): Coordination Compounds"
                ],
                "Organic Chemistry": [
                    "Ch 12: Organic Chemistry — Some Basic Principles",
                    "Ch 13: Hydrocarbons",
                    "Ch 14: Environmental Chemistry",
                    "Ch 9 (XII): Haloalkanes and Haloarenes",
                    "Ch 10 (XII): Alcohols, Phenols and Ethers",
                    "Ch 11 (XII): Aldehydes, Ketones and Carboxylic Acids",
                    "Ch 12 (XII): Amines",
                    "Ch 13 (XII): Biomolecules",
                    "Ch 14 (XII): Polymers",
                    "Ch 15 (XII): Chemistry in Everyday Life"
                ]
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
                    "Ch 4 (XII): Determinants"
                ],
                "Calculus": [
                    "Ch 13: Limits and Derivatives",
                    "Ch 5 (XII): Continuity and Differentiability",
                    "Ch 6 (XII): Application of Derivatives",
                    "Ch 7 (XII): Integrals",
                    "Ch 8 (XII): Application of Integrals",
                    "Ch 9 (XII): Differential Equations"
                ],
                "Coordinate Geometry": [
                    "Ch 10: Straight Lines",
                    "Ch 11: Conic Sections",
                    "Ch 12: Introduction to 3D Geometry"
                ],
                "Vectors & 3D": [
                    "Ch 10 (XII): Vector Algebra",
                    "Ch 11 (XII): Three-Dimensional Geometry"
                ],
                "Statistics & Probability": [
                    "Ch 15: Statistics",
                    "Ch 16: Probability",
                    "Ch 13 (XII): Probability"
                ]
            },
            "Biology": {
                "Cell Biology & Diversity": [
                    "Ch 1: The Living World",
                    "Ch 2: Biological Classification",
                    "Ch 3: Plant Kingdom",
                    "Ch 4: Animal Kingdom",
                    "Ch 8: Cell — The Unit of Life",
                    "Ch 9: Biomolecules",
                    "Ch 10: Cell Cycle and Cell Division"
                ],
                "Plant Physiology": [
                    "Ch 5: Morphology of Flowering Plants",
                    "Ch 6: Anatomy of Flowering Plants",
                    "Ch 11: Transport in Plants",
                    "Ch 12: Mineral Nutrition",
                    "Ch 13: Photosynthesis in Higher Plants",
                    "Ch 14: Respiration in Plants",
                    "Ch 15: Plant Growth and Development"
                ],
                "Human Physiology": [
                    "Ch 7: Structural Organisation in Animals",
                    "Ch 16: Digestion and Absorption",
                    "Ch 17: Breathing and Exchange of Gases",
                    "Ch 18: Body Fluids and Circulation",
                    "Ch 19: Excretory Products and Elimination",
                    "Ch 20: Locomotion and Movement",
                    "Ch 21: Neural Control and Coordination",
                    "Ch 22: Chemical Coordination and Integration"
                ],
                "Genetics & Evolution": [
                    "Ch 1 (XII): Reproduction in Organisms",
                    "Ch 2 (XII): Sexual Reproduction in Flowering Plants",
                    "Ch 3 (XII): Human Reproduction",
                    "Ch 4 (XII): Reproductive Health",
                    "Ch 5 (XII): Principles of Inheritance and Variation",
                    "Ch 6 (XII): Molecular Basis of Inheritance",
                    "Ch 7 (XII): Evolution"
                ],
                "Ecology & Environment": [
                    "Ch 13 (XII): Organisms and Populations",
                    "Ch 14 (XII): Ecosystem",
                    "Ch 15 (XII): Biodiversity and Conservation",
                    "Ch 16 (XII): Environmental Issues"
                ]
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
                    "Ch 8: Bills of Exchange"
                ],
                "Partnership Accounts": [
                    "Ch 1 (XII): Accounting for Partnership — Basic Concepts",
                    "Ch 2 (XII): Change in Profit-Sharing Ratio",
                    "Ch 3 (XII): Admission of a Partner",
                    "Ch 4 (XII): Retirement and Death of a Partner",
                    "Ch 5 (XII): Dissolution of Partnership Firm"
                ],
                "Company Accounts": [
                    "Ch 6 (XII): Accounting for Share Capital",
                    "Ch 7 (XII): Issue and Redemption of Debentures"
                ],
                "Analysis of Financial Statements": [
                    "Ch 8 (XII): Financial Statements of a Company",
                    "Ch 9 (XII): Analysis of Financial Statements",
                    "Ch 10 (XII): Accounting Ratios",
                    "Ch 11 (XII): Cash Flow Statement"
                ]
            },
            "Business Studies": {
                "Nature and Forms of Business": [
                    "Ch 1: Nature and Purpose of Business",
                    "Ch 2: Forms of Business Organisation",
                    "Ch 3: Private, Public and Global Enterprises",
                    "Ch 4: Business Services",
                    "Ch 5: Emerging Modes of Business",
                    "Ch 6: Social Responsibility of Business"
                ],
                "Management Principles": [
                    "Ch 1 (XII): Nature and Significance of Management",
                    "Ch 2 (XII): Principles of Management",
                    "Ch 3 (XII): Business Environment",
                    "Ch 4 (XII): Planning",
                    "Ch 5 (XII): Organising",
                    "Ch 6 (XII): Staffing",
                    "Ch 7 (XII): Directing",
                    "Ch 8 (XII): Controlling"
                ],
                "Business Finance and Marketing": [
                    "Ch 9 (XII): Financial Management",
                    "Ch 10 (XII): Financial Markets",
                    "Ch 11 (XII): Marketing Management",
                    "Ch 12 (XII): Consumer Protection"
                ]
            },
            "Economics": {
                "Microeconomics": [
                    "Ch 1: Introduction to Microeconomics",
                    "Ch 2: Theory of Consumer Behaviour",
                    "Ch 3: Production and Costs",
                    "Ch 4: Theory of the Firm under Perfect Competition",
                    "Ch 5: Market Equilibrium",
                    "Ch 6: Non-Competitive Markets"
                ],
                "Macroeconomics": [
                    "Ch 1 (XII): Introduction to Macroeconomics",
                    "Ch 2 (XII): National Income Accounting",
                    "Ch 3 (XII): Money and Banking",
                    "Ch 4 (XII): Determination of Income and Employment",
                    "Ch 5 (XII): Government Budget and the Economy",
                    "Ch 6 (XII): Balance of Payments"
                ],
                "Indian Economic Development": [
                    "Ch 1: Indian Economy on the Eve of Independence",
                    "Ch 2: Indian Economy 1950–1990",
                    "Ch 3: Liberalisation, Privatisation and Globalisation",
                    "Ch 4: Poverty",
                    "Ch 5: Human Capital Formation",
                    "Ch 6: Rural Development",
                    "Ch 7: Employment",
                    "Ch 8: Infrastructure",
                    "Ch 9: Environment and Sustainable Development",
                    "Ch 10: Comparative Development Experiences"
                ]
            },
            "History": {
                "Themes in Indian History": [
                    "Ch 1: Bricks, Beads and Bones (Harappan Civilisation)",
                    "Ch 2: Kings, Farmers and Towns",
                    "Ch 3: Kinship, Caste and Class",
                    "Ch 4: Thinkers, Beliefs and Buildings",
                    "Ch 5: Through the Eyes of Travellers",
                    "Ch 6: Bhakti-Sufi Traditions",
                    "Ch 7: An Imperial Capital — Vijayanagara",
                    "Ch 8: Peasants, Zamindars and the State",
                    "Ch 9: Kings and Chronicles",
                    "Ch 10: Colonialism and the Countryside",
                    "Ch 11: Rebels and the Raj",
                    "Ch 12: Colonial Cities",
                    "Ch 13: Mahatma Gandhi and the Nationalist Movement",
                    "Ch 14: Understanding Partition",
                    "Ch 15: Framing the Constitution"
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
                    "Ch 11: Paths to Modernisation"
                ]
            },
            "Psychology": {
                "Foundations of Psychology": [
                    "Ch 1: What is Psychology?",
                    "Ch 2: Methods of Enquiry in Psychology",
                    "Ch 3: The Bases of Human Behaviour"
                ],
                "Human Behaviour and Processes": [
                    "Ch 4: Human Development",
                    "Ch 5: Sensory, Attentional and Perceptual Processes",
                    "Ch 6: Learning",
                    "Ch 7: Human Memory",
                    "Ch 8: Thinking",
                    "Ch 9: Motivation and Emotion"
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
                    "Ch 9 (XII): Developing Psychological Skills"
                ]
            }
        }
    }
}

# =====================================================================
# HELPERS
# =====================================================================
def get_topics(category, course, subject):
    """Return topic list. Works for both dict-of-dict and dict-of-list structures."""
    course_data = TOPIC_MAP.get(category, {}).get(course, {})
    if isinstance(course_data, dict):
        topics = course_data.get(subject, [])
    else:
        topics = []
    return topics if topics else ["General Topics"]


def get_chapters(category, course, subject, topic):
    """Return chapter list from local map; fall back to AI only if missing."""
    chapters = (
        CHAPTER_MAP
        .get(category, {})
        .get(course, {})
        .get(subject, {})
        .get(topic, [])
    )
    if chapters:
        return chapters

    # AI fallback — only triggered when local data is absent
    prompt = (
        f"You are an academic syllabus expert. "
        f"List the standard chapter names for the topic area '{topic}' "
        f"in '{subject}' for {course}. "
        f"Return ONLY a comma-separated list of chapter names. "
        f"No numbers, no explanation, no extra text."
    )
    result, _ = generate_with_fallback(prompt)
    if "failed" in result.lower() or not result.strip():
        return [f"Introduction to {topic}", f"Core Concepts of {topic}", f"Advanced {topic}"]
    chapters = [c.strip() for c in result.split(",") if c.strip() and len(c.strip()) > 2]
    return chapters if chapters else [f"Introduction to {topic}"]

# =====================================================================
# MAIN APP
# =====================================================================
def main_app():
    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.title("🎓 StudyFiesta")
        st.markdown(f"**Welcome, {st.session_state.username}** 👋")
        st.divider()
        tool = st.radio(
            "SELECT TOOL",
            ["📝 Summary", "🧠 Quiz", "📌 Revision Notes", "❓ Exam Q&A"]
        )
        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.rerun()

    # ── Header ────────────────────────────────────────────────────
    st.markdown(f"# {tool}")
    st.write("Streamlining your preparation with AI precision.")

    # ── Selection card ────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        cat = st.selectbox("📚 Category", list(DATA_MAP.keys()))
    with col2:
        course = st.selectbox("🎓 Exam / Course", list(DATA_MAP[cat].keys()))
    with col3:
        if "School" in cat:
            board = st.selectbox("🏫 Education Board", BOARDS)
        else:
            board = "University / National Syllabus"

    col4, col5 = st.columns(2)
    with col4:
        sub = st.selectbox("📖 Subject", DATA_MAP[cat][course])

    # Row 2: Topic  +  Chapter
    col6, col7 = st.columns(2)

    topics_list = get_topics(cat, course, sub)
    with col6:
        topic = st.selectbox("🗂️ Topic / Unit", topics_list)

    # Load chapters whenever cat/course/sub/topic changes
    chapter_key = f"{cat}||{course}||{sub}||{topic}"
    if "last_chapter_key"   not in st.session_state: st.session_state.last_chapter_key   = ""
    if "current_chapters"   not in st.session_state: st.session_state.current_chapters   = []

    if st.session_state.last_chapter_key != chapter_key:
        st.session_state.current_chapters   = get_chapters(cat, course, sub, topic)
        st.session_state.last_chapter_key   = chapter_key

    with col7:
        chap = st.selectbox("📝 Chapter", st.session_state.current_chapters)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Output style selector ─────────────────────────────────────
    output_style = st.radio(
        "Output Style",
        ["📄 Detailed", "⚡ Short & Quick", "📋 Notes Format"],
        horizontal=True
    )

    # ── Generate button ───────────────────────────────────────────
    if st.button(f"Generate {tool} ✨", use_container_width=True):

        audience = f"{board} {course} students" if "School" in cat else f"{course} students"

        style_instruction = {
            "📄 Detailed":       "Give a thorough, well-structured detailed explanation.",
            "⚡ Short & Quick":  "Keep it concise — key points only, no fluff.",
            "📋 Notes Format":   "Format as clean bullet-point notes, easy to revise quickly."
        }[output_style]

        # Step 3 — improved structured prompts
        prompt_map = {
            "📝 Summary": (
                f"Write a clear student-friendly summary for '{chap}' "
                f"(Topic: {topic}) in '{sub}' for {audience}.\n"
                f"Structure:\n"
                f"1. Overview\n"
                f"2. Key Concepts\n"
                f"3. Important Points\n"
                f"4. Exam Focus\n"
                f"5. Quick Revision Notes\n"
                f"{style_instruction}"
            ),
            "🧠 Quiz": (
                f"Generate 5 high-quality MCQs for '{chap}' (Topic: {topic}) "
                f"in '{sub}' for {audience}.\n"
                f"For each question include:\n"
                f"- The question\n"
                f"- Options A, B, C, D\n"
                f"- Correct answer\n"
                f"- Brief explanation\n"
                f"{style_instruction}"
            ),
            "📌 Revision Notes": (
                f"Create revision notes for '{chap}' (Topic: {topic}) "
                f"in '{sub}' for {audience}.\n"
                f"Include: key definitions, important formulas, dates/facts, "
                f"and quick memory tips.\n"
                f"{style_instruction}"
            ),
            "❓ Exam Q&A": (
                f"List 5 probable exam questions with detailed model answers for "
                f"'{chap}' (Topic: {topic}) in '{sub}' for {audience}.\n"
                f"Make them exam-ready and easy to revise.\n"
                f"{style_instruction}"
            )
        }

        final_prompt = (
            f"{prompt_map[tool]}\n\n"
            f"If mathematical expressions are needed, use LaTeX format. "
            f"Keep the response accurate, structured and student-friendly."
        )

        # Step 3 — safe generation with visible error
        with st.spinner(f"Generating {tool} for '{chap}'..."):
            try:
                result, model_used = generate_with_fallback(final_prompt)
            except Exception as e:
                result, model_used = f"Unexpected error: {e}", "None"

        st.markdown("---")

        if model_used != "None":
            st.success(f"✅ Done! (Powered by {model_used})")
            st.markdown(f"### 📄 {tool} — {chap}")
            st.markdown(result)
        else:
            st.error("⚠️ AI service is currently unavailable.")
            st.info(f"🔍 Debug info: {result}")

# =====================================================================
# AUTH UI
# =====================================================================
def auth_ui():
    st.title("📚 StudyFiesta AI")
    st.subheader("Your Smart Exam Preparation Platform 🎓")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login", use_container_width=True):
            conn = sqlite3.connect("users.db")
            c    = conn.cursor()
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (u, hash_p(p))
            )
            user = c.fetchone()
            conn.close()
            if user:
                st.session_state.logged_in = True
                st.session_state.username  = u
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    with tab2:
        nu = st.text_input("Choose a Username", key="reg_u")
        np = st.text_input("Choose a Password", type="password", key="reg_p")
        if st.button("Create Account", use_container_width=True):
            if not nu.strip() or not np.strip():
                st.error("Username and password cannot be empty.")
            else:
                try:
                    conn = sqlite3.connect("users.db")
                    c    = conn.cursor()
                    c.execute("INSERT INTO users VALUES (?, ?)", (nu.strip(), hash_p(np)))
                    conn.commit()
                    conn.close()
                    st.success("✅ Account created! Please go to the Login tab.")
                except sqlite3.IntegrityError:
                    st.error("❌ Username already exists. Please choose another.")

# =====================================================================
# ENTRY POINT
# =====================================================================
init_db()

if "logged_in"  not in st.session_state: st.session_state.logged_in  = False
if "username"   not in st.session_state: st.session_state.username   = ""

if st.session_state.logged_in:
    main_app()
else:
    auth_ui()
