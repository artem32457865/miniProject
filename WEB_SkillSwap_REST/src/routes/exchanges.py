from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from settings import get_db
from src.repository import exchanges as repository_exchanges
from src.schemas.exchange import (
    ExchangeCreate, 
    ExchangeUpdate, 
    ExchangeResponse, 
    ExchangeWithDetailsResponse,
    ExchangeFilter
)
from src.enum_models import ExchangeStatus

router = APIRouter(prefix="/exchanges", tags=["Exchanges"])

@router.get("/", response_model=List[ExchangeWithDetailsResponse])
def get_exchanges(
    status: Optional[ExchangeStatus] = Query(None),
    sender_id: Optional[int] = Query(None),
    receiver_id: Optional[int] = Query(None),
    skill_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Отримати обміни з фільтрацією"""
    filters = ExchangeFilter(
        status=status,
        sender_id=sender_id,
        receiver_id=receiver_id,
        skill_id=skill_id,
        from_date=from_date,
        to_date=to_date,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    exchanges = repository_exchanges.get_exchanges_with_filters(db, filters, skip, limit)
    
    # Конвертуємо в response з деталями
    result = []
    for exchange in exchanges:
        result.append(ExchangeWithDetailsResponse(
            id=exchange.id,
            sender_id=exchange.sender_id,
            receiver_id=exchange.receiver_id,
            skill_id=exchange.skill_id,
            message=exchange.message,
            hours_proposed=exchange.hours_proposed,
            status=exchange.status,
            created_at=exchange.created_at,
            updated_at=exchange.updated_at,
            sender_username=exchange.sender.username,
            receiver_username=exchange.receiver.username,
            skill_title=exchange.skill.title
        ))
    
    return result

@router.get("/{exchange_id}", response_model=ExchangeWithDetailsResponse)
def get_exchange(exchange_id: int, db: Session = Depends(get_db)):
    """Отримати деталі обміну за ID"""
    exchange = repository_exchanges.get_exchange(db, exchange_id)
    if not exchange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Обмін з ID {exchange_id} не знайдено"
        )
    
    return ExchangeWithDetailsResponse(
        id=exchange.id,
        sender_id=exchange.sender_id,
        receiver_id=exchange.receiver_id,
        skill_id=exchange.skill_id,
        message=exchange.message,
        hours_proposed=exchange.hours_proposed,
        status=exchange.status,
        created_at=exchange.created_at,
        updated_at=exchange.updated_at,
        sender_username=exchange.sender.username,
        receiver_username=exchange.receiver.username,
        skill_title=exchange.skill.title
    )

@router.post("/", response_model=ExchangeWithDetailsResponse, status_code=status.HTTP_201_CREATED)
def create_exchange(
    exchange: ExchangeCreate,
    # TODO: Додати автентифікацію для отримання sender_id
    sender_id: int = 1,  # Тимчасово - замінити на отримання з токена
    db: Session = Depends(get_db)
):
    """Створити новий обмін"""
    try:
        created_exchange = repository_exchanges.create_exchange(db, exchange, sender_id)
        return ExchangeWithDetailsResponse(
            id=created_exchange.id,
            sender_id=created_exchange.sender_id,
            receiver_id=created_exchange.receiver_id,
            skill_id=created_exchange.skill_id,
            message=created_exchange.message,
            hours_proposed=created_exchange.hours_proposed,
            status=created_exchange.status,
            created_at=created_exchange.created_at,
            updated_at=created_exchange.updated_at,
            sender_username=created_exchange.sender.username,
            receiver_username=created_exchange.receiver.username,
            skill_title=created_exchange.skill.title
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{exchange_id}", response_model=ExchangeWithDetailsResponse)
def update_exchange(
    exchange_id: int,
    exchange_update: ExchangeUpdate,
    # TODO: Додати автентифікацію
    user_id: int = 1,  # Тимчасово
    db: Session = Depends(get_db)
):
    """Оновити обмін"""
    try:
        updated_exchange = repository_exchanges.update_exchange(db, exchange_id, exchange_update, user_id)
        if not updated_exchange:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Обмін з ID {exchange_id} не знайдено"
            )
        
        return ExchangeWithDetailsResponse(
            id=updated_exchange.id,
            sender_id=updated_exchange.sender_id,
            receiver_id=updated_exchange.receiver_id,
            skill_id=updated_exchange.skill_id,
            message=updated_exchange.message,
            hours_proposed=updated_exchange.hours_proposed,
            status=updated_exchange.status,
            created_at=updated_exchange.created_at,
            updated_at=updated_exchange.updated_at,
            sender_username=updated_exchange.sender.username,
            receiver_username=updated_exchange.receiver.username,
            skill_title=updated_exchange.skill.title
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{exchange_id}/status", response_model=ExchangeWithDetailsResponse)
def update_exchange_status(
    exchange_id: int,
    status: ExchangeStatus,
    # TODO: Додати автентифікацію
    user_id: int = 1,  # Тимчасово
    db: Session = Depends(get_db)
):
    """Оновити статус обміну (для отримувача)"""
    try:
        updated_exchange = repository_exchanges.update_exchange_status(db, exchange_id, status, user_id)
        if not updated_exchange:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Обмін з ID {exchange_id} не знайдено"
            )
        
        return ExchangeWithDetailsResponse(
            id=updated_exchange.id,
            sender_id=updated_exchange.sender_id,
            receiver_id=updated_exchange.receiver_id,
            skill_id=updated_exchange.skill_id,
            message=updated_exchange.message,
            hours_proposed=updated_exchange.hours_proposed,
            status=updated_exchange.status,
            created_at=updated_exchange.created_at,
            updated_at=updated_exchange.updated_at,
            sender_username=updated_exchange.sender.username,
            receiver_username=updated_exchange.receiver.username,
            skill_title=updated_exchange.skill.title
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange(
    exchange_id: int,
    # TODO: Додати автентифікацію
    user_id: int = 1,  # Тимчасово
    db: Session = Depends(get_db)
):
    """Видалити обмін"""
    try:
        success = repository_exchanges.delete_exchange(db, exchange_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Обмін з ID {exchange_id} не знайдено"
            )
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/user/{user_id}", response_model=List[ExchangeWithDetailsResponse])
def get_user_exchanges(user_id: int, db: Session = Depends(get_db)):
    """Отримати всі обміни користувача"""
    exchanges = repository_exchanges.get_user_exchanges(db, user_id)
    
    result = []
    for exchange in exchanges:
        result.append(ExchangeWithDetailsResponse(
            id=exchange.id,
            sender_id=exchange.sender_id,
            receiver_id=exchange.receiver_id,
            skill_id=exchange.skill_id,
            message=exchange.message,
            hours_proposed=exchange.hours_proposed,
            status=exchange.status,
            created_at=exchange.created_at,
            updated_at=exchange.updated_at,
            sender_username=exchange.sender.username,
            receiver_username=exchange.receiver.username,
            skill_title=exchange.skill.title
        ))
    
    return result