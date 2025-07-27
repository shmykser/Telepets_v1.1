"""
Система мониторинга и метрик для Telepets API.
Отслеживает производительность, ошибки и игровую статистику.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from backend.db import AsyncSessionLocal
from backend.models import Pet, Notification, PetState

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self):
        self.request_times = []
        self.error_counts = defaultdict(int)
        self.active_pets = 0
        self.total_pets = 0
        self.dead_pets = 0
        self.stage_distribution = defaultdict(int)
        self.last_update = datetime.utcnow()
    
    def record_request_time(self, endpoint: str, duration: float):
        """Записывает время выполнения запроса"""
        self.request_times.append({
            'endpoint': endpoint,
            'duration': duration,
            'timestamp': datetime.utcnow()
        })
        
        # Ограничиваем размер истории
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-500:]
    
    def record_error(self, error_type: str, error_message: str):
        """Записывает ошибку"""
        self.error_counts[error_type] += 1
        logger.error(f"Ошибка {error_type}: {error_message}")
    
    async def update_pet_metrics(self):
        """Обновляет метрики питомцев"""
        async with AsyncSessionLocal() as db:
            # Общее количество питомцев
            result = await db.execute(select(func.count(Pet.id)))
            self.total_pets = result.scalar()
            
            # Активные питомцы
            result = await db.execute(
                select(func.count(Pet.id)).where(Pet.state != PetState.dead)
            )
            self.active_pets = result.scalar()
            
            # Мертвые питомцы
            result = await db.execute(
                select(func.count(Pet.id)).where(Pet.state == PetState.dead)
            )
            self.dead_pets = result.scalar()
            
            # Распределение по стадиям
            result = await db.execute(
                select(Pet.state, func.count(Pet.id))
                .group_by(Pet.state)
            )
            self.stage_distribution.clear()
            for stage, count in result:
                self.stage_distribution[stage.value] = count
        
        self.last_update = datetime.utcnow()
    
    def get_metrics(self) -> Dict:
        """Возвращает текущие метрики"""
        avg_response_time = 0
        if self.request_times:
            recent_times = [r['duration'] for r in self.request_times[-100:]]
            avg_response_time = sum(recent_times) / len(recent_times)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'pets': {
                'total': self.total_pets,
                'active': self.active_pets,
                'dead': self.dead_pets,
                'stages': dict(self.stage_distribution)
            },
            'performance': {
                'avg_response_time_ms': round(avg_response_time * 1000, 2),
                'total_requests': len(self.request_times)
            },
            'errors': dict(self.error_counts),
            'last_update': self.last_update.isoformat()
        }

# Глобальный экземпляр сборщика метрик
metrics_collector = MetricsCollector()

class MonitoringMiddleware:
    """Middleware для мониторинга запросов"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Обработка запроса
            try:
                await self.app(scope, receive, send)
                
                # Записываем метрики успешного запроса
                duration = time.time() - start_time
                endpoint = scope.get('path', 'unknown')
                metrics_collector.record_request_time(endpoint, duration)
                
            except Exception as e:
                # Записываем метрики ошибки
                duration = time.time() - start_time
                error_type = type(e).__name__
                metrics_collector.record_error(error_type, str(e))
                raise

async def start_monitoring_task():
    """Запускает задачу мониторинга"""
    logger.info("Запуск системы мониторинга")
    
    while True:
        try:
            await metrics_collector.update_pet_metrics()
            logger.debug("Метрики обновлены")
        except Exception as e:
            logger.error(f"Ошибка обновления метрик: {e}")
        
        # Обновляем метрики каждые 5 минут
        await asyncio.sleep(300)

def get_health_status() -> Dict:
    """Возвращает статус здоровья системы"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.1.0',
        'uptime': 'running'
    } 