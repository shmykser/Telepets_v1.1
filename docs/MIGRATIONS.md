## Миграции БД (Alembic)

### Инициализация

```bash
alembic init alembic
```

Проверьте `alembic.ini` и `alembic/env.py` — подключение к `DATABASE_URL` из `.env`/`backend/config/settings.py`.

### Создание ревизии

```bash
alembic revision -m "add creature_json column to pets"
```

В созданном файле ревизии:

```python
def upgrade():
    # добавляем колонку creature_json, если её нет
    from alembic import op
    import sqlalchemy as sa
    with op.batch_alter_table('pets') as batch_op:
        batch_op.add_column(sa.Column('creature_json', sa.Text(), nullable=True))


def downgrade():
    from alembic import op
    with op.batch_alter_table('pets') as batch_op:
        batch_op.drop_column('creature_json')
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграции

```bash
alembic downgrade -1
```

### Примечания

- В dev-режиме SQLite допускается автосоздание таблиц `Base.metadata.create_all`. Для синхронизации схемы между средами используйте Alembic как основной механизм.
- Добавляя новые поля в модели, создавайте миграции, а не полагайтесь на автосоздание.


