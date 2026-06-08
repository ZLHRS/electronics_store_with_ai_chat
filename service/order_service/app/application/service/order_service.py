import logging
import uuid
from decimal import Decimal

from app.application.dto.order_dto import (
    CreateOrderCommand,
    OrderItemResult,
    OrderResult,
    UpdateStatusCommand,
)
from app.domain.entity.order_entity import CreateOrder, CreateOrderItem, OrderStatus
from app.domain.permissions import P
from app.domain.repo.order_repo_protocol import OrderRepository
from app.exceptions import (
    CartEmptyError,
    OrderAccessDeniedError,
    OrderCancelForbiddenError,
    OrderNotFoundError,
    ProductNotAvailableError,
    ProductNotFoundError,
)
from app.infrastructure.cart_client import CartServiceClient
from app.infrastructure.product_client import ProductServiceClient

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        cart_client: CartServiceClient,
        product_client: ProductServiceClient,
    ):
        self._orders = order_repository
        self._cart = cart_client
        self._products = product_client

    async def create_order(
        self, user_id: uuid.UUID, access_token: str, command: CreateOrderCommand
    ) -> OrderResult:
        cart = await self._cart.get_cart(access_token)
        if cart is None or not cart.items:
            raise CartEmptyError("Cart is empty")

        order_items = []
        total = Decimal("0")

        for cart_item in cart.items:
            product = await self._products.get_product(cart_item.product_id)
            if product is None:
                raise ProductNotFoundError(f"Product {cart_item.product_id} not found")
            if product.status != "active":
                raise ProductNotAvailableError(f"Product '{product.name}' is not available")

            item_total = cart_item.unit_price * cart_item.quantity
            total += item_total
            order_items.append(
                CreateOrderItem(
                    product_id=cart_item.product_id,
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    total_price=item_total,
                )
            )

        order = await self._orders.create(
            CreateOrder(
                user_id=user_id,
                status=OrderStatus.PENDING_PAYMENT,
                total_amount=total,
                delivery_address=command.delivery_address,
                payment_method=command.payment_method,
                items=order_items,
            )
        )

        await self._cart.clear_cart(access_token)
        logger.info("Order created order_id=%s user_id=%s total=%s", order.id, user_id, total)

        return _to_result(order)

    async def get_order(
        self, order_id: uuid.UUID, user_id: uuid.UUID, permissions: frozenset[str]
    ) -> OrderResult:
        order = await self._orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found")
        if order.user_id != user_id and P.ORDERS_READ_ALL not in permissions:
            raise OrderAccessDeniedError("Access denied")
        return _to_result(order)

    async def list_orders(
        self, user_id: uuid.UUID, permissions: frozenset[str]
    ) -> list[OrderResult]:
        if P.ORDERS_READ_ALL in permissions:
            orders = await self._orders.get_by_user(user_id)
        else:
            orders = await self._orders.get_by_user(user_id)
        return [_to_result(o) for o in orders]

    async def cancel_order(self, order_id: uuid.UUID, user_id: uuid.UUID) -> OrderResult:
        order = await self._orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found")
        if order.user_id != user_id:
            raise OrderAccessDeniedError("Access denied")
        if order.status not in OrderStatus.CANCELLABLE:
            raise OrderCancelForbiddenError(f"Cannot cancel order with status '{order.status}'")
        order = await self._orders.update_status(order_id, OrderStatus.CANCELLED)
        logger.info("Order cancelled order_id=%s", order_id)
        return _to_result(order)

    async def update_status(self, order_id: uuid.UUID, command: UpdateStatusCommand) -> OrderResult:
        order = await self._orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError("Order not found")
        order = await self._orders.update_status(order_id, command.status)
        logger.info("Order status updated order_id=%s status=%s", order_id, command.status)
        return _to_result(order)


def _to_result(order) -> OrderResult:
    return OrderResult(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        delivery_address=order.delivery_address,
        payment_method=order.payment_method,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemResult(
                id=i.id,
                order_id=i.order_id,
                product_id=i.product_id,
                product_name=i.product_name,
                quantity=i.quantity,
                unit_price=i.unit_price,
                total_price=i.total_price,
            )
            for i in order.items
        ],
    )
