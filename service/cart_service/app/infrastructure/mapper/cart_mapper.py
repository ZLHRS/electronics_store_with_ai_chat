from app.domain.entity.cart_entity import CartEntity, CartItemEntity
from app.infrastructure.db.model.cart_item_model import CartItemModel
from app.infrastructure.db.model.cart_model import CartModel


def cart_model_to_entity(model: CartModel) -> CartEntity:
    return CartEntity(
        id=model.id,
        user_id=model.user_id,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def cart_item_model_to_entity(model: CartItemModel) -> CartItemEntity:
    return CartItemEntity(
        id=model.id,
        cart_id=model.cart_id,
        product_id=model.product_id,
        quantity=model.quantity,
        unit_price=model.unit_price,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
