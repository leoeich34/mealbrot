from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.modules.auth.schemas import LoginRequest, UserCreate, UserRead
from app.security import (
    clear_auth_cookie,
    get_current_user,
    hash_password,
    set_auth_cookie,
    verify_password,
)
from app.shared.crud import commit_refresh


router = APIRouter()
@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        role="user",
        preferences=payload.preferences,
        allergies=payload.allergies,
        diet=payload.diet,
        favorite_dishes=payload.favorite_dishes,
        weekly_budget=payload.weekly_budget,
        monthly_budget=payload.monthly_budget,
    )
    commit_refresh(db, user)
    set_auth_cookie(response, user)
    return user

@router.post("/auth/login", response_model=UserRead)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    set_auth_cookie(response, user)
    return user

@router.post("/auth/logout")
def logout(response: Response):
    clear_auth_cookie(response)
    return {"ok": True}

@router.get("/auth/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
