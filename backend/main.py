from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import auth, user, study, flashcards, notes, planner, quiz, agent
from routers import school_auth, school_admin, school_teacher, school_student
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    from services.curriculum_service import seed_curriculum
    from database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await seed_curriculum(db)
    yield

app = FastAPI(
    title=settings.app_name,
    description="AI-powered study platform API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(study.router, prefix="/api")
app.include_router(flashcards.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(planner.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(school_auth.router, prefix="/api")
app.include_router(school_admin.router, prefix="/api")
app.include_router(school_teacher.router, prefix="/api")
app.include_router(school_student.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "StudySmart AI API v2.0", "status": "running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
