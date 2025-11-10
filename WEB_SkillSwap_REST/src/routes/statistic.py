from fastapi import APIRouter

from temp_db import skill_counter, skills_db

router = APIRouter(prefix="/skills/statistic", tags=["Statistics"])


@router.get("/stats/categories")
async def get_category_stats():
    """Отримати статистику навичок по категоріях"""
    stats = {}

    for skill in skills_db.values():
        category = skill["category"]
        if category not in stats:
            stats[category] = {"total": 0, "can_teach": 0, "want_learn": 0}

        stats[category]["total"] += 1
        if skill["can_teach"]:
            stats[category]["can_teach"] += 1
        if skill["want_learn"]:
            stats[category]["want_learn"] += 1

    return {"total_skills": len(skills_db), "categories": stats}
