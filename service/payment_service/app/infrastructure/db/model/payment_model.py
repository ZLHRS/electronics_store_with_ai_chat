import datetime
import uuid

from sqlalchemy import UUID, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.model.base_model import BaseModel


class PaymentModel(BaseModel):
    __tablename__ = "payments"

    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="KZT")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="created", server_default="created"
    )
    provider_payment_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    payment_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
