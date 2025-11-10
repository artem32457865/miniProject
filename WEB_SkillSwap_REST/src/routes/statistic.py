from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from settings import get_db
from src.models.user_skills import User, Skill, Exchange, ExchangeStatus

router = APIRouter(prefix="/api/stats", tags=["Statistics"])

@router.get("/top-skills")
async def get_top_skills(db: AsyncSession = Depends(get_db)):

    stmt = (
        select(Skill.title, Skill.category, func.count(Exchange.id).label("exchange_count"))
        .select_from(Skill)
        .join(Exchange, Skill.id == Exchange.skill_id)
        .group_by(Skill.id, Skill.title, Skill.category)
        .order_by(func.count(Exchange.id).desc())
        .limit(10)
    )
    
    result = await db.execute(stmt)
    skills = result.all()
    
    return {
        "top_skills": [
            {
                "title": skill.title,
                "category": skill.category,
                "exchange_count": skill.exchange_count
            }
            for skill in skills
        ]
    }

@router.get("/active-users")
async def get_active_users(db: AsyncSession = Depends(get_db)):

    stmt = (
        select(
            User.username,
            User.full_name,
            func.count(Exchange.id).label("total_exchanges")
        )
        .select_from(User)
        .join(Exchange, (User.id == Exchange.sender_id) | (User.id == Exchange.receiver_id))
        .group_by(User.id, User.username, User.full_name)
        .order_by(func.count(Exchange.id).desc())
        .limit(10)
    )
    
    result = await db.execute(stmt)
    users = result.all()
    
    return {
        "active_users": [
            {
                "username": user.username,
                "full_name": user.full_name,
                "total_exchanges": user.total_exchanges
            }
            for user in users
        ]
    }

@router.get("/exchange-success-rate")
async def get_exchange_success_rate(db: AsyncSession = Depends(get_db)):

    stmt = select(
        func.count(Exchange.id).label("total_exchanges"),
        func.count().filter(Exchange.status == ExchangeStatus.completed).label("completed_exchanges")
    )
    
    result = await db.execute(stmt)
    stats = result.first()
    
    total = stats.total_exchanges or 1 
    completed = stats.completed_exchanges or 0
    success_rate = (completed / total) * 100
    
    return {
        "total_exchanges": total,
        "completed_exchanges": completed,
        "success_rate": round(success_rate, 2),
        "success_percentage": f"{success_rate:.2f}%"
    }