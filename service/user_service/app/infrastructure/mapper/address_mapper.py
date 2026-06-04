from app.domain.entity.address_entity import AddressEntity
from app.infrastructure.db.model.address_model import AddressModel


def address_model_to_entity(model: AddressModel) -> AddressEntity:
    return AddressEntity(
        id=model.id,
        user_id=model.user_id,
        city=model.city,
        street=model.street,
        house=model.house,
        apartment=model.apartment,
        comment=model.comment,
        is_default=model.is_default,
    )
