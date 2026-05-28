import datetime
from app.infrastructure.db.model.base_model import BaseModel
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc))