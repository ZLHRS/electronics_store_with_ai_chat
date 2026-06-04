"""init

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-06-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('auth_user_id', sa.UUID(), nullable=False),
        sa.Column('first_name', sa.String(length=128), nullable=True),
        sa.Column('last_name', sa.String(length=128), nullable=True),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('city', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_profiles_auth_user_id'), 'user_profiles', ['auth_user_id'], unique=True)

    op.create_table(
        'user_addresses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('city', sa.String(length=128), nullable=False),
        sa.Column('street', sa.String(length=256), nullable=False),
        sa.Column('house', sa.String(length=32), nullable=False),
        sa.Column('apartment', sa.String(length=32), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_addresses_user_id'), 'user_addresses', ['user_id'], unique=False)

    op.create_table(
        'user_favorites',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'product_id'),
    )

    op.create_table(
        'user_view_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'product_id'),
    )
    op.create_index(op.f('ix_user_view_history_user_id'), 'user_view_history', ['user_id'], unique=False)

    op.create_table(
        'user_preferences',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('language', sa.String(length=8), nullable=False, server_default='ru'),
        sa.Column('currency', sa.String(length=8), nullable=False, server_default='KZT'),
        sa.Column('notification_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('preferred_categories', JSONB(), nullable=False, server_default='[]'),
        sa.Column('min_budget', sa.Integer(), nullable=True),
        sa.Column('max_budget', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_preferences')
    op.drop_index(op.f('ix_user_view_history_user_id'), table_name='user_view_history')
    op.drop_table('user_view_history')
    op.drop_table('user_favorites')
    op.drop_index(op.f('ix_user_addresses_user_id'), table_name='user_addresses')
    op.drop_table('user_addresses')
    op.drop_index(op.f('ix_user_profiles_auth_user_id'), table_name='user_profiles')
    op.drop_table('user_profiles')
