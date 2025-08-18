from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models import Pet, PetState, PetLifeStatus, User, Wallet
import logging
from datetime import datetime, timedelta
from config.settings import STAGE_TRANSITION_INTERVAL, STAGE_ORDER, HEALTH_MAX, INITIAL_COINS
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["Pet"])

def calculate_time_to_next_stage(current_stage: str, created_at: datetime, updated_at: datetime | None) -> int:
    """
    Рассчитывает время до следующей стадии в секундах.
    """
    try:
        # Находим индекс текущей стадии
        current_index = STAGE_ORDER.index(current_stage)
        
        # Если это последняя стадия, возвращаем 0
        if current_index >= len(STAGE_ORDER) - 1:
            return 0
        
        # От какого времени считать: начало текущей стадии = updated_at (если уже были апдейты) иначе created_at
        stage_started_at = updated_at or created_at
        # Рассчитываем время начала стадии + интервал перехода
        transition_time = stage_started_at + timedelta(seconds=STAGE_TRANSITION_INTERVAL)
        
        # Вычисляем оставшееся время
        now = datetime.utcnow()
        remaining_seconds = max(0, int((transition_time - now).total_seconds()))
        
        return remaining_seconds
    except Exception as e:
        logger.error(f"Ошибка расчета времени до следующей стадии: {e}")
        return 0

