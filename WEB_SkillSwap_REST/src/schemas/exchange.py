from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from src.enum_models import ExchangeStatus

class ExchangeBase(BaseModel):
    message: str = Field(..., min_length=5, max_length=1000, description="Повідомлення для обміну")
    hours_proposed: int = Field(1, ge=1, le=100, description="Запропоновані години (1-100)")

class ExchangeCreate(ExchangeBase):
    receiver_id: int = Field(..., description="ID отримувача")
    skill_id: int = Field(..., description="ID навички")

class ExchangeUpdate(BaseModel):
    status: Optional[ExchangeStatus] = None
    message: Optional[str] = Field(None, min_length=5, max_length=1000)
    hours_proposed: Optional[int] = Field(None, ge=1, le=100)

class ExchangeResponse(ExchangeBase):
    id: int
    sender_id: int
    receiver_id: int
    skill_id: int
    status: ExchangeStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ExchangeFilter(BaseModel):
    status: Optional[ExchangeStatus] = None
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    skill_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"

class ExchangeWithDetailsResponse(ExchangeResponse):
    sender_username: str
    receiver_username: str
    skill_title: str