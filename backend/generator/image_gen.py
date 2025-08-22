import requests
import base64
import io
import time
import os
import json
import re
from PIL import Image
from typing import Optional, Dict, Any
import argparse
from .promt_gen import CreatureGenerator
from config.settings import (
    MODELS, DEFAULT_SETTINGS, QUALITY_PRESETS, 
    FILE_SETTINGS, API_SETTINGS, REALISM_PROMPTS, GENERATION_DEFAULTS,
    get_quality_settings, get_model_info,
    get_all_models, get_default_settings,
    get_file_settings, get_api_settings, get_realism_prompt, get_all_realism_styles,
    get_generation_defaults
)

# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Загружены переменные окружения из .env")
except ImportError:
    print("[WARN] python-dotenv не установлен. Установите: pip install python-dotenv")

# Попробуем импортировать huggingface_hub для более надежной работы
try:
    from huggingface_hub import InferenceClient as HFInferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("[WARN] huggingface_hub не установлен. Установите: pip install huggingface_hub")

def safe_filename(text: str) -> str:
    """Создает безопасное имя файла из текста"""
    file_settings = get_file_settings()
    
    # Заменяем недопустимые символы
    safe = re.sub(file_settings["safe_filename_chars"], file_settings["replacement_char"], text)
    # Убираем множественные подчеркивания
    safe = re.sub(r'_+', '_', safe)
    # Убираем пробелы в начале и конце
    safe = safe.strip()
    # Ограничиваем длину
    if len(safe) > file_settings["max_filename_length"]:
        safe = safe[:file_settings["max_filename_length"]]
    return safe

