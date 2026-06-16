from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models.user import User
from models.flashcard import Flashcard
from schemas.flashcard import FlashcardCreate, FlashcardReview, FlashcardGenerateRequest
from middleware.auth import get_current_user
from services.ai_service import generate_content, build_flashcard_prompt
from services.gamification import award_xp, auto_check_badges
from datetime import date, timedelta
import re

router = APIRouter(prefix="/flashcards", tags=["flashcards"])

def parse_flashcards(raw_text: str) -> list:
    cards = []
    pattern = r"CARD\s*\d+\s*\nFRONT:\s*(.*?)\nBACK:\s*(.*?)(?=---|\Z)"
    matches = re.findall(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    for front, back in matches:
        if front.strip() and back.strip():
            cards.append({"front": front.strip(), "back": back.strip()})
    return cards

def calculate_sm2(ease_factor: float, interval: int, performance: int):
    if performance >= 3:
        if interval == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)
        new_ef = ease_factor + (0.1 - (5 - performance) * (0.08 + (5 - performance) * 0.02))
        new_ef = max(1.3, new_ef)
    else:
        new_interval = 1
        new_ef = ease_factor
    return new_ef, new_interval

@router.get("/")
async def get_all_flashcards(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Flashcard).where(Flashcard.username == current_user.username))
    cards = result.scalars().all()
    return [{"id": c.id, "front_text": c.front_text, "back_text": c.back_text, "subject": c.subject,
             "chapter": c.chapter, "next_review_date": c.next_review_date, "ease_factor": c.ease_factor,
             "interval_days": c.interval_days, "review_count": c.review_count, "tags": c.tags} for c in cards]

@router.get("/due")
async def get_due_flashcards(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    today = date.today().isoformat()
    result = await db.execute(
        select(Flashcard).where(Flashcard.username == current_user.username, Flashcard.next_review_date <= today)
    )
    cards = result.scalars().all()
    return [{"id": c.id, "front_text": c.front_text, "back_text": c.back_text, "subject": c.subject,
             "chapter": c.chapter, "next_review_date": c.next_review_date, "ease_factor": c.ease_factor,
             "interval_days": c.interval_days, "review_count": c.review_count} for c in cards]

@router.post("/")
async def create_flashcard(data: FlashcardCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    today = date.today().isoformat()
    card = Flashcard(
        username=current_user.username,
        front_text=data.front_text,
        back_text=data.back_text,
        subject=data.subject,
        chapter=data.chapter,
        topic=data.topic,
        tags=data.tags,
        created_date=today,
        next_review_date=today,
        ease_factor=2.5,
        interval_days=1,
        review_count=0
    )
    db.add(card)
    await award_xp(db, current_user.username, 2)
    await db.commit()
    await auto_check_badges(db, current_user.username)
    return {"message": "Flashcard created", "id": card.id, "xp_awarded": 2}

@router.post("/generate")
async def generate_flashcards(data: FlashcardGenerateRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    prompt = build_flashcard_prompt(data.subject, data.chapter, data.topic, data.count)
    raw, model = await generate_content(prompt)
    parsed = parse_flashcards(raw)

    today = date.today().isoformat()
    created_ids = []
    for p in parsed:
        card = Flashcard(
            username=current_user.username,
            front_text=p["front"],
            back_text=p["back"],
            subject=data.subject,
            chapter=data.chapter,
            created_date=today,
            next_review_date=today,
            ease_factor=2.5,
            interval_days=1,
            review_count=0
        )
        db.add(card)
        created_ids.append(card)

    await award_xp(db, current_user.username, len(parsed) * 2)
    await db.commit()
    await auto_check_badges(db, current_user.username)
    return {"created": len(parsed), "xp_awarded": len(parsed) * 2, "model": model}

@router.post("/{card_id}/review")
async def review_flashcard(card_id: int, data: FlashcardReview, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Flashcard).where(Flashcard.id == card_id, Flashcard.username == current_user.username))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    new_ef, new_interval = calculate_sm2(card.ease_factor, card.interval_days, data.performance)
    card.ease_factor = new_ef
    card.interval_days = new_interval
    card.review_count += 1
    next_date = (date.today() + timedelta(days=new_interval)).isoformat()
    card.next_review_date = next_date

    xp = {1: 1, 2: 2, 3: 3, 4: 5}.get(data.performance, 2)
    await award_xp(db, current_user.username, xp)
    await db.commit()
    return {"next_review": next_date, "interval": new_interval, "xp_awarded": xp}

@router.delete("/{card_id}")
async def delete_flashcard(card_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Flashcard).where(Flashcard.id == card_id, Flashcard.username == current_user.username))
    await db.commit()
    return {"message": "Flashcard deleted"}
