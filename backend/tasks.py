from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db import AsyncSessionLocal
from backend.models import Pet, PetState, Notification
from backend.config.settings import (
    HEALTH_DOWN_INTERVALS, 
    HEALTH_DOWN_AMOUNTS, 
    HEALTH_LOW, 
    HEALTH_MIN,
    STAGE_TRANSITION_INTERVAL,
    STAGE_ORDER,
    STAGE_MESSAGES,
    TELEGRAM_MESSAGES
)
from backend.telegram_client import telegram_client
import asyncio
import logging
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def decrease_health_task():
    """
    Асинхронная задача для уменьшения здоровья питомцев в зависимости от стадии.
    Работает в фоновом режиме и учитывает разные интервалы для разных стадий.
    Также обрабатывает переходы между стадиями и смерть питомцев.
    Отправляет уведомления в Telegram при критических событиях.
    """
    logger.info("Запуск фоновой задачи уменьшения здоровья")
    
    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Получаем всех живых питомцев
                result = await db.execute(
                    select(Pet).where(Pet.state != PetState.dead)
                )
                pets = result.scalars().all()
                
                for pet in pets:
                    # Проверяем смерть питомца
                    if pet.health <= HEALTH_MIN:
                        # Сохраняем стадию до смерти для уведомления
                        stage_before_death = pet.state.value
                        
                        pet.state = PetState.dead
                        pet.health = 0
                        await db.commit()
                        
                        # Создаем уведомление о смерти в базе данных
                        notification = Notification(
                            user_id=pet.user_id,
                            type='death',
                            message=STAGE_MESSAGES[stage_before_death]['death']
                        )
                        db.add(notification)
                        await db.commit()
                        
                        # Отправляем уведомление в Telegram
                        await telegram_client.send_death_notification(
                            chat_id=pet.user_id,
                            pet_name=pet.name,
                            stage=stage_before_death
                        )
                        
                        logger.info(f"Питомец {pet.name} умер (стадия: {stage_before_death})")
                        continue
                    
                    # Уменьшаем здоровье в зависимости от стадии
                    decrease_amount = HEALTH_DOWN_AMOUNTS.get(pet.state.value, 5)
                    old_health = pet.health
                    pet.health = max(HEALTH_MIN, pet.health - decrease_amount)
                    
                    # Проверяем переход на новую стадию
                    current_time = datetime.utcnow()
                    time_since_creation = current_time - pet.created_at.replace(tzinfo=None)
                    
                    if (time_since_creation.total_seconds() >= STAGE_TRANSITION_INTERVAL and 
                        pet.health > HEALTH_MIN):
                        
                        # Находим следующую стадию
                        current_stage_index = STAGE_ORDER.index(pet.state.value)
                        if current_stage_index < len(STAGE_ORDER) - 1:
                            next_stage = STAGE_ORDER[current_stage_index + 1]
                            old_stage = pet.state.value
                            pet.state = PetState(next_stage)
                            
                            # Создаем уведомление о переходе в базе данных
                            notification = Notification(
                                user_id=pet.user_id,
                                type='stage_transition',
                                message=STAGE_MESSAGES[old_stage]['transition']
                            )
                            db.add(notification)
                            
                            # Отправляем уведомление в Telegram
                            await telegram_client.send_stage_transition_notification(
                                chat_id=pet.user_id,
                                pet_name=pet.name,
                                old_stage=old_stage,
                                new_stage=next_stage
                            )
                            
                            logger.info(f"Питомец {pet.name} перешел с {old_stage} на {next_stage}")
                    
                    # Проверяем низкое здоровье и отправляем уведомление
                    if pet.health <= HEALTH_LOW and old_health > HEALTH_LOW:
                        # Создаем уведомление в базе данных
                        notification = Notification(
                            user_id=pet.user_id,
                            type='low_health',
                            message=TELEGRAM_MESSAGES['low_health']
                        )
                        db.add(notification)
                        
                        # Отправляем уведомление в Telegram
                        await telegram_client.send_low_health_notification(
                            chat_id=pet.user_id,
                            pet_name=pet.name,
                            health=pet.health,
                            stage=pet.state.value
                        )
                        
                        logger.info(f"Отправлено уведомление о низком здоровье питомцу {pet.name}")
                    
                    logger.info(f"Питомец {pet.name} (стадия: {pet.state.value}): здоровье {old_health} -> {pet.health}")
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Ошибка в фоновой задаче: {e}")
        
        # Ждем 60 секунд перед следующей итерацией
        await asyncio.sleep(60)

async def start_health_decrease_task():
    """
    Запускает фоновую задачу по уменьшению здоровья питомцев.
    """
    logger.info("Инициализация фоновой задачи уменьшения здоровья")
    asyncio.create_task(decrease_health_task()) 