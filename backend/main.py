from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from db import init_db
from api import create, health_up, summary, economy
from api import monitoring, debug, pet_images
from api import auth_api
from api import market
from api import user_profile
from tasks import start_health_decrease_task, start_auction_finalize_task
from monitoring import start_monitoring_task, MonitoringMiddleware
from config.settings import APP_VERSION, API_HOST, API_PORT
import asyncio
import logging
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Современный способ управления жизненным циклом приложения.
    """
    # Startup
    logger.info(f"Запуск Telepets API {APP_VERSION}")
    
    # Инициализация базы данных
    await init_db()
    logger.info("База данных инициализирована")
    
    # Запуск фоновой задачи по уменьшению здоровья
    await start_health_decrease_task()
    logger.info("Фоновая задача здоровья запущена")
    
    # Запуск фоновой задачи финализации аукционов
    await start_auction_finalize_task()
    logger.info("Фоновая задача аукционов запущена")
    
    # Запуск задачи мониторинга
    asyncio.create_task(start_monitoring_task())
    logger.info("Система мониторинга запущена")
    
    yield
    
    # Shutdown
    logger.info("Выключение Telepets API")

app = FastAPI(
    title="Telepets API",
    description="Современный тамагочи для Telegram Web App",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "message": f"Telepets API {APP_VERSION}",
        "docs": "/docs",
        "health": "/monitoring/health",
        "metrics": "/monitoring/metrics"
    }

@app.get("/test")
async def test():
    """Простой тестовый endpoint"""
    return {
        "status": "success",
        "message": "API работает",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/time-test")
async def time_test():
    """Тестовый endpoint для проверки времени"""
    from datetime import datetime, timedelta
    from config.settings import STAGE_TRANSITION_INTERVAL
    
    created_at = datetime.utcnow() - timedelta(seconds=STAGE_TRANSITION_INTERVAL)
    now = datetime.utcnow()
    transition_time = created_at + timedelta(seconds=STAGE_TRANSITION_INTERVAL)
    remaining_seconds = max(0, int((transition_time - now).total_seconds()))
    
    return {
        "created_at": created_at.isoformat(),
        "now": now.isoformat(),
        "transition_time": transition_time.isoformat(),
        "remaining_seconds": remaining_seconds,
        "stage_transition_interval": STAGE_TRANSITION_INTERVAL
    }

# Подключение роутеров
app.include_router(create.router)
app.include_router(health_up.router)
app.include_router(summary.router)
app.include_router(economy.router)
app.include_router(monitoring.router)
app.include_router(debug.router)
app.include_router(pet_images.router)
app.include_router(auth_api.router)
app.include_router(market.router)
app.include_router(user_profile.router)

# Добавляем мониторинг middleware после всех определений
app = MonitoringMiddleware(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT) 