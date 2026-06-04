from app.domain.entity.view_history_entity import ViewHistoryEntity
from app.infrastructure.db.model.view_history_model import ViewHistoryModel


def view_history_model_to_entity(model: ViewHistoryModel) -> ViewHistoryEntity:
    return ViewHistoryEntity(
        id=model.id,
        user_id=model.user_id,
        product_id=model.product_id,
        viewed_at=model.viewed_at,
    )
