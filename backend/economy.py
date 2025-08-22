"""
Сервис экономики для Telepets.
Управляет монетами, транзакциями и наградами пользователей.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models import User, Wallet, Transaction, TransactionType, TransactionStatus, Achievement
from config.settings import (
    INITIAL_COINS, ACTION_COSTS, ACHIEVEMENT_REWARDS, 
    ACTION_REWARDS, REWARD_LIMITS
)
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)

class EconomyService:
    """Сервис для управления экономикой"""
    
    @staticmethod
    async def create_user_wallet(db: AsyncSession, user_id: str, username: str = None) -> Wallet:
        """Создает кошелек для нового пользователя"""
        try:
            # Проверяем, существует ли пользователь
            user_result = await db.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                # Создаем пользователя с telegram_username
                user = User(
                    user_id=user_id,
                    telegram_username=username,
                    username=username  # Оставляем для обратной совместимости
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            
            # Проверяем, есть ли уже кошелек
            wallet_result = await db.execute(
                select(Wallet).where(Wallet.user_id == user_id)
            )
            wallet = wallet_result.scalar_one_or_none()
            
            if not wallet:
                # Создаем кошелек с начальными монетами
                wallet = Wallet(
                    user_id=user_id,
                    coins=INITIAL_COINS
                )
                db.add(wallet)
                await db.commit()
                await db.refresh(wallet)
                
                # Создаем транзакцию для начальных монет
                await EconomyService.create_transaction(
                    db=db,
                    user_id=user_id,
                    transaction_type=TransactionType.bonus,
                    amount=INITIAL_COINS,
                    description="Начальные монеты",
                    transaction_data={"source": "new_user"}
                )
                
                logger.info(f"Создан кошелек для пользователя {user_id} с {INITIAL_COINS} монетами")
            
            return wallet
            
        except Exception as e:
            logger.error(f"Ошибка создания кошелька для {user_id}: {e}")
            raise
    
    @staticmethod
    async def get_wallet(db: AsyncSession, user_id: str) -> Optional[Wallet]:
        """Получает кошелек пользователя"""
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_balance(db: AsyncSession, user_id: str) -> int:
        """Получает баланс пользователя (включая замороженные монеты)."""
        wallet = await EconomyService.get_wallet(db, user_id)
        return wallet.coins if wallet else 0

    @staticmethod
    async def get_available_balance(db: AsyncSession, user_id: str) -> int:
        """Доступный баланс (с учётом замороженных монет)."""
        wallet = await EconomyService.get_wallet(db, user_id)
        if not wallet:
            return 0
        locked = getattr(wallet, 'coins_locked', 0) or 0
        return max(0, wallet.coins - locked)
    
    @staticmethod
    async def create_transaction(
        db: AsyncSession,
        user_id: str,
        transaction_type: TransactionType,
        amount: int,
        description: str,
        transaction_data: Dict = None
    ) -> Transaction:
        """Создает транзакцию"""
        try:
            wallet = await EconomyService.get_wallet(db, user_id)
            if not wallet:
                raise ValueError(f"Кошелек пользователя {user_id} не найден")
            
            balance_before = wallet.coins
            
            # Обновляем баланс
            if transaction_type in [TransactionType.purchase, TransactionType.earning, TransactionType.bonus, TransactionType.refund]:
                wallet.coins += amount
                if transaction_type in [TransactionType.earning, TransactionType.bonus]:
                    wallet.total_earned += amount
            elif transaction_type == TransactionType.spending:
                if wallet.coins < amount:
                    raise ValueError(f"Недостаточно монет. Требуется: {amount}, доступно: {wallet.coins}")
                wallet.coins -= amount
                wallet.total_spent += amount
            
            balance_after = wallet.coins
            
            # Создаем транзакцию
            transaction = Transaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                description=description,
                transaction_data=json.dumps(transaction_data) if transaction_data else None
            )
            
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            
            logger.info(f"Транзакция создана: {user_id} - {transaction_type.value} {amount} монет")
            return transaction
            
        except Exception as e:
            logger.error(f"Ошибка создания транзакции: {e}")
            raise
    
    @staticmethod
    async def spend_coins(
        db: AsyncSession,
        user_id: str,
        amount: int,
        description: str,
        transaction_data: Dict = None
    ) -> bool:
        """Тратит монеты пользователя"""
        try:
            await EconomyService.create_transaction(
                db=db,
                user_id=user_id,
                transaction_type=TransactionType.spending,
                amount=amount,
                description=description,
                transaction_data=transaction_data
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка траты монет: {e}")
            return False
    
    @staticmethod
    async def add_coins(
        db: AsyncSession,
        user_id: str,
        amount: int,
        description: str,
        source: str = "reward"
    ) -> bool:
        """Добавляет монеты пользователю"""
        try:
            # Гарантируем, что кошелек существует (важно для фоновых наград)
            wallet = await EconomyService.get_wallet(db, user_id)
            if not wallet:
                wallet = await EconomyService.create_user_wallet(db, user_id)

            await EconomyService.create_transaction(
                db=db,
                user_id=user_id,
                transaction_type=TransactionType.earning,
                amount=amount,
                description=description,
                transaction_data={"source": source}
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления монет: {e}")
            return False
    
    @staticmethod
    async def can_afford_action(db: AsyncSession, user_id: str, action: str, stage: str = None) -> bool:
        """Проверяет, может ли пользователь позволить себе действие"""
        try:
            wallet = await EconomyService.get_wallet(db, user_id)
            if not wallet:
                return False
            
            if action == 'health_up' and stage:
                cost = ACTION_COSTS.get('health_up', {}).get(stage, 0)
            else:
                cost = ACTION_COSTS.get(action, 0)
            
            return wallet.coins >= cost
            
        except Exception as e:
            logger.error(f"Ошибка проверки возможности действия: {e}")
            return False
    
    @staticmethod
    async def get_action_cost(action: str, stage: str = None) -> int:
        """Получает стоимость действия"""
        if action == 'health_up' and stage:
            return ACTION_COSTS.get('health_up', {}).get(stage, 0)
        return ACTION_COSTS.get(action, 0)
    
    @staticmethod
    async def get_transaction_history(
        db: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> List[Transaction]:
        """Получает историю транзакций пользователя"""
        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: str) -> Dict:
        """Получает статистику пользователя"""
        try:
            wallet = await EconomyService.get_wallet(db, user_id)
            if not wallet:
                return {}
            
            # Статистика транзакций
            transactions_result = await db.execute(
                select(
                    Transaction.transaction_type,
                    func.sum(Transaction.amount).label('total_amount'),
                    func.count(Transaction.id).label('count')
                )
                .where(Transaction.user_id == user_id)
                .group_by(Transaction.transaction_type)
            )
            
            transaction_stats = {}
            for row in transactions_result:
                transaction_stats[row.transaction_type.value] = {
                    'total_amount': row.total_amount,
                    'count': row.count
                }
            
            return {
                'current_balance': wallet.coins,
                'total_earned': wallet.total_earned,
                'total_spent': wallet.total_spent,
                'transaction_stats': transaction_stats
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики пользователя: {e}")
            return {}
    
    @staticmethod
    async def check_achievement(
        db: AsyncSession,
        user_id: str,
        achievement_type: str,
        title: str,
        description: str,
        coins_reward: int
    ) -> bool:
        """Проверяет и выдает достижение"""
        try:
            # Проверяем, есть ли уже это достижение
            existing_result = await db.execute(
                select(Achievement)
                .where(
                    Achievement.user_id == user_id,
                    Achievement.achievement_type == achievement_type
                )
            )
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                return False  # Достижение уже получено
            
            # Создаем достижение
            achievement = Achievement(
                user_id=user_id,
                achievement_type=achievement_type,
                title=title,
                description=description,
                coins_reward=coins_reward
            )
            db.add(achievement)
            await db.commit()
            await db.refresh(achievement)
            
            # Выдаем награду
            await EconomyService.add_coins(
                db=db,
                user_id=user_id,
                amount=coins_reward,
                description=f"Достижение: {title}",
                source="achievement"
            )
            
            logger.info(f"Достижение выдано: {user_id} - {title}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки достижения: {e}")
            return False 