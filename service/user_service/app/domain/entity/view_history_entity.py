import datetime
import uuid
from dataclasses import dataclass


@dataclass
class ViewHistoryEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    product_id: uuid.UUID
    viewed_at: datetime.datetime
