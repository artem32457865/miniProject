from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.models import User
from src.schemas import UserCreate, UserUpdate


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Отримати список користувачів з пагінацією."""
    stmt = select(User).offset(skip).limit(limit)
    result = await db.scalars(stmt)
    return result.all()


# -======================================


async def get_user(db: Session, user_id: int) -> Optional[User]:
    """Отримати користувача за його ID."""
    return db.query(User).filter(User.id == user_id).first()


async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Отримати користувача за email."""
    return db.query(User).filter(User.email == email).first()


async def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Отримати користувача за username."""
    return db.query(User).filter(User.username == username).first()


async def create_user(db: Session, user: UserCreate) -> User:
    """Створити нового користувача."""
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Оновити дані користувача."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


async def get_user_skills(db: Session, user_id: int) -> Optional[List]:
    """Отримати всі навички користувача за ID."""
    user = db.query(User).filter(User.id == user_id).first()
    return user.skills if user else None