@router.get("")
async def get_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает информацию о питомце пользователя из базы данных.
    """
    try:
        # Получаем всех питомцев пользователя
        result = await db.execute(
            select(Pet).where(Pet.user_id == user_id).order_by(Pet.created_at.desc())
        )
        pets = result.scalars().all()
        
        # Если питомцев нет вообще
        if not pets:
            logger.info(f"Питомцы для пользователя {user_id} не найдены")
            
            # Получаем кошелек пользователя
            wallet_result = await db.execute(
                select(Wallet).where(Wallet.user_id == user_id)
            )
            wallet = wallet_result.scalar_one_or_none()
            
            return {
                "status": "no_pets",
                "message": "У вас пока нет питомцев. Создайте первого!",
                "user_id": user_id,
                "total_pets": 0,
                "alive_pets": 0,
                "dead_pets": 0,
                "wallet": {
                    "coins": wallet.coins if wallet else INITIAL_COINS,
                    "total_earned": wallet.total_earned if wallet else INITIAL_COINS,
                    "total_spent": wallet.total_spent if wallet else 0
                }
            }
        
        # Проверяем, есть ли живые питомцы
        alive_pets = [pet for pet in pets if pet.status == PetLifeStatus.alive]
        dead_pets = [pet for pet in pets if pet.status == PetLifeStatus.dead]
        
        # Если есть только мертвые питомцы
        if not alive_pets:
            logger.info(f"У пользователя {user_id} только мертвые питомцы")
            
            # Получаем кошелек пользователя
            wallet_result = await db.execute(
                select(Wallet).where(Wallet.user_id == user_id)
            )
            wallet = wallet_result.scalar_one_or_none()
            
            return {
                "status": "all_dead",
                "message": "Все ваши питомцы умерли. Создайте нового!",
                "user_id": user_id,
                "total_pets": len(pets),
                "alive_pets": 0,
                "dead_pets": len(dead_pets),
                "wallet": {
                    "coins": wallet.coins if wallet else INITIAL_COINS,
                    "total_earned": wallet.total_earned if wallet else INITIAL_COINS,
                    "total_spent": wallet.total_spent if wallet else 0
                }
            }
        
        # Берем самого нового живого питомца
        active_pet = alive_pets[0]
        
        # Получаем кошелек пользователя
        wallet_result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = wallet_result.scalar_one_or_none()
        
        # Рассчитываем время до следующей стадии
        time_to_next_stage = calculate_time_to_next_stage(
            active_pet.state.value,
            active_pet.created_at.replace(tzinfo=None),
            active_pet.updated_at.replace(tzinfo=None) if active_pet.updated_at else None,
        )
        
        # Определяем жизненный статус питомца
        life_status = active_pet.status.value
        
        # Определяем следующую стадию
        current_index = STAGE_ORDER.index(active_pet.state.value)
        next_stage = STAGE_ORDER[current_index + 1] if current_index < len(STAGE_ORDER) - 1 else active_pet.state.value
        
        # URL изображения (сервер сам сгенерирует при первом запросе)
        image_url = f"/pet-images/{active_pet.user_id}/{active_pet.name}"
        
        # Подготовка расширенных данных
        creature = None
        try:
            creature = json.loads(active_pet.creature_json) if active_pet.creature_json else None
        except Exception:
            creature = None

        prompts = {
            "egg_en": active_pet.prompt_egg_en,
            "baby_en": active_pet.prompt_baby_en,
            "adult_en": active_pet.prompt_adult_en,
        }

        return {
            "status": "success",
            "id": active_pet.id,
            "user_id": active_pet.user_id,
            "name": active_pet.name,
            "state": active_pet.state.value,
            "health": active_pet.health,
            "life_status": life_status,
            "next_stage": next_stage,
            "time_to_next_stage_seconds": time_to_next_stage,
            "image_url": image_url,
            "created_at": active_pet.created_at.isoformat() + "Z",
            "updated_at": active_pet.updated_at.isoformat() + "Z" if active_pet.updated_at else active_pet.created_at.isoformat() + "Z",
            "total_pets": len(pets),
            "alive_pets": len(alive_pets),
            "dead_pets": len(dead_pets),
            "selected_pet_type": "alive",
            "creature": creature,
            "prompts": prompts,
            "wallet": {
                "coins": wallet.coins if wallet else INITIAL_COINS,
                "total_earned": wallet.total_earned if wallet else INITIAL_COINS,
                "total_spent": wallet.total_spent if wallet else 0
            }
        }
    except Exception as e:
        logger.error(f"Ошибка получения питомца: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения питомца")

@router.get("/all")
async def get_all_pets_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает сводку всех питомцев пользователя из базы данных.
    """
    try:
        # Получаем всех питомцев пользователя
        result = await db.execute(
            select(Pet).where(Pet.user_id == user_id).order_by(Pet.created_at.desc())
        )
        pets = result.scalars().all()
        
        # Получаем кошелек пользователя
        wallet_result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = wallet_result.scalar_one_or_none()
        
        # Если питомцев нет
        if not pets:
            logger.info(f"Питомцы для пользователя {user_id} не найдены")
            return {
                "status": "no_pets",
                "message": "У вас пока нет питомцев. Создайте первого!",
                "user_id": user_id,
                "pets": [],
                "total_pets": 0,
                "alive_pets": 0,
                "dead_pets": 0,
                "wallet": {
                    "coins": INITIAL_COINS,
                    "total_earned": INITIAL_COINS,
                    "total_spent": 0
                }
            }
        
        # Формируем список питомцев
        pets_data = []
        alive_pets = 0
        dead_pets = 0
        
        for pet in pets:
            status = pet.status.value
            if pet.status == PetLifeStatus.alive:
                alive_pets += 1
            else:
                dead_pets += 1
                
            # Расширенные данные для каждого питомца
            try:
                creature = json.loads(pet.creature_json) if pet.creature_json else None
            except Exception:
                creature = None
            prompts = {
                "egg_en": pet.prompt_egg_en,
                "baby_en": pet.prompt_baby_en,
                "adult_en": pet.prompt_adult_en,
            }

            # Рассчитываем таймер перехода стадии для каждого питомца (0 для последней стадии и мёртвых)
            try:
                time_to_next_stage = calculate_time_to_next_stage(
                    pet.state.value,
                    pet.created_at.replace(tzinfo=None),
                    pet.updated_at.replace(tzinfo=None) if pet.updated_at else None,
                ) if pet.status == PetLifeStatus.alive else 0
            except Exception:
                time_to_next_stage = 0

            pets_data.append({
                "id": pet.id,
                "name": pet.name,
                "state": pet.state.value,
                "health": pet.health,
                "status": status,
                "time_to_next_stage_seconds": time_to_next_stage,
                "created_at": pet.created_at.isoformat() + "Z",
                "updated_at": pet.updated_at.isoformat() + "Z" if pet.updated_at else pet.created_at.isoformat() + "Z",
                "creature": creature,
                "prompts": prompts,
            })
        
        # Проверяем, есть ли живые питомцы
        if alive_pets == 0:
            return {
                "status": "all_dead",
                "message": "Все ваши питомцы умерли. Создайте нового!",
                "user_id": user_id,
                "pets": pets_data,
                "total_pets": len(pets),
                "alive_pets": alive_pets,
                "dead_pets": dead_pets,
                "wallet": {
                    "coins": wallet.coins if wallet else INITIAL_COINS,
                    "total_earned": wallet.total_earned if wallet else INITIAL_COINS,
                    "total_spent": wallet.total_spent if wallet else 0
                }
            }
        
        return {
            "status": "success",
            "user_id": user_id,
            "pets": pets_data,
            "total_pets": len(pets),
            "alive_pets": alive_pets,
            "dead_pets": dead_pets,
            "wallet": {
                "coins": wallet.coins if wallet else INITIAL_COINS,
                "total_earned": wallet.total_earned if wallet else INITIAL_COINS,
                "total_spent": wallet.total_spent if wallet else 0
            }
        }
    except Exception as e:
        logger.error(f"Ошибка получения сводки питомцев: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения сводки питомцев") 