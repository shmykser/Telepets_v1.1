"""
API endpoints для экономики Telepets.
Управляет кошельками, транзакциями и покупками.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models import Pet, PetState, PetLifeStatus, User, Wallet, Transaction
from economy import EconomyService
from config.settings import ACTION_COSTS, PURCHASE_OPTIONS, GAME_REWARD_ALLOWED_GAMES, GAME_REWARD_COINS_PER_SCORE, GAME_REWARD_MAX_PER_REQUEST
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/economy", tags=["Economy"])

@router.get("/wallet/{user_id}")
async def get_wallet(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает информацию о кошельке пользователя.
    Создает кошелек, если его нет.
    """
    try:
        # Создаем кошелек, если его нет
        wallet = await EconomyService.create_user_wallet(db, user_id)
        
        return {
            "user_id": user_id,
            "coins": wallet.coins,
            "total_earned": wallet.total_earned,
            "total_spent": wallet.total_spent,
            "created_at": wallet.created_at,
            "updated_at": wallet.updated_at
        }
    except Exception as e:
        logger.error(f"Ошибка получения кошелька: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения кошелька")

@router.get("/balance/{user_id}")
async def get_balance(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает текущий баланс пользователя.
    """
    try:
        balance = await EconomyService.get_balance(db, user_id)
        return {
            "user_id": user_id,
            "coins": balance
        }
    except Exception as e:
        logger.error(f"Ошибка получения баланса: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения баланса")

@router.get("/transactions/{user_id}")
async def get_transactions(
    user_id: str, 
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Получает историю транзакций пользователя.
    """
    try:
        transactions = await EconomyService.get_transaction_history(db, user_id, limit)
        
        return {
            "user_id": user_id,
            "transactions": [
                {
                    "id": t.id,
                    "type": t.transaction_type.value,
                    "amount": t.amount,
                    "balance_before": t.balance_before,
                    "balance_after": t.balance_after,
                    "description": t.description,
                    "status": t.status.value,
                    "created_at": t.created_at.isoformat(),
                    "transaction_data": t.transaction_data
                }
                for t in transactions
            ],
            "total": len(transactions)
        }
    except Exception as e:
        logger.error(f"Ошибка получения транзакций: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения транзакций")

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получает статистику пользователя.
    """
    try:
        stats = await EconomyService.get_user_stats(db, user_id)
        return {
            "user_id": user_id,
            **stats
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")

@router.post("/purchase/{user_id}")
async def purchase_coins(
    user_id: str,
    package_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Покупка монет (симуляция).
    В реальном приложении здесь будет интеграция с платежными системами.
    """
    try:
        if package_id not in PURCHASE_OPTIONS:
            raise HTTPException(status_code=400, detail="Неверный пакет монет")
        
        package = PURCHASE_OPTIONS[package_id]
        coins = package['coins']
        price = package['price_usd']
        
        # В реальном приложении здесь будет проверка платежа
        # Пока что просто добавляем монеты
        
        await EconomyService.add_coins(
            db=db,
            user_id=user_id,
            amount=coins,
            description=f"Покупка {coins} монет за ${price}",
            source="purchase"
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "coins_added": coins,
            "price_usd": price,
            "package_id": package_id
        }
        
    except Exception as e:
        logger.error(f"Ошибка покупки монет: {e}")
        raise HTTPException(status_code=500, detail="Ошибка покупки монет")

@router.get("/actions/costs")
async def get_action_costs():
    """
    Получает стоимость всех действий.
    """
    return {
        "action_costs": ACTION_COSTS,
        "purchase_options": PURCHASE_OPTIONS,
    }

@router.post("/games/{user_id}/claim")
async def claim_game_reward(
    user_id: str,
    game: str,
    score: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Начисляет монеты за результат мини-игры.
    Валидация на сервере: допустимые игры, лимиты, конвертация очков в монеты.
    """
    try:
        game_key = game.strip().lower()
        if game_key not in GAME_REWARD_ALLOWED_GAMES:
            raise HTTPException(status_code=400, detail="Игра не поддерживается")
        if score < 0:
            raise HTTPException(status_code=400, detail="Некорректный результат игры")

        ratio = GAME_REWARD_COINS_PER_SCORE.get(game_key, 0)
        coins = int(score * ratio)
        coins = max(0, min(coins, GAME_REWARD_MAX_PER_REQUEST))

        if coins == 0:
            return {"success": True, "coins_added": 0, "new_balance": await EconomyService.get_balance(db, user_id), "message": "Недостаточно очков для награды"}

        await EconomyService.add_coins(
            db=db,
            user_id=user_id,
            amount=coins,
            description=f"Награда за игру {game_key}: {score} очков",
            source="game"
        )

        return {
            "success": True,
            "coins_added": coins,
            "new_balance": await EconomyService.get_balance(db, user_id),
            "message": "Награда за мини-игру начислена"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка начисления награды за игру: {e}")
        raise HTTPException(status_code=500, detail="Ошибка начисления награды")

@router.post("/actions/{user_id}/health_up")
async def health_up_with_cost(
    user_id: str,
    pet_name: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Увеличивает здоровье питомца с проверкой стоимости.
    """
    try:
        # Находим питомца пользователя: по имени либо единственного живого
        if pet_name:
            result = await db.execute(
                select(Pet).where(Pet.user_id == user_id, Pet.name == pet_name, Pet.status == PetLifeStatus.alive)
            )
            pet = result.scalar_one_or_none()
        else:
            result = await db.execute(
                select(Pet).where(Pet.user_id == user_id, Pet.status == PetLifeStatus.alive)
            )
            pets = result.scalars().all()
            if len(pets) > 1:
                raise HTTPException(status_code=400, detail="Уточните питомца (несколько живых питомцев)")
            pet = pets[0] if pets else None
        
        if not pet:
            raise HTTPException(status_code=404, detail="Питомец не найден или умер")
        
        # Проверяем стоимость действия
        cost = await EconomyService.get_action_cost('health_up', pet.state.value)
        
        # Проверяем, может ли пользователь позволить себе действие
        can_afford = await EconomyService.can_afford_action(db, user_id, 'health_up', pet.state.value)
        
        if not can_afford:
            wallet = await EconomyService.get_wallet(db, user_id)
            raise HTTPException(
                status_code=400, 
                detail=f"Недостаточно монет. Требуется: {cost}, доступно: {wallet.coins if wallet else 0}"
            )
        
        # Тратим монеты
        await EconomyService.spend_coins(
            db=db,
            user_id=user_id,
            amount=cost,
            description=f"Увеличение здоровья питомца {pet.name} (стадия: {pet.state.value})",
                            transaction_data={"pet_id": pet.id, "action": "health_up", "stage": pet.state.value}
        )
        
        # Увеличиваем здоровье
        from api.health_up import health_up_logic
        result = await health_up_logic(user_id, db, pet.name)
        
        return {
            "success": True,
            "coins_spent": cost,
            "new_balance": await EconomyService.get_balance(db, user_id),
            "pet_info": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка увеличения здоровья с оплатой: {e}")
        raise HTTPException(status_code=500, detail="Ошибка увеличения здоровья")

@router.post("/actions/{user_id}/resurrect")
async def resurrect_pet(
    user_id: str,
    pet_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Воскрешает мёртвого питомца за монеты:
    - статус: dead -> alive
    - здоровье: полное
    - таймер стадии: стартует заново (updated_at = now)
    """
    try:
        # Находим мёртвого питомца по имени
        result = await db.execute(
            select(Pet).where(Pet.user_id == user_id, Pet.name == pet_name, Pet.status == PetLifeStatus.dead)
        )
        pet = result.scalar_one_or_none()
        if not pet:
            raise HTTPException(status_code=404, detail="Питомец не найден или уже жив")

        # Стоимость
        from config.settings import HEALTH_MAX
        cost = ACTION_COSTS.get('resurrect', 500)

        # Проверяем баланс
        can_afford = await EconomyService.can_afford_action(db, user_id, 'resurrect')
        if not can_afford:
            wallet = await EconomyService.get_wallet(db, user_id)
            raise HTTPException(status_code=400, detail=f"Недостаточно монет. Требуется: {cost}, доступно: {wallet.coins if wallet else 0}")

        # Списываем монеты
        spent = await EconomyService.spend_coins(
            db=db,
            user_id=user_id,
            amount=cost,
            description=f"Воскрешение питомца {pet.name} (стадия: {pet.state.value})",
            transaction_data={"pet_id": pet.id, "action": "resurrect", "stage": pet.state.value}
        )
        if not spent:
            raise HTTPException(status_code=500, detail="Не удалось списать монеты за воскрешение")

        # Меняем статус и здоровье, обновляем таймер стадии
        pet.status = PetLifeStatus.alive
        pet.health = HEALTH_MAX
        from datetime import datetime
        pet.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(pet)

        return {
            "success": True,
            "coins_spent": cost,
            "new_balance": await EconomyService.get_balance(db, user_id),
            "pet": {
                "id": pet.id,
                "name": pet.name,
                "state": pet.state.value,
                "health": pet.health,
                "status": pet.status.value,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка воскрешения питомца: {e}")
        raise HTTPException(status_code=500, detail="Ошибка воскрешения питомца")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка увеличения здоровья с оплатой: {e}")
        raise HTTPException(status_code=500, detail="Ошибка увеличения здоровья")

@router.post("/rewards/{user_id}/daily_login")
async def claim_daily_login_reward(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение ежедневной награды за вход.
    """
    try:
        # Проверяем, получал ли пользователь награду сегодня
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        
        # Проверяем последнюю транзакцию ежедневной награды
        result = await db.execute(
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.description.like("%ежедневная награда%"),
                Transaction.created_at >= today
            )
            .order_by(Transaction.created_at.desc())
        )
        
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Ежедневная награда уже получена сегодня")
        
        # Выдаем награду
        reward_amount = 5  # Из настроек
        await EconomyService.add_coins(
            db=db,
            user_id=user_id,
            amount=reward_amount,
            description="Ежедневная награда за вход",
            source="daily_login"
        )
        
        return {
            "success": True,
            "reward_amount": reward_amount,
            "new_balance": await EconomyService.get_balance(db, user_id),
            "message": "Ежедневная награда получена!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения ежедневной награды: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения награды") 