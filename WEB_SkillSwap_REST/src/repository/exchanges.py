from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from src.models.user_skills import Exchange, User, Skill, ExchangeStatus
from src.schemas.exchange import ExchangeCreate, ExchangeUpdate, ExchangeFilter

def get_exchange(db: Session, exchange_id: int) -> Optional[Exchange]:
    """Отримати обмін за ID"""
    return (
        db.query(Exchange)
        .options(
            joinedload(Exchange.sender),
            joinedload(Exchange.receiver),
            joinedload(Exchange.skill)
        )
        .filter(Exchange.id == exchange_id)
        .first()
    )

def get_exchanges_with_filters(
    db: Session, 
    filters: ExchangeFilter,
    skip: int = 0, 
    limit: int = 100
) -> List[Exchange]:
    """Отримати обміни з фільтрацією"""
    query = (
        db.query(Exchange)
        .options(
            joinedload(Exchange.sender),
            joinedload(Exchange.receiver),
            joinedload(Exchange.skill)
        )
    )
    
    # Фільтрація за статусом
    if filters.status:
        query = query.filter(Exchange.status == filters.status)
    
    # Фільтрація за користувачем
    if filters.sender_id:
        query = query.filter(Exchange.sender_id == filters.sender_id)
    if filters.receiver_id:
        query = query.filter(Exchange.receiver_id == filters.receiver_id)
    
    # Фільтрація за навичкою
    if filters.skill_id:
        query = query.filter(Exchange.skill_id == filters.skill_id)
    
    # Фільтрація за датою
    if filters.from_date:
        query = query.filter(Exchange.created_at >= filters.from_date)
    if filters.to_date:
        query = query.filter(Exchange.created_at <= filters.to_date)
    
    # Сортування
    order_field = getattr(Exchange, filters.sort_by, Exchange.created_at)
    if filters.sort_order == "asc":
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    # Пагінація
    return query.offset(skip).limit(limit).all()

def create_exchange(db: Session, exchange: ExchangeCreate, sender_id: int) -> Exchange:
    """Створити новий обмін"""
    # Перевірка чи існує отримувач
    receiver = db.query(User).filter(User.id == exchange.receiver_id).first()
    if not receiver:
        raise ValueError("Отримувач не знайдений")
    
    # Перевірка чи існує навичка
    skill = db.query(Skill).filter(Skill.id == exchange.skill_id).first()
    if not skill:
        raise ValueError("Навичка не знайдена")
    
    # Перевірка чи відправник не є отримувачем
    if sender_id == exchange.receiver_id:
        raise ValueError("Не можна створити обмін із самим собою")
    
    db_exchange = Exchange(
        sender_id=sender_id,
        receiver_id=exchange.receiver_id,
        skill_id=exchange.skill_id,
        message=exchange.message,
        hours_proposed=exchange.hours_proposed,
        status=ExchangeStatus.pending
    )
    
    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)
    return db_exchange

def update_exchange_status(
    db: Session, 
    exchange_id: int, 
    status: ExchangeStatus,
    user_id: int
) -> Optional[Exchange]:
    """Оновити статус обміну (тільки отримувач може прийняти/відхилити)"""
    exchange = get_exchange(db, exchange_id)
    if not exchange:
        return None
    
    # Перевірка прав: тільки отримувач може змінювати статус
    if exchange.receiver_id != user_id:
        raise ValueError("Тільки отримувач може змінювати статус обміну")
    
    exchange.status = status
    db.commit()
    db.refresh(exchange)
    return exchange

def update_exchange(
    db: Session, 
    exchange_id: int, 
    exchange_update: ExchangeUpdate,
    user_id: int
) -> Optional[Exchange]:
    """Оновити обмін (тільки відправник може оновлювати)"""
    exchange = get_exchange(db, exchange_id)
    if not exchange:
        return None
    
    # Перевірка прав: тільки відправник може оновлювати
    if exchange.sender_id != user_id:
        raise ValueError("Тільки відправник може оновлювати обмін")
    
    # Перевірка статусу: можна оновлювати тільки pending обміни
    if exchange.status != ExchangeStatus.pending:
        raise ValueError("Можна оновлювати тільки обміни зі статусом 'pending'")
    
    update_data = exchange_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exchange, field, value)
    
    db.commit()
    db.refresh(exchange)
    return exchange

def delete_exchange(db: Session, exchange_id: int, user_id: int) -> bool:
    """Видалити обмін (тільки відправник або адмін)"""
    exchange = get_exchange(db, exchange_id)
    if not exchange:
        return False
    
    # Перевірка прав: тільки відправник може видалити
    if exchange.sender_id != user_id:
        raise ValueError("Тільки відправник може видалити обмін")
    
    # Перевірка статусу: можна видаляти тільки pending обміни
    if exchange.status != ExchangeStatus.pending:
        raise ValueError("Можна видаляти тільки обміни зі статусом 'pending'")
    
    db.delete(exchange)
    db.commit()
    return True

def get_user_exchanges(db: Session, user_id: int) -> List[Exchange]:
    """Отримати всі обміни користувача (як відправника та отримувача)"""
    return (
        db.query(Exchange)
        .options(
            joinedload(Exchange.sender),
            joinedload(Exchange.receiver),
            joinedload(Exchange.skill)
        )
        .filter(
            or_(
                Exchange.sender_id == user_id,
                Exchange.receiver_id == user_id
            )
        )
        .order_by(Exchange.created_at.desc())
        .all()
    )