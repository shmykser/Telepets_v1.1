from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.settings import HEALTH_MAX, INITIAL_COINS, ANONYMOUS_MODE_ENABLED
import enum

Base = declarative_base()

class PetState(enum.Enum):
    egg = 'egg'
    baby = 'baby'
    adult = 'adult'

class PetLifeStatus(enum.Enum):
    alive = 'alive'
    dead = 'dead'

class TransactionType(enum.Enum):
    purchase = 'purchase'           # Покупка монет
    earning = 'earning'             # Заработок монет
    spending = 'spending'           # Трата монет
    bonus = 'bonus'                # Бонусные монеты
    refund = 'refund'              # Возврат монет
    market_purchase = 'market_purchase'  # Покупка на рынке (списание у покупателя)
    market_sale = 'market_sale'          # Продажа на рынке (начисление продавцу)
    market_fee = 'market_fee'            # Комиссия маркетплейса

class TransactionStatus(enum.Enum):
    pending = 'pending'             # В ожидании
    completed = 'completed'         # Завершена
    failed = 'failed'              # Неудачна
    cancelled = 'cancelled'        # Отменена

class Pet(Base):
    __tablename__ = 'pets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    state = Column(Enum(PetState), default=PetState.egg, nullable=False)
    status = Column(Enum(PetLifeStatus), default=PetLifeStatus.alive, nullable=False)
    health = Column(Integer, default=HEALTH_MAX, nullable=False)
    # Полное JSON-описание существа (характеристики), как в cache/*_prompts.json → ключ creature
    creature_json = Column(Text, nullable=True)
    # Промпты стадий на английском
    prompt_egg_en = Column(Text, nullable=True)
    prompt_baby_en = Column(Text, nullable=True)
    prompt_adult_en = Column(Text, nullable=True)
    # Картинки по стадиям (base64 PNG). Для текущей и прошлых стадий заполняются, для будущих — null
    image_egg_b64 = Column(Text, nullable=True)
    image_baby_b64 = Column(Text, nullable=True)
    image_adult_b64 = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='pending')

class User(Base):
    """Модель пользователя с кошельком"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)  # Оставляем для обратной совместимости
    telegram_username = Column(String, nullable=True)  # Оригинальный username из Telegram
    display_name = Column(String, nullable=True)  # Кастомное имя для отображения
    is_anonymous = Column(Boolean, default=False, nullable=False)  # Переключатель анонимности
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")
    
    @property
    def public_name(self) -> str:
        """Возвращает публичное имя пользователя с учетом анонимности"""
        if ANONYMOUS_MODE_ENABLED:
            if self.is_anonymous and self.display_name:
                return self.display_name
            elif self.is_anonymous:
                return "Анонимный игрок"
        # Если анонимность отключена — всегда показываем нормальное имя
        return self.telegram_username or self.username or "Неизвестный игрок"

class Wallet(Base):
    """Кошелек пользователя"""
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.user_id'), unique=True, nullable=False)
    coins = Column(Integer, default=INITIAL_COINS, nullable=False)  # Начальные монеты
    coins_locked = Column(Integer, default=0, nullable=False)       # Замороженные монеты (холды под ставки)
    total_earned = Column(Integer, default=0, nullable=False)  # Всего заработано
    total_spent = Column(Integer, default=0, nullable=False)   # Всего потрачено
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="wallet")

class Transaction(Base):
    """Транзакции пользователя"""
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Количество монет
    balance_before = Column(Integer, nullable=False)  # Баланс до транзакции
    balance_after = Column(Integer, nullable=False)   # Баланс после транзакции
    description = Column(String, nullable=False)      # Описание транзакции
    status = Column(Enum(TransactionStatus), default=TransactionStatus.completed)
    transaction_data = Column(Text, nullable=True)  # Дополнительные данные (JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="transactions")

class Achievement(Base):
    """Достижения пользователя"""
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    achievement_type = Column(String, nullable=False)  # Тип достижения
    title = Column(String, nullable=False)             # Название достижения
    description = Column(String, nullable=False)       # Описание
    coins_reward = Column(Integer, default=0)         # Награда в монетах
    is_claimed = Column(Boolean, default=False)       # Получена ли награда
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 

# ===== МАРКЕТ / АУКЦИОНЫ =====

class AuctionStatus(enum.Enum):
    active = 'active'
    completed = 'completed'
    cancelled = 'cancelled'
    expired = 'expired'

class WalletHoldStatus(enum.Enum):
    active = 'active'
    released = 'released'
    captured = 'captured'

class Auction(Base):
    __tablename__ = 'auctions'
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    seller_user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    start_price = Column(Integer, nullable=False)
    current_price = Column(Integer, nullable=False)
    buy_now_price = Column(Integer, nullable=True)
    min_increment_abs = Column(Integer, nullable=True)
    min_increment_pct = Column(Integer, nullable=True)
    soft_close_seconds = Column(Integer, nullable=False, default=60)
    status = Column(Enum(AuctionStatus), nullable=False, default=AuctionStatus.active)
    current_winner_user_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AuctionBid(Base):
    __tablename__ = 'auction_bids'
    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey('auctions.id'), nullable=False, index=True)
    bidder_user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WalletHold(Base):
    __tablename__ = 'wallet_holds'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False, index=True)
    auction_id = Column(Integer, ForeignKey('auctions.id'), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    status = Column(Enum(WalletHoldStatus), nullable=False, default=WalletHoldStatus.active)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)

class PetOwnershipHistory(Base):
    __tablename__ = 'pet_ownership_history'
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    from_user_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    to_user_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    price = Column(Integer, nullable=True)
    auction_id = Column(Integer, ForeignKey('auctions.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())