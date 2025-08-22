## Telepets v1.1 — документация по функционалу

Этот документ описывает пользовательские фичи, механику игры, основные API и архитектурные аспекты проекта Telepets (Telegram Web App + FastAPI backend).

### Обзор

- **Назначение**: современный «тамагочи» для Telegram Web Apps с генерацией изображений питомца, экономикой и мониторингом.
- **Версия**: 1.1.0 (`config/settings.py: APP_VERSION`).
- **Технологии**: FastAPI, SQLAlchemy (Async), SQLite (по умолчанию), React + TypeScript + Vite + Tailwind, Framer Motion.
- **Документация API**: Swagger доступен по `/docs`, ReDoc — по `/redoc`.
- **Примечание по настройкам**: все глобальные настройки и константы централизованы в `backend/config/settings.py` (см. раздел Конфигурация).
- **Миграции БД**: Alembic (каталог `alembic/`, команды `alembic upgrade head`).

---

### Игровые фичи

- **Жизненный цикл питомца** (`models.Pet`, `models.PetState`, `backend/tasks.py`):
  - Стадии: `egg` → `baby` → `adult` → `dead`.
  - Переход на следующую стадию по таймеру (`STAGE_TRANSITION_INTERVAL`), учитывается время начала текущей стадии.
  - Автоматическое уменьшение здоровья по этапам (`HEALTH_DOWN_INTERVALS`, `HEALTH_DOWN_AMOUNTS`).
  - Увеличение здоровья действием игрока (`/health_up`, различная прибавка по стадиям `HEALTH_UP_AMOUNTS`).
  - Смерть при достижении `HEALTH_MIN`.

- **Здоровье** (`HEALTH_MAX`, `HEALTH_LOW`, `HEALTH_MIN`):
  - Здоровье хранится в `Pet.health` (0–100).
  - При критическом уровне создаются уведомления; при нуле — фиксация смерти.
  - Специальные сообщения по стадиям (`STAGE_MESSAGES`).

- **Достижения и награды** (`backend/economy.py: EconomyService.check_achievement`):
  - Примеры: первый питомец, выжил 1 час/1 день, достиг взрослой стадии, идеальное здоровье.
  - Награда — монеты (см. Экономика).

---

### Генерация изображений питомца

- **API эндпоинты** (`backend/api/pet_images.py`):
  - `GET /pet-images/{user_id}/{pet_name}` — отдать или сгенерировать картинку текущей стадии.
  - `GET /pet-images/{user_id}/{pet_name}/metadata` — метаданные изображения (всегда доступны для SVG-fallback).
  - `POST /pet-images/{user_id}/regenerate` — перегенерация изображений всех питомцев пользователя.
  - `DELETE /pet-images/cache` — очистить кэш изображений.

- **Как это работает (актуально)**:
  - При создании питомца сохраняются промпты для всех стадий и полное описание существа (`creature_json`) в БД; для стадии `egg` генерируется и сохраняется картинка в `image_egg_b64`.
  - Эндпоинт изображений читает и отдаёт картинку строго из БД (`image_*_b64`). При отсутствии — генерирует по промпту, сохраняет в БД и возвращает.
  - Метаданные генерации во время работы могут сохраняться во временные файлы; источником истины является БД.

- **Промпты**:
  - Для `egg/baby/adult` промпты хранятся в БД и/или файловом хранилище (`prompt_store`).
  - Есть негативные промпты по стадиям и общие `DEFAULT_SETTINGS.negative_prompt`.

Подробности API генерации: см. `backend/docs/pet_images_api.md`.

---

### Экономика

- **Сущности** (`models.User`, `models.Wallet`, `models.Transaction`, `models.Achievement`):
  - Кошелек (`Wallet`): баланс монет, всего заработано/потрачено.
  - Транзакции: типы `purchase | earning | spending | bonus | refund`, статус.
  - Достижения: запись факта получения + монетная награда.

- **Начальные значения и лимиты**:
  - Начальные монеты пользователя — `INITIAL_COINS` (кошелек создается автоматически при первом обращении).
  - Стоимости действий — `ACTION_COSTS` (зависят от стадии для `health_up`).
  - Награды и лимиты — `ACHIEVEMENT_REWARDS`, `ACTION_REWARDS`, `REWARD_LIMITS`.

- **API эндпоинты** (`backend/api/economy.py`):
  - `GET /economy/wallet/{user_id}` — создать при необходимости и вернуть кошелек.
  - `GET /economy/balance/{user_id}` — текущий баланс.
  - `GET /economy/transactions/{user_id}?limit=N` — последние транзакции.
  - `GET /economy/stats/{user_id}` — агрегированные статистики кошелька и транзакций.
  - `POST /economy/purchase/{user_id}?package_id=...` — симуляция покупки монет (настройки в `PURCHASE_OPTIONS`).
  - `GET /economy/actions/costs` — стоимости действий и пакеты.
  - `POST /economy/actions/{user_id}/health_up` — увеличить здоровье с оплатой (списывает монеты, затем вызывает логику `health_up`).
  - `POST /economy/rewards/{user_id}/daily_login` — ежедневная награда.

---

### Мониторинг и метрики

- **Middleware мониторинга** (`backend/monitoring.py: MonitoringMiddleware`):
  - Измеряет время ответа для каждого запроса, собирает ошибки.
  - Фоновая задача обновляет метрики питомцев (общее число, живые/мертвые, распределение по стадиям).

- **API эндпоинты** (`backend/api/monitoring.py`):
  - `GET /monitoring/health` — статус системы (версия, время).
  - `GET /monitoring/metrics` — метрики производительности и питомцев.
  - `GET /monitoring/stats` — агрегированная статистика (детальная по питомцам/уведомлениям).
  - `GET /monitoring/users/{user_id}/history` — история объектов пользователя (питомцы, уведомления).

---

### Фоновые задачи

- **Уменьшение здоровья и переходы** (`backend/tasks.py`):
  - Цикл раз в `TASK_SLEEP_INTERVAL` обрабатывает всех живых питомцев.
  - Уменьшает здоровье по текущей стадии, создает уведомления о низком здоровье.
  - Фиксирует смерть и очищает изображения в БД (`StageLifecycleService.wipe_images_on_death`).
  - По таймеру переводит на следующую стадию, сохраняет артефакты (`persist_stage_artifacts`).
  - Проверяет достижения (`check_pet_achievements`).

Запуск задач происходит в `backend/main.py` в `lifespan`.

---

### Telegram-уведомления

- **Клиент** (`backend/telegram_client.py`):
  - Использует Bot API для отправки сообщений в событиях: низкое здоровье, смерть, переход стадии.
  - Токен `TELEGRAM_BOT_TOKEN` — обязателен для реальной отправки (иначе предупреждение, вызовы пропускаются).

---

### Основные API по питомцам

- `POST /create?user_id=&name=` — создать питомца (валидируется `user_id` и `name` по паттернам в настройках). Создаёт кошелек при необходимости, подготавливает промпты/картинку для `egg`.
- `POST /health_up?user_id=` — увеличить здоровье с учётом стадии, без списания монет.
- `GET /summary?user_id=` — расширенная сводка активного питомца пользователя (включая `image_url`, таймер до следующей стадии, кошелёк, `creature`, `prompts`).
- `GET /summary/all?user_id=` — расширенная сводка по всем питомцам пользователя (также включает `creature`, `prompts`).

Для отладки доступны руты `backend/api/debug.py` (проверка БД, выборки сущностей, создание тест-питомца).

---

### Фронтенд: основные экраны

- `Home` — обзор питомца, создание питомца, быстрые действия (`health_up`), краткая статистика и баланс.
- `Play` — «боевой» экран питомца: изображение стадии, здоровье, таймер, CTA-кнопки действий.
- `History` — история всех питомцев: статус, здоровье, временная линия.
- `Economy` — кошелек, транзакции, ежедневная награда, покупка монет, стоимости действий.
- `Settings` — настройки пользователя (ID), тема, справка по API и игре.

Фронтенд использует `frontend/src/lib/api.ts` для обращения к API и хуки `usePet`, `useEconomy` для работы с данными (React Query).

---

### Конфигурация и окружение

- Все глобальные константы и настройки — в `backend/config/settings.py`:
  - Здоровье: `HEALTH_MAX`, `HEALTH_LOW`, `HEALTH_MIN`, интервалы уменьшения/переходов.
  - Экономика: `INITIAL_COINS`, `ACTION_COSTS`, `PURCHASE_OPTIONS`, награды и лимиты.
  - Мониторинг: интервалы и лимиты истории.
  - Генерация изображений (HF): токен `HF_API_TOKEN`, пресеты качества/модели, реализм-промпты, negative prompts, файловый кэш.
  - Безопасность: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
  - База: `DATABASE_URL` (по умолчанию SQLite), API-хост/порт.

- Файл `.env` (хранится у вас, пример — `env.example`):
  - `TELEGRAM_BOT_TOKEN`, `HF_API_TOKEN`, `DATABASE_URL`, `API_HOST`, `API_PORT`, `SECRET_KEY` и др.

- Кэш изображений: `cache/pet_images/` (PNG/SVG + `*_data.json`).

---

### Миграции Alembic

- Инициализация: `alembic init alembic`
- Конфигурация: `alembic.ini`, `alembic/env.py` (подключение к `DATABASE_URL`)
- Генерация ревизии: `alembic revision -m "add creature_json column"`
- Применение: `alembic upgrade head`
- Откат: `alembic downgrade -1`

---

### Расширение функционала

- Новые глобальные настройки: добавляйте в `backend/config/settings.py` (по правилу проекта).
- Новые эндпоинты: создавайте в `backend/api/*`, подключайте в `backend/main.py` через `app.include_router(...)`. Обновляйте Swagger-описания (docstrings + типы ответов) — они появятся в `/docs` автоматически.
- Новая механика стадий/изображений: расширяйте `StageLifecycleService` и/или генераторы в `backend/generator/*` и `pet_generator_alternative.py`.
- Новые действия экономики: добавляйте стоимости в `ACTION_COSTS`, реализуйте логику в `EconomyService` и соответствующие эндпоинты.

---

### Быстрый старт API (примеры)

```http
POST /create?user_id=273065571&name=Zaxc
GET  /summary?user_id=273065571
POST /health_up?user_id=273065571
GET  /pet-images/273065571/Zaxc
GET  /economy/wallet/273065571
POST /economy/actions/273065571/health_up
```

Ответы детально описаны в Swagger (`/docs`).

---

### Известные ограничения и заметки

- Имя питомца по умолчанию строго латиницей (`PET_NAME_PATTERN = ^[A-Za-z]+$`).
- HF-генерация требует `HF_API_TOKEN`. Без токена всегда сработает SVG-fallback.
- Уведомления Telegram требуют валидного `TELEGRAM_BOT_TOKEN`.
- По умолчанию база — локальный SQLite. Для продакшена используйте внешний DB URL (Postgres и т. п.).

---

### Ссылки

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- Док по изображениям: `backend/docs/pet_images_api.md`


