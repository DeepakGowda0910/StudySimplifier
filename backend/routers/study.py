from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.user import User, UserProfile
from schemas.study import GenerateRequest, ChatRequest
from middleware.auth import get_current_user
from services.ai_service import generate_content, build_study_prompt, build_chat_prompt, build_document_prompt, build_socratic_prompt
from services.gamification import award_xp, auto_check_badges
from services.retrieval_service import get_grounding_context
from sqlalchemy import select
import json
import io
import os
import PyPDF2
import docx

router = APIRouter(prefix="/study", tags=["study"])

_here = os.path.dirname(os.path.abspath(__file__))
_data_path = os.path.join(_here, "..", "..", "data", "study_data.json")
with open(_data_path) as f:
    STUDY_DATA = json.load(f)

@router.get("/data")
async def get_study_data():
    return STUDY_DATA

@router.get("/categories")
async def get_categories():
    return list(STUDY_DATA.keys())

@router.get("/courses/{category}")
async def get_courses(category: str):
    return list(STUDY_DATA.get(category, {}).keys())

@router.get("/streams/{category}/{course}")
async def get_streams(category: str, course: str):
    return list(STUDY_DATA.get(category, {}).get(course, {}).keys())

@router.get("/subjects/{category}/{course}/{stream}")
async def get_subjects(category: str, course: str, stream: str):
    return list(STUDY_DATA.get(category, {}).get(course, {}).get(stream, {}).keys())

@router.get("/topics/{category}/{course}/{stream}/{subject}")
async def get_topics(category: str, course: str, stream: str, subject: str):
    return list(STUDY_DATA.get(category, {}).get(course, {}).get(stream, {}).get(subject, {}).keys())

@router.get("/chapters/{category}/{course}/{stream}/{subject}/{topic}")
async def get_chapters(category: str, course: str, stream: str, subject: str, topic: str):
    return STUDY_DATA.get(category, {}).get(course, {}).get(stream, {}).get(subject, {}).get(topic, [])

@router.post("/generate")
async def generate_study_material(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserProfile).where(UserProfile.username == current_user.username))
    profile = result.scalar_one_or_none()

    course = request.course or (profile.course if profile else "")
    subject = request.subject or ""

    grounding_context = ""
    if course and subject and request.chapter:
        grounding_context = await get_grounding_context(
            db, course=course, subject=subject, chapter=request.chapter,
            query=f"{request.tool} {request.chapter} {request.topic or ''}",
        )

    prompt = build_study_prompt(
        tool=request.tool,
        chapter=request.chapter,
        topic=request.topic or "",
        subject=subject,
        course=course,
        board=request.board or (profile.board if profile else ""),
        stream=request.stream or (profile.stream if profile else ""),
        language=request.language,
        grounding_context=grounding_context,
    )

    content, model_name = await generate_content(prompt)
    await award_xp(db, current_user.username, 10)
    await auto_check_badges(db, current_user.username)

    return {
        "content": content,
        "tool": request.tool,
        "model_used": model_name,
        "xp_awarded": 10
    }

@router.post("/chat")
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserProfile).where(UserProfile.username == current_user.username))
    profile = result.scalar_one_or_none()

    profile_dict = {
        "course": profile.course if profile else "General",
        "category": profile.category if profile else "",
        "stream": profile.stream if profile else "",
        "board": profile.board if profile else "",
    }

    history = [{"role": m.role, "content": m.content} for m in (request.history or [])]

    if request.socratic_mode:
        prompt = build_socratic_prompt(request.message, profile_dict, history)
    else:
        prompt = build_chat_prompt(request.message, profile_dict, history)

    response, model = await generate_content(prompt)
    return {"response": response, "model": model, "mode": "socratic" if request.socratic_mode else "normal"}

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    action: str = Form("summary"),
    language: str = Form("English"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    text = ""

    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file.filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        text = content.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document")

    prompt = build_document_prompt(text, action, language)
    result, model = await generate_content(prompt)

    await award_xp(db, current_user.username, 15)
    return {"content": result, "model": model, "xp_awarded": 15, "filename": file.filename}
