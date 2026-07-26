from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from models.user import User
from models.quiz import QuizAttempt, MistakeEntry
from models.flashcard import Flashcard
from middleware.auth import get_current_user
from services.ai_service import generate_content, build_quiz_prompt
from services.gamification import award_xp
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
import json
import re

router = APIRouter(prefix="/quiz", tags=["quiz"])


class QuizGenerateRequest(BaseModel):
    subject: str
    chapter: str
    content_snippet: str


class QuizSubmitItem(BaseModel):
    question: str
    correct_answer: str
    user_answer: str
    correct_letter: str
    concept: str
    time_taken_secs: int = 30


class QuizSubmitRequest(BaseModel):
    subject: str
    chapter: str
    answers: List[QuizSubmitItem]


@router.post("/generate")
async def generate_quiz(
    req: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    prompt = build_quiz_prompt(req.chapter, req.subject, req.content_snippet)
    raw, model = await generate_content(prompt)

    try:
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group())
        else:
            questions = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse quiz questions from AI")

    return {"questions": questions, "model": model}


@router.post("/submit")
async def submit_quiz(
    req: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    correct_count = 0
    xp_earned = 0

    for ans in req.answers:
        is_correct = ans.user_answer.strip().upper() == ans.correct_letter.strip().upper()

        attempt = QuizAttempt(
            username=current_user.username,
            subject=req.subject,
            chapter=req.chapter,
            question=ans.question,
            correct_answer=ans.correct_answer,
            user_answer=ans.user_answer,
            is_correct=is_correct,
            time_taken_secs=ans.time_taken_secs,
        )
        db.add(attempt)

        if is_correct:
            correct_count += 1
            xp_earned += 5
        else:
            result2 = await db.execute(
                select(MistakeEntry).where(
                    MistakeEntry.username == current_user.username,
                    MistakeEntry.question == ans.question
                )
            )
            existing_mistake = result2.scalar_one_or_none()
            if existing_mistake:
                existing_mistake.times_wrong += 1
                existing_mistake.user_answer = ans.user_answer
            else:
                mistake = MistakeEntry(
                    username=current_user.username,
                    subject=req.subject,
                    chapter=req.chapter,
                    question=ans.question,
                    correct_answer=ans.correct_answer,
                    user_answer=ans.user_answer,
                    concept_tag=ans.concept,
                    times_wrong=1
                )
                db.add(mistake)

            # Auto-create flashcard for wrong answers
            today = date.today().isoformat()
            fc = Flashcard(
                username=current_user.username,
                front_text=ans.question,
                back_text=f"✓ {ans.correct_answer}",
                subject=req.subject,
                chapter=req.chapter,
                tags="auto-generated,mistake",
                created_date=today,
                next_review_date=today,
                ease_factor=1.8,
                interval_days=1,
                review_count=0
            )
            db.add(fc)

    await award_xp(db, current_user.username, xp_earned)
    await db.commit()

    accuracy = correct_count / max(len(req.answers), 1)
    return {
        "correct": correct_count,
        "total": len(req.answers),
        "accuracy": accuracy,
        "xp_earned": xp_earned,
        "auto_flashcards_created": len(req.answers) - correct_count
    }


@router.get("/mistakes")
async def get_mistakes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MistakeEntry)
        .where(MistakeEntry.username == current_user.username)
        .order_by(desc(MistakeEntry.times_wrong))
        .limit(50)
    )
    mistakes = result.scalars().all()
    return [
        {
            "id": m.id, "subject": m.subject, "chapter": m.chapter,
            "question": m.question, "correct_answer": m.correct_answer,
            "user_answer": m.user_answer, "concept_tag": m.concept_tag,
            "times_wrong": m.times_wrong, "last_seen": m.last_seen.isoformat()
        }
        for m in mistakes
    ]
