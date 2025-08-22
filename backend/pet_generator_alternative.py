#!/usr/bin/env python3
"""
Альтернативный генератор изображений питомцев
Использует локальные изображения и эмодзи вместо DALL-E API
"""

import os
import hashlib
import json
import asyncio
import aiohttp
import aiofiles
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PetType(Enum):
    CAT = "cat"
    DOG = "dog"
    BIRD = "bird"
    FISH = "fish"
    RABBIT = "rabbit"
    HAMSTER = "hamster"
    DRAGON = "dragon"
    UNICORN = "unicorn"
    ROBOT = "robot"
    ALIEN = "alien"

class PetStyle(Enum):
    CUTE = "cute"
    COOL = "cool"
    MYSTICAL = "mystical"
    ANIME = "anime"
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    PIXEL = "pixel"
    WATERCOLOR = "watercolor"

@dataclass
class PetVisualConfig:
    pet_type: PetType
    style: PetStyle
    stage: str
    health: int
    unique_features: List[str]
    color_scheme: str
    accessories: List[str]
    mood: str
    background: str

class AlternativePetVisualGenerator:
    def __init__(self):
        self.cache_dir = "cache/pet_images"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Эмодзи для разных типов питомцев
        self.pet_emojis = {
            PetType.CAT: "🐱",
            PetType.DOG: "🐕",
            PetType.BIRD: "🐦",
            PetType.FISH: "🐠",
            PetType.RABBIT: "🐰",
            PetType.HAMSTER: "🐹",
            PetType.DRAGON: "🐉",
            PetType.UNICORN: "🦄",
            PetType.ROBOT: "🤖",
            PetType.ALIEN: "👽"
        }
        
        # Цвета для разных уровней здоровья
        self.health_colors = {
            "excellent": "#4CAF50",  # Зеленый
            "good": "#8BC34A",       # Светло-зеленый
            "average": "#FFC107",    # Желтый
            "poor": "#FF9800",       # Оранжевый
            "critical": "#F44336"    # Красный
        }
        
        # Настроения для разных уровней здоровья
        self.health_moods = {
            "excellent": "happy",
            "good": "content",
            "average": "neutral",
            "poor": "sad",
            "critical": "sick"
        }
        
        # Стили для разных стадий
        self.stage_styles = {
            "egg": "small, simple",
            "baby": "tiny, adorable",
            "teen": "medium, growing",
            "adult": "large, mature",
            "dead": "gray, lifeless"
        }

    def _generate_unique_features(self, user_id: str, pet_name: str) -> List[str]:
        """Генерирует уникальные особенности питомца"""
        combined = f"{user_id}_{pet_name}"
        hash_value = hashlib.md5(combined.encode()).hexdigest()
        
        features = [
            "особые отметины", "крылья", "рога", "хвост", "уши",
            "пятна", "полоски", "блестящая шерсть", "длинные усы",
            "большие глаза", "маленький нос", "пушистый хвост"
        ]
        
        # Выбираем 2-3 особенности на основе хеша
        selected = []
        for i in range(3):
            index = int(hash_value[i*4:(i+1)*4], 16) % len(features)
            if features[index] not in selected:
                selected.append(features[index])
        
        return selected

    def _determine_pet_type(self, user_id: str) -> PetType:
        """Определяет тип питомца на основе user_id"""
        hash_value = hashlib.md5(user_id.encode()).hexdigest()
        index = int(hash_value[:8], 16) % len(PetType)
        return list(PetType)[index]

    def _determine_style(self, user_id: str) -> PetStyle:
        """Определяет стиль питомца на основе user_id"""
        hash_value = hashlib.md5(user_id.encode()).hexdigest()
        index = int(hash_value[8:16], 16) % len(PetStyle)
        return list(PetStyle)[index]

    def _get_health_mood(self, health: int) -> str:
        """Определяет настроение на основе здоровья"""
        if health >= 80:
            return self.health_moods["excellent"]
        elif health >= 60:
            return self.health_moods["good"]
        elif health >= 40:
            return self.health_moods["average"]
        elif health >= 20:
            return self.health_moods["poor"]
        else:
            return self.health_moods["critical"]

    def _get_health_colors(self, health: int) -> str:
        """Определяет цветовую схему на основе здоровья"""
        if health >= 80:
            return "excellent"
        elif health >= 60:
            return "good"
        elif health >= 40:
            return "average"
        elif health >= 20:
            return "poor"
        else:
            return "critical"

    def _generate_svg_image(self, config: PetVisualConfig) -> str:
        """Генерирует SVG изображение питомца"""
        emoji = self.pet_emojis[config.pet_type]
        color = self.health_colors[config.color_scheme]
        
        # Размеры в зависимости от стадии
        sizes = {
            "egg": "60",
            "baby": "80",
            "teen": "100",
            "adult": "120",
            "dead": "80"
        }
        size = sizes.get(config.stage, "100")
        
        # Создаем простой SVG с эмодзи
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="background" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f0f8ff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#e6f3ff;stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Фон -->
  <rect width="100%" height="100%" fill="url(#background)" rx="10"/>
  
  <!-- Питомец (эмодзи) -->
  <text x="50%" y="50%" text-anchor="middle" dy="0.35em" 
        font-size="{int(int(size)*0.6)}" font-family="Arial, sans-serif"
        filter="url(#glow)">
    {emoji}
  </text>
  
  <!-- Индикатор здоровья -->
  <rect x="10%" y="85%" width="80%" height="8%" rx="4" 
        fill="#ddd" stroke="#999" stroke-width="1"/>
  <rect x="10%" y="85%" width="{config.health}%" height="8%" rx="4" 
        fill="{color}" stroke="#999" stroke-width="1"/>
  
  <!-- Особенности -->
  {self._generate_features_svg(config.unique_features, size)}
