from app.domain.entity.category_entity import CategoryEntity
from app.infrastructure.db.model.category_model import CategoryModel


def category_model_to_entity(model: CategoryModel) -> CategoryEntity:
    return CategoryEntity(
        id=model.id,
        name=model.name,
        slug=model.slug,
        parent_id=model.parent_id,
    )
