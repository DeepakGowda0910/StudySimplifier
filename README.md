# StudySmart AI v2.0

A production-grade AI-powered study platform rebuilt with **FastAPI** backend and **React** frontend.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion, Recharts |
| Backend | FastAPI, SQLAlchemy (async), SQLite/PostgreSQL |
| AI | Google Gemini 1.5 Pro/Flash |
| Auth | JWT (python-jose), bcrypt |
| State | Zustand + TanStack Query |

## Features

- **9 AI Study Tools** — Quick Notes, Summary, Notes, Detailed Guide, Revision, Quiz, Q&A, Question Paper, Document Upload
- **Spaced Repetition Flashcards** — SM-2 algorithm, AI card generation
- **Rich Notes Editor** — with AI enhancement (expand, improve, generate questions)
- **Study Planner** — AI-generated study schedules from exam dates
- **Pomodoro Timer** — built-in focus timer with session tracking
- **Exam Countdown** — track upcoming exams with days remaining
- **Progress Analytics** — charts for study time, subject distribution, XP trends
- **Gamification** — XP, levels, streaks, 17 achievement badges
- **Leaderboard** — compete with other students
- **AI Chat (StudyBot)** — course-aware AI tutor, always accessible
- **Dark Mode** — system-wide theme switching
- **Multi-language** — 12 language output support
- **Document Analysis** — upload PDF/DOCX and generate study material

## Quick Start

### 1. Set your Gemini API Key

Edit `backend/.env`:
```
GEMINI_API_KEY=your_key_here
SECRET_KEY=change_this_in_production
```

### 2. Start Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend: http://localhost:8000  |  Docs: http://localhost:8000/docs

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Project Structure

```
StudySimplifier/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   └── services/            # Business logic + AI
├── frontend/
│   └── src/
│       ├── pages/           # All pages
│       ├── components/      # UI components
│       ├── api/             # API client
│       └── store/           # Zustand state
└── data/
    └── study_data.json      # Curriculum data
```

## Production

- Swap SQLite for PostgreSQL: `DATABASE_URL=postgresql+asyncpg://user:pass@host/db`
- Build frontend: `cd frontend && npm run build` (serve `dist/` with nginx)
- Run: `gunicorn -k uvicorn.workers.UvicornWorker main:app`
