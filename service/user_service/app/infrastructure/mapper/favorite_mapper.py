from app.domain.entity.favorite_entity import FavoriteEntity
from app.infrastructure.db.model.favorite_model import FavoriteModel


def favorite_model_to_entity(model: FavoriteModel) -> FavoriteEntity:
    return FavoriteEntity(
        user_id=model.user_id,
        product_id=model.product_id,
        created_at=model.created_at,
    )
