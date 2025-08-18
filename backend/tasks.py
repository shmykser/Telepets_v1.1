from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import AsyncSessionLocal
from models import Pet, PetState, PetLifeStatus, Notification
from services.stages import StageLifecycleService
from config.settings import (
    HEALTH_DOWN_INTERVALS, 
    HEALTH_DOWN_AMOUNTS, 
    HEALTH_LOW, 
    HEALTH_MIN,
    STAGE_TRANSITION_INTERVAL,
    STAGE_ORDER,
    STAGE_MESSAGES,
    TELEGRAM_MESSAGES,
    TASK_SLEEP_INTERVAL,
    ACHIEVEMENT_CHECK_INTERVALS,
)
from telegram_client import telegram_client
from economy import EconomyService
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
                    select(Pet).where(Pet.status == PetLifeStatus.alive)
                )
                pets = result.scalars().all()
                
                for pet in pets:
                    try:
                        # Получаем интервал и количество уменьшения для текущей стадии
                        interval = HEALTH_DOWN_INTERVALS.get(pet.state.value, 60)
                        decrease_amount = HEALTH_DOWN_AMOUNTS.get(pet.state.value, 5)
                        
                        # Уменьшаем здоровье
                        old_health = pet.health
                        pet.health = max(HEALTH_MIN, pet.health - decrease_amount)
                        
                        # Проверяем смерть питомца
                        if pet.health <= HEALTH_MIN:
                            stage_before_death = pet.state.value
                            pet.status = PetLifeStatus.dead
                            # фиксируем момент окончания жизненного цикла
                            pet.updated_at = datetime.utcnow()
                            
                            # Создаем уведомление о смерти
                            death_message = STAGE_MESSAGES.get(stage_before_death, {}).get('death', 'Питомец умер')
                            notification = Notification(
                                user_id=pet.user_id,
                                type='death',
                                message=death_message
                            )
                            db.add(notification)
                            
                            # Отправляем уведомление в Telegram
                            await telegram_client.send_death_notification(
                                user_id=pet.user_id,
                                pet_name=pet.name,
                                stage=stage_before_death
                            )
                            
                            logger.info(f"Питомец {pet.name} умер на стадии {stage_before_death}")
                            # Стираем изображения из БД при смерти
                            try:
                                await StageLifecycleService.wipe_images_on_death(db, pet)
                            except Exception:
                                pass
                        
                        # Проверяем низкое здоровье
                        elif pet.health <= HEALTH_LOW:
                            # Создаем уведомление о низком здоровье
                            from config.settings import HEALTH_MAX
                            low_health_message = f"Здоровье питомца {pet.name} критически низкое: {pet.health}/{HEALTH_MAX}"
                            notification = Notification(
                                user_id=pet.user_id,
                                type='low_health',
                                message=low_health_message
                            )
                            db.add(notification)
                            
                            # Отправляем уведомление в Telegram
                            await telegram_client.send_low_health_notification(
                                user_id=pet.user_id,
                                pet_name=pet.name,
                                stage=pet.state.value,
                                health=pet.health
                            )
                        
                        # Проверяем переход на следующую стадию
                        current_time = datetime.utcnow()
                        # Используем момент начала текущей стадии: updated_at (если было изменение стадии)
                        stage_started_at = (pet.updated_at or pet.created_at)
                        stage_started_at_naive = stage_started_at.replace(tzinfo=None)
                        time_since_stage_start = current_time - stage_started_at_naive
                        
                        if (
                            pet.status == PetLifeStatus.alive and 
                            pet.health > HEALTH_MIN and 
                            time_since_stage_start.total_seconds() >= STAGE_TRANSITION_INTERVAL
                        ):
                            
                            current_stage_index = STAGE_ORDER.index(pet.state.value)
                            if current_stage_index < len(STAGE_ORDER) - 1:
                                old_stage = pet.state.value
                                new_stage = STAGE_ORDER[current_stage_index + 1]
                                pet.state = PetState(new_stage)
                                # фиксируем момент начала новой стадии (для корректного таймера)
                                pet.updated_at = datetime.utcnow()
                                # Фиксируем смену стадии сразу, чтобы другие запросы видели актуальное состояние
                                await db.commit()
                                
                                # Создаем уведомление о переходе
                                transition_message = STAGE_MESSAGES.get(old_stage, {}).get('transition', f'Питомец перешел с {old_stage} на {new_stage}')
                                notification = Notification(
                                    user_id=pet.user_id,
                                    type='stage_transition',
                                    message=transition_message
                                )
                                db.add(notification)
                                
                                # Отправляем уведомление в Telegram
                                await telegram_client.send_stage_transition_notification(
                                    user_id=pet.user_id,
                                    pet_name=pet.name,
                                    old_stage=old_stage,
                                    new_stage=new_stage
                                )
                                
                                # Начисление монет за переход стадии удалено по требованиям

                                # Проверяем достижения
                                await check_pet_achievements(db, pet.user_id, pet)
                                
                                logger.info(f"Питомец {pet.name} перешел с {old_stage} на {new_stage}")
                                # Генерация и сохранение артефактов для новой стадии
                                try:
                                    # Берем промпт из БД как источник истины
                                    prompt_en_db = None
                                    try:
                                        prompt_en_db = StageLifecycleService._get_prompt_from_db_sync(pet.user_id, pet.name, new_stage)
                                    except Exception:
                                        prompt_en_db = None

                                    image_path, metadata = StageLifecycleService.get_or_generate_image(
                                        pet.user_id, pet.name, new_stage, pet.health
                                    )
                                    await StageLifecycleService.persist_stage_artifacts(
                                        db, pet.user_id, pet.name, new_stage, prompt_en_db, image_path
                                    )
                                except Exception:
                                    pass
                        
                        logger.debug(f"Питомец {pet.name}: здоровье {old_health} -> {pet.health}")
                        
                    except Exception as e:
                        logger.error(f"Ошибка обработки питомца {pet.id}: {e}")
                        continue
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Ошибка в фоновой задаче: {e}")
        
        # Ждем 1 минуту перед следующей итерацией
        await asyncio.sleep(TASK_SLEEP_INTERVAL)

