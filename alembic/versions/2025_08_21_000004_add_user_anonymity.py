"""Add user anonymity fields

Revision ID: 000004
Revises: 000003
Create Date: 2025-08-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '000004'
down_revision = '2025_08_20_000003'
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем новые поля для анонимности
    op.add_column('users', sa.Column('telegram_username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('display_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='0'))
    
    # Создаем индекс для быстрого поиска по display_name
    op.create_index(op.f('ix_users_display_name'), 'users', ['display_name'], unique=False)
    
    # Переносим существующие username в telegram_username
    op.execute("UPDATE users SET telegram_username = username WHERE telegram_username IS NULL AND username IS NOT NULL")


def downgrade():
    # Удаляем индекс
    try:
        op.drop_index(op.f('ix_users_display_name'), table_name='users')
    except:
        pass
    
    # Удаляем новые поля
    try:
        op.drop_column('users', 'is_anonymous')
        op.drop_column('users', 'display_name')
        op.drop_column('users', 'telegram_username')
    except:
        pass
