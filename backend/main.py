from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db import init_db
from backend.api import create, health_up, summary
from backend.tasks import start_health_decrease_task
import asyncio

app = FastAPI(
    title="Telepets API",
    description="Современный тамагочи для Telegram Web App",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    """
    Инициализация приложения при запуске.
    Создает базу данных и запускает фоновые задачи.
    """
    # Инициализация базы данных
    await init_db()
    
    # Запуск фоновой задачи по уменьшению здоровья
    await start_health_decrease_task()

# Подключение роутеров
app.include_router(create.router)
app.include_router(health_up.router)
app.include_router(summary.router) 