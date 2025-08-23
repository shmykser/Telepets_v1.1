from __future__ import annotations

from logging.config import fileConfig
import os
import asyncio
import time
from sqlalchemy import pool
from sqlalchemy.engine import engine_from_config
from sqlalchemy.engine.url import make_url
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
    # Предпочитаем переменную окружения, иначе читаем из настроек
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        try:
            from backend.config.settings import DATABASE_URL as SETTINGS_DB_URL
            db_url = SETTINGS_DB_URL
        except Exception:
            db_url = "sqlite:///./telepets.db"
    # Alembic должен работать через синхронный драйвер
    if db_url.startswith("sqlite+"):
        db_url = db_url.replace("sqlite+aiosqlite://", "sqlite:///")
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    # Для внешних URL PostgreSQL можно добавлять sslmode=require, для internal — не трогаем
    try:
        url_obj = make_url(db_url)
        if url_obj.drivername.startswith("postgresql"):
            url_obj = url_obj.set(drivername="postgresql")
            host = url_obj.host or ""
            if "." in host:  # внешний хост
                url_obj = url_obj.set(query={"sslmode": "require"})
        return str(url_obj)
    except Exception:
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
    configuration["sqlalchemy.url"] = sync_url

    connect_args = {}
    if sync_url.startswith("postgresql://"):
        from sqlalchemy.engine.url import make_url as _make
        host = _make(sync_url).host or ""
        # sslmode только для внешних URL
        if "." in host:
            connect_args["sslmode"] = "require"
        connect_args.update({
            "keepalives": 1,
            "keepalives_idle": 5,
            "keepalives_interval": 5,
            "keepalives_count": 5,
        })

    connectable = engine_from_config(
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

    # Ретраи подключения (синхронные)
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            with connectable.connect() as connection:
                _do_run_migrations(connection)
            last_error = None
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(2 ** attempt)
    if last_error is not None:
        raise last_error


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


