"""
add market auction tables and coins_locked

Revision ID: 2025_08_20_000003
Revises: 2025_08_16_000002
Create Date: 2025-08-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_08_20_000003'
down_revision = '2025_08_16_000002'
branch_labels = None
depends_on = None


def upgrade():
    # coins_locked
    with op.batch_alter_table('wallets') as batch_op:
        batch_op.add_column(sa.Column('coins_locked', sa.Integer(), nullable=False, server_default='0'))
    op.execute("UPDATE wallets SET coins_locked = 0 WHERE coins_locked IS NULL")

    # auctions
    op.create_table(
        'auctions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('pet_id', sa.Integer(), sa.ForeignKey('pets.id'), nullable=False),
        sa.Column('seller_user_id', sa.String(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('start_price', sa.Integer(), nullable=False),
        sa.Column('current_price', sa.Integer(), nullable=False),
        sa.Column('buy_now_price', sa.Integer(), nullable=True),
        sa.Column('min_increment_abs', sa.Integer(), nullable=True),
        sa.Column('min_increment_pct', sa.Integer(), nullable=True),
        sa.Column('soft_close_seconds', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('status', sa.Enum('active','completed','cancelled','expired', name='auctionstatus'), nullable=False, server_default='active'),
        sa.Column('current_winner_user_id', sa.String(), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_auctions_end_time_status', 'auctions', ['status', 'end_time'])

    # auction_bids
    op.create_table(
        'auction_bids',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('auction_id', sa.Integer(), sa.ForeignKey('auctions.id'), nullable=False),
        sa.Column('bidder_user_id', sa.String(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_auction_bids_auction_id', 'auction_bids', ['auction_id'])

    # wallet_holds
    op.create_table(
        'wallet_holds',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('auction_id', sa.Integer(), sa.ForeignKey('auctions.id'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('active','released','captured', name='walletholdstatus'), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_wallet_holds_user_id', 'wallet_holds', ['user_id'])
    op.create_index('ix_wallet_holds_auction_id', 'wallet_holds', ['auction_id'])

    # pet_ownership_history
    op.create_table(
        'pet_ownership_history',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('pet_id', sa.Integer(), sa.ForeignKey('pets.id'), nullable=False),
        sa.Column('from_user_id', sa.String(), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('to_user_id', sa.String(), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('price', sa.Integer(), nullable=True),
        sa.Column('auction_id', sa.Integer(), sa.ForeignKey('auctions.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('pet_ownership_history')
    op.drop_index('ix_wallet_holds_user_id', table_name='wallet_holds')
    op.drop_index('ix_wallet_holds_auction_id', table_name='wallet_holds')
    op.drop_table('wallet_holds')
    try:
        op.execute("DROP TYPE IF EXISTS walletholdstatus")
    except Exception:
        pass

    op.drop_index('ix_auction_bids_auction_id', table_name='auction_bids')
    op.drop_table('auction_bids')

    op.drop_index('ix_auctions_end_time_status', table_name='auctions')
    op.drop_table('auctions')
    try:
        op.execute("DROP TYPE IF EXISTS auctionstatus")
    except Exception:
        pass

    with op.batch_alter_table('wallets') as batch_op:
        batch_op.drop_column('coins_locked')


