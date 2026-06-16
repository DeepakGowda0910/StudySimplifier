from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.user import User, UserProfile, UserStats, Streak
from schemas.auth import RegisterRequest, LoginRequest, Token
from services.auth_service import hash_password, verify_password, create_access_token
from services.gamification import award_badge, check_daily_login

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(username=request.username, email=request.email, hashed_password=hash_password(request.password))
    db.add(user)

    profile = UserProfile(username=request.username)
    db.add(profile)

    stats = UserStats(username=request.username)
    db.add(stats)

    streak = Streak(username=request.username, current_streak=0, longest_streak=0)
    db.add(streak)

    await db.commit()
    await award_badge(db, request.username, "first_login")

    token = create_access_token({"sub": request.username})
    return Token(access_token=token, username=request.username, onboarded=False)

@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == request.username.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result2 = await db.execute(select(UserProfile).where(UserProfile.username == user.username))
    profile = result2.scalar_one_or_none()

    await check_daily_login(db, user.username)

    token = create_access_token({"sub": user.username})
    return Token(
        access_token=token,
        username=user.username,
        onboarded=profile.onboarded if profile else False
    )

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