</svg>'''
        
        return svg

    def _generate_features_svg(self, features: List[str], size: str) -> str:
        """Генерирует SVG элементы для особенностей питомца"""
        svg_elements = []
        
        for i, feature in enumerate(features[:3]):  # Максимум 3 особенности
            x = 20 + (i * 25)
            y = 20 + (i * 5)
            
            if "крылья" in feature:
                svg_elements.append(f'''
  <path d="M {x} {y} Q {x+10} {y-10} {x+20} {y}" 
        fill="none" stroke="#87CEEB" stroke-width="2" opacity="0.7"/>
  <path d="M {x+20} {y} Q {x+30} {y-10} {x+40} {y}" 
        fill="none" stroke="#87CEEB" stroke-width="2" opacity="0.7"/>''')
            elif "рога" in feature:
                svg_elements.append(f'''
  <path d="M {x+10} {y} L {x+15} {y-15} L {x+20} {y}" 
        fill="none" stroke="#8B4513" stroke-width="3"/>
  <path d="M {x+20} {y} L {x+25} {y-15} L {x+30} {y}" 
        fill="none" stroke="#8B4513" stroke-width="3"/>''')
            elif "хвост" in feature:
                svg_elements.append(f'''
  <path d="M {x} {y+20} Q {x-10} {y+10} {x-20} {y+20}" 
        fill="none" stroke="#FF6B6B" stroke-width="3" opacity="0.8"/>''')
        
        return "".join(svg_elements)

    def _get_cache_filename(self, user_id: str, pet_name: str, stage: str) -> str:
        """Генерирует имя файла для кэша"""
        combined = f"{user_id}_{pet_name}_{stage}"
        hash_value = hashlib.md5(combined.encode()).hexdigest()
        return f"{hash_value}.svg"

    async def generate_pet_image(self, user_id: str, pet_name: str, stage: str, health: int) -> tuple[str, Dict[str, Any]]:
        """Генерирует изображение питомца"""
        cache_filename = self._get_cache_filename(user_id, pet_name, stage)
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        # Проверяем кэш
        if os.path.exists(cache_path):
            logger.info(f"Используем кэшированное изображение: {cache_path}")
            metadata = self._load_metadata(cache_path)
            return cache_path, metadata
        
        # Генерируем новое изображение
        logger.info(f"Генерируем новое изображение для {pet_name}")
        
        # Определяем параметры
        pet_type = self._determine_pet_type(user_id)
        style = self._determine_style(user_id)
        unique_features = self._generate_unique_features(user_id, pet_name)
        color_scheme = self._get_health_colors(health)
        mood = self._get_health_mood(health)
        
        # Создаем конфигурацию
        config = PetVisualConfig(
            pet_type=pet_type,
            style=style,
            stage=stage,
            health=health,
            unique_features=unique_features,
            color_scheme=color_scheme,
            accessories=[],
            mood=mood,
            background="мягкий градиентный фон"
        )
        
        # Генерируем SVG
        svg_content = self._generate_svg_image(config)
        
        # Сохраняем изображение
        async with aiofiles.open(cache_path, 'w', encoding='utf-8') as f:
            await f.write(svg_content)
        
        # Создаем метаданные
        metadata = {
            "config": {
                "pet_type": config.pet_type.value,
                "style": config.style.value,
                "stage": config.stage,
                "health": config.health,
                "unique_features": config.unique_features,
                "color_scheme": config.color_scheme,
                "accessories": config.accessories,
                "mood": config.mood,
                "background": config.background
            },
            "generation_info": {
                "method": "svg_generation",
                "user_id": user_id,
                "pet_name": pet_name,
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        
        # Сохраняем метаданные
        await self._save_metadata(cache_path, metadata)
        
        logger.info(f"Изображение сохранено: {cache_path}")
        return cache_path, metadata

    async def _save_metadata(self, image_path: str, metadata: Dict[str, Any]) -> None:
        """Сохраняет метаданные изображения"""
        metadata_path = image_path.replace('.svg', '.json')
        async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(metadata, ensure_ascii=False, indent=2))

    def _load_metadata(self, image_path: str) -> Dict[str, Any]:
        """Загружает метаданные изображения"""
        metadata_path = image_path.replace('.svg', '.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_pet_image_url(self, user_id: str, pet_name: str, stage: str, health: int) -> str:
        """Возвращает URL изображения питомца"""
        # Для SVG файлов возвращаем путь к файлу
        cache_filename = self._get_cache_filename(user_id, pet_name, stage)
        return f"/static/pet_images/{cache_filename}"

    async def clear_cache(self, user_id: Optional[str] = None) -> None:
        """Очищает кэш изображений"""
        if user_id:
            # Удаляем файлы для конкретного пользователя
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(hashlib.md5(user_id.encode()).hexdigest()[:8]):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"Удален файл кэша: {file_path}")
        else:
            # Удаляем все файлы кэша
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Удален файл кэша: {file_path}")

# Создаем глобальный экземпляр по умолчанию (SVG-эмуляция)
pet_generator_alternative = AlternativePetVisualGenerator()