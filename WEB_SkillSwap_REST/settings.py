import os

import dotenv
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

dotenv.load_dotenv()


class DatabaseConfig:
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    SECRET_KEY = os.getenv("SECRET_KEY", "secret_key_123")
    # DB_URL_ALEMBIC = "sqlite:///async_alchemy.db"

    def uri_postgres(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@localhost:5432/{self.DATABASE_NAME}"

    def uri_sqlite(self):
        return f"sqlite+aiosqlite:///{self.DATABASE_NAME}.db"

    def alembic_uri(self):
        return f"sqlite:///{self.DATABASE_NAME}.db"

    def alembic_uri_postgres(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@localhost:5432/{self.DATABASE_NAME}"


api_config = DatabaseConfig()


# Налаштування бази даних Postgres
# engine = create_engine(config.uri_postgres(), echo=True)
async_engine: AsyncEngine = create_async_engine(api_config.uri_postgres(), echo=True)
async_session = async_sessionmaker(bind=async_engine)  # AsyncSession


# Декларація базового класу для моделей, Необхідно для реалізації відношень у ORM
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Dependency: сесія БД для FastAPI
async def get_db():
    async with async_session() as session:
        yield session
