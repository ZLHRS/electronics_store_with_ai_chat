import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal

import httpx

logger = logging.getLogger(__name__)


@dataclass
class CartItemData:
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal


@dataclass
class CartData:
    id: uuid.UUID
    items: list[CartItemData]


class CartServiceClient:
    def __init__(self, client: httpx.AsyncClient, access_token_name: str):
        self._client = client
        self._token_name = access_token_name

    async def get_cart(self, access_token: str) -> CartData | None:
        try:
            response = await self._client.get(
                "/api/v1/cart",
                cookies={self._token_name: access_token},
            )
        except httpx.RequestError as e:
            logger.warning("Cart service unavailable: %s", e)
            return None
        if not response.is_success:
            logger.warning("Cart service returned %s", response.status_code)
            return None
        data = response.json()
        return CartData(
            id=uuid.UUID(data["id"]),
            items=[
                CartItemData(
                    product_id=uuid.UUID(item["product_id"]),
                    quantity=item["quantity"],
                    unit_price=Decimal(str(item["unit_price"])),
                )
                for item in data.get("items", [])
            ],
        )

    async def clear_cart(self, access_token: str) -> None:
        try:
            await self._client.delete(
                "/api/v1/cart",
                cookies={self._token_name: access_token},
            )
        except httpx.RequestError as e:
            logger.warning("Failed to clear cart: %s", e)
