"""
API endpoints для мониторинга и метрик Telepets.
Предоставляет информацию о состоянии системы и производительности.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from db import get_db
from models import Pet, Notification, PetState, PetLifeStatus
from monitoring import metrics_collector, get_health_status
from config.settings import APP_VERSION
from auth import get_current_user
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@router.get("/health")
async def health_check():
    """
    Проверка здоровья системы.
    Возвращает базовую информацию о состоянии API.
    """
    return get_health_status()

@router.get("/metrics")
async def get_metrics():
    """
    Получение метрик системы.
    Возвращает статистику по питомцам, производительности и ошибкам.
    """
    return metrics_collector.get_metrics()

@router.get("/stats")
async def get_statistics(db: AsyncSession = Depends(get_db)):
    """
    Получение детальной статистики.
    Возвращает подробную информацию о питомцах и уведомлениях.
    """
    try:
        # Статистика питомцев
        total_pets = await db.execute(select(func.count(Pet.id)))
        total_pets = total_pets.scalar()
        
        active_pets = await db.execute(
            select(func.count(Pet.id)).where(Pet.status == PetLifeStatus.alive)
        )
        active_pets = active_pets.scalar()
        
        dead_pets = await db.execute(
            select(func.count(Pet.id)).where(Pet.status == PetLifeStatus.dead)
        )
        dead_pets = dead_pets.scalar()
        
        # Статистика по стадиям
        stage_stats = await db.execute(
            select(Pet.state, func.count(Pet.id))
            .group_by(Pet.state)
        )
        stage_distribution = {stage.value: count for stage, count in stage_stats}
        
        # Статистика уведомлений
        total_notifications = await db.execute(select(func.count(Notification.id)))
        total_notifications = total_notifications.scalar()
        
        notification_types = await db.execute(
            select(Notification.type, func.count(Notification.id))
            .group_by(Notification.type)
        )
        notification_distribution = {ntype: count for ntype, count in notification_types}
        
        # Статистика за последние 24 часа
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_pets = await db.execute(
            select(func.count(Pet.id))
            .where(Pet.created_at >= yesterday)
        )
        recent_pets = recent_pets.scalar()
        
        recent_notifications = await db.execute(
            select(func.count(Notification.id))
            .where(Notification.created_at >= yesterday)
        )
        recent_notifications = recent_notifications.scalar()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "pets": {
                "total": total_pets,
                "active": active_pets,
                "dead": dead_pets,
                "stages": stage_distribution,
                "created_last_24h": recent_pets
            },
            "notifications": {
                "total": total_notifications,
                "types": notification_distribution,
                "sent_last_24h": recent_notifications
            },
            "system": {
                "uptime": "running",
                "version": APP_VERSION
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")

@router.get("/users/{user_id}/history")
async def get_user_history(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Получение истории пользователя.
    Возвращает всех питомцев и уведомления пользователя.
    """
    try:
        # Все питомцы пользователя
        pets_result = await db.execute(
            select(Pet)
            .where(Pet.user_id == user_id)
            .order_by(Pet.created_at.desc())
        )
        pets = pets_result.scalars().all()
        
        # Все уведомления пользователя
        notifications_result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        notifications = notifications_result.scalars().all()
        
        # Статистика пользователя
        total_pets = len(pets)
        alive_pets = len([p for p in pets if p.status == PetLifeStatus.alive])
        dead_pets = len([p for p in pets if p.status == PetLifeStatus.dead])
        
        # Группировка уведомлений по типам
        notification_stats = {}
        for notification in notifications:
            ntype = notification.type
            if ntype not in notification_stats:
                notification_stats[ntype] = 0
            notification_stats[ntype] += 1
        
        return {
            "user_id": user_id,
            "pets": {
                "total": total_pets,
                "alive": alive_pets,
                "dead": dead_pets,
                "list": [
                    {
                        "id": pet.id,
                        "name": pet.name,
                        "state": pet.state.value,
                        "health": pet.health,
                        "created_at": pet.created_at.isoformat(),
                        "updated_at": pet.updated_at.isoformat() if pet.updated_at else None
                    }
                    for pet in pets
                ]
            },
            "notifications": {
                "total": len(notifications),
                "types": notification_stats,
                "list": [
                    {
                        "id": notif.id,
                        "type": notif.type,
                        "message": notif.message,
                        "created_at": notif.created_at.isoformat()
                    }
                    for notif in notifications
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения истории пользователя {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения истории")

@router.get("/debug")
async def debug_info(db: AsyncSession = Depends(get_db)):
    """
    Отладочная информация (только для разработки).
    Возвращает детальную информацию о системе.
    """
    try:
        # Последние 10 питомцев
        recent_pets = await db.execute(
            select(Pet)
            .order_by(Pet.created_at.desc())
            .limit(10)
        )
        recent_pets = recent_pets.scalars().all()
        
        # Последние 10 уведомлений
        recent_notifications = await db.execute(
            select(Notification)
            .order_by(Notification.created_at.desc())
            .limit(10)
        )
        recent_notifications = recent_notifications.scalars().all()
        
        return {
            "debug_info": {
                "timestamp": datetime.utcnow().isoformat(),
                "recent_pets": [
                    {
                        "id": pet.id,
                        "user_id": pet.user_id,
                        "name": pet.name,
                        "state": pet.state.value,
                        "health": pet.health,
                        "created_at": pet.created_at.isoformat()
                    }
                    for pet in recent_pets
                ],
                "recent_notifications": [
                    {
                        "id": notif.id,
                        "user_id": notif.user_id,
                        "type": notif.type,
                        "message": notif.message,
                        "created_at": notif.created_at.isoformat()
                    }
                    for notif in recent_notifications
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения отладочной информации: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения отладочной информации") 