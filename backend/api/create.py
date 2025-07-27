from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db import get_db
from backend.models import Pet, PetState
from backend.config.settings import HEALTH_MAX

router = APIRouter(prefix="/create", tags=["Pet"])

@router.post("")
async def create_pet(user_id: str, name: str, db: AsyncSession = Depends(get_db)):
    # Проверка на существующего живого питомца
    result = await db.execute(select(Pet).where(Pet.user_id == user_id, Pet.state != PetState.dead))
    existing_pet = result.scalars().first()
    if existing_pet:
        raise HTTPException(status_code=400, detail="У вас уже есть живой питомец.")
    # Создание нового питомца
    new_pet = Pet(user_id=user_id, name=name, state=PetState.egg, health=HEALTH_MAX)
    db.add(new_pet)
    await db.commit()
    await db.refresh(new_pet)
    return {
        "id": new_pet.id,
        "user_id": new_pet.user_id,
        "name": new_pet.name,
        "state": new_pet.state.value,
        "health": new_pet.health
    } 