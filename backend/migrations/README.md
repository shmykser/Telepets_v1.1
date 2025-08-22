# Alembic

Команды:

```bash
# Инициализация уже выполнена (см. backend/migrations)

# Создать миграцию по изменениям моделей
alembic revision --autogenerate -m "add creature_json to pets"

# Применить миграции
alembic upgrade head

# Откатить на шаг назад
alembic downgrade -1
```

Конфигурация: `alembic.ini` и `backend/migrations/env.py`.


