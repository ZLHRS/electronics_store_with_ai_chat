import logging
import uuid

from app.application.dto.user_dto import AddressResult, CreateAddressCommand, UpdateAddressCommand
from app.domain.entity.address_entity import CreateAddress, UpdateAddress
from app.domain.repo.address_repo_protocol import AddressRepository
from app.exceptions import AddressLimitExceededError, AddressNotFoundError

logger = logging.getLogger(__name__)

_MAX_ADDRESSES_PER_USER = 10


class AddressService:
    def __init__(self, address_repository: AddressRepository):
        self._addresses = address_repository

    async def get_addresses(self, user_id: uuid.UUID) -> list[AddressResult]:
        addresses = await self._addresses.get_all_by_user(user_id)
        return [_to_result(a) for a in addresses]

    async def create_address(
        self, user_id: uuid.UUID, command: CreateAddressCommand
    ) -> AddressResult:
        existing = await self._addresses.get_all_by_user(user_id)
        if len(existing) >= _MAX_ADDRESSES_PER_USER:
            raise AddressLimitExceededError(
                f"Cannot have more than {_MAX_ADDRESSES_PER_USER} addresses"
            )
        if command.is_default:
            await self._addresses.unset_default(user_id)
        address = await self._addresses.create(
            CreateAddress(
                user_id=user_id,
                city=command.city,
                street=command.street,
                house=command.house,
                apartment=command.apartment,
                comment=command.comment,
                is_default=command.is_default,
            )
        )
        logger.info("Address created user_id=%s address_id=%s", user_id, address.id)
        return _to_result(address)

    async def update_address(
        self, user_id: uuid.UUID, address_id: uuid.UUID, command: UpdateAddressCommand
    ) -> AddressResult:
        address = await self._addresses.get_by_id(address_id)
        if address is None or address.user_id != user_id:
            raise AddressNotFoundError("Address not found")
        if command.is_default:
            await self._addresses.unset_default(user_id)
        updated = await self._addresses.update(
            address_id,
            UpdateAddress(
                city=command.city,
                street=command.street,
                house=command.house,
                apartment=command.apartment,
                comment=command.comment,
                is_default=command.is_default,
            ),
        )
        logger.info("Address updated user_id=%s address_id=%s", user_id, address_id)
        return _to_result(updated)

    async def delete_address(self, user_id: uuid.UUID, address_id: uuid.UUID) -> None:
        address = await self._addresses.get_by_id(address_id)
        if address is None or address.user_id != user_id:
            raise AddressNotFoundError("Address not found")
        await self._addresses.delete(address_id)
        logger.info("Address deleted user_id=%s address_id=%s", user_id, address_id)


def _to_result(address) -> AddressResult:
    return AddressResult(
        id=address.id,
        user_id=address.user_id,
        city=address.city,
        street=address.street,
        house=address.house,
        apartment=address.apartment,
        comment=address.comment,
        is_default=address.is_default,
    )
