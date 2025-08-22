"""
add_status_to_pets

Revision ID: 2025_08_16_000002
Revises: 0001_add_creature_json
Create Date: 2025-08-16 00:00:02
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_08_16_000002'
down_revision = '0001_add_creature_json'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_cols = {c['name'] for c in insp.get_columns('pets')}

    # Создаём Enum, если требуется (на SQLite это будет VARCHAR)
    pet_life_status = sa.Enum('alive', 'dead', name='petlifestatus')
    try:
        pet_life_status.create(bind, checkfirst=True)
    except Exception:
        pass

    # Добавляем колонку status, если её ещё нет
    if 'status' not in existing_cols:
        op.add_column('pets', sa.Column('status', pet_life_status, nullable=False, server_default='alive'))
        # Нормализуем значения по умолчанию
        op.execute("UPDATE pets SET status='alive' WHERE status IS NULL")

    # Если бы были данные, можно было бы выполнить миграцию значений из state == 'dead' → status = 'dead'
    # и далее скорректировать state на предыдущую стадию (недоступно без знания истории).
    # Ваша таблица пустая, поэтому этот шаг не требуется.


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_cols = {c['name'] for c in insp.get_columns('pets')}
    if 'status' in existing_cols:
        op.drop_column('pets', 'status')
    pet_life_status = sa.Enum('alive', 'dead', name='petlifestatus')
    try:
        pet_life_status.drop(bind, checkfirst=True)
    except Exception:
        pass


