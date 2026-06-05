import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    id: uuid.UUID
    name: str
    price: Decimal
    status: str
    image_url: str | None


class ProductServiceClient:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def get_product(self, product_id: uuid.UUID) -> ProductInfo | None:
        try:
            response = await self._client.get(f"/api/v1/products/{product_id}")
        except httpx.RequestError as e:
            logger.warning("Product service unavailable: %s", e)
            return None
        if response.status_code == 404:
            return None
        if not response.is_success:
            logger.warning("Product service returned %s for product_id=%s", response.status_code, product_id)
            return None
        data = response.json()
        image_url = data["images"][0]["image_url"] if data.get("images") else None
        return ProductInfo(
            id=uuid.UUID(data["id"]),
            name=data["name"],
            price=Decimal(str(data["price"])),
            status=data["status"],
            image_url=image_url,
        )
