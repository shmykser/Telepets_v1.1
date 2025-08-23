import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = "https://api.telegram.org/bot"

# OpenAI settings (legacy, не используется) — оставлено для совместимости переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настройки здоровья для разных стадий
HEALTH_MAX = 100
HEALTH_LOW = 20
HEALTH_MIN = 0  # Минимальное здоровье (смерть)

# Настройки уменьшения здоровья для разных стадий (в секундах)
HEALTH_DOWN_INTERVALS = {
    'egg': 10,      # 10 секунд для яйца (температура)
    'baby': 20,    # 20 секунд для детеныша (сытость)
    'adult': 30    # 30 секунд для взрослого (настроение)
}

# Количество уменьшения здоровья для разных стадий
HEALTH_DOWN_AMOUNTS = {
    'egg': 3,       # Быстрое падение температуры
    'baby': 5,      # Умеренное падение сытости
    'adult': 2      # Медленное падение настроения
}

# Количество увеличения здоровья при действиях игрока
HEALTH_UP_AMOUNTS = {
    'egg': 15,      # Быстрое повышение температуры
    'baby': 25,     # Умеренное повышение сытости
    'adult': 15     # Медленное повышение настроения
}

# Настройки перехода между стадиями (в секундах)
STAGE_TRANSITION_INTERVAL = 30  # для всех стадий

# Порядок стадий развития
STAGE_ORDER = ['egg', 'baby', 'adult']

# Сообщения для разных стадий
STAGE_MESSAGES = {
    'egg': {
        'health_up': 'Яйцо согрето',
        'health_down': 'Яйцо остывает',
        'transition': 'Яйцо треснуло! Появился детеныш!',
        'death': 'Яйцо замерзло...'
    },
    'baby': {
        'health_up': 'Детеныш накормлен',
        'health_down': 'Детеныш голоден',
        'transition': 'Детеныш вырос! Теперь он взрослый!',
        'death': 'Детеныш умер от голода...'
    },
    'adult': {
        'health_up': 'Взрослый питомец счастлив',
        'health_down': 'Взрослый питомец грустит',
        'transition': 'Питомец достиг совершенства!',
        'death': 'Взрослый питомец умер от тоски...'
    }
}

# Награды за переход стадии отключены

# Сообщения для Telegram
TELEGRAM_MESSAGES = {
    'low_health': '⚠️ Внимание! Здоровье питомца низкое!',
    'death': '💀 Питомец умер! Игра окончена.',
    'stage_transition': '🎉 Питомец перешел на новую стадию!'
}

# ===== НАСТРОЙКИ ЭКОНОМИКИ =====

# Начальные монеты для новых пользователей
INITIAL_COINS = 100

# Стоимость действий в монетах
ACTION_COSTS = {
    'health_up': {
        'egg': 5,      # Согревание яйца
        'baby': 10,    # Кормление детеныша
        'adult': 20    # Развлечение взрослого
    },
    'resurrect': 200,     # Воскрешение питомца
    'special_food': 25,    # Специальная еда
    'medicine': 30,        # Лекарство
    'toy': 15,            # Игрушка
    'grooming': 20,        # Уход за питомцем
    'paid_pet': 300,       # Платное создание питомца
}


# Награды за достижения
ACHIEVEMENT_REWARDS = {
    'first_pet': 50,          # Первый питомец
    'pet_survived_1_hour': 25,    # Питомец прожил 1 час
    'pet_survived_1_day': 100,    # Питомец прожил 1 день
    'pet_reached_adult': 200,      # Питомец достиг взрослого возраста
    'perfect_health': 50,          # Идеальное здоровье
    'daily_login': 10,             # Ежедневный вход
    'weekly_streak': 100,          # Недельная серия
    'monthly_streak': 500          # Месячная серия
}

# Награды за действия
ACTION_REWARDS = {
    'daily_login': 5,         # Ежедневный вход
    'pet_care': 2,           # Уход за питомцем
    'stage_completion': 25,   # Завершение стадии
    'referral': 50,          # Приглашение друга
    'achievement': 10        # Получение достижения
}

# Награды за мини-игры
GAME_REWARD_ALLOWED_GAMES = ["runner", "puzzle"]
GAME_REWARD_COINS_PER_SCORE = {
    "runner": 0.1,  # каждые 10 очков = 1 монета
    "puzzle": 0.2,  # каждые 5 очков = 1 монета
}
GAME_REWARD_MAX_PER_REQUEST = 100

