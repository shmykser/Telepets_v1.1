from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.db import init_db
from backend.api import create, health_up, summary
from backend.api import monitoring
from backend.tasks import start_health_decrease_task
from backend.monitoring import start_monitoring_task, MonitoringMiddleware
import asyncio
import logging
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Telepets API",
    description="Современный тамагочи для Telegram Web App",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем мониторинг middleware
app = MonitoringMiddleware(app)

@app.on_event("startup")
async def on_startup():
    """
    Инициализация приложения при запуске.
    Создает базу данных и запускает фоновые задачи.
    """
    logger.info("🚀 Запуск Telepets API v1.1.0")
    
    # Инициализация базы данных
    await init_db()
    logger.info("✅ База данных инициализирована")
    
    # Запуск фоновой задачи по уменьшению здоровья
    await start_health_decrease_task()
    logger.info("✅ Фоновая задача здоровья запущена")
    
    # Запуск задачи мониторинга
    asyncio.create_task(start_monitoring_task())
    logger.info("✅ Система мониторинга запущена")

@app.on_event("shutdown")
async def on_shutdown():
    """Очистка при выключении приложения"""
    logger.info("🛑 Выключение Telepets API")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик исключений"""
    logger.error(f"Необработанная ошибка: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error_type": type(exc).__name__,
            "timestamp": time.time()
        }
    )

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Telepets API v1.1.0",
        "docs": "/docs",
        "health": "/monitoring/health",
        "metrics": "/monitoring/metrics"
    }

# Подключение роутеров
app.include_router(create.router)
app.include_router(health_up.router)
app.include_router(summary.router)
app.include_router(monitoring.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000) 