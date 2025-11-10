from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from src.schemas.skills import (SkillCategory, SkillCreate, SkillLevel,
                                SkillResponse, SkillUpdate)
from temp_db import skills_db

router = APIRouter(prefix="/skills", tags=["Skills"])


# CREATE - Створення нової навички
@router.post("/", response_model=SkillResponse, status_code=201, tags=["Skills"])
async def create_skill(skill: SkillCreate):
    """
    Створити нову навичку.


    - **title**: назва навички (3-100 символів)
    - **description**: опис навички (10-500 символів)
    - **category**: категорія навички
    - **level**: рівень володіння
    - **can_teach**: чи можете навчати
    - **want_learn**: чи хочете вивчити
    """
    global skill_counter
    skill_counter += 1

    new_skill = {
        "id": skill_counter,
        **skill.model_dump(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    skills_db[skill_counter] = new_skill
    return new_skill


# READ - Отримання списку навичок з фільтрацією
@router.get("/", response_model=List[SkillResponse], tags=["Skills"])
async def get_skills(
    category: Optional[SkillCategory] = None,
    level: Optional[SkillLevel] = None,
    can_teach: Optional[bool] = None,
    want_learn: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    """
    Отримати список навичок з можливістю фільтрації.


    Фільтри:
    - **category**: фільтр за категорією
    - **level**: фільтр за рівнем
    - **can_teach**: показати тільки тих, хто може навчати
    - **want_learn**: показати тільки тих, хто хоче вчитися
    - **search**: пошук за назвою або описом
    """
    filtered_skills = list(skills_db.values())

    if category:
        filtered_skills = [s for s in filtered_skills if s["category"] == category]

    if level:
        filtered_skills = [s for s in filtered_skills if s["level"] == level]

    if can_teach is not None:
        filtered_skills = [s for s in filtered_skills if s["can_teach"] == can_teach]

    if want_learn is not None:
        filtered_skills = [s for s in filtered_skills if s["want_learn"] == want_learn]

    if search:
        search_lower = search.lower()
        filtered_skills = [
            s for s in filtered_skills if search_lower in s["title"].lower() or search_lower in s["description"].lower()
        ]

    # Сортуємо за датою створення (новіші зверху)
    filtered_skills.sort(key=lambda x: x["created_at"], reverse=True)

    # Пагінація
    total = len(filtered_skills)
    skills_page = filtered_skills[skip : skip + limit]

    return skills_page


# READ - Отримання однієї навички
@router.get("/{skill_id}", response_model=SkillResponse, tags=["Skills"])
async def get_skill(skill_id: int):
    """Отримати детальну інформацію про навичку за ID"""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail=f"Навичка з ID {skill_id} не знайдена")
    return skills_db[skill_id]


# UPDATE - Оновлення навички
@router.put("/{skill_id}", response_model=SkillResponse, tags=["Skills"])
async def update_skill(skill_id: int, skill_update: SkillUpdate):
    """Оновити існуючу навичку. Всі поля опціональні."""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail=f"Навичка з ID {skill_id} не знайдена")

    stored_skill = skills_db[skill_id]
    update_data = skill_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        stored_skill[field] = value

    stored_skill["updated_at"] = datetime.now()
    return stored_skill


# DELETE - Видалення навички
@router.delete("/{skill_id}", status_code=204, tags=["Skills"])
async def delete_skill(skill_id: int):
    """Видалити навичку за ID"""
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail=f"Навичка з ID {skill_id} не знайдена")

    del skills_db[skill_id]
    return None


# автоматичний пошук людей зі спільними інтересами
@router.get("/{skill_id}/matches", tags=["Skills"])
async def find_matches(skill_id: int):
    """
    Знайти потенційні збіги для обміну навичками.


    Повертає список користувачів, які:
    - Можуть навчити тому, що ви хочете вивчити
    - Хочуть вивчити те, що ви можете навчити
    """
    if skill_id not in skills_db:
        raise HTTPException(status_code=404, detail=f"Навичка з ID {skill_id} не знайдена")

    my_skill = skills_db[skill_id]
    matches = []

    for other_id, other_skill in skills_db.items():
        if other_id != skill_id:
            # Перевіряємо збіги за назвою та категорією
            same_skill = (
                my_skill["title"].lower() == other_skill["title"].lower()
                and my_skill["category"] == other_skill["category"]
            )

            if same_skill:
                # Я хочу вчитися, а хтось може навчити
                if my_skill["want_learn"] and other_skill["can_teach"]:
                    matches.append(
                        {
                            "match_type": "teacher",
                            "skill": other_skill,
                            "compatibility": "high",
                        }
                    )
                # Я можу навчити, а хтось хоче вчитися
                elif my_skill["can_teach"] and other_skill["want_learn"]:
                    matches.append(
                        {
                            "match_type": "student",
                            "skill": other_skill,
                            "compatibility": "high",
                        }
                    )

    return {
        "skill_id": skill_id,
        "my_skill": my_skill["title"],
        "matches_count": len(matches),
        "matches": matches,
    }