# Лимиты наград
REWARD_LIMITS = {
    'daily_login': 1,        # Раз в день
    'pet_care': 10,          # 10 раз в день
    'stage_completion': 1,   # Раз за стадию
    'referral': 10,          # 10 приглашений
    'achievement': 1         # Раз за достижение
}

# Настройки покупок
PURCHASE_OPTIONS = {
    'coins_100': {'coins': 100, 'price_usd': 0.99},
    'coins_500': {'coins': 500, 'price_usd': 3.99},
    'coins_1000': {'coins': 1000, 'price_usd': 6.99},
    'coins_2500': {'coins': 2500, 'price_usd': 14.99},
    'coins_5000': {'coins': 5000, 'price_usd': 24.99}
}

# ===== НАСТРОЙКИ РЫНКА/АУКЦИОНОВ =====
# Фичефлаг рынка
MARKET_ENABLED = True

# Длительность аукциона и soft-close
AUCTION_DEFAULT_DURATION_SECONDS = 60 * 60  # 60 минут
AUCTION_SOFT_CLOSE_SECONDS = 60             # продление при ставке в последние 60 сек

# Минимальный инкремент ставки
AUCTION_MIN_BID_INCREMENT_PERCENT = 5       # не ниже 5% от текущей цены
AUCTION_MIN_BID_INCREMENT_ABS = 1           # и не меньше 1 монеты

# Лимиты рынка
AUCTION_MAX_ACTIVE_PER_USER = 5

# Комиссия маркетплейса (учитывается в нетто-выплате продавцу; отдельная транзакция комиссии не создаётся)
MARKET_FEE_PERCENT = 5

# Пагинация
AUCTION_LIST_PAGE_SIZE = 20

# Telegram Stars настройки
TELEGRAM_STARS = {
    'enabled': True,
    'star_to_coin_ratio': 1,  # 1 звезда = 1 монета
    'min_stars_for_purchase': 1
}

