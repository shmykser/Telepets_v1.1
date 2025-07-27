from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from backend.db import get_db
from backend.models import Pet, PetState
from backend.config.settings import STAGE_TRANSITION_INTERVAL, STAGE_ORDER, HEALTH_MIN
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["Pet"])

@router.get("")
async def get_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает сводку о питомце пользователя.
    Включает информацию о здоровье, стадии и времени до следующего перехода.
    Если у пользователя несколько питомцев, возвращает самого последнего живого
    или самого последнего мертвого, если живых нет.
    """
    # Находим всех питомцев пользователя, отсортированных по времени создания
    result = await db.execute(
        select(Pet)
        .where(Pet.user_id == user_id)
        .order_by(desc(Pet.created_at))
    )
    pets = result.scalars().all()
    
    if not pets:
        raise HTTPException(status_code=404, detail="Питомец не найден")
    
    # Выбираем питомца: сначала ищем живого, если нет - берем последнего мертвого
    pet = None
    for p in pets:
        if p.state != PetState.dead:
            pet = p
            break
    
    # Если живых нет, берем последнего мертвого
    if pet is None:
        pet = pets[0]  # Самый последний (первый в отсортированном списке)
    
    # Вычисляем время до следующей стадии
    current_time = datetime.utcnow()
    time_since_creation = current_time - pet.created_at.replace(tzinfo=None)
    time_to_next_stage = None
    next_stage = None
    
    if pet.state != PetState.dead and pet.health > HEALTH_MIN:
        current_stage_index = STAGE_ORDER.index(pet.state.value)
        if current_stage_index < len(STAGE_ORDER) - 1:
            next_stage = STAGE_ORDER[current_stage_index + 1]
            time_elapsed = time_since_creation.total_seconds()
            if time_elapsed < STAGE_TRANSITION_INTERVAL:
                time_to_next_stage = STAGE_TRANSITION_INTERVAL - time_elapsed
            else:
                time_to_next_stage = 0
    
    # Определяем статус питомца
    status = "alive"
    if pet.state == PetState.dead:
        status = "dead"
    elif pet.health <= HEALTH_MIN:
        status = "dying"
    
    return {
        "id": pet.id,
        "user_id": pet.user_id,
        "name": pet.name,
        "state": pet.state.value,
        "health": pet.health,
        "status": status,
        "next_stage": next_stage,
        "time_to_next_stage_seconds": time_to_next_stage,
        "created_at": pet.created_at,
        "updated_at": pet.updated_at,
        "total_pets": len(pets),  # Добавляем информацию о количестве питомцев
        "selected_pet_type": "alive" if pet.state != PetState.dead else "dead"
    }

@router.get("/all")
async def get_all_pets(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает список всех питомцев пользователя.
    Полезно для отладки и анализа истории питомцев.
    """
    # Находим всех питомцев пользователя, отсортированных по времени создания
    result = await db.execute(
        select(Pet)
        .where(Pet.user_id == user_id)
        .order_by(desc(Pet.created_at))
    )
    pets = result.scalars().all()
    
    if not pets:
        raise HTTPException(status_code=404, detail="Питомцы не найдены")
    
    pets_data = []
    for pet in pets:
        # Определяем статус питомца
        status = "alive"
        if pet.state == PetState.dead:
            status = "dead"
        elif pet.health <= HEALTH_MIN:
            status = "dying"
        
        pets_data.append({
            "id": pet.id,
            "user_id": pet.user_id,
            "name": pet.name,
            "state": pet.state.value,
            "health": pet.health,
            "status": status,
            "created_at": pet.created_at,
            "updated_at": pet.updated_at
        })
    
    return {
        "user_id": user_id,
        "total_pets": len(pets),
        "alive_pets": len([p for p in pets if p.state != PetState.dead]),
        "dead_pets": len([p for p in pets if p.state == PetState.dead]),
        "pets": pets_data
    } 