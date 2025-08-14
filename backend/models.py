from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.settings import HEALTH_MAX, INITIAL_COINS
import enum

Base = declarative_base()

class PetState(enum.Enum):
    egg = 'egg'
    baby = 'baby'
    adult = 'adult'
    dead = 'dead'

class TransactionType(enum.Enum):
    purchase = 'purchase'           # Покупка монет
    earning = 'earning'             # Заработок монет
    spending = 'spending'           # Трата монет
    bonus = 'bonus'                # Бонусные монеты
    refund = 'refund'              # Возврат монет

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
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")

class Wallet(Base):
    """Кошелек пользователя"""
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.user_id'), unique=True, nullable=False)
    coins = Column(Integer, default=INITIAL_COINS, nullable=False)  # Начальные монеты
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