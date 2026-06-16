import google.generativeai as genai
from config import settings
from typing import Optional, Tuple
import asyncio

genai.configure(api_key=settings.gemini_api_key)

GENERATION_CONFIG = {
    "temperature": 0.3,
    "max_output_tokens": 8192,
    "top_p": 0.9,
}

AVAILABLE_MODELS = [
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-pro",
]

async def generate_content(prompt: str, stream: bool = False) -> Tuple[str, str]:
    for model_name in AVAILABLE_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=GENERATION_CONFIG
            )
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text, model_name
        except Exception as e:
            if "not found" in str(e).lower() or "not supported" in str(e).lower():
                continue
            raise e
    raise Exception("No available Gemini models")

def build_study_prompt(tool: str, chapter: str, topic: str, subject: str,
                        course: str, board: str, stream: str, language: str) -> str:
    audience = f"{course} student" if course else "student"
    if board:
        audience += f" ({board})"

    lang_instruction = f"\nIMPORTANT: Generate all content in {language} language.\n" if language != "English" else ""

    prompts = {
        "short": f"""You are a world-class {subject} professor. Create ultra-concise last-minute revision notes.
{lang_instruction}
**Topic:** {chapter} | **Subject:** {subject} | **Course:** {course}

Format EXACTLY:
## ⚡ Quick Revision: {chapter}
**Definition:** [One-line definition]

### 🎯 10 Key Points
1. [Point]
2. [Point]
(continue to 10)

### 📐 Formula Sheet
| Formula | Meaning |
|---------|---------|
| [formula] | [what it means] |

### 💡 Memory Trick
[Mnemonic or trick]

### ⚠️ Common Exam Mistakes
- [Mistake 1]
- [Mistake 2]
- [Mistake 3]""",

        "summary": f"""You are an expert {subject} teacher for {audience}.
{lang_instruction}
**Chapter:** {chapter} | **Subject:** {subject}

Write a comprehensive academic summary with:
## 📝 Summary: {chapter}
### Overview
[2-3 paragraph overview]

### Key Concepts
[Detailed explanation of 5-7 core concepts]

### Important Formulas/Theorems
[All relevant formulas with explanations]

### Real-World Applications
[3-4 practical applications]

### Key Takeaways
[5 bullet points of what students must remember]""",

        "notes": f"""You are a meticulous {subject} notes specialist for {audience}.
{lang_instruction}
**Chapter:** {chapter}

Create perfectly structured notes:
## 📋 Notes: {chapter}
### 1. Introduction
### 2. Core Theory
   2.1 [Sub-concept]
   2.2 [Sub-concept]
### 3. Formulas & Theorems
| Name | Formula | When to Use |
|------|---------|-------------|
### 4. Worked Examples
**Example 1:** [Problem] → **Solution:** [Step-by-step]
### 5. Summary Table
| Concept | Definition | Formula |
|---------|-----------|---------|""",

        "detailed": f"""You are a leading author of {subject} textbooks for {audience}.
{lang_instruction}
**Chapter:** {chapter}

Write an exhaustive textbook-level chapter:
## 📄 {chapter} - Complete Study Guide

### 1. Historical Background & Context
### 2. Fundamental Definitions
### 3. Core Principles (with mathematical derivations where applicable)
### 4. Theorems & Proofs
### 5. Classification / Types
### 6. Detailed Examples with Step-by-Step Solutions
### 7. Diagrams & Visual Representations (describe with ASCII/text)
### 8. Advanced Topics & Extensions
### 9. Common Errors & Misconceptions
### 10. Practice Problems (with answers)
### 11. Summary & Revision Checklist""",

        "revision": f"""You are an expert exam coach for {audience} studying {subject}.
{lang_instruction}
**Chapter:** {chapter}

Create targeted revision notes:
## 📌 Exam Revision: {chapter}

### 🏆 Top 10 Must-Know Points
1-10 numbered critical points

### 📐 Formula Cheat Sheet
| Formula | Variables | When Used |
|---------|----------|----------|

### 🧠 Mnemonics & Memory Tricks
[Creative mnemonics]

### 🎯 High-Probability Exam Topics
- [Topic 1] ★★★★★
- [Topic 2] ★★★★☆

### ⚡ 5-Minute Pre-Exam Review
[Ultra-compressed final revision]

### 🔮 Predicted Exam Questions
1. [Question likely to appear]
2. [Question likely to appear]
3. [Question likely to appear]""",

        "quiz": f"""You are an expert {subject} examiner for {audience}.
{lang_instruction}
**Chapter:** {chapter}

Generate a comprehensive quiz:
## 🧠 Quiz: {chapter}

### Section A: Multiple Choice (1 mark each)
**Q1.** [Question]
(A) [Option] (B) [Option] (C) [Option] (D) [Option]
**Answer:** [Letter] - [Brief explanation]

(Repeat for Q2-Q10)

### Section B: Short Answer (2 marks each)
**Q11.** [Question]
**Answer:** [2-3 sentence answer]

(Repeat for Q12-Q15)

### Section C: Long Answer (5 marks each)
**Q16.** [Question]
**Answer:** [Detailed answer with steps]

(Repeat for Q17-Q18)""",

        "qa": f"""You are an expert {subject} question paper setter and model answer writer for {audience}.
{lang_instruction}
**Chapter:** {chapter}

Generate highly probable exam questions with model answers:
## ❓ Question Bank: {chapter}

For each question provide:
**Q[n].** [Question] *(Marks: X)*
**Model Answer:**
[Comprehensive answer that would score full marks]
---

Generate 10 questions ranging from 1-mark to 10-mark questions.""",

        "paper": f"""You are the chief examiner for {board} {course} {subject}.
{lang_instruction}
Create a complete 100-mark examination paper for **{chapter}** / full syllabus:

## 📄 {board} {course} {subject} EXAMINATION
### Time: 3 Hours | Maximum Marks: 100

---
## SECTION A – Objective (20 × 1 = 20 marks)
*Choose the correct answer:*
Q1-Q20: [MCQs with 4 options each, mark answers at end]

---
## SECTION B – Very Short Answer (5 × 2 = 10 marks)
Q21-Q25: [2-mark questions]

---
## SECTION C – Short Answer (5 × 3 = 15 marks)
Q26-Q30: [3-mark questions]

---
## SECTION D – Long Answer (3 × 5 = 15 marks)
Q31-Q33: [5-mark questions]

---
## SECTION E – Extended Response (2 × 20 = 40 marks)
Q34-Q35: [Case study / essay questions]

---
### ANSWER KEY
[Complete answers for all sections]""",
    }

    return prompts.get(tool, prompts["summary"])

