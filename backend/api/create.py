from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models import Pet, PetState
from config.settings import HEALTH_MAX, NEW_PET_PAID_CREATION_COST
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

        # Логика оплаты: если есть живые и среди них есть не-adult → создание платное
        non_adult_alive = [p for p in alive_pets if p.state != PetState.adult]
        is_paid_creation_required = len(alive_pets) > 0 and len(non_adult_alive) > 0

        # Уникальность имени в рамках пользователя
        same_name = await db.execute(
            select(Pet).where(Pet.user_id == user_id, Pet.name == name)
        )
        if same_name.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Питомец с таким именем у вас уже существует")
        
        # Создаем кошелек для пользователя (если его нет)
        wallet = await EconomyService.create_user_wallet(db, user_id)

        # Если требуется платное создание — списываем монеты
        if is_paid_creation_required:
            # Проверяем достаточность средств
            if wallet.coins < NEW_PET_PAID_CREATION_COST:
                raise HTTPException(status_code=400, detail=f"Недостаточно монет для создания питомца. Требуется: {NEW_PET_PAID_CREATION_COST}, доступно: {wallet.coins}")
            spent = await EconomyService.spend_coins(
                db=db,
                user_id=user_id,
                amount=NEW_PET_PAID_CREATION_COST,
                description=f"Платное создание нового питомца ({name})",
                transaction_data={"action": "create_pet", "pet_name": name}
            )
            if not spent:
                raise HTTPException(status_code=500, detail="Не удалось списать монеты за создание питомца")
        
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
            },
            "paid": is_paid_creation_required,
            "paid_cost": NEW_PET_PAID_CREATION_COST if is_paid_creation_required else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания питомца: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания питомца") 