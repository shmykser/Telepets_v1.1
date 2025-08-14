from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config.settings import DATABASE_URL

# Используем настройку из settings.py
# Для SQLite используем асинхронный движок
if DATABASE_URL.startswith("sqlite://"):
    # Заменяем sqlite:// на sqlite+aiosqlite:// для асинхронной работы
    async_database_url = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    async_database_url = DATABASE_URL

engine = create_async_engine(async_database_url, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 