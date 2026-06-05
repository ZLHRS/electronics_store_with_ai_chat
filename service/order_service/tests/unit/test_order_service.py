import datetime
import uuid
from decimal import Decimal

import pytest

from app.application.dto.order_dto import CreateOrderCommand, UpdateStatusCommand
from app.application.service.order_service import OrderService
from app.domain.entity.order_entity import CreateOrder, OrderEntity, OrderStatus
from app.exceptions import (
    CartEmptyError,
    OrderAccessDeniedError,
    OrderCancelForbiddenError,
    OrderNotFoundError,
    ProductNotAvailableError,
)
from app.infrastructure.cart_client import CartData, CartItemData
from app.infrastructure.product_client import ProductData


class FakeOrderRepo:
    def __init__(self):
        self._store: dict[uuid.UUID, OrderEntity] = {}

    async def get_by_id(self, order_id: uuid.UUID) -> OrderEntity | None:
        return self._store.get(order_id)

    async def get_by_user(self, user_id: uuid.UUID) -> list[OrderEntity]:
        return [o for o in self._store.values() if o.user_id == user_id]

    async def create(self, data: CreateOrder) -> OrderEntity:
        now = datetime.datetime.now(datetime.UTC)
        order = OrderEntity(
            id=uuid.uuid4(),
            user_id=data.user_id,
            status=data.status,
            total_amount=data.total_amount,
            delivery_address=data.delivery_address,
            payment_method=data.payment_method,
            created_at=now,
            updated_at=now,
            items=[],
        )
        self._store[order.id] = order
        return order

    async def update_status(self, order_id: uuid.UUID, status: str) -> OrderEntity:
        order = self._store[order_id]
        updated = OrderEntity(
            id=order.id, user_id=order.user_id, status=status,
            total_amount=order.total_amount, delivery_address=order.delivery_address,
            payment_method=order.payment_method,
            created_at=order.created_at, updated_at=datetime.datetime.now(datetime.UTC),
            items=order.items,
        )
        self._store[order_id] = updated
        return updated


class FakeCartClient:
    def __init__(self, cart: CartData | None):
        self._cart = cart
        self.cleared = False

    async def get_cart(self, access_token: str) -> CartData | None:
        return self._cart

    async def clear_cart(self, access_token: str) -> None:
        self.cleared = True


class FakeProductClient:
    def __init__(self, products: dict[uuid.UUID, ProductData]):
        self._products = products

    async def get_product(self, product_id: uuid.UUID) -> ProductData | None:
        return self._products.get(product_id)


def _make_cart(*product_ids: uuid.UUID) -> CartData:
    return CartData(
        id=uuid.uuid4(),
        items=[
            CartItemData(product_id=pid, quantity=1, unit_price=Decimal("100000"))
            for pid in product_ids
        ],
    )


def _make_product(product_id: uuid.UUID, status: str = "active") -> ProductData:
    return ProductData(id=product_id, name="Gaming PC", price=Decimal("100000"), status=status)


@pytest.mark.asyncio
async def test_create_order_success():
    product_id = uuid.uuid4()
    user_id = uuid.uuid4()
    cart_client = FakeCartClient(_make_cart(product_id))
    product_client = FakeProductClient({product_id: _make_product(product_id)})
    service = OrderService(FakeOrderRepo(), cart_client, product_client)

    result = await service.create_order(
        user_id, "token",
        CreateOrderCommand(delivery_address="Astana, Mangilik El 55", payment_method="kaspi"),
    )

    assert result.status == OrderStatus.PENDING_PAYMENT
    assert result.total_amount == Decimal("100000")
    assert cart_client.cleared


@pytest.mark.asyncio
async def test_create_order_empty_cart():
    service = OrderService(
        FakeOrderRepo(),
        FakeCartClient(CartData(id=uuid.uuid4(), items=[])),
        FakeProductClient({}),
    )
    with pytest.raises(CartEmptyError):
        await service.create_order(
            uuid.uuid4(), "token",
            CreateOrderCommand(delivery_address="addr", payment_method="kaspi"),
        )


@pytest.mark.asyncio
async def test_create_order_product_not_active():
    product_id = uuid.uuid4()
    service = OrderService(
        FakeOrderRepo(),
        FakeCartClient(_make_cart(product_id)),
        FakeProductClient({product_id: _make_product(product_id, status="archived")}),
    )
    with pytest.raises(ProductNotAvailableError):
        await service.create_order(
            uuid.uuid4(), "token",
            CreateOrderCommand(delivery_address="addr", payment_method="kaspi"),
        )


@pytest.mark.asyncio
async def test_cancel_order_success():
    product_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = FakeOrderRepo()
    service = OrderService(
        repo,
        FakeCartClient(_make_cart(product_id)),
        FakeProductClient({product_id: _make_product(product_id)}),
    )
    order = await service.create_order(
        user_id, "token",
        CreateOrderCommand(delivery_address="addr", payment_method="kaspi"),
    )
    result = await service.cancel_order(order.id, user_id)
    assert result.status == OrderStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_delivered_order_forbidden():
    repo = FakeOrderRepo()
    user_id = uuid.uuid4()
    product_id = uuid.uuid4()
    service = OrderService(
        repo,
        FakeCartClient(_make_cart(product_id)),
        FakeProductClient({product_id: _make_product(product_id)}),
    )
    order = await service.create_order(
        user_id, "token",
        CreateOrderCommand(delivery_address="addr", payment_method="kaspi"),
    )
    await repo.update_status(order.id, OrderStatus.DELIVERED)

    with pytest.raises(OrderCancelForbiddenError):
        await service.cancel_order(order.id, user_id)


@pytest.mark.asyncio
async def test_get_order_access_denied():
    repo = FakeOrderRepo()
    user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    product_id = uuid.uuid4()
    service = OrderService(
        repo,
        FakeCartClient(_make_cart(product_id)),
        FakeProductClient({product_id: _make_product(product_id)}),
    )
    order = await service.create_order(
        user_id, "token",
        CreateOrderCommand(delivery_address="addr", payment_method="kaspi"),
    )
    with pytest.raises(OrderAccessDeniedError):
        await service.get_order(order.id, other_user_id, frozenset())