def build_chat_prompt(message: str, profile: dict, history: list) -> str:
    course = profile.get("course", "General")
    category = profile.get("category", "")
    subject_context = f"{profile.get('subject', '')} student" if profile.get('subject') else f"{course} student"

    history_text = ""
    for msg in history[-10:]:
        role = "Student" if msg["role"] == "user" else "StudyBot"
        history_text += f"{role}: {msg['content']}\n"

    return f"""You are StudyBot, an expert AI tutor exclusively for {subject_context} in {category}.
Your student is studying {course}. You ONLY answer questions related to {course} curriculum.
If asked about unrelated topics, politely redirect to their curriculum.

Be helpful, encouraging, and educational. Use examples relevant to {course}.
Keep responses concise but complete. Use markdown formatting.

Conversation History:
{history_text}

Student: {message}
StudyBot:"""

def build_flashcard_prompt(subject: str, chapter: str, topic: str, count: int = 10) -> str:
    return f"""Generate exactly {count} flashcards for studying {chapter} in {subject}.
Topic focus: {topic or 'all key concepts'}

Format each flashcard EXACTLY as:
CARD [n]
FRONT: [Question or term - concise]
BACK: [Answer or definition - clear and complete]
---

Generate all {count} cards. Make them progressively harder. Include definitions, formulas, applications."""

