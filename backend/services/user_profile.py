"""
Сервис для управления профилем пользователя и настройками анонимности.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models import User
from config.settings import MIN_DISPLAY_NAME_LENGTH, MAX_DISPLAY_NAME_LENGTH, ANONYMOUS_MODE_ENABLED
import logging
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)


class UserProfileService:
    """Сервис для управления профилем пользователя"""
    
    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: str) -> Optional[Dict[str, Any]]:
        """Получает профиль пользователя"""
        try:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
                
            return {
                "user_id": user.user_id,
                "telegram_username": user.telegram_username,
                "display_name": user.display_name,
                "is_anonymous": user.is_anonymous,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "public_name": user.public_name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения профиля пользователя {user_id}: {e}")
            return None
    
    @staticmethod
    async def get_public_user_info(db: AsyncSession, user_id: str) -> Optional[Dict[str, Any]]:
        """Получает публичную информацию о пользователе (с учетом анонимности)"""
        try:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
                
            is_anon = user.is_anonymous if ANONYMOUS_MODE_ENABLED else False
            return {
                "user_id": user.user_id,
                "public_name": user.public_name,
                "is_anonymous": is_anon
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения публичной информации о пользователе {user_id}: {e}")
            return None
    
    @staticmethod
    async def update_user_profile(
        db: AsyncSession, 
        user_id: str, 
        is_anonymous: Optional[bool] = None,
        display_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Обновляет настройки профиля пользователя"""
        try:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Валидация display_name
            if display_name is not None:
                if not UserProfileService._validate_display_name(display_name):
                    raise ValueError(f"Недопустимое имя. Длина должна быть от {MIN_DISPLAY_NAME_LENGTH} до {MAX_DISPLAY_NAME_LENGTH} символов, только буквы, цифры и пробелы.")
                
                # Если включаем анонимность, display_name обязателен
                if is_anonymous and not display_name.strip():
                    raise ValueError("При включении анонимности необходимо указать отображаемое имя")
            
            # Обновляем поля
            if is_anonymous is not None:
                user.is_anonymous = is_anonymous
                # Если анонимность выключают — очищаем display_name, чтобы не хранить устаревшее значение
                if not is_anonymous:
                    user.display_name = None
            
            # Явное обновление display_name, если поле передано (включая пустую строку → очистка)
            if display_name is not None:
                user.display_name = display_name.strip() if display_name else None
            
            # Обновляем время изменения
            user.updated_at = func.now()
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Обновлен профиль пользователя {user_id}: анонимность={user.is_anonymous}, display_name={user.display_name}")
            # Возвращаем полную актуальную структуру профиля, как в GET
            return await UserProfileService.get_user_profile(db, user_id)
            
        except ValueError as e:
            logger.warning(f"Валидация профиля пользователя {user_id} не пройдена: {e}")
            raise e
        except Exception as e:
            logger.error(f"Ошибка обновления профиля пользователя {user_id}: {e}")
            await db.rollback()
            return None
    
    @staticmethod
    async def set_telegram_username(db: AsyncSession, user_id: str, telegram_username: str) -> bool:
        """Устанавливает telegram_username для пользователя"""
        try:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.telegram_username = telegram_username
            user.updated_at = func.now()
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Установлен telegram_username для пользователя {user_id}: {telegram_username}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки telegram_username для пользователя {user_id}: {e}")
            await db.rollback()
            return False
    
    @staticmethod
    def _validate_display_name(display_name: str) -> bool:
        """Валидирует отображаемое имя пользователя"""
        if not display_name or not display_name.strip():
            return False
            
        name = display_name.strip()
        
        # Проверяем длину
        if len(name) < MIN_DISPLAY_NAME_LENGTH or len(name) > MAX_DISPLAY_NAME_LENGTH:
            return False
        
        # Проверяем допустимые символы (буквы, цифры, пробелы, дефисы, подчеркивания)
        if not re.match(r'^[a-zA-Zа-яА-Я0-9\s\-_]+$', name):
            return False
        
        # Проверяем что имя не состоит только из пробелов
        if not name.replace(' ', ''):
            return False
            
        return True
