from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models import Pet, PetState
from config.settings import HEALTH_MAX
from economy import EconomyService
import logging
from prompt_store import generate_and_store_prompts
from services.stages import StageLifecycleService
from .validators import CreatePetRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/create", tags=["Pet"])

@router.post("")
async def create_pet(user_id: str, name: str, override: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Создает нового питомца для пользователя.
    Автоматически создает кошелек, если его нет.
    """
    try:
        # Валидация имени и user_id (строгая проверка английских букв)
        try:
            CreatePetRequest(user_id=user_id, name=name)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

        # Ищем всех живых питомцев
        result = await db.execute(
            select(Pet).where(Pet.user_id == user_id, Pet.state != PetState.dead)
        )
        alive_pets = result.scalars().all()

        # Правило: можно создать нового питомца, только если все живые питомцы уже adult
        non_adult_alive = [p for p in alive_pets if p.state != PetState.adult]
        if non_adult_alive:
            if override:
                # Заглушка платного оверрайда
                raise HTTPException(status_code=501, detail="Платное создание нового питомца при наличии не-взрослых пока не реализовано")
            raise HTTPException(status_code=400, detail="Создание нового питомца доступно только когда все живые питомцы уже взрослые")

        # Уникальность имени в рамках пользователя
        same_name = await db.execute(
            select(Pet).where(Pet.user_id == user_id, Pet.name == name)
        )
        if same_name.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Питомец с таким именем у вас уже существует")
        
        # Создаем кошелек для пользователя (если его нет)
        wallet = await EconomyService.create_user_wallet(db, user_id)
        
        # Создание нового питомца
        new_pet = Pet(user_id=user_id, name=name, state=PetState.egg, health=HEALTH_MAX)
        db.add(new_pet)
        await db.commit()
        await db.refresh(new_pet)

        # Подготовка стадий (сохранение creature_json и всех промтов в БД)
        try:
            await StageLifecycleService.prepare_on_create(db, user_id, name)
        except Exception as e:
            logger.warning(f"Подготовка стадий/изображения не удалась: {e}")
        
        # Проверяем достижение "Первый питомец"
        await EconomyService.check_achievement(
            db=db,
            user_id=user_id,
            achievement_type="first_pet",
            title="Первый питомец",
            description="Создал своего первого питомца!",
            coins_reward=50
        )
        
        # URL эндпоинта получения изображения (сервер отдаёт из БД и при отсутствии — генерирует и сохраняет)
        image_url = f"/pet-images/{user_id}/{name}"
        
        return {
            "id": new_pet.id,
            "user_id": new_pet.user_id,
            "name": new_pet.name,
            "state": new_pet.state.value,
            "health": new_pet.health,
            "image_url": image_url,
            "wallet": {
                "coins": wallet.coins,
                "total_earned": wallet.total_earned,
                "total_spent": wallet.total_spent
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания питомца: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания питомца") 