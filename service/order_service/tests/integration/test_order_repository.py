import uuid
from decimal import Decimal

import pytest

from app.domain.entity.order_entity import CreateOrder, CreateOrderItem, OrderStatus
from app.infrastructure.db.repo.order_repo import SQLAlchemyOrderRepo


def _make_order(user_id: uuid.UUID) -> CreateOrder:
    product_id = uuid.uuid4()
    return CreateOrder(
        user_id=user_id,
        status=OrderStatus.PENDING_PAYMENT,
        total_amount=Decimal("390000"),
        delivery_address="Astana, Mangilik El 55",
        payment_method="kaspi",
        items=[
            CreateOrderItem(
                product_id=product_id,
                product_name="Gaming PC RTX 4060",
                quantity=1,
                unit_price=Decimal("390000"),
                total_price=Decimal("390000"),
            )
        ],
    )


@pytest.mark.asyncio
async def test_create_and_get_order(db_session):
    repo = SQLAlchemyOrderRepo(db_session)
    user_id = uuid.uuid4()

    order = await repo.create(_make_order(user_id))

    assert order.status == OrderStatus.PENDING_PAYMENT
    assert order.total_amount == Decimal("390000")
    assert len(order.items) == 1
    assert order.items[0].product_name == "Gaming PC RTX 4060"

    fetched = await repo.get_by_id(order.id)
    assert fetched is not None
    assert fetched.id == order.id
    assert len(fetched.items) == 1


@pytest.mark.asyncio
async def test_update_status(db_session):
    repo = SQLAlchemyOrderRepo(db_session)
    user_id = uuid.uuid4()

    order = await repo.create(_make_order(user_id))
    updated = await repo.update_status(order.id, OrderStatus.PAID)

    assert updated.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_get_by_user(db_session):
    repo = SQLAlchemyOrderRepo(db_session)
    user_id = uuid.uuid4()

    await repo.create(_make_order(user_id))
    await repo.create(_make_order(user_id))

    orders = await repo.get_by_user(user_id)
    assert len(orders) == 2


@pytest.mark.asyncio
async def test_items_are_snapshots(db_session):
    repo = SQLAlchemyOrderRepo(db_session)
    user_id = uuid.uuid4()

    order = await repo.create(_make_order(user_id))
    item = order.items[0]

    assert item.product_name == "Gaming PC RTX 4060"
    assert item.unit_price == Decimal("390000")