# ===== НАСТРОЙКИ БЕЗОПАСНОСТИ =====
SECRET_KEY = os.getenv("SECRET_KEY", "telepets-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===== НАСТРОЙКИ БАЗЫ ДАННЫХ =====
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./telepets.db")

# ===== НАСТРОЙКИ API =====
API_HOST = os.getenv("API_HOST", "127.0.0.1")
def _parse_port(default_port: int = 3000) -> int:
    """Безопасно парсит порт из переменных окружения.

    Поддерживает случаи, когда переменная API_PORT содержит алиас вида
    "$PORT" (как на Render). В таком случае читаем реальное значение
    из переменной PORT. Если значений нет или они некорректны —
    возвращаем default_port.
    """
    raw = os.getenv("API_PORT")
    if raw:
        stripped = raw.strip()
        # Поддержка алиаса вида "$PORT"
        if stripped.startswith("$"):
            alias = stripped.lstrip("$")
            alias_val = os.getenv(alias)
            if alias_val and alias_val.isdigit():
                return int(alias_val)
        # Обычное числовое значение
        if stripped.isdigit():
            return int(stripped)

    # Платформенный порт (Render задаёт PORT)
    platform_port = os.getenv("PORT")
    if platform_port and platform_port.isdigit():
        return int(platform_port)

    return default_port

API_PORT = _parse_port(3000)

# Разрешить пропуск инициализации БД/фоновых задач при старте (для деплоя)
SKIP_DB_ON_STARTUP = os.getenv("SKIP_DB_ON_STARTUP", "false").strip().lower() in {"1", "true", "yes", "y"}

# Разрешить автозапуск Alembic миграций при старте
RUN_MIGRATIONS_ON_STARTUP = os.getenv("RUN_MIGRATIONS_ON_STARTUP", "false").strip().lower() in {"1", "true", "yes", "y"}

# ===== НАСТРОЙКИ МОНИТОРИНГА =====
MONITORING_UPDATE_INTERVAL = 300  # 5 минут
MONITORING_REQUEST_HISTORY_LIMIT = 1000
MONITORING_RECENT_REQUESTS_LIMIT = 500
MONITORING_AVERAGE_CALCULATION_LIMIT = 100

# ===== НАСТРОЙКИ ЗАДАЧ =====
TASK_SLEEP_INTERVAL = 60  # 1 минута
ACHIEVEMENT_CHECK_INTERVALS = {
    'hour': 3600,      # 1 час
    'day': 86400,      # 1 день
    'perfect_health': 100  # Идеальное здоровье
}

# ===== НАСТРОЙКИ ВАЛИДАЦИИ =====
USER_ID_MAX_LENGTH = 50
USER_ID_MIN_LENGTH = 1
PET_NAME_MAX_LENGTH = 30
PET_NAME_MIN_LENGTH = 1
USER_ID_PATTERN = r'^[0-9a-zA-Z_-]+$'
# Имя питомца: только английские буквы (по запросу), цифры и пробелы/дефисы/подчеркивания запрещены
# Если разрешены только буквы (без цифр и символов): используйте r'^[A-Za-z]+$'
PET_NAME_PATTERN = r'^[A-Za-z]+$'

# ===== НАСТРОЙКИ HTTP =====
HTTP_TIMEOUT = 10
HTTP_STATUS_SUCCESS = 200

# ===== НАСТРОЙКИ ВЕРСИИ =====
APP_VERSION = "1.1.0" 

# ===== НАСТРОЙКИ ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ (Hugging Face) =====
# Эти настройки унифицированы с генератором в `PetsGenerator/` и
# используются сервером напрямую. Новые глобальные переменные следует
# добавлять сюда.

# Токен доступа к Hugging Face Inference API
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Современные модели для генерации изображений на Hugging Face
MODELS = {
    "stable-diffusion-xl": {
        "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
        "description": "Stable Diffusion XL - лучшее качество"
    },
    "flux1-dev": {
        "model_id": "black-forest-labs/FLUX.1-dev",
        "description": "FLUX.1-dev - быстрая генерация с хорошим качеством"
    },
    "flux1-schnell": {
        "model_id": "black-forest-labs/FLUX.1-schnell",
        "description": "FLUX.1-schnell - сверхбыстрая генерация"
    }
}

# Базовые настройки для генерации изображений
DEFAULT_SETTINGS = {
    "steps": 30,
    "guidance_scale": 8.5,
    "width": 1024,
    "height": 1024,
    "negative_prompt": (
        "blurry, low quality, watermark, text, logo, extra limbs, cropped, cut off, deformed, "
        "ugly, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, poorly drawn hands, "
        "missing limb, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, "
        "long body, mutated hands and fingers, out of frame, double, two heads, blurred, ugly, disfigured, "
        "too many limbs, deformed, repetitive, black and white, grainy, extra limbs, bad anatomy, high contrast, "
        "overexposed, underexposed, over-saturated, under-saturated, low quality, low quality multiple views, "
        "worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, "
        "cartoon, anime, illustration, drawing, painting, sketch, 2d, flat, stylized, unrealistic, fantasy art style, digital art style"
    )
}

# Предустановленные настройки качества
QUALITY_PRESETS = {
    "fast": {"steps": 20, "guidance_scale": 7.0, "width": 512, "height": 512, "description": "Быстрая генерация"},
    "balanced": {"steps": 25, "guidance_scale": 8.0, "width": 768, "height": 768, "description": "Баланс"},
    "high": {"steps": 30, "guidance_scale": 8.5, "width": 1024, "height": 1024, "description": "Высокое качество"},
    "ultra": {"steps": 40, "guidance_scale": 9.0, "width": 1024, "height": 1024, "description": "Макс. качество"}
}

# Настройки для работы с файлами (используем общий кэш проекта)
FILE_SETTINGS = {
    "output_dir": os.path.join("cache", "pet_images"),
    "max_filename_length": 50,
    "safe_filename_chars": r'[<>:"/\\|?*]',
    "replacement_char": "_",
}

# Промпты для реалистичности
REALISM_PROMPTS = {
    "photorealistic": "photorealistic, hyperrealistic, ultra realistic, detailed skin texture, natural lighting, professional photography, wildlife photography, nature documentary, National Geographic style, detailed fur, detailed scales, detailed feathers, natural environment, realistic anatomy, detailed eyes, detailed features, high resolution, 8k, professional camera, natural colors, realistic shadows, depth of field, bokeh, natural pose, realistic proportions",
    "scientific": "scientific illustration, biological accuracy, anatomical correctness, detailed study, specimen photography, museum quality, scientific documentation, precise details, accurate proportions, realistic textures, natural behavior, environmental context, detailed observation, scientific accuracy, research quality, specimen detail, natural habitat, ecological accuracy",
    "wildlife": "wildlife photography, natural behavior, wild animal, natural habitat, environmental photography, nature documentary, realistic animal behavior, natural lighting, outdoor photography, natural environment, realistic fur texture, realistic scale texture, realistic feather texture, natural pose, realistic proportions, natural colors, realistic shadows, depth of field, natural background, ecological accuracy",
    "portrait": "professional portrait photography, studio lighting, natural skin texture, detailed features, realistic eyes, natural expression, professional camera, high resolution, detailed hair, natural lighting, realistic shadows, depth of field, professional photography, natural colors, realistic proportions, detailed anatomy, natural pose, realistic details",
}

# Стадии развития для генератора изображений (синхронизация с PetState/STAGE_ORDER)
CREATURE_LIFE_STAGES = {
    "egg": {"ru": "яйцо", "en": "egg"},
    "baby": {"ru": "детёныш", "en": "hatchling"},
    "adult": {"ru": "взрослая особь", "en": "adult"},
}

STAGE_PROMPT_MODIFIERS = {
    "egg": {
        "ru": "одиночное яйцо, узнаваемые узоры на скорлупе, отсылки к покровам и окраске вида, гладкая/текстурная скорлупа, лёгкие намёки на форму будущих придатков",
        "en": "single egg, recognizable shell patterns, hints of the species' surface and palette, textured shell, subtle motifs of future appendages",
    },
    "baby": {
        "ru": "умилительные пропорции, крупные глаза, большая голова, мягкие черты, короткие конечности, нежные покровы",
        "en": "cute proportions, large eyes, bigger head, soft features, short limbs, tender coverings",
    },
    "adult": {
        "ru": "полностью сформировавшиеся признаки вида, выразительная анатомия, зрелые способности",
        "en": "fully developed species traits, expressive anatomy, mature abilities",
    },
}

STAGE_NEGATIVE_PROMPTS = {
    "egg": "eyes, pupils, eyelids, face, mouth, beak, teeth, lips, limbs, legs, arms, hands, feet, claws, wings, tail, open egg, cracked shell, broken shell, embryo, fetus, creature visible, animal inside, multiple eggs, nest, characters, text, logo",
    "baby": "adult proportions, muscular, overly defined muscles, scars, battle damage, aggressive posture, fully developed horns, heavy armor, weapons, complex accessories, elderly features, deep wrinkles",
    "adult": "baby-like proportions, chibi, oversized eyes, pacifier, toys, diaper, cute cartoon style, egg shell, nest",
}

API_SETTINGS = {
    "base_url": "https://api-inference.huggingface.co",
    "timeout": 120,
    "default_model": "black-forest-labs/FLUX.1-dev",
}

GENERATION_DEFAULTS = {
    "preferred_model": "flux1-dev",
    "realism_style": "photorealistic",
    "quality_preset": "high",
}

# Вспомогательные функции доступа к настройкам генерации
def get_quality_settings(preset: str = "high"):
    return QUALITY_PRESETS.get(preset, QUALITY_PRESETS["high"]).copy()

def get_model_info(model_name: str):
    return MODELS.get(model_name, {}).copy()

def get_all_models():
    return MODELS.copy()

def get_default_settings():
    return DEFAULT_SETTINGS.copy()

def get_file_settings():
    return FILE_SETTINGS.copy()

def get_api_settings():
    return API_SETTINGS.copy()

def get_realism_prompt(style: str = "photorealistic") -> str:
    return REALISM_PROMPTS.get(style, REALISM_PROMPTS["photorealistic"])

def get_all_realism_styles():
    return REALISM_PROMPTS.copy()

def get_generation_defaults():
    return GENERATION_DEFAULTS.copy()

def get_stage_negative_prompt(stage_key: str, include_global: bool = True) -> str:
    base = DEFAULT_SETTINGS.get("negative_prompt", "") if include_global else ""
    stage_np = STAGE_NEGATIVE_PROMPTS.get(stage_key, "")
    if base and stage_np:
        return f"{base}, {stage_np}"
    return stage_np or base

# ===== НАСТРОЙКИ АНОНИМНОСТИ =====

# Настройки анонимности пользователей
ANONYMOUS_MODE_ENABLED = True
MIN_DISPLAY_NAME_LENGTH = 2
MAX_DISPLAY_NAME_LENGTH = 20
DEFAULT_ANONYMOUS_MODE = False
ANONYMOUS_NAME_PLACEHOLDER = "Анонимный игрок"