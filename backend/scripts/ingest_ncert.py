"""
Ingest confirmed NCERT chapter PDFs into the content_chunks table for RAG retrieval.

Usage: python scripts/ingest_ncert.py
Requires: sentence-transformers installed, run from backend/ with venv active.
"""
import os
import re
import sqlite3
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ncert_raw")
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "studysmart.db")
NCERT_BASE = "https://ncert.nic.in/textbook/pdf/{code}.pdf"

# category, course, stream, subject, topic, chapter, ncert_code
CHAPTER_MAP = [
    ("K-12th", "Class 11", "Science", "Physics", "Kinematics", "Motion in a Straight Line", "keph102"),
    ("K-12th", "Class 11", "Science", "Physics", "Kinematics", "Motion in a Plane", "keph103"),

    ("K-12th", "Class 12", "Science", "Physics", "Current Electricity & Magnetism", "Current Electricity", "leph103"),
    ("K-12th", "Class 12", "Science", "Physics", "Current Electricity & Magnetism", "Moving Charges and Magnetism", "leph104"),
    ("K-12th", "Class 12", "Science", "Physics", "Current Electricity & Magnetism", "Magnetism and Matter", "leph105"),
    ("K-12th", "Class 12", "Science", "Physics", "Current Electricity & Magnetism", "Electromagnetic Induction", "leph106"),
    ("K-12th", "Class 12", "Science", "Physics", "Current Electricity & Magnetism", "Alternating Current", "leph107"),

    ("K-12th", "Class 11", "Science", "Biology", "Plant Physiology", "Transport in Plants", "kebo111"),
    ("K-12th", "Class 11", "Science", "Biology", "Plant Physiology", "Respiration in Plants", "kebo112"),
    ("K-12th", "Class 11", "Science", "Biology", "Plant Physiology", "Plant Growth and Development", "kebo113"),

    ("K-12th", "Class 12", "Science", "Biology", "Genetics & Evolution", "Principles of Inheritance and Variation", "lebo104"),
    ("K-12th", "Class 12", "Science", "Biology", "Genetics & Evolution", "Molecular Basis of Inheritance", "lebo105"),
    ("K-12th", "Class 12", "Science", "Biology", "Genetics & Evolution", "Evolution", "lebo106"),
]

# NCERT-syllabus chapters we could not source as standalone current PDFs (2023 rationalization
# dropped or merged these) — logged so the gap is visible, not silently missing.
KNOWN_GAPS = [
    ("K-12th", "Class 11", "Science", "Biology", "Plant Physiology", "Mineral Nutrition"),
    ("K-12th", "Class 11", "Science", "Biology", "Plant Physiology", "Photosynthesis in Higher Plants"),
]


def download(code: str) -> str:
    path = os.path.join(RAW_DIR, f"{code}.pdf")
    if os.path.exists(path) and os.path.getsize(path) > 50_000:
        return path
    url = NCERT_BASE.format(code=code)
    # NCERT's server intermittently resets connections under rapid successive requests —
    # retry the whole request a few times with backoff, on top of curl's own --retry.
    last_err = ""
    for attempt in range(5):
        result = subprocess.run(
            ["curl", "-sL", "--retry", "4", "--retry-delay", "2", "--max-time", "60", "-o", path, url],
            capture_output=True,
        )
        if result.returncode == 0 and os.path.exists(path) and os.path.getsize(path) > 50_000:
            return path
        last_err = result.stderr.decode(errors="ignore") or f"returncode={result.returncode}, size={os.path.getsize(path) if os.path.exists(path) else 0}"
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"download failed for {code} after retries: {last_err}")


def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)


def clean_text(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        if len(stripped) < 3:
            continue
        cleaned.append(stripped)
    return " ".join(cleaned)


def chunk_text(text: str, target_words: int = 220, overlap_words: int = 30) -> list:
    words = text.split(" ")
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + target_words])
        if len(chunk.split(" ")) > 30:
            chunks.append(chunk)
        i += target_words - overlap_words
    return chunks


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS content_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR(100) NOT NULL,
            course VARCHAR(100) NOT NULL,
            stream VARCHAR(100),
            subject VARCHAR(200) NOT NULL,
            topic VARCHAR(200),
            chapter VARCHAR(200) NOT NULL,
            source VARCHAR(50) NOT NULL DEFAULT 'NCERT',
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding_json TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    total_chunks = 0
    for category, course, stream, subject, topic, chapter, code in CHAPTER_MAP:
        cur.execute(
            "SELECT COUNT(*) FROM content_chunks WHERE chapter = ? AND subject = ? AND course = ?",
            (chapter, subject, course),
        )
        if cur.fetchone()[0] > 0:
            print(f"skip (already ingested): {course} / {subject} / {chapter}")
            continue

        print(f"ingesting: {course} / {subject} / {chapter}  ({code})")
        time.sleep(2)
        pdf_path = download(code)
        raw = extract_text(pdf_path)
        cleaned = clean_text(raw)
        chunks = chunk_text(cleaned)
        if not chunks:
            print(f"  WARNING: no chunks extracted for {code}")
            continue

        embeddings = model.encode(chunks, show_progress_bar=False)

        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            cur.execute(
                """INSERT INTO content_chunks
                   (category, course, stream, subject, topic, chapter, source, chunk_index, content, embedding_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (category, course, stream, subject, topic, chapter, "NCERT", idx, chunk,
                 ",".join(f"{x:.6f}" for x in emb)),
            )
        conn.commit()
        total_chunks += len(chunks)
        print(f"  -> {len(chunks)} chunks stored")

    conn.close()
    print(f"\nDone. {total_chunks} new chunks ingested.")
    if KNOWN_GAPS:
        print("\nKnown gaps (no standalone current NCERT chapter found):")
        for category, course, stream, subject, topic, chapter in KNOWN_GAPS:
            print(f"  - {course} / {subject} / {topic} / {chapter}")


if __name__ == "__main__":
    main()
