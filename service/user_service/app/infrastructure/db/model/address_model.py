import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.model.base_model import BaseModel


class AddressModel(BaseModel):
    __tablename__ = "user_addresses"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    street: Mapped[str] = mapped_column(String(256), nullable=False)
    house: Mapped[str] = mapped_column(String(32), nullable=False)
    apartment: Mapped[str | None] = mapped_column(String(32), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