async def check_pet_achievements(db: AsyncSession, user_id: str, pet: Pet):
    """Проверяет достижения питомца"""
    try:
        current_time = datetime.utcnow()
        time_since_creation = current_time - pet.created_at.replace(tzinfo=None)
        
        # Достижение за выживание 1 час
        if time_since_creation.total_seconds() >= ACHIEVEMENT_CHECK_INTERVALS['hour']:  # 1 час
            await EconomyService.check_achievement(
                db=db,
                user_id=user_id,
                achievement_type="pet_survived_1_hour",
                title="Выживший",
                description="Питомец прожил 1 час!",
                coins_reward=25
            )
        
        # Достижение за выживание 1 день
        if time_since_creation.total_seconds() >= ACHIEVEMENT_CHECK_INTERVALS['day']:  # 1 день
            await EconomyService.check_achievement(
                db=db,
                user_id=user_id,
                achievement_type="pet_survived_1_day",
                title="Долгожитель",
                description="Питомец прожил 1 день!",
                coins_reward=100
            )
        
        # Достижение за достижение взрослого возраста
        if pet.state == PetState.adult:
            await EconomyService.check_achievement(
                db=db,
                user_id=user_id,
                achievement_type="pet_reached_adult",
                title="Взрослый",
                description="Питомец достиг взрослого возраста!",
                coins_reward=200
            )
        
        # Достижение за идеальное здоровье
        if pet.health >= HEALTH_MAX:
            await EconomyService.check_achievement(
                db=db,
                user_id=user_id,
                achievement_type="perfect_health",
                title="Идеальное здоровье",
                description="Питомец имеет идеальное здоровье!",
                coins_reward=50
            )
            
    except Exception as e:
        logger.error(f"Ошибка проверки достижений: {e}")

async def start_health_decrease_task():
    """Запускает фоновую задачу уменьшения здоровья"""
    asyncio.create_task(decrease_health_task()) 