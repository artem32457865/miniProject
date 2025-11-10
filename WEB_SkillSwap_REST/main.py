from datetime import datetime

import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from settings import get_db
from src.routes import skills, statistic

# Створюємо екземпляр FastAPI з метаданими
app = FastAPI(
    title="SkillSwap API",
    description="API для платформи обміну навичками між підлітками",
    version="1.0.0",
    contact={"name": "SkillSwap Team", "email": "support@skillswap.com"},
)

app.include_router(skills.router)
app.include_router(statistic.router)


@app.get("/", tags=["General"])
def read_root():
    """Головна сторінка API з інформацією про доступні endpoints"""
    return {
        "message": "Ласкаво просимо до SkillSwap API!",
        "description": "Платформа для обміну навичками",
        "version": "1.0.0",
        "endpoints": {"documentation": "/docs", "skills": "/skills", "health": "/health"},
    }


@app.get("/health", tags=["General"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Перевірка стану сервера"""
    try:
        res = await db.execute(text("SELECT 1"))
        db_status = "connected" if res else "not connected"
    except Exception as e:
        db_status = f"not connected: error: {str(e)}"

    return {
        "status": "healthy",
        "database": {
            "status": db_status,
            "timestamp": datetime.now().isoformat(),
        },
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", port=8000, reload=True)
