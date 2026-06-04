import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.model.base_model import Base


class PreferencesModel(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    language: Mapped[str] = mapped_column(
        String(8), nullable=False, default="ru", server_default="ru"
    )
    currency: Mapped[str] = mapped_column(
        String(8), nullable=False, default="KZT", server_default="KZT"
    )
    notification_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    preferred_categories: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    min_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
