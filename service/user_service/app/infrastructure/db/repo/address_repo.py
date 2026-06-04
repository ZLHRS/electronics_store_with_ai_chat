import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.address_entity import AddressEntity, CreateAddress, UpdateAddress
from app.domain.repo.address_repo_protocol import AddressRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.address_model import AddressModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.address_mapper import address_model_to_entity


class SQLAlchemyAddressRepo(SQLAlchemyBaseRepo, AddressRepository):
    async def get_all_by_user(self, user_id: uuid.UUID) -> list[AddressEntity]:
        stmt = select(AddressModel).where(AddressModel.user_id == user_id)
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get addresses") from e
        return [address_model_to_entity(r) for r in rows]

    async def get_by_id(self, address_id: uuid.UUID) -> AddressEntity | None:
        stmt = select(AddressModel).where(AddressModel.id == address_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get address by id") from e
        return address_model_to_entity(result) if result else None

    async def create(self, data: CreateAddress) -> AddressEntity:
        model = AddressModel(
            user_id=data.user_id,
            city=data.city,
            street=data.street,
            house=data.house,
            apartment=data.apartment,
            comment=data.comment,
            is_default=data.is_default,
        )
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create address") from e
        return address_model_to_entity(model)

    async def update(self, address_id: uuid.UUID, data: UpdateAddress) -> AddressEntity:
        stmt = select(AddressModel).where(AddressModel.id == address_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to fetch address for update") from e
        if model is None:
            raise DatabaseError("Address not found")
        model.city = data.city
        model.street = data.street
        model.house = data.house
        model.apartment = data.apartment
        model.comment = data.comment
        model.is_default = data.is_default
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update address") from e
        return address_model_to_entity(model)

    async def delete(self, address_id: uuid.UUID) -> None:
        stmt = select(AddressModel).where(AddressModel.id == address_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
            if model:
                await self.session.delete(model)
                await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to delete address") from e

    async def unset_default(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(AddressModel)
            .where(AddressModel.user_id == user_id, AddressModel.is_default.is_(True))
            .values(is_default=False)
        )
        try:
            await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to unset default address") from e
