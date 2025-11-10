from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.enum_models import SkillCategory, SkillLevel


class SkillBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Назва навички")
    description: str = Field(..., min_length=10, max_length=500, description="Детальний опис навички")
    category: SkillCategory
    level: SkillLevel

    # Новий валідатор для очищення рядків
    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class SkillCreate(SkillBase):
    can_teach: bool = Field(..., description="Чи можу навчати цій навичці")
    want_learn: bool = Field(..., description="Чи хочу вивчити цю навичку")

    # Перевірка логіки між can_teach і want_learn
    @field_validator("want_learn")
    @classmethod
    def check_teach_learn_conflict(cls, v, info):
        can_teach = info.data.get("can_teach")
        if can_teach is True and v is True:
            raise ValueError("Не можна одночасно вміти і хотіти вчитися одній навичці")
        return v


class SkillUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    category: Optional[SkillCategory] = None
    level: Optional[SkillLevel] = None
    can_teach: Optional[bool] = None
    want_learn: Optional[bool] = None


class SkillResponse(SkillBase):
    id: int
    can_teach: bool
    want_learn: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
