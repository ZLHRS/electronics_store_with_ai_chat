from app.domain.entity.brand_entity import BrandEntity
from app.infrastructure.db.model.brand_model import BrandModel


def brand_model_to_entity(model: BrandModel) -> BrandEntity:
    return BrandEntity(id=model.id, name=model.name, slug=model.slug)
