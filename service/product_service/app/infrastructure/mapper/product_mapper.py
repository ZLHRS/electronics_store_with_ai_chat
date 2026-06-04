from app.domain.entity.product_entity import (
    ProductAttributeEntity,
    ProductEntity,
    ProductImageEntity,
)
from app.infrastructure.db.model.product_attribute_model import ProductAttributeModel
from app.infrastructure.db.model.product_image_model import ProductImageModel
from app.infrastructure.db.model.product_model import ProductModel


def product_model_to_entity(
    model: ProductModel,
    images: list[ProductImageModel],
    attributes: list[ProductAttributeModel],
) -> ProductEntity:
    return ProductEntity(
        id=model.id,
        name=model.name,
        slug=model.slug,
        description=model.description,
        price=model.price,
        category_id=model.category_id,
        brand_id=model.brand_id,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
        images=[
            ProductImageEntity(
                id=i.id,
                product_id=i.product_id,
                image_url=i.image_url,
                sort_order=i.sort_order,
            )
            for i in images
        ],
        attributes=[
            ProductAttributeEntity(
                id=a.id,
                product_id=a.product_id,
                name=a.name,
                value=a.value,
            )
            for a in attributes
        ],
    )
