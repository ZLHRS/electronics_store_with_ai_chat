from __future__ import annotations

import uuid
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.domain.repo.chat_repo import EmbeddingRepository, ProductContext
from app.exceptions import DatabaseError
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo


class SQLAlchemyEmbeddingRepo(SQLAlchemyBaseRepo, EmbeddingRepository):
    async def upsert(self, product_id: uuid.UUID, content: str, embedding: list[float]) -> None:
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        stmt = text("""
            INSERT INTO product_embeddings (id, product_id, content, embedding, updated_at)
            VALUES (:id, :product_id, :content, CAST(:embedding AS vector), NOW())
            ON CONFLICT (product_id) DO UPDATE
            SET content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                updated_at = NOW()
        """)
        try:
            await self.session.execute(
                stmt,
                {
                    "id": str(uuid4()),
                    "product_id": str(product_id),
                    "content": content,
                    "embedding": embedding_str,
                },
            )
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to upsert embedding") from e

    async def search(self, query_embedding: list[float], limit: int) -> list[ProductContext]:
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        stmt = text("""
            SELECT product_id, content,
                   1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM product_embeddings
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)
        try:
            result = await self.session.execute(stmt, {"embedding": embedding_str, "limit": limit})
        except SQLAlchemyError as e:
            raise DatabaseError("Vector search failed") from e
        return [
            ProductContext(
                product_id=uuid.UUID(str(row.product_id)),
                content=row.content,
                similarity=float(row.similarity),
            )
            for row in result
        ]

    async def clear(self) -> None:
        try:
            await self.session.execute(text("DELETE FROM product_embeddings"))
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to clear embeddings") from e
