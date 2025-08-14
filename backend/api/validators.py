"""
Валидаторы для API endpoints Telepets.
Обеспечивают проверку входных данных и безопасности.
"""

from pydantic import BaseModel, validator, Field
from typing import Optional
from config.settings import (
    USER_ID_MAX_LENGTH, USER_ID_MIN_LENGTH, 
    PET_NAME_MAX_LENGTH, PET_NAME_MIN_LENGTH,
    USER_ID_PATTERN, PET_NAME_PATTERN
)
import re

class CreatePetRequest(BaseModel):
    """Валидатор для создания питомца"""
    user_id: str = Field(..., min_length=USER_ID_MIN_LENGTH, max_length=USER_ID_MAX_LENGTH, description="ID пользователя")
    name: str = Field(..., min_length=PET_NAME_MIN_LENGTH, max_length=PET_NAME_MAX_LENGTH, description="Имя питомца")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Проверяет формат user_id"""
        if not re.match(USER_ID_PATTERN, v):
            raise ValueError('user_id может содержать только буквы, цифры, дефисы и подчеркивания')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Проверяет имя питомца"""
        if not re.match(PET_NAME_PATTERN, v):
            raise ValueError('Имя может содержать только буквы A-Z')
        return v.strip()

class HealthUpRequest(BaseModel):
    """Валидатор для увеличения здоровья"""
    user_id: str = Field(..., min_length=USER_ID_MIN_LENGTH, max_length=USER_ID_MAX_LENGTH, description="ID пользователя")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Проверяет формат user_id"""
        if not re.match(USER_ID_PATTERN, v):
            raise ValueError('user_id может содержать только буквы, цифры, дефисы и подчеркивания')
        return v

class SummaryRequest(BaseModel):
    """Валидатор для получения сводки"""
    user_id: str = Field(..., min_length=USER_ID_MIN_LENGTH, max_length=USER_ID_MAX_LENGTH, description="ID пользователя")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        """Проверяет формат user_id"""
        if not re.match(USER_ID_PATTERN, v):
            raise ValueError('user_id может содержать только буквы, цифры, дефисы и подчеркивания')
        return v

class PetResponse(BaseModel):
    """Схема ответа для питомца"""
    id: int
    user_id: str
    name: str
    state: str
    health: int
    status: Optional[str] = None
    next_stage: Optional[str] = None
    time_to_next_stage_seconds: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    total_pets: Optional[int] = None
    selected_pet_type: Optional[str] = None
    
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    """Схема ответа для ошибок"""
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None 