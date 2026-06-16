import datetime
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import UUID, DateTime, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.model.base_model import BaseModel


class ProductEmbeddingModel(BaseModel):
    __tablename__ = "product_embeddings"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    )
