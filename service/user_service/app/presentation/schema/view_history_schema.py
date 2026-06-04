import datetime
import uuid

from pydantic import BaseModel


class ViewHistoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    product_id: uuid.UUID
    viewed_at: datetime.datetime