def build_study_plan_prompt(exam_name: str, exam_date: str, subjects: list, daily_hours: int, start_date: str) -> str:
    return f"""You are an expert academic planner. Create a detailed study plan.

Exam: {exam_name}
Exam Date: {exam_date}
Start Date: {start_date}
Subjects: {', '.join(subjects)}
Daily Study Hours: {daily_hours} hours

Create a week-by-week study plan in markdown format:
## 📅 Study Plan: {exam_name}

### Overview
- Total days: [calculate]
- Daily commitment: {daily_hours} hours
- Strategy: [overview]

### Week-by-Week Schedule
**Week 1: Foundation**
- Mon: [Subject] - [Topics] (X hours)
- Tue: [Subject] - [Topics] (X hours)
...

**Week 2: Core Concepts**
...

### Daily Study Template
- 0:00-X:XX: [Subject/Topic]
- Break: 10 min
...

### Revision Strategy
[Spaced repetition plan]

### Mock Test Schedule
[When to take practice tests]

### Tips for Success
[5 specific tips]"""

def build_document_prompt(text: str, action: str, language: str) -> str:
    lang = f"Respond entirely in {language}.\n" if language != "English" else ""

    actions = {
        "summary": f"""{lang}You are an expert study material creator. Analyze this document and create:
## 📚 Document Study Guide

### Executive Summary
[3-4 paragraph comprehensive summary]

### Key Concepts
[Bullet-pointed list of all important concepts]

### Critical Information
[Tables, formulas, dates, names that students must memorize]

### Exam-Ready Q&A
[10 probable exam questions with answers]

Document Content:
{text[:15000]}""",

        "flashcards": f"""{lang}Create 15 study flashcards from this document.
Format:
CARD [n]
FRONT: [Question]
BACK: [Answer]
---

Document: {text[:12000]}""",

        "quiz": f"""{lang}Create a 20-question quiz from this document with answers.
Include MCQs, short answer, and essay questions.
Document: {text[:12000]}""",

        "notes": f"""{lang}Transform this document into organized, hierarchical study notes.
Use headings, subheadings, bullet points, and tables.
Document: {text[:12000]}""",

        "mindmap": f"""{lang}Create a text-based mind map of this document's key concepts.
Format as a hierarchical tree structure.
Document: {text[:8000]}""",
    }
    return actions.get(action, actions["summary"])

async def enhance_note(content: str, action: str) -> str:
    prompts = {
        "improve": f"Improve the clarity and structure of these notes:\n{content}",
        "expand": f"Expand these notes with more detail and examples:\n{content}",
        "questions": f"Generate 10 study questions from these notes:\n{content}",
        "summary": f"Create a concise summary of these notes:\n{content}",
        "flashcards": f"Create 10 flashcards from these notes. Format: CARD n\\nFRONT: question\\nBACK: answer\\n---\n{content}",
    }
    result, _ = await generate_content(prompts.get(action, prompts["improve"]))
    return result


def build_auto_quiz_prompt(chapter: str, subject: str, content_snippet: str, elo: float = 1000.0) -> str:
    if elo < 900:
        level = "basic (beginner-friendly, focus on definitions and simple recall)"
    elif elo < 1100:
        level = "intermediate (application and understanding)"
    elif elo < 1300:
        level = "advanced (analysis, synthesis, edge cases)"
    else:
        level = "expert (tricky variations, common misconceptions, deep reasoning)"

    return f"""You are an adaptive quiz engine. Generate exactly 5 MCQ questions for:
Subject: {subject} | Chapter: {chapter}
Student ELO: {elo:.0f} → Difficulty: {level}

Base questions on this content:
{content_snippet[:3000]}

Output STRICT JSON array (no markdown, no extra text):
[
  {{
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct": "A",
    "explanation": "Brief explanation why A is correct",
    "concept": "concept being tested",
    "difficulty": {min(1500, max(700, elo)):.0f}
  }}
]

Rules:
- correct must be exactly "A", "B", "C", or "D"
- All 4 options must be plausible
- Avoid trivially easy or trick questions
- Match difficulty to ELO level"""


