from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from config.settings import DATABASE_URL
import ssl
import certifi
from urllib.parse import urlparse

# Преобразуем синхронные URL в асинхронные драйверы при необходимости
if DATABASE_URL.startswith("sqlite://"):
    async_database_url = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
elif DATABASE_URL.startswith("postgresql://"):
    async_database_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    async_database_url = DATABASE_URL

# Аргументы подключения (SSL включаем только для внешних URL)
connect_args: dict = {}
if async_database_url.startswith("postgresql+asyncpg://"):
    parsed = urlparse(async_database_url)
    hostname = parsed.hostname or ""
    is_external_host = "." in hostname  # внутренние хосты Render вида 'dpg-xxxxx' без точки
    if is_external_host:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connect_args = {"ssl": ssl_context}

engine = create_async_engine(
    async_database_url,
    echo=True,
    future=True,
    connect_args=connect_args,
)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session 