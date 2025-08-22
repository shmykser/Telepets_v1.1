#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных Telepets.
"""

import asyncio
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import init_db
from models import Base
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    """Основная функция инициализации базы данных"""
    print("Init Telepets database...")
    
    try:
        # Инициализируем базу данных
        await init_db()
        print("Database initialized successfully.")
        
        # Проверяем, что таблицы созданы
        from db import engine
        async with engine.begin() as conn:
            tables = await conn.run_sync(
                lambda sync_conn: sync_conn.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            )
            print(f"Tables created: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"Init DB error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 