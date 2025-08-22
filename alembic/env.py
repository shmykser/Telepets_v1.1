from __future__ import annotations

from logging.config import fileConfig
import os
import asyncio
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# import models' metadata
import sys
from pathlib import Path

# Ensure project root is importable so `import backend` works
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# Also add backend/ to support imports like `from config.settings import ...`
BACKEND_DIR = PROJECT_ROOT / 'backend'
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.models import Base  # noqa: E402

target_metadata = Base.metadata


def get_url() -> str:
    # Prefer env var DATABASE_URL, else fallback to settings
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        try:
            from backend.config.settings import DATABASE_URL as SETTINGS_DB_URL
            db_url = SETTINGS_DB_URL
        except Exception:
            db_url = "sqlite:///./telepets.db"
    # Alembic expects sync driver; replace aiosqlite URL for offline config if needed
    if db_url.startswith("sqlite+"):
        db_url = db_url.replace("sqlite+aiosqlite://", "sqlite:///")
    return db_url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    sync_url = get_url()
    async_url = sync_url
    if sync_url.startswith("postgresql://"):
        async_url = sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    configuration["sqlalchemy.url"] = async_url

    connect_args = {}
    if async_url.startswith("postgresql+asyncpg://"):
        connect_args = {"ssl": True}

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    def _do_run_migrations(sync_connection):
        # Гарантируем наличие базовых таблиц из моделей перед применением миграций
        try:
            Base.metadata.create_all(sync_connection)
        except Exception:
            pass
        context.configure(connection=sync_connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    async def _run_async() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(_do_run_migrations)

    asyncio.run(_run_async())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