def build_socratic_prompt(message: str, profile: dict, history: list) -> str:
    course = profile.get("course", "General")
    history_text = ""
    for m in history[-8:]:
        role = "Student" if m["role"] == "user" else "Tutor"
        history_text += f"{role}: {m['content']}\n"

    return f"""You are a Socratic tutor for a {course} student. Your ONLY method is asking guiding questions — never give direct answers.

Rules:
- NEVER directly state the answer
- Ask 1-2 short, targeted questions that guide the student toward the answer
- Build on their previous response
- If they're completely lost, give a small hint then ask again
- Be warm and encouraging
- Keep responses under 80 words

Context from conversation:
{history_text}

Student just said: "{message}"

Respond with guiding questions only:"""


def build_daily_agenda_prompt(username: str, profile: dict, weak_subjects: list,
                               due_flashcards: int, exams: list, study_minutes_today: int,
                               mistake_patterns: list) -> str:
    exam_text = "\n".join([f"- {e['exam_name']}: {e['days_left']} days away" for e in exams[:3]]) or "None"
    weak_text = "\n".join([f"- {w['subject']} / {w['chapter']}: {w['accuracy']:.0%} accuracy, ELO {w['elo']:.0f}" for w in weak_subjects[:5]]) or "None"
    mistake_text = "\n".join([f"- '{m['concept_tag']}' wrong {m['times']} times" for m in mistake_patterns[:5]]) or "None"

    return f"""You are a personal AI study coach. Create a smart, personalized daily study agenda.

Student: {username}
Course: {profile.get('course', 'General')} | Board: {profile.get('board', '')}
Study done today: {study_minutes_today} minutes
Flashcards due: {due_flashcards}

Weak Areas (by quiz ELO):
{weak_text}

Recurring Mistakes:
{mistake_text}

Upcoming Exams:
{exam_text}

Generate a JSON agenda for today. Output ONLY valid JSON, no markdown:
{{
  "greeting": "Personalized motivational message referencing their specific situation",
  "priority_alert": "One urgent thing they must focus on today (based on weak areas/exams)",
  "predicted_score": "e.g. 'At current pace: ~68% on Physics. Focus on Thermodynamics to reach 80%+'",
  "blocks": [
    {{
      "time": "e.g. 9:00 AM - 9:25 AM",
      "type": "flashcards|study|quiz|revision|break",
      "subject": "...",
      "topic": "...",
      "action": "Specific action to take",
      "why": "Why this matters right now",
      "xp": 25,
      "minutes": 25
    }}
  ],
  "daily_goal": "One sentence goal for today",
  "insight": "One data-driven insight about their learning pattern"
}}

Rules:
- Total blocks should add up to 60-120 minutes of study
- Prioritize weak areas and upcoming exams
- Include flashcard review if cards are due
- Add breaks every 25-30 min (Pomodoro)
- Be specific about topics, not generic"""


def build_knowledge_graph_prompt(subject: str, course: str, chapters: list) -> str:
    chapter_list = "\n".join([f"- {c}" for c in chapters[:30]])
    return f"""You are a curriculum expert. Map prerequisite relationships between chapters.

Subject: {subject} | Course: {course}
Chapters:
{chapter_list}

Output ONLY valid JSON, no markdown:
{{
  "nodes": [
    {{
      "id": "chapter_name",
      "label": "Short display name",
      "difficulty": 1-5,
      "estimated_hours": 2,
      "prerequisites": ["other_chapter_id"],
      "category": "foundation|core|advanced|application"
    }}
  ]
}}

Rules:
- id must exactly match a chapter from the list
- prerequisites must be chapter ids that MUST be studied first
- Foundation chapters have no prerequisites
- Be accurate about academic dependencies
- difficulty 1=easiest, 5=hardest"""
