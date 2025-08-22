from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime, timedelta
from typing import Optional, Tuple

from models import (
    Pet,
    PetLifeStatus,
    Auction,
    AuctionBid,
    AuctionStatus,
    Wallet,
    WalletHold,
    WalletHoldStatus,
    TransactionType,
    PetOwnershipHistory,
)
from config.settings import (
    AUCTION_DEFAULT_DURATION_SECONDS,
    AUCTION_SOFT_CLOSE_SECONDS,
    AUCTION_MIN_BID_INCREMENT_PERCENT,
    AUCTION_MIN_BID_INCREMENT_ABS,
    MARKET_FEE_PERCENT,
    AUCTION_MAX_ACTIVE_PER_USER,
)
from economy import EconomyService
from telegram_client import telegram_client
from services.user_profile import UserProfileService

import logging

logger = logging.getLogger(__name__)


class AuctionService:
    """Сервис аукционов. Логика изолирована от остальной экономики.

    Примечание по конкурентности: при SQLite записи сериализуются, что упрощает гонки.
    В будущих СУБД добавим row-level locks.
    """

    @staticmethod
    async def _get_pet(db: AsyncSession, pet_id: int) -> Optional[Pet]:
        result = await db.execute(select(Pet).where(Pet.id == pet_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_wallet(db: AsyncSession, user_id: str) -> Optional[Wallet]:
        result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def _get_auction(db: AsyncSession, auction_id: int) -> Optional[Auction]:
        result = await db.execute(select(Auction).where(Auction.id == auction_id))
        return result.scalar_one_or_none()

    @staticmethod
    def _calc_min_next_bid(current_price: int, min_inc_abs: Optional[int], min_inc_pct: Optional[int]) -> int:
        pct_inc = (current_price * (min_inc_pct or AUCTION_MIN_BID_INCREMENT_PERCENT)) // 100
        abs_inc = max(min_inc_abs or AUCTION_MIN_BID_INCREMENT_ABS, AUCTION_MIN_BID_INCREMENT_ABS)
        return current_price + max(pct_inc, abs_inc)

    @staticmethod
    async def create_auction(
        db: AsyncSession,
        seller_user_id: str,
        pet_id: int,
        start_price: int,
        duration_seconds: Optional[int] = None,
        buy_now_price: Optional[int] = None,
        min_increment_abs: Optional[int] = None,
        min_increment_pct: Optional[int] = None,
        soft_close_seconds: Optional[int] = None,
    ) -> Auction:
        if start_price <= 0:
            raise ValueError("Стартовая цена должна быть > 0")

        pet = await AuctionService._get_pet(db, pet_id)
        if not pet:
            raise ValueError("Питомец не найден")
        if pet.user_id != seller_user_id:
            raise PermissionError("Вы не являетесь владельцем питомца")
        if pet.status != PetLifeStatus.alive:
            raise ValueError("Продавать можно только живого питомца")

        # Лимит активных аукционов на пользователя
        active_count_result = await db.execute(
            select(Auction).where(Auction.seller_user_id == seller_user_id, Auction.status == AuctionStatus.active)
        )
        active_count = len(active_count_result.scalars().all())
        if active_count >= AUCTION_MAX_ACTIVE_PER_USER:
            raise ValueError("Превышен лимит активных аукционов на пользователя")

        # Проверка отсутствия активного аукциона по этому питомцу
        existing = await db.execute(
            select(Auction).where(Auction.pet_id == pet_id, Auction.status == AuctionStatus.active)
        )
        if existing.scalar_one_or_none():
            raise ValueError("У питомца уже есть активный аукцион")

        end_time = datetime.utcnow() + timedelta(seconds=duration_seconds or AUCTION_DEFAULT_DURATION_SECONDS)
        auction = Auction(
            pet_id=pet_id,
            seller_user_id=seller_user_id,
            start_price=start_price,
            current_price=start_price,
            buy_now_price=buy_now_price,
            min_increment_abs=min_increment_abs,
            min_increment_pct=min_increment_pct,
            soft_close_seconds=soft_close_seconds or AUCTION_SOFT_CLOSE_SECONDS,
            status=AuctionStatus.active,
            end_time=end_time,
        )
        db.add(auction)
        await db.commit()
        await db.refresh(auction)
        logger.info(f"Создан аукцион {auction.id} для питомца {pet_id} продавцом {seller_user_id}")
        return auction

    @staticmethod
    async def place_bid(
        db: AsyncSession,
        auction_id: int,
        bidder_user_id: str,
        amount: int,
    ) -> Tuple[Auction, AuctionBid]:
        if amount <= 0:
            raise ValueError("Ставка должна быть > 0")

        auction = await AuctionService._get_auction(db, auction_id)
        if not auction:
            raise ValueError("Аукцион не найден")
        if auction.status != AuctionStatus.active:
            raise ValueError("Аукцион не активен")
        if datetime.utcnow() >= auction.end_time:
            raise ValueError("Аукцион уже завершен по времени")
        if auction.seller_user_id == bidder_user_id:
            raise PermissionError("Нельзя ставить на свой аукцион")

        # Минимально допустимая ставка
        min_next = AuctionService._calc_min_next_bid(
            auction.current_price,
            auction.min_increment_abs,
            auction.min_increment_pct,
        )
        if amount < min_next:
            raise ValueError(f"Слишком маленькая ставка. Минимум: {min_next}")

        # Проверяем доступный баланс с учётом холдов
        wallet = await AuctionService._get_wallet(db, bidder_user_id)
        if not wallet:
            wallet = await EconomyService.create_user_wallet(db, bidder_user_id)
        available = wallet.coins - (wallet.coins_locked or 0)
        if available < amount:
            raise ValueError("Недостаточно монет для ставки")

        # Снимаем hold у предыдущего лидера, если он был
        if auction.current_winner_user_id:
            prev_hold_result = await db.execute(
                select(WalletHold)
                .where(
                    WalletHold.auction_id == auction.id,
                    WalletHold.user_id == auction.current_winner_user_id,
                    WalletHold.status == WalletHoldStatus.active,
                )
                .order_by(WalletHold.created_at.desc())
            )
            prev_hold = prev_hold_result.scalar_one_or_none()
            if prev_hold:
                prev_wallet = await AuctionService._get_wallet(db, prev_hold.user_id)
                if prev_wallet and prev_wallet.coins_locked >= prev_hold.amount:
                    prev_wallet.coins_locked -= prev_hold.amount
                prev_hold.status = WalletHoldStatus.released
                prev_hold.released_at = datetime.utcnow()
                # Уведомляем предыдущего лидера о перебитии
                try:
                    await telegram_client.send_auction_outbid(prev_hold.user_id, auction.id, amount)
                except Exception:
                    pass

        # Создаем новый hold
        wallet.coins_locked += amount
        hold = WalletHold(
            user_id=bidder_user_id,
            auction_id=auction.id,
            amount=amount,
            status=WalletHoldStatus.active,
        )
        db.add(hold)

        # Записываем ставку
        bid = AuctionBid(
            auction_id=auction.id,
            bidder_user_id=bidder_user_id,
            amount=amount,
        )
        db.add(bid)

        # Обновляем текущую цену и лидера
        auction.current_price = amount
        auction.current_winner_user_id = bidder_user_id

        # Soft-close продление
        remaining = (auction.end_time - datetime.utcnow()).total_seconds()
        if remaining <= (auction.soft_close_seconds or AUCTION_SOFT_CLOSE_SECONDS):
            auction.end_time = datetime.utcnow() + timedelta(seconds=auction.soft_close_seconds or AUCTION_SOFT_CLOSE_SECONDS)

        await db.commit()
        await db.refresh(auction)
        await db.refresh(bid)
        logger.info(f"Новая ставка {amount} в аукционе {auction.id} от {bidder_user_id}")
        return auction, bid

    @staticmethod
    async def buy_now(
        db: AsyncSession,
        auction_id: int,
        buyer_user_id: str,
    ) -> Auction:
        auction = await AuctionService._get_auction(db, auction_id)
        if not auction:
            raise ValueError("Аукцион не найден")
        if auction.status != AuctionStatus.active:
            raise ValueError("Аукцион не активен")
        if auction.buy_now_price is None:
            raise ValueError("Buy-now не доступен в этом аукционе")
        if auction.seller_user_id == buyer_user_id:
            raise PermissionError("Нельзя купить свой лот")

        price = auction.buy_now_price

        # Проверка средств
        wallet = await AuctionService._get_wallet(db, buyer_user_id)
        if not wallet:
            wallet = await EconomyService.create_user_wallet(db, buyer_user_id)
        available = wallet.coins - (wallet.coins_locked or 0)
        if available < price:
            raise ValueError("Недостаточно монет для покупки")

        # Финализация сделки как мгновенная покупка
        await AuctionService._finalize_transfer(
            db=db,
            auction=auction,
            winner_user_id=buyer_user_id,
            final_price=price,
            skip_hold=True,
        )
        return auction

    @staticmethod
    async def cancel_auction(db: AsyncSession, auction_id: int, seller_user_id: str) -> Auction:
        auction = await AuctionService._get_auction(db, auction_id)
        if not auction:
            raise ValueError("Аукцион не найден")
        if auction.seller_user_id != seller_user_id:
            raise PermissionError("Можно отменить только свой аукцион")
        if auction.status != AuctionStatus.active:
            raise ValueError("Аукцион уже не активен")

        # Нельзя отменить при наличии лидирующей ставки
        if auction.current_winner_user_id:
            raise ValueError("Нельзя отменить аукцион с активной ставкой")

        auction.status = AuctionStatus.cancelled
        await db.commit()
        await db.refresh(auction)
        logger.info(f"Аукцион {auction.id} отменен продавцом {seller_user_id}")
        return auction

    @staticmethod
    async def finalize_single(db: AsyncSession, auction_id: int) -> Optional[Auction]:
        auction = await AuctionService._get_auction(db, auction_id)
        if not auction or auction.status != AuctionStatus.active:
            return auction
        if datetime.utcnow() < auction.end_time:
            return auction

        if auction.current_winner_user_id:
            await AuctionService._finalize_transfer(
                db=db,
                auction=auction,
                winner_user_id=auction.current_winner_user_id,
                final_price=auction.current_price,
                skip_hold=False,
            )
        else:
            auction.status = AuctionStatus.expired
            await db.commit()
            await db.refresh(auction)
            logger.info(f"Аукцион {auction.id} завершен без ставок")
            # Уведомляем продавца об истечении без продажи
            try:
                await telegram_client.send_auction_expired(auction.seller_user_id, auction.id)
            except Exception:
                pass
        return auction

    @staticmethod
    async def _finalize_transfer(
        db: AsyncSession,
        auction: Auction,
        winner_user_id: str,
        final_price: int,
        skip_hold: bool,
    ) -> None:
        # Захватываем или списываем средства победителя
        if skip_hold:
            # Прямое списание
            await EconomyService.create_transaction(
                db=db,
                user_id=winner_user_id,
                transaction_type=TransactionType.spending,
                amount=final_price,
                description=f"Покупка питомца на рынке (аукцион {auction.id})",
                transaction_data={"auction_id": auction.id, "pet_id": auction.pet_id},
            )
        else:
            # Ищем активный hold победителя на финальную сумму (или ближайшую)
            hold_result = await db.execute(
                select(WalletHold)
                .where(
                    WalletHold.auction_id == auction.id,
                    WalletHold.user_id == winner_user_id,
                    WalletHold.status == WalletHoldStatus.active,
                )
                .order_by(WalletHold.created_at.desc())
            )
            hold = hold_result.scalar_one_or_none()
            if not hold or hold.amount < final_price:
                raise ValueError("Нет достаточного хода средств для финализации")
            # Списываем через уменьшение coins и coins_locked
            winner_wallet = await AuctionService._get_wallet(db, winner_user_id)
            if not winner_wallet or winner_wallet.coins_locked < hold.amount or winner_wallet.coins < final_price:
                raise ValueError("Недостаточно средств у победителя при финализации")
            winner_wallet.coins_locked -= hold.amount
            winner_wallet.coins -= final_price
            hold.status = WalletHoldStatus.captured
            hold.captured_at = datetime.utcnow()

            # Транзакция market_purchase как запись истории
            await EconomyService.create_transaction(
                db=db,
                user_id=winner_user_id,
                transaction_type=TransactionType.market_purchase,
                amount=final_price,
                description=f"Покупка на рынке (аукцион {auction.id})",
                transaction_data={"auction_id": auction.id, "pet_id": auction.pet_id},
            )

        # Начисляем продавцу за вычетом комиссии
        fee = (final_price * MARKET_FEE_PERCENT) // 100
        seller_amount = max(0, final_price - fee)
        await EconomyService.create_transaction(
            db=db,
            user_id=auction.seller_user_id,
            transaction_type=TransactionType.market_sale,
            amount=seller_amount,
            description=f"Продажа питомца на рынке (аукцион {auction.id})",
            transaction_data={"auction_id": auction.id, "pet_id": auction.pet_id, "fee": fee},
        )

        # Комиссию можно списать с «системного кошелька» позже; пока учтена только в нетто

        # Переводим право собственности
        pet = await AuctionService._get_pet(db, auction.pet_id)
        if not pet:
            raise ValueError("Питомец не найден при финализации")
        prev_owner = pet.user_id
        pet.user_id = winner_user_id

        # История владения
        history = PetOwnershipHistory(
            pet_id=pet.id,
            from_user_id=prev_owner,
            to_user_id=winner_user_id,
            price=final_price,
            auction_id=auction.id,
        )
        db.add(history)

        # Закрываем аукцион
        auction.status = AuctionStatus.completed
        await db.commit()
        await db.refresh(auction)
        logger.info(f"Аукцион {auction.id} завершен. Победитель {winner_user_id}, цена {final_price}")

        # Уведомления
        try:
            # Получаем анонимные имена для уведомлений
            winner_info = await UserProfileService.get_public_user_info(db, winner_user_id)
            seller_info = await UserProfileService.get_public_user_info(db, auction.seller_user_id)
            
            # Уведомляем победителя
            await telegram_client.send_auction_won(winner_user_id, auction.id, final_price)
            
            # Уведомляем продавца
            await telegram_client.send_pet_sold(
                auction.seller_user_id, 
                auction.id, 
                seller_amount,
                winner_info.public_name if winner_info else "Неизвестный игрок"
            )
        except Exception as e:
            logger.warning(f"Ошибка отправки уведомлений для аукциона {auction.id}: {e}")


