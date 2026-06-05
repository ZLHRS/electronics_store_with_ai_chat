import datetime
import uuid
from decimal import Decimal

from sqlalchemy import UUID, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.model.base_model import BaseModel


class OrderModel(BaseModel):
    __tablename__ = "orders"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending_payment", server_default="pending_payment"
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
