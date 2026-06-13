from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.repo.chat_repo import EmbeddingRepository, ProductContext

logger = logging.getLogger(__name__)


@dataclass
class ProductData:
    id: UUID
    name: str
    description: str
    price: Decimal
    status: str
    attributes: list[dict]
    image_url: str | None


class RAGService:
    def __init__(
        self,
        embedding_repo: EmbeddingRepository,
        embedding_service,
        product_client,
    ):
        self._repo = embedding_repo
        self._embedder = embedding_service
        self._product_client = product_client

    async def search(self, query: str, limit: int = 5) -> list[ProductContext]:
        embedding = await self._embedder.embed(query)
        return await self._repo.search(embedding, limit)

    async def index_all_products(self) -> int:
        products = await self._product_client.get_all_products()
        indexed = 0
        for product in products:
            content = self._build_content(product)
            embedding = await self._embedder.embed(content)
            await self._repo.upsert(product.id, content, embedding)
            indexed += 1
            logger.info("Indexed product %s", product.id)
        return indexed

    def _build_content(self, product: ProductData) -> str:
        parts = [product.name]
        if product.description:
            parts.append(product.description)
        for attr in product.attributes:
            parts.append(f"{attr.get('name', '')}: {attr.get('value', '')}")
        parts.append(f"Цена: {product.price} ₸")
        return " | ".join(p for p in parts if p)
