import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    # Якщо потрібно, можна додати оновлення username/email:
    # username: Optional[str] = Field(None, min_length=3, max_length=50)
    # email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int
    # created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
