#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import asyncio
from typing import Optional, Tuple, Dict, Any

from config.settings import (
    get_file_settings,
    get_generation_defaults,
    get_quality_settings,
    get_stage_negative_prompt,
    get_realism_prompt,
)
from prompt_store import generate_and_store_prompts, load_prompts
from generator.image_gen import HFImageGenerator
from generator.promt_gen import CreatureGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Pet, PetState
from pet_generator_alternative import pet_generator_alternative


class StageLifecycleService:
    @staticmethod
    def ensure_prompts(user_id: str, pet_name: str) -> Dict[str, Any]:
        stored = load_prompts(user_id, pet_name)
        if not stored:
            stored = generate_and_store_prompts(user_id, pet_name)
        return stored or {}

    @staticmethod
    def _generate_png_for_stage(user_id: str, pet_name: str, stage_key: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Пытается сгенерировать PNG через HF по сохранённому промпту. Возвращает (path, metadata)."""
        stored = StageLifecycleService.ensure_prompts(user_id, pet_name)
        stage_prompts = (stored.get("stage_prompts", {}) or {})
        prompt_en = (stage_prompts.get(stage_key, {}) or {}).get("en")

        # 1) Пытаемся взять промпт из БД (источник истины)
        if not prompt_en:
            try:
                prompt_en = StageLifecycleService._get_prompt_from_db_sync(user_id, pet_name, stage_key)
            except Exception:
                prompt_en = None

        if not prompt_en:
            # Fallback: сгенерировать рандомного зверя (для совместимости)
            cg = CreatureGenerator()
            gen = HFImageGenerator()
            result = gen.generate_creature_image(cg, output_dir=get_file_settings()["output_dir"], stage=stage_key)
            if result and result.get("success"):
                return result["image_path"], result.get("metadata", {})
            return None, {}

        gen_defaults = get_generation_defaults()
        preferred_model = gen_defaults["preferred_model"]
        quality_settings = get_quality_settings(gen_defaults["quality_preset"])  # type: ignore
        stage_negative = get_stage_negative_prompt(stage_key, include_global=True)
        realism_prompt = get_realism_prompt(gen_defaults["realism_style"])  # type: ignore
        enhanced_prompt = f"{prompt_en}, {realism_prompt}, masterpiece, best quality, highly detailed, ultra detailed, 8k resolution, professional photography, natural lighting, realistic creature, detailed anatomy, natural environment, realistic proportions, detailed features, natural colors, realistic shadows, depth of field, natural pose"

        gen = HFImageGenerator()
        img = gen.generate_image(
            enhanced_prompt,
            model=preferred_model,
            negative_prompt=stage_negative,
            **quality_settings,
        )

        if img is None:
            return None, {}

        import time as _time
        ts = int(_time.time())
        safe_name = f"{user_id}_{pet_name}_{stage_key}_{preferred_model.replace('-', '_')}_{ts}"
        out_dir = get_file_settings()["output_dir"]
        os.makedirs(out_dir, exist_ok=True)
        image_path = os.path.join(out_dir, f"{safe_name}.png")
        img.save(image_path)

        metadata = {
            "user_id": user_id,
            "pet_name": pet_name,
            "stage": stage_key,
            "model": preferred_model,
            "prompt": enhanced_prompt,
            "base_prompt": prompt_en,
            "negative_prompt": stage_negative,
            "image_path": image_path,
            "timestamp": ts,
        }
        json_path = os.path.join(out_dir, f"{safe_name}_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return image_path, metadata

    @staticmethod
    def get_or_generate_image(user_id: str, pet_name: str, stage_key: str, health: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        image_path, metadata = StageLifecycleService._generate_png_for_stage(user_id, pet_name, stage_key)
        if image_path:
            return image_path, metadata
        # Fallback SVG
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(pet_generator_alternative.generate_pet_image(user_id, pet_name, stage_key, health or 100))

    @staticmethod
    async def warm_stage_image_async(user_id: str, pet_name: str, stage_key: str, health: int) -> None:
        def _run() -> None:
            try:
                StageLifecycleService.get_or_generate_image(user_id, pet_name, stage_key, health)
            except Exception:
                pass

        await asyncio.get_event_loop().run_in_executor(None, _run)

    @staticmethod
    async def prepare_on_create(db: AsyncSession, user_id: str, pet_name: str) -> None:
        """Генерирует creature-json и промпты для всех стадий, сохраняет в БД;
        затем генерирует изображение для стадии egg и сохраняет base64 в БД."""
        stored = StageLifecycleService.ensure_prompts(user_id, pet_name)
        stage_prompts = (stored.get("stage_prompts", {}) or {})

        # Сохраняем creature_json и промпты в БД (источник истины — БД)
        result = await db.execute(select(Pet).where(Pet.user_id == user_id, Pet.name == pet_name))
        pet = result.scalar_one_or_none()
        if pet:
            pet.creature_json = json.dumps(stored.get("creature", {}), ensure_ascii=False)
            egg_en = (stage_prompts.get("egg", {}) or {}).get("en")
            baby_en = (stage_prompts.get("baby", {}) or {}).get("en")
            adult_en = (stage_prompts.get("adult", {}) or {}).get("en")
            if egg_en:
                pet.prompt_egg_en = egg_en
            if baby_en:
                pet.prompt_baby_en = baby_en
            if adult_en:
                pet.prompt_adult_en = adult_en
            await db.commit()

        # Сразу генерируем изображение для первой стадии (egg) и сохраняем в БД как base64
        image_path, metadata = StageLifecycleService.get_or_generate_image(user_id, pet_name, "egg", health=100)
        try:
            await StageLifecycleService.persist_stage_artifacts(db, user_id, pet_name, "egg", (stage_prompts.get("egg", {}) or {}).get("en"), image_path)
        except Exception:
            pass

    @staticmethod
    async def persist_stage_artifacts(db: AsyncSession, user_id: str, pet_name: str, stage_key: str, prompt_en: Optional[str], image_path: Optional[str]) -> None:
        """Сохраняет promt_en и image_b64 текущей стадии в таблицу pets."""
        result = await db.execute(select(Pet).where(Pet.user_id == user_id, Pet.name == pet_name))
        pet = result.scalar_one_or_none()
        if not pet:
            return
        # Промпты
        if stage_key == 'egg' and prompt_en:
            pet.prompt_egg_en = prompt_en
        elif stage_key == 'baby' and prompt_en:
            pet.prompt_baby_en = prompt_en
        elif stage_key == 'adult' and prompt_en:
            pet.prompt_adult_en = prompt_en
        # Картинка в base64
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as f:
                    import base64
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                if stage_key == 'egg':
                    pet.image_egg_b64 = b64
                elif stage_key == 'baby':
                    pet.image_baby_b64 = b64
                elif stage_key == 'adult':
                    pet.image_adult_b64 = b64
            except Exception:
                pass
        await db.commit()

    @staticmethod
    async def wipe_images_on_death(db: AsyncSession, pet: Pet) -> None:
        pet.image_egg_b64 = None
        pet.image_baby_b64 = None
        pet.image_adult_b64 = None
        await db.commit()

    # ===== Helpers =====
    @staticmethod
    def _get_prompt_from_db_sync(user_id: str, pet_name: str, stage_key: str) -> Optional[str]:
        """Синхронный helper для получения промпта из БД (используется в sync-пайплайне генерации изображений)."""
        from db import AsyncSessionLocal
        from models import Pet
        import asyncio as _asyncio

        async def _fetch() -> Optional[str]:
            async with AsyncSessionLocal() as _db:
                res = await _db.execute(select(Pet).where(Pet.user_id == user_id, Pet.name == pet_name))
                pet = res.scalar_one_or_none()
                if not pet:
                    return None
                if stage_key == 'egg':
                    return pet.prompt_egg_en
                if stage_key == 'baby':
                    return pet.prompt_baby_en
                if stage_key == 'adult':
                    return pet.prompt_adult_en
                return None

        loop = _asyncio.get_event_loop()
        return loop.run_until_complete(_fetch())


