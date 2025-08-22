"""add creature_json column to pets

Revision ID: 0001_add_creature_json
Revises: 
Create Date: 2025-08-12 00:00:01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_add_creature_json'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('pets') as batch_op:
        batch_op.add_column(sa.Column('creature_json', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('pets') as batch_op:
        batch_op.drop_column('creature_json')


