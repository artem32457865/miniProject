from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from settings import get_db
from src.repository import users as repository_users
from src.schemas import SkillResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Отримати список користувачів."""
    return await repository_users.get_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """Отримати інформацію про користувача."""
    user = await repository_users.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено",
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Створити нового користувача."""

    # Перевіряємо чи існує користувач з таким email
    if await repository_users.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email вже зареєстрований")

    # Перевіряємо чи username зайнятий
    if await repository_users.get_user_by_username(db, username=user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username вже зайнятий")

    return await repository_users.create_user(db, user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Оновити дані користувача."""
    user = await repository_users.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено",
        )
    return user


@router.get("/{user_id}/skills", response_model=List[SkillResponse])
async def read_user_skills(user_id: int, db: Session = Depends(get_db)):
    """Отримати всі навички користувача."""
    skills = await repository_users.get_user_skills(db, user_id)
    if skills is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з ID {user_id} не знайдено",
        )
    return skills
