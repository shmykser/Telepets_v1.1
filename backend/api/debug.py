from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db, engine, init_db
from sqlalchemy import text
from sqlalchemy.future import select
from models import Pet, User, Wallet
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/test")
async def test_api():
    """
    Простой тест API без базы данных.
    """
    return {
        "status": "success",
        "message": "API работает",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.get("/db-test")
async def test_database(db: AsyncSession = Depends(get_db)):
    """
    Тестирует подключение к базе данных и проверяет таблицы.
    """
    try:
        # Проверяем подключение
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        
        # Проверяем таблицы
        result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        
        return {
            "status": "success",
            "message": "База данных работает",
            "tables": [table[0] for table in tables],
            "table_count": len(tables)
        }
    except Exception as e:
        logger.error(f"Ошибка тестирования базы данных: {e}")
        return {
            "status": "error",
            "message": f"Ошибка базы данных: {str(e)}",
            "tables": [],
            "table_count": 0
        }

@router.get("/init-db")
async def initialize_database():
    """
    Инициализирует базу данных и создает таблицы.
    """
    try:
        await init_db()
        return {
            "status": "success",
            "message": "База данных инициализирована",
            "tables_created": True
        }
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        return {
            "status": "error",
            "message": f"Ошибка инициализации: {str(e)}",
            "tables_created": False
        }

@router.get("/pets")
async def get_all_pets(db: AsyncSession = Depends(get_db)):
    """
    Показывает всех питомцев в базе данных.
    """
    try:
        # Получаем всех питомцев
        result = await db.execute(select(Pet))
        pets = result.scalars().all()
        
        pets_data = []
        for pet in pets:
            pets_data.append({
                "id": pet.id,
                "user_id": pet.user_id,
                "name": pet.name,
                "state": pet.state.value,
                "health": pet.health,
                "created_at": pet.created_at.isoformat() + "Z",
                "updated_at": pet.updated_at.isoformat() + "Z" if pet.updated_at else None
            })
        
        return {
            "status": "success",
            "total_pets": len(pets),
            "pets": pets_data
        }
    except Exception as e:
        logger.error(f"Ошибка получения питомцев: {e}")
        return {
            "status": "error",
            "message": f"Ошибка получения питомцев: {str(e)}",
            "total_pets": 0,
            "pets": []
        }

@router.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """
    Показывает всех пользователей в базе данных.
    """
    try:
        # Получаем всех пользователей
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "user_id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat() + "Z"
            })
        
        return {
            "status": "success",
            "total_users": len(users),
            "users": users_data
        }
    except Exception as e:
        logger.error(f"Ошибка получения пользователей: {e}")
        return {
            "status": "error",
            "message": f"Ошибка получения пользователей: {str(e)}",
            "total_users": 0,
            "users": []
        }

@router.get("/wallets")
async def get_all_wallets(db: AsyncSession = Depends(get_db)):
    """
    Показывает все кошельки в базе данных.
    """
    try:
        # Получаем все кошельки
        result = await db.execute(select(Wallet))
        wallets = result.scalars().all()
        
        wallets_data = []
        for wallet in wallets:
            wallets_data.append({
                "id": wallet.id,
                "user_id": wallet.user_id,
                "coins": wallet.coins,
                "total_earned": wallet.total_earned,
                "total_spent": wallet.total_spent,
                "created_at": wallet.created_at.isoformat() + "Z"
            })
        
        return {
            "status": "success",
            "total_wallets": len(wallets),
            "wallets": wallets_data
        }
    except Exception as e:
        logger.error(f"Ошибка получения кошельков: {e}")
        return {
            "status": "error",
            "message": f"Ошибка получения кошельков: {str(e)}",
            "total_wallets": 0,
            "wallets": []
        } 

@router.post("/create-test-pet-with-logging")
async def create_test_pet_with_logging(db: AsyncSession = Depends(get_db)):
    """
    Создает тестового питомца с подробным логированием.
    """
    try:
        from datetime import datetime, timedelta
        from config.settings import HEALTH_MAX
        from models import PetState, User, Wallet
        
        user_id = "273065571"
        name = "Тестовый питомец"
        
        print(f"🔍 Начинаем создание питомца для пользователя {user_id}")
        
        # Проверяем существующих питомцев
        result = await db.execute(
            select(Pet).where(Pet.user_id == user_id)
        )
        existing_pets = result.scalars().all()
        print(f"🔍 Найдено существующих питомцев: {len(existing_pets)}")
        
        # Проверяем пользователя
        user_result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()
        print(f"🔍 Пользователь найден: {user is not None}")
        
        # Проверяем кошелек
        wallet_result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = wallet_result.scalar_one_or_none()
        print(f"🔍 Кошелек найден: {wallet is not None}")
        if wallet:
            print(f"🔍 Баланс кошелька: {wallet.coins}")
        
        # Создаем питомца
        print("🔍 Создаем нового питомца...")
        pet = Pet(
            user_id=user_id,
            name=name,
            state=PetState.egg,
            health=HEALTH_MAX
        )
        
        print("🔍 Добавляем питомца в сессию...")
        db.add(pet)
        
        print("🔍 Коммитим изменения...")
        await db.commit()
        
        print("🔍 Обновляем объект питомца...")
        await db.refresh(pet)
        
        print(f"🔍 Питомец создан с ID: {pet.id}")
        
        return {
            "status": "success",
            "message": "Тестовый питомец создан с логированием",
            "pet": {
                "id": pet.id,
                "user_id": pet.user_id,
                "name": pet.name,
                "state": pet.state.value,
                "health": pet.health,
                "created_at": pet.created_at.isoformat() + "Z"
            }
        }
    except Exception as e:
        print(f"❌ Ошибка создания питомца: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Ошибка создания питомца: {str(e)}"
        } 