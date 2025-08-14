"""
Система аутентификации и авторизации для Telepets API.
Поддерживает простую аутентификацию по user_id для MVP.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models import Pet
import logging
from datetime import datetime, timedelta
import jwt
from typing import Optional

logger = logging.getLogger(__name__)

from config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Простая система безопасности для MVP

security = HTTPBearer()

class AuthService:
    """Сервис аутентификации"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Создает JWT токен"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str):
        """Проверяет JWT токен"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except jwt.PyJWTError:
            return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Получает текущего пользователя по токену"""
    token = credentials.credentials
    user_id = AuthService.verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, есть ли у пользователя питомец
    result = await db.execute(
        select(Pet).where(Pet.user_id == user_id).order_by(Pet.created_at.desc())
    )
    pet = result.scalars().first()
    
    return {
        "user_id": user_id,
        "has_pet": pet is not None,
        "pet_id": pet.id if pet else None
    }

async def require_user_with_pet(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Требует, чтобы у пользователя был питомец"""
    if not current_user["has_pet"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У вас нет питомца. Создайте питомца сначала."
        )
    return current_user

def create_user_token(user_id: str) -> str:
    """Создает токен для пользователя (для MVP)"""
    return AuthService.create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    ) 