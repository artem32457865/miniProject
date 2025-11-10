import datetime as dt

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from settings import Base
from src.enum_models import ExchangeStatus, SkillLevel

skill_user_association = Table(
    "skill_user_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE")),
)



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    

    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=True,
    )



    # Relationships
    skills: Mapped[list["Skill"]] = relationship(
        "Skill",
        secondary=skill_user_association,
        back_populates="users",
        lazy="selectin",
    )

    sent_exchanges = relationship(
        "Exchange",
        foreign_keys="Exchange.sender_id",
        back_populates="sender",
        lazy="selectin",
    )
    received_exchanges = relationship(
        "Exchange",
        foreign_keys="Exchange.receiver_id",
        back_populates="receiver",
        lazy="selectin",
    )
    given_reviews = relationship(
        "Review",
        foreign_keys="Review.reviewer_id",
        back_populates="reviewer",
        lazy="selectin",
    )
    received_reviews = relationship(
        "Review",
        foreign_keys="Review.reviewed_id",
        back_populates="reviewed",
        lazy="selectin",
    )

    def __str__(self):
        return f"<User(id={self.id}, name={self.username})>"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    level: Mapped[SkillLevel] = mapped_column(SQLEnum(SkillLevel), nullable=False)

    can_teach: Mapped[bool] = mapped_column(Boolean, default=False)
    want_learn: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=True,
    )

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="skill_user_association",
        back_populates="skills",
        lazy="selectin",
    )
    exchanges = relationship("Exchange", back_populates="skill", lazy="selectin")


class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[ExchangeStatus] = mapped_column(SQLEnum(ExchangeStatus), default=ExchangeStatus.pending)
    hours_proposed: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True
    )

    sender: Mapped["User"] = relationship(back_populates="sent_exchanges", foreign_keys=[sender_id], lazy="selectin")
    receiver: Mapped["User"] = relationship(
        back_populates="received_exchanges", foreign_keys=[receiver_id], lazy="selectin"
    )
    skill: Mapped["Skill"] = relationship(back_populates="exchanges", lazy="selectin")
    reviews: Mapped[list["Review"]] = relationship(back_populates="exchange", lazy="selectin")

    def __str__(self):
        return (
            f"Exchange(id={self.id}, sender_id={self.sender_id}, "
            f"receiver_id={self.receiver_id}, skill_id={self.skill_id}, "
            f"status={self.status.name}, hours={self.hours_proposed})"
        )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exchange_id: Mapped[int] = mapped_column(Integer, ForeignKey("exchanges.id"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    # Relationships
    exchange = relationship("Exchange", back_populates="reviews")
    reviewer = relationship(
        "User",
        foreign_keys=[reviewer_id],
        back_populates="given_reviews",
        lazy="selectin",
    )
    reviewed = relationship(
        "User",
        foreign_keys=[reviewed_id],
        back_populates="received_reviews",
        lazy="selectin",
    )

    def __str__(self):
        return f"<Review: {self.reviewer_id} to {self.reviewed_id} -- {self.rating}>"
