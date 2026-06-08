import uuid
from decimal import Decimal

import pytest

from app.domain.entity.cart_entity import CartStatus, CreateCartItem
from app.infrastructure.db.repo.cart_item_repo import SQLAlchemyCartItemRepo
from app.infrastructure.db.repo.cart_repo import SQLAlchemyCartRepo


@pytest.mark.asyncio
async def test_get_or_create_active_creates_cart(db_session):
    repo = SQLAlchemyCartRepo(db_session)
    user_id = uuid.uuid4()

    cart = await repo.get_or_create_active(user_id)

    assert cart.user_id == user_id
    assert cart.status == CartStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_or_create_returns_existing(db_session):
    repo = SQLAlchemyCartRepo(db_session)
    user_id = uuid.uuid4()

    first = await repo.get_or_create_active(user_id)
    second = await repo.get_or_create_active(user_id)

    assert first.id == second.id


@pytest.mark.asyncio
async def test_add_and_get_cart_item(db_session):
    cart_repo = SQLAlchemyCartRepo(db_session)
    item_repo = SQLAlchemyCartItemRepo(db_session)
    user_id = uuid.uuid4()
    product_id = uuid.uuid4()

    cart = await cart_repo.get_or_create_active(user_id)
    item = await item_repo.create(
        CreateCartItem(
            cart_id=cart.id, product_id=product_id, quantity=2, unit_price=Decimal("50000")
        )
    )

    assert item.quantity == 2
    assert item.unit_price == Decimal("50000")

    items = await item_repo.get_by_cart(cart.id)
    assert len(items) == 1


@pytest.mark.asyncio
async def test_update_quantity(db_session):
    cart_repo = SQLAlchemyCartRepo(db_session)
    item_repo = SQLAlchemyCartItemRepo(db_session)
    user_id = uuid.uuid4()

    cart = await cart_repo.get_or_create_active(user_id)
    item = await item_repo.create(
        CreateCartItem(
            cart_id=cart.id, product_id=uuid.uuid4(), quantity=1, unit_price=Decimal("10000")
        )
    )
    updated = await item_repo.update_quantity(item.id, 5)

    assert updated.quantity == 5


@pytest.mark.asyncio
async def test_delete_by_cart_clears_items(db_session):
    cart_repo = SQLAlchemyCartRepo(db_session)
    item_repo = SQLAlchemyCartItemRepo(db_session)
    user_id = uuid.uuid4()

    cart = await cart_repo.get_or_create_active(user_id)
    await item_repo.create(
        CreateCartItem(
            cart_id=cart.id, product_id=uuid.uuid4(), quantity=1, unit_price=Decimal("5000")
        )
    )
    await item_repo.delete_by_cart(cart.id)

    items = await item_repo.get_by_cart(cart.id)
    assert items == []
