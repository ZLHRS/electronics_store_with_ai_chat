import datetime
import uuid
from dataclasses import dataclass


@dataclass
class FavoriteEntity:
    user_id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime.datetime
