#!/usr/bin/env python3
"""
Хранилище стадийных промптов и описания существа для детерминированной генерации
"""
from __future__ import annotations

import os
import json
import hashlib
from typing import Dict, Any, Tuple, Optional


def _get_hash_prefix(text: str, length: int = 32) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:length]


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_prompt_store_path(user_id: str, pet_name: str) -> str:
    from config.settings import FILE_SETTINGS
    base_dir = FILE_SETTINGS.get("output_dir", os.path.join("cache", "pet_images"))
    _ensure_dir(base_dir)
    key = f"{user_id}_{pet_name}"
    filename = f"{_get_hash_prefix(key)}_prompts.json"
    return os.path.join(base_dir, filename)


def generate_and_store_prompts(user_id: str, pet_name: str) -> Dict[str, Any]:
    """
    Генерирует описание существа и стадийные промпты, сохраняет на диск.
    Возвращает словарь с ключами: creature, stage_prompts
    """
    # Подключаем генератор
    try:
        from backend.generator.promt_gen import CreatureGenerator
    except Exception:
        # fallback на относительный импорт
        from .generator.promt_gen import CreatureGenerator  # type: ignore

    generator = CreatureGenerator()
    creature = generator.generate_creature()
    stage_prompts = generator.generate_stage_prompts(creature)

    # Сериализуем creature через JSON описание
    creature_json = json.loads(generator.generate_json_description(creature))

    payload = {
        "user_id": user_id,
        "pet_name": pet_name,
        "creature": creature_json,
        "stage_prompts": stage_prompts,
    }

    path = get_prompt_store_path(user_id, pet_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload


def load_prompts(user_id: str, pet_name: str) -> Optional[Dict[str, Any]]:
    path = get_prompt_store_path(user_id, pet_name)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


