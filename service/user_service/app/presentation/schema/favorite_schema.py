import datetime
import uuid

from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    user_id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime.datetime
