"""init

Revision ID: b2c3d4e5f6a7
Revises:
Create Date: 2026-06-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('slug', sa.String(length=256), nullable=False),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=True)

    op.create_table(
        'brands',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('slug', sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_brands_slug'), 'brands', ['slug'], unique=True)

    op.create_table(
        'products',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=512), nullable=False),
        sa.Column('slug', sa.String(length=512), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=True),
        sa.Column('brand_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_products_slug'), 'products', ['slug'], unique=True)
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'])
    op.create_index(op.f('ix_products_brand_id'), 'products', ['brand_id'])

    op.create_table(
        'product_images',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_product_images_product_id'), 'product_images', ['product_id'])

    op.create_table(
        'product_attributes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('value', sa.String(length=512), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_product_attributes_product_id'), 'product_attributes', ['product_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_product_attributes_product_id'), table_name='product_attributes')
    op.drop_table('product_attributes')
    op.drop_index(op.f('ix_product_images_product_id'), table_name='product_images')
    op.drop_table('product_images')
    op.drop_index(op.f('ix_products_brand_id'), table_name='products')
    op.drop_index(op.f('ix_products_category_id'), table_name='products')
    op.drop_index(op.f('ix_products_slug'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_brands_slug'), table_name='brands')
    op.drop_table('brands')
    op.drop_index(op.f('ix_categories_slug'), table_name='categories')
    op.drop_table('categories')
