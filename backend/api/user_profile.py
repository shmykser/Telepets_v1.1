"""
API для управления профилем пользователя и настройками анонимности.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from db import get_db
from auth import get_current_user
from services.user_profile import UserProfileService
from config.settings import ANONYMOUS_MODE_ENABLED
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["User Profile"])


class UserProfileResponse(BaseModel):
    """Ответ с профилем пользователя"""
    user_id: str
    telegram_username: Optional[str]
    display_name: Optional[str]
    is_anonymous: bool
    first_name: Optional[str]
    last_name: Optional[str]
    public_name: str
    created_at: str
    updated_at: Optional[str]


class UpdateProfileRequest(BaseModel):
    """Запрос на обновление профиля"""
    is_anonymous: Optional[bool] = Field(None, description="Переключатель анонимности")
    display_name: Optional[str] = Field(None, min_length=2, max_length=20, description="Кастомное имя для отображения")


class PublicUserInfoResponse(BaseModel):
    """Публичная информация о пользователе"""
    user_id: str
    public_name: str
    is_anonymous: bool


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получает профиль текущего пользователя"""
    try:
        profile = await UserProfileService.get_user_profile(db, current_user["user_id"])
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль пользователя не найден"
            )
        
        return profile
        
    except Exception as e:
        logger.error(f"Ошибка получения профиля пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения профиля"
        )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновляет настройки профиля пользователя"""
    try:
        # Если анонимность отключена — запрещаем менять связанные поля
        if not ANONYMOUS_MODE_ENABLED:
            return await UserProfileService.get_user_profile(db, current_user["user_id"])  # no-op
        profile = await UserProfileService.update_user_profile(
            db=db,
            user_id=current_user["user_id"],
            is_anonymous=request.is_anonymous,
            display_name=request.display_name
        )
        
        if not profile:
            # Попробуем отдать актуальный профиль, если апдейт не вернул данных (например, no-op)
            fallback = await UserProfileService.get_user_profile(db, current_user["user_id"])
            if fallback:
                return fallback
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Профиль пользователя не найден"
            )
        
        return profile
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка обновления профиля пользователя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления профиля"
        )


@router.get("/{user_id}/public", response_model=PublicUserInfoResponse)
async def get_public_user_info(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получает публичную информацию о пользователе (с учетом анонимности)"""
    try:
        public_info = await UserProfileService.get_public_user_info(db, user_id)
        # Если анонимность отключена — принудительно выставляем is_anonymous=false
        if public_info and not ANONYMOUS_MODE_ENABLED:
            public_info["is_anonymous"] = False
        
        if not public_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        return public_info
        
    except Exception as e:
        logger.error(f"Ошибка получения публичной информации о пользователе: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения информации о пользователе"
        )