class HFImageGenerator:
    """Генератор изображений через Hugging Face Inference API"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HF_API_TOKEN")
        api_settings = get_api_settings()
        self.base_url = api_settings["base_url"]
        
        # Инициализируем huggingface_hub клиент если доступен
        api_settings = get_api_settings()
        if HF_AVAILABLE and self.api_token:
            try:
                self.hf_client = HFInferenceClient(model=api_settings["default_model"], token=self.api_token)
                print("[OK] Используем huggingface_hub клиент")
            except Exception as e:
                print(f"[WARN] Не удалось инициализировать huggingface_hub клиент: {e}")
                self.hf_client = None
        else:
            self.hf_client = None
        
        # Загружаем модели и настройки из config/settings.py
        self.models = get_all_models()
        self.default_settings = get_default_settings()
        # анимация удалена
    
    def generate_image_with_hf_client(self, prompt: str, model_id: Optional[str] = None, **kwargs) -> Optional[Image.Image]:
        """Генерирует изображение через huggingface_hub клиент. Учитывает выбранную модель."""
        if not self.hf_client:
            return None
        
        try:
            settings = {**self.default_settings, **kwargs}
            
            # Создаем параметры для запроса
            parameters = {
                "negative_prompt": settings.get("negative_prompt", self.default_settings.get("negative_prompt")),
                "num_inference_steps": settings["steps"],
                "guidance_scale": settings["guidance_scale"],
                "width": settings["width"],
                "height": settings["height"]
            }
            
            # Если указана модель и она отличается от модели по умолчанию клиента — создаем временный клиент
            client = self.hf_client
            try:
                if model_id and hasattr(self.hf_client, 'model') and getattr(self.hf_client, 'model') != model_id:
                    from huggingface_hub import InferenceClient as HFInferenceClient  # type: ignore
                    client = HFInferenceClient(model=model_id, token=self.api_token)
            except Exception:
                client = self.hf_client

            print(f"[...] Используем huggingface_hub клиент ({model_id or 'default'})...")
            result = client.text_to_image(prompt, **parameters)
            
            if result:
                return result
            else:
                print("[ERR] huggingface_hub клиент вернул пустой результат")
                return None
                
        except Exception as e:
            print(f"[ERR] Ошибка в huggingface_hub клиенте: {e}")
            return None
    
    def _make_request(self, model_id: str, payload: Dict[str, Any]) -> Optional[Image.Image]:
        """Выполняет запрос к Hugging Face Inference API"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/models/{model_id}"
        
        try:
            api_settings = get_api_settings()
            print(f"[...] Отправляем запрос к {model_id}...")
            response = requests.post(url, headers=headers, json=payload, timeout=api_settings["timeout"])
            
            if response.status_code == 200:
                # Проверяем тип контента
                content_type = response.headers.get('content-type', '')
                
                if 'image' in content_type:
                    # API вернул изображение напрямую
                    image_bytes = response.content
                    return Image.open(io.BytesIO(image_bytes))
                else:
                    # Пытаемся обработать как JSON с base64
                    try:
                        image_data = response.json()
                        if isinstance(image_data, list) and len(image_data) > 0:
                            image_bytes = base64.b64decode(image_data[0])
                            return Image.open(io.BytesIO(image_bytes))
                        else:
                            print(f"[ERR] Неожиданный формат ответа: {image_data}")
                            return None
                    except json.JSONDecodeError:
                        # Если не JSON, возможно это изображение
                        image_bytes = response.content
                        return Image.open(io.BytesIO(image_bytes))
            else:
                print(f"[ERR] Ошибка API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] Таймаут при запросе к {model_id}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ERR] Ошибка сети: {e}")
            return None
        except Exception as e:
            print(f"[ERR] Неожиданная ошибка: {e}")
            return None
    
    def generate_image(self, prompt: str, model: str = "stable-diffusion-xl", **kwargs) -> Optional[Image.Image]:
        """Генерирует изображение через указанную модель"""
        if model not in self.models:
            print(f"[ERR] Неизвестная модель: {model}")
            return None
        
        if not self.api_token:
            print("[ERR] Не установлен API токен. Установите переменную окружения HF_API_TOKEN")
            return None
        
        # Сначала пробуем huggingface_hub клиент
        if self.hf_client:
            print("[...] Пробуем huggingface_hub клиент...")
            model_id = self.models[model]["model_id"]
            result = self.generate_image_with_hf_client(prompt, model_id=model_id, **kwargs)
            if result:
                return result
            else:
                print("[WARN] huggingface_hub клиент не сработал, пробуем прямой API...")
        
        # Если huggingface_hub не сработал, используем прямой API
        model_id = self.models[model]["model_id"]
        settings = {**self.default_settings, **kwargs}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": settings.get("negative_prompt", self.default_settings.get("negative_prompt")),
                "num_inference_steps": settings["steps"],
                "guidance_scale": settings["guidance_scale"],
                "width": settings["width"],
                "height": settings["height"]
            }
        }
        
        return self._make_request(model_id, payload)

    # (удалено): вся логика анимации
    
    def test_api_availability(self) -> Dict[str, bool]:
        """Тестирует доступность API и моделей"""
        if not self.api_token:
            print("❌ API токен не установлен")
            return {}
        
        results = {}
        print("[TEST] Тестируем доступность Hugging Face Inference API...")
        
        for model_name, model_info in self.models.items():
            print(f"Тестируем {model_name}...")
            try:
                headers = {"Authorization": f"Bearer {self.api_token}"}
                url = f"{self.base_url}/models/{model_info['model_id']}"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    results[model_name] = True
                    print(f"  {model_name}: [OK] Доступен")
                else:
                    results[model_name] = False
                    print(f"  {model_name}: [ERR] Недоступен ({response.status_code})")
                    
            except Exception as e:
                results[model_name] = False
                print(f"  {model_name}: [ERR] Ошибка: {e}")
        
        return results
    
    def _get_quality_settings(self, preset: str = "high") -> Dict[str, Any]:
        """Возвращает настройки качества для генерации"""
        return get_quality_settings(preset)
    

    
    def generate_creature_image(self, creature_generator: CreatureGenerator,
                               output_dir: str = None,
                               preferred_model: str = None,
                               quality_preset: str = None,
                               realism_style: str = None,
                               stage: str = "adult") -> Dict[str, Any]:
        """Генерирует изображение существа с реалистичным стилем

        Args:
            stage: стадия для выбора промпта ("egg" | "baby" | "adult"). По умолчанию "adult".
        """
        # Используем настройки файлов из config/settings.py
        file_settings = get_file_settings()
        if output_dir is None:
            output_dir = file_settings["output_dir"]
        
        # Используем настройки по умолчанию если не указаны
        generation_defaults = get_generation_defaults()
        if preferred_model is None:
            preferred_model = generation_defaults["preferred_model"]
        if quality_preset is None:
            quality_preset = generation_defaults["quality_preset"]
        if realism_style is None:
            realism_style = generation_defaults["realism_style"]
        
        # Создаем папку для выходных файлов
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Генерируем существо
        creature = creature_generator.generate_creature()
        
        # Получаем промпты по стадиям и выбираем нужный
        stage = stage.lower()
        if stage not in {"egg", "baby", "adult"}:
            stage = "adult"
        stage_prompts = creature_generator.generate_stage_prompts(creature)
        prompt = stage_prompts[stage]["en"]
        
        # Добавляем реалистичные улучшения к промпту
        realism_prompt = get_realism_prompt(realism_style)
        enhanced_prompt = f"{prompt}, {realism_prompt}, masterpiece, best quality, highly detailed, ultra detailed, 8k resolution, professional photography, natural lighting, realistic creature, detailed anatomy, natural environment, realistic proportions, detailed features, natural colors, realistic shadows, depth of field, natural pose"
        
        print(f"[GEN] Генерация изображения для {creature.habitat.value} {creature.creature_type.value} (стадия: {stage})...")
        print(f"[PROMPT] {enhanced_prompt[:100]}...")
        
        # Настройки качества
        quality_settings = self._get_quality_settings(quality_preset)
        
        # Негативный промпт с учетом стадии
        try:
            from config.settings import get_stage_negative_prompt
            stage_negative = get_stage_negative_prompt(stage, include_global=True)
        except Exception:
            stage_negative = self.default_settings.get("negative_prompt")
        
        # Генерируем изображение
        start_time = time.time()
        image = self.generate_image(enhanced_prompt, model=preferred_model, negative_prompt=stage_negative, **quality_settings)
        generation_time = time.time() - start_time
        
        if image is None:
            print("❌ Не удалось сгенерировать изображение")
            return {"success": False, "error": "Не удалось сгенерировать изображение"}
        
        # Создаем безопасное имя файла с названием модели
        timestamp = int(time.time())
        creature_type_safe = safe_filename(creature.creature_type.value.lower())
        habitat_safe = safe_filename(creature.habitat.value.lower())
        model_safe = preferred_model.replace("-", "_")
        base_name = f"{creature_type_safe}_{habitat_safe}_{stage}_{model_safe}_{timestamp}"
        
        # Сохраняем изображение
        image_path = os.path.join(output_dir, f"{base_name}.png")
        image.save(image_path)
        print(f"[OK] Изображение сохранено: {image_path}")
        
        # Получаем JSON описание как словарь
        json_description = creature_generator.generate_json_description(creature)
        if isinstance(json_description, str):
            # Если это строка, парсим JSON
            import json
            metadata = json.loads(json_description)
        else:
            metadata = json_description
        
        # Добавляем дополнительные поля
        metadata["prompt"] = enhanced_prompt
        metadata["stage"] = stage
        metadata["base_prompt"] = prompt
        metadata["negative_prompt"] = stage_negative
        metadata["model"] = preferred_model
        metadata["timestamp"] = timestamp
        metadata["generation_time"] = generation_time
        metadata["image_path"] = image_path
        
        # Сохраняем JSON с данными
        json_path = os.path.join(output_dir, f"{base_name}_data.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"[META] JSON данные сохранены: {json_path}")
        
        return {
            "success": True,
            "image_path": image_path,
            "json_path": json_path,
            "generation_time": generation_time,
            "prompt": enhanced_prompt,
            "model": preferred_model,
            "creature_type": creature.creature_type.value,
            "habitat": creature.habitat.value,
            "metadata": metadata
        }

def main():
    """CLI: генерация изображений и анимация через Hugging Face Inference API"""
    parser = argparse.ArgumentParser(description="Генерация существ и анимация (Hugging Face)")
    parser.add_argument("--stage", choices=["egg", "baby", "adult"], default="adult", help="Стадия развития")
    parser.add_argument("--preferred_model", choices=list(get_all_models().keys()), default=get_generation_defaults()["preferred_model"], help="Модель генерации изображения")
    parser.add_argument("--quality_preset", choices=list(QUALITY_PRESETS.keys()), default=get_generation_defaults()["quality_preset"], help="Качество изображения")
    parser.add_argument("--realism_style", choices=list(get_all_realism_styles().keys()), default=get_generation_defaults()["realism_style"], help="Стиль реализма")
    parser.add_argument("--output_dir", default=get_file_settings()["output_dir"], help="Директория для сохранения изображений")
    # опции анимации удалены
    args = parser.parse_args()

    print("[CLI] Генератор (HF)")
    print("=" * 60)

    creature_generator = CreatureGenerator()
    image_generator = HFImageGenerator()

    # Генерация изображения по стадии
    gen_result = image_generator.generate_creature_image(
        creature_generator,
        output_dir=args.output_dir,
        preferred_model=args.preferred_model,
        quality_preset=args.quality_preset,
        realism_style=args.realism_style,
        stage=args.stage
    )

    if not gen_result or not gen_result.get("success"):
        print("❌ Не удалось сгенерировать изображение")
        return

    print(f"[OK] Изображение: {gen_result['image_path']}")

    # конец CLI

if __name__ == "__main__":
    main()


