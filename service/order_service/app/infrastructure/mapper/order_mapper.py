from app.domain.entity.order_entity import OrderEntity, OrderItemEntity
from app.infrastructure.db.model.order_item_model import OrderItemModel
from app.infrastructure.db.model.order_model import OrderModel


def order_model_to_entity(
    model: OrderModel, items: list[OrderItemModel]
) -> OrderEntity:
    return OrderEntity(
        id=model.id,
        user_id=model.user_id,
        status=model.status,
        total_amount=model.total_amount,
        delivery_address=model.delivery_address,
        payment_method=model.payment_method,
        created_at=model.created_at,
        updated_at=model.updated_at,
        items=[
            OrderItemEntity(
                id=i.id,
                order_id=i.order_id,
                product_id=i.product_id,
                product_name=i.product_name,
                quantity=i.quantity,
                unit_price=i.unit_price,
                total_price=i.total_price,
            )
            for i in items
        ],
    )
