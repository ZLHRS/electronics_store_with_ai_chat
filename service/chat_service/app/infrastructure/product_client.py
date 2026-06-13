from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal

import httpx

from app.application.service.rag_service import ProductData

logger = logging.getLogger(__name__)


class ProductServiceClient:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def get_all_products(self) -> list[ProductData]:
        products: list[ProductData] = []
        page = 1
        while True:
            try:
                response = await self._client.get(
                    f"/api/v1/products?page={page}&limit=100"
                )
            except httpx.RequestError as e:
                logger.warning("Product service unavailable: %s", e)
                break
            if not response.is_success:
                logger.warning("Product service returned %s", response.status_code)
                break
            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            for item in items:
                products.append(self._parse(item))
            if len(products) >= data.get("total", 0):
                break
            page += 1
        return products

    def _parse(self, data: dict) -> ProductData:
        images = data.get("images", [])
        image_url = images[0].get("image_url") if images else None
        return ProductData(
            id=uuid.UUID(data["id"]),
            name=data["name"],
            description=data.get("description", ""),
            price=Decimal(str(data["price"])),
            status=data["status"],
            attributes=data.get("attributes", []),
            image_url=image_url,
        )
