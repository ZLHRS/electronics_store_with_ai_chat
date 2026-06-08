import datetime
import uuid
from decimal import Decimal

import pytest

from app.application.dto.cart_dto import AddItemCommand
from app.application.service.cart_service import CartService
from app.domain.entity.cart_entity import CartEntity, CartItemEntity, CartStatus, CreateCartItem
from app.exceptions import (
    CartItemNotFoundError,
    InvalidQuantityError,
    ProductNotAvailableError,
    ProductNotFoundError,
)
from app.infrastructure.product_client import ProductInfo


class FakeCartRepo:
    def __init__(self):
        self._carts: dict[uuid.UUID, CartEntity] = {}

    def _make(self, user_id: uuid.UUID) -> CartEntity:
        now = datetime.datetime.now(datetime.UTC)
        cart = CartEntity(
            id=uuid.uuid4(),
            user_id=user_id,
            status=CartStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        self._carts[user_id] = cart
        return cart

    async def get_active_by_user_id(self, user_id: uuid.UUID) -> CartEntity | None:
        return self._carts.get(user_id)

    async def get_or_create_active(self, user_id: uuid.UUID) -> CartEntity:
        return self._carts.get(user_id) or self._make(user_id)

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        self._carts.pop(user_id, None)


class FakeCartItemRepo:
    def __init__(self):
        self._items: list[CartItemEntity] = []

    async def get_by_cart(self, cart_id: uuid.UUID) -> list[CartItemEntity]:
        return [i for i in self._items if i.cart_id == cart_id]

    async def get_by_cart_and_product(
        self, cart_id: uuid.UUID, product_id: uuid.UUID
    ) -> CartItemEntity | None:
        return next(
            (i for i in self._items if i.cart_id == cart_id and i.product_id == product_id), None
        )

    async def create(self, data: CreateCartItem) -> CartItemEntity:
        now = datetime.datetime.now(datetime.UTC)
        item = CartItemEntity(
            id=uuid.uuid4(),
            cart_id=data.cart_id,
            product_id=data.product_id,
            quantity=data.quantity,
            unit_price=data.unit_price,
            created_at=now,
            updated_at=now,
        )
        self._items.append(item)
        return item

    async def update_quantity(self, item_id: uuid.UUID, quantity: int) -> CartItemEntity:
        for i, item in enumerate(self._items):
            if item.id == item_id:
                updated = CartItemEntity(
                    id=item.id,
                    cart_id=item.cart_id,
                    product_id=item.product_id,
                    quantity=quantity,
                    unit_price=item.unit_price,
                    created_at=item.created_at,
                    updated_at=datetime.datetime.now(datetime.UTC),
                )
                self._items[i] = updated
                return updated
        raise ValueError("Item not found")

    async def delete(self, item_id: uuid.UUID) -> None:
        self._items = [i for i in self._items if i.id != item_id]

    async def delete_by_cart(self, cart_id: uuid.UUID) -> None:
        self._items = [i for i in self._items if i.cart_id != cart_id]


class FakeProductClient:
    def __init__(self, products: dict[uuid.UUID, ProductInfo]):
        self._products = products

    async def get_product(self, product_id: uuid.UUID) -> ProductInfo | None:
        return self._products.get(product_id)


def _make_product(
    product_id: uuid.UUID, status: str = "active", price: str = "50000"
) -> ProductInfo:
    return ProductInfo(
        id=product_id, name="Test Product", price=Decimal(price), status=status, image_url=None
    )


@pytest.mark.asyncio
async def test_add_item_creates_cart_and_item():
    product_id = uuid.uuid4()
    user_id = uuid.uuid4()
    service = CartService(
        FakeCartRepo(),
        FakeCartItemRepo(),
        FakeProductClient({product_id: _make_product(product_id)}),
    )

    result = await service.add_item(user_id, AddItemCommand(product_id=product_id, quantity=2))

    assert len(result.items) == 1
    assert result.items[0].quantity == 2
    assert result.items[0].unit_price == Decimal("50000")
    assert result.total == Decimal("100000")


@pytest.mark.asyncio
async def test_add_item_increases_quantity_if_exists():
    product_id = uuid.uuid4()
    user_id = uuid.uuid4()
    service = CartService(
        FakeCartRepo(),
        FakeCartItemRepo(),
        FakeProductClient({product_id: _make_product(product_id)}),
    )

    await service.add_item(user_id, AddItemCommand(product_id=product_id, quantity=1))
    result = await service.add_item(user_id, AddItemCommand(product_id=product_id, quantity=2))

    assert len(result.items) == 1
    assert result.items[0].quantity == 3


@pytest.mark.asyncio
async def test_add_item_product_not_found():
    service = CartService(FakeCartRepo(), FakeCartItemRepo(), FakeProductClient({}))

    with pytest.raises(ProductNotFoundError):
        await service.add_item(uuid.uuid4(), AddItemCommand(product_id=uuid.uuid4(), quantity=1))


@pytest.mark.asyncio
async def test_add_item_product_not_active():
    product_id = uuid.uuid4()
    service = CartService(
        FakeCartRepo(),
        FakeCartItemRepo(),
        FakeProductClient({product_id: _make_product(product_id, status="draft")}),
    )

    with pytest.raises(ProductNotAvailableError):
        await service.add_item(uuid.uuid4(), AddItemCommand(product_id=product_id, quantity=1))


@pytest.mark.asyncio
async def test_add_item_invalid_quantity():
    service = CartService(FakeCartRepo(), FakeCartItemRepo(), FakeProductClient({}))

    with pytest.raises(InvalidQuantityError):
        await service.add_item(uuid.uuid4(), AddItemCommand(product_id=uuid.uuid4(), quantity=0))


@pytest.mark.asyncio
async def test_remove_item_not_in_cart():
    service = CartService(FakeCartRepo(), FakeCartItemRepo(), FakeProductClient({}))

    with pytest.raises(CartItemNotFoundError):
        await service.remove_item(uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_clear_cart():
    product_id = uuid.uuid4()
    user_id = uuid.uuid4()
    service = CartService(
        FakeCartRepo(),
        FakeCartItemRepo(),
        FakeProductClient({product_id: _make_product(product_id)}),
    )

    await service.add_item(user_id, AddItemCommand(product_id=product_id, quantity=3))
    result = await service.clear_cart(user_id)

    assert result.items == []
    assert result.total == Decimal("0")
