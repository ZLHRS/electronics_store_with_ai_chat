import logging
import uuid
from decimal import Decimal

from app.application.dto.cart_dto import (
    AddItemCommand,
    CartItemResult,
    CartResult,
    ProductSnapshot,
    UpdateItemCommand,
)
from app.domain.entity.cart_entity import CreateCartItem
from app.domain.repo.cart_item_repo_protocol import CartItemRepository
from app.domain.repo.cart_repo_protocol import CartRepository
from app.exceptions import (
    CartItemNotFoundError,
    InvalidQuantityError,
    ProductNotAvailableError,
    ProductNotFoundError,
)
from app.infrastructure.product_client import ProductServiceClient

logger = logging.getLogger(__name__)


class CartService:
    def __init__(
        self,
        cart_repository: CartRepository,
        cart_item_repository: CartItemRepository,
        product_client: ProductServiceClient,
    ):
        self._carts = cart_repository
        self._items = cart_item_repository
        self._products = product_client

    async def get_cart(self, user_id: uuid.UUID) -> CartResult:
        cart = await self._carts.get_or_create_active(user_id)
        return await self._build_result(cart.id, cart.user_id, cart.status, cart.created_at, cart.updated_at)

    async def add_item(self, user_id: uuid.UUID, command: AddItemCommand) -> CartResult:
        if command.quantity < 1:
            raise InvalidQuantityError("Quantity must be at least 1")

        product = await self._products.get_product(command.product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")
        if product.status != "active":
            raise ProductNotAvailableError("Product is not available")

        cart = await self._carts.get_or_create_active(user_id)

        existing = await self._items.get_by_cart_and_product(cart.id, command.product_id)
        if existing:
            await self._items.update_quantity(existing.id, existing.quantity + command.quantity)
            logger.info("Cart item quantity increased cart_id=%s product_id=%s", cart.id, command.product_id)
        else:
            await self._items.create(
                CreateCartItem(
                    cart_id=cart.id,
                    product_id=command.product_id,
                    quantity=command.quantity,
                    unit_price=product.price,
                )
            )
            logger.info("Cart item added cart_id=%s product_id=%s", cart.id, command.product_id)

        return await self._build_result(cart.id, cart.user_id, cart.status, cart.created_at, cart.updated_at)

    async def update_item(
        self, user_id: uuid.UUID, product_id: uuid.UUID, command: UpdateItemCommand
    ) -> CartResult:
        if command.quantity < 1:
            raise InvalidQuantityError("Quantity must be at least 1")

        cart = await self._carts.get_or_create_active(user_id)
        item = await self._items.get_by_cart_and_product(cart.id, product_id)
        if item is None:
            raise CartItemNotFoundError("Item not found in cart")

        await self._items.update_quantity(item.id, command.quantity)
        logger.info("Cart item updated cart_id=%s product_id=%s qty=%s", cart.id, product_id, command.quantity)

        return await self._build_result(cart.id, cart.user_id, cart.status, cart.created_at, cart.updated_at)

    async def remove_item(self, user_id: uuid.UUID, product_id: uuid.UUID) -> CartResult:
        cart = await self._carts.get_or_create_active(user_id)
        item = await self._items.get_by_cart_and_product(cart.id, product_id)
        if item is None:
            raise CartItemNotFoundError("Item not found in cart")

        await self._items.delete(item.id)
        logger.info("Cart item removed cart_id=%s product_id=%s", cart.id, product_id)

        return await self._build_result(cart.id, cart.user_id, cart.status, cart.created_at, cart.updated_at)

    async def clear_cart(self, user_id: uuid.UUID) -> CartResult:
        cart = await self._carts.get_or_create_active(user_id)
        await self._items.delete_by_cart(cart.id)
        logger.info("Cart cleared cart_id=%s", cart.id)

        return await self._build_result(cart.id, cart.user_id, cart.status, cart.created_at, cart.updated_at)

    async def _build_result(
        self,
        cart_id: uuid.UUID,
        user_id: uuid.UUID,
        status: str,
        created_at,
        updated_at,
    ) -> CartResult:
        items = await self._items.get_by_cart(cart_id)
        item_results = []
        for item in items:
            product = await self._products.get_product(item.product_id)
            snapshot = (
                ProductSnapshot(
                    name=product.name,
                    image_url=product.image_url,
                    current_price=product.price,
                    status=product.status,
                )
                if product
                else None
            )
            line_total = item.unit_price * item.quantity
            item_results.append(
                CartItemResult(
                    id=item.id,
                    cart_id=item.cart_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=line_total,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    product=snapshot,
                )
            )
        total = sum((r.line_total for r in item_results), Decimal("0"))
        return CartResult(
            id=cart_id,
            user_id=user_id,
            status=status,
            items=item_results,
            total=total,
            created_at=created_at,
            updated_at=updated_at,
        )
