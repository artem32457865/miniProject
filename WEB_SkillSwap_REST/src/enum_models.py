import enum


class SkillLevel(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class ExchangeStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    completed = "completed"
    cancelled = "cancelled"


class SkillCategory(str, enum.Enum):
    programming = "programming"
    music = "music"
    sports = "sports"
    languages = "languages"
    art = "art"
    science = "science"
    cooking = "cooking"
    other = "other"
