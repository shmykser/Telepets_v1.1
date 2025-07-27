from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db import get_db
from backend.models import Pet, PetState
from backend.config.settings import HEALTH_MAX, HEALTH_UP_AMOUNTS, STAGE_MESSAGES, HEALTH_MIN
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health_up", tags=["Pet"])

@router.post("")
async def health_up(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Увеличивает здоровье питомца в зависимости от его стадии.
    Для каждой стадии используется разная логика и сообщения.
    """
    # Находим питомца пользователя
    result = await db.execute(
        select(Pet).where(Pet.user_id == user_id, Pet.state != PetState.dead)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Питомец не найден или умер")
    
    # Проверяем, не умер ли питомец
    if pet.health <= HEALTH_MIN:
        raise HTTPException(status_code=400, detail="Питомец умер и не может быть вылечен")
    
    # Получаем количество увеличения здоровья для текущей стадии
    health_up_amount = HEALTH_UP_AMOUNTS.get(pet.state.value, 15)
    
    # Увеличиваем здоровье
    old_health = pet.health
    pet.health = min(HEALTH_MAX, pet.health + health_up_amount)
    
    # Получаем сообщение для текущей стадии
    stage_message = STAGE_MESSAGES.get(pet.state.value, {}).get('health_up', 'Здоровье увеличено')
    
    await db.commit()
    
    logger.info(f"Питомец {pet.name} (стадия: {pet.state.value}): здоровье {old_health} -> {pet.health}")
    
    return {
        "message": stage_message,
        "health": pet.health,
        "stage": pet.state.value
    } 