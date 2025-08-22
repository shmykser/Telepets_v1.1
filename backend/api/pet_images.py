from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_db
from models import Pet
from pet_generator_alternative import pet_generator_alternative
from typing import Optional
import json
from . import *  # noqa: F401
from backend.generator.image_gen import HFImageGenerator
from backend.generator.promt_gen import CreatureGenerator
from prompt_store import load_prompts, generate_and_store_prompts
from config.settings import GENERATION_DEFAULTS, get_file_settings
from services.stages import StageLifecycleService
import logging
import os
import base64

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pet-images", tags=["Pet Images"])

@router.get("/{user_id}/{pet_name}")
async def get_pet_image(
    user_id: str,
    pet_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получает изображение питомца исключительно из БД (base64).
    При его отсутствии генерирует и сохраняет в БД, затем отдает.
    """
    try:
        # Получаем информацию о питомце из БД
        result = await db.execute(
            select(Pet).where(
                Pet.user_id == user_id, 
                Pet.name == pet_name
            )
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(status_code=404, detail="Питомец не найден")
        stage_key = pet.state.value if pet.state.value in {"egg", "baby", "adult"} else "adult"

        # 1) Пытаемся отдать сохранённое изображение из БД
        b64_map = {
            'egg': pet.image_egg_b64,
            'baby': pet.image_baby_b64,
            'adult': pet.image_adult_b64,
        }
        existing_b64 = b64_map.get(stage_key)
        if existing_b64:
            try:
                raw = base64.b64decode(existing_b64)
                return Response(content=raw, media_type="image/png", headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "X-Pet-Stage": stage_key,
                    "X-Pet-Source": "db_base64",
                })
            except Exception:
                pass

        # 2) Нет изображения — генерируем по промпту из БД/хранилища и сохраняем в БД
        image_path: Optional[str] = None
        try:
            from config.settings import (
                get_generation_defaults,
                get_quality_settings,
                get_stage_negative_prompt,
                get_realism_prompt,
            )
            generator = HFImageGenerator()

            # Промпт: сначала пытаемся из БД
            prompt_en = None
            try:
                prompt_en = StageLifecycleService._get_prompt_from_db_sync(user_id, pet_name, stage_key)
            except Exception:
                prompt_en = None
            if not prompt_en:
                stored = load_prompts(user_id, pet_name) or {}
                prompt_en = ((stored.get("stage_prompts", {}) or {}).get(stage_key, {}) or {}).get("en")

            if prompt_en:
                gen_defaults = get_generation_defaults()
                preferred_model = gen_defaults["preferred_model"]
                quality_settings = get_quality_settings(gen_defaults["quality_preset"])  # type: ignore
                stage_negative = get_stage_negative_prompt(stage_key, include_global=True)
                realism_prompt = get_realism_prompt(gen_defaults["realism_style"])  # type: ignore
                enhanced_prompt = f"{prompt_en}, {realism_prompt}, masterpiece, best quality, highly detailed, ultra detailed, 8k resolution, professional photography, natural lighting, realistic creature, detailed anatomy, natural environment, realistic proportions, detailed features, natural colors, realistic shadows, depth of field, natural pose"

                img = generator.generate_image(
                    enhanced_prompt,
                    model=preferred_model,
                    negative_prompt=stage_negative,
                    **quality_settings,
                )
                if img is not None:
                    # Сохраняем в файловую систему временно, затем кладем в БД через persist
                    out_dir = get_file_settings()["output_dir"]
                    os.makedirs(out_dir, exist_ok=True)
                    temp_path = os.path.join(out_dir, f"{user_id}_{pet_name}_{stage_key}_temp.png")
                    img.save(temp_path)
                    image_path = temp_path
            # Если не удалось — SVG fallback
            if image_path is None:
                image_path, _ = await pet_generator_alternative.generate_pet_image(
                    user_id=user_id,
                    pet_name=pet_name,
                    stage=stage_key,
                    health=pet.health
                )

            # Persist в БД и повторная отдача
            await StageLifecycleService.persist_stage_artifacts(db, user_id, pet_name, stage_key, prompt_en, image_path)

            # Обновим pet и отдадим
            await db.refresh(pet)
            refreshed_b64 = {
                'egg': pet.image_egg_b64,
                'baby': pet.image_baby_b64,
                'adult': pet.image_adult_b64,
            }.get(stage_key)
            if refreshed_b64:
                raw = base64.b64decode(refreshed_b64)
                return Response(content=raw, media_type="image/png", headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "X-Pet-Stage": stage_key,
                    "X-Pet-Source": "generated_and_persisted",
                })

            # Если по какой-то причине не удалось — безопасный SVG placeholder
            placeholder_svg = f"""
<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200' viewBox='0 0 200 200'>
  <defs>
    <linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='#f0f9ff' />
      <stop offset='100%' stop-color='#e0f2fe' />
    </linearGradient>
  </defs>
  <rect x='0' y='0' width='200' height='200' rx='16' fill='url(#bg)' />
  <text x='100' y='100' text-anchor='middle' dominant-baseline='middle' font-size='18' fill='#0b1220'>Telepets</text>
  <text x='100' y='130' text-anchor='middle' dominant-baseline='middle' font-size='12' fill='#334155'>{pet_name} · {user_id}</text>
  <text x='100' y='155' text-anchor='middle' dominant-baseline='middle' font-size='10' fill='#64748b'>stage: {stage_key}</text>
  <title>generated inline svg placeholder</title>
  </svg>""".strip()
            return Response(content=placeholder_svg, media_type="image/svg+xml")
        except Exception:
            # Если генерация/сохранение упала, продолжим на общий обработчик ниже
            pass
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения изображения питомца: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения изображения")

@router.get("/{user_id}/{pet_name}/metadata")
async def get_pet_image_metadata(
    user_id: str, 
    pet_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получает метаданные изображения питомца.
    """
    try:
        # Получаем информацию о питомце из БД
        result = await db.execute(
            select(Pet).where(
                Pet.user_id == user_id, 
                Pet.name == pet_name
            )
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(status_code=404, detail="Питомец не найден")
        
        # Генерируем изображение и получаем метаданные
        _, metadata = await pet_generator_alternative.generate_pet_image(
            user_id=user_id,
            pet_name=pet_name,
            stage=pet.state.value,
            health=pet.health
        )
        
        return {
            "user_id": user_id,
            "pet_name": pet_name,
            "stage": pet.state.value,
            "health": pet.health,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения метаданных изображения: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения метаданных")

@router.post("/{user_id}/regenerate")
async def regenerate_pet_images(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Перегенерирует все изображения питомцев пользователя.
    """
    try:
        # Получаем всех питомцев пользователя
        result = await db.execute(
            select(Pet).where(Pet.user_id == user_id)
        )
        pets = result.scalars().all()
        
        if not pets:
            raise HTTPException(status_code=404, detail="Питомцы не найдены")
        
        # Очищаем кэш для пользователя
        await pet_generator_alternative.clear_cache(user_id)
        
        # Перегенерируем изображения для всех питомцев
        regenerated_images = []
        for pet in pets:
            try:
                image_path, metadata = await pet_generator_alternative.generate_pet_image(
                    user_id=user_id,
                    pet_name=pet.name,
                    stage=pet.state.value,
                    health=pet.health
                )
                regenerated_images.append({
                    "pet_name": pet.name,
                    "stage": pet.state.value,
                    "health": pet.health,
                    "image_path": image_path
                })
            except Exception as e:
                logger.error(f"Ошибка перегенерации изображения для {pet.name}: {e}")
        
        return {
            "message": f"Перегенерировано {len(regenerated_images)} изображений",
            "regenerated_images": regenerated_images
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка перегенерации изображений: {e}")
        raise HTTPException(status_code=500, detail="Ошибка перегенерации изображений")

@router.delete("/cache")
async def clear_image_cache():
    """
    Очищает весь кэш изображений питомцев.
    """
    try:
        await pet_generator_alternative.clear_cache()
        return {"message": "Кэш изображений очищен"}
    except Exception as e:
        logger.error(f"Ошибка очистки кэша: {e}")
        raise HTTPException(status_code=500, detail="Ошибка очистки кэша") 