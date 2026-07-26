from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.user import User
from models.school import School, SchoolInvite, StudentEnrollment, ClassSection
from schemas.school import SchoolCreate, SchoolLoginRequest, SchoolJoinRequest, SchoolAuthResponse
from services.auth_service import hash_password, verify_password, create_access_token
from datetime import datetime

router = APIRouter(prefix="/school", tags=["school-auth"])


@router.post("/register", response_model=SchoolAuthResponse)
async def register_school(payload: SchoolCreate, db: AsyncSession = Depends(get_db)):
    """School admin registers their school + creates their admin account."""
    # Check username/email uniqueness
    existing = await db.execute(
        select(User).where(
            (User.username == payload.admin_username) | (User.email == payload.admin_email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already taken")

    # Create school
    school = School(
        name=payload.name,
        city=payload.city,
        board=payload.board,
    )
    db.add(school)
    await db.flush()  # get school.id

    # Create admin user
    admin = User(
        username=payload.admin_username,
        email=payload.admin_email,
        hashed_password=hash_password(payload.admin_password),
        full_name=payload.admin_full_name,
        role="school_admin",
        school_id=school.id,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(school)
    await db.refresh(admin)

    token = create_access_token({"sub": admin.username, "role": admin.role, "school_id": school.id})
    return SchoolAuthResponse(
        access_token=token,
        role=admin.role,
        school_id=school.id,
        school_name=school.name,
        username=admin.username,
        full_name=admin.full_name,
    )


@router.post("/login", response_model=SchoolAuthResponse)
async def school_login(payload: SchoolLoginRequest, db: AsyncSession = Depends(get_db)):
    """Login for school_admin, school_teacher, and school_student."""
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.role not in ("school_admin", "school_teacher", "school_student"):
        raise HTTPException(status_code=403, detail="Not a school account — use the main login")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    school = await db.get(School, user.school_id)
    if not school or not school.is_active:
        raise HTTPException(status_code=403, detail="School account not active")

    token = create_access_token({"sub": user.username, "role": user.role, "school_id": user.school_id})
    return SchoolAuthResponse(
        access_token=token,
        role=user.role,
        school_id=user.school_id,
        school_name=school.name,
        username=user.username,
        full_name=user.full_name,
    )


@router.post("/join", response_model=SchoolAuthResponse)
async def join_with_invite(payload: SchoolJoinRequest, db: AsyncSession = Depends(get_db)):
    """Teacher or student joins a school using an invite code."""
    # Validate invite code
    result = await db.execute(
        select(SchoolInvite).where(SchoolInvite.invite_code == payload.invite_code.upper())
    )
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    if invite.is_used:
        raise HTTPException(status_code=400, detail="Invite code already used")
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invite code has expired")

    # Check username uniqueness
    existing = await db.execute(select(User).where(User.username == payload.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=invite.role,
        school_id=invite.school_id,
    )
    db.add(new_user)
    await db.flush()

    # If student, create enrollment — auto-link to an existing class section for this grade, if any
    if invite.role == "school_student" and invite.grade:
        class_r = await db.execute(
            select(ClassSection)
            .where(ClassSection.school_id == invite.school_id)
            .where(ClassSection.grade == invite.grade)
            .where(ClassSection.is_active == True)
            .order_by(ClassSection.id)
        )
        matching_class = class_r.scalars().first()

        enrollment = StudentEnrollment(
            student_id=new_user.id,
            school_id=invite.school_id,
            grade=invite.grade,
            class_section_id=matching_class.id if matching_class else None,
            status="active",
        )
        db.add(enrollment)

    # Mark invite as used
    invite.is_used = True
    invite.used_by = new_user.id

    await db.commit()
    await db.refresh(new_user)

    school = await db.get(School, invite.school_id)
    token = create_access_token({"sub": new_user.username, "role": new_user.role, "school_id": new_user.school_id})
    return SchoolAuthResponse(
        access_token=token,
        role=new_user.role,
        school_id=new_user.school_id,
        school_name=school.name if school else "",
        username=new_user.username,
        full_name=new_user.full_name,
    )
