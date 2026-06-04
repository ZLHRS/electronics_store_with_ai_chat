import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.user_dto import CreateAddressCommand, UpdateAddressCommand
from app.application.service.address_service import AddressService
from app.presentation.deps import CurrentUser, get_current_user
from app.presentation.schema.address_schema import (
    AddressResponse,
    CreateAddressRequest,
    UpdateAddressRequest,
)

router = APIRouter(prefix="/users/me/addresses")


@router.get("", response_model=list[AddressResponse])
@inject
async def get_addresses(
    service: FromDishka[AddressService],
    user: CurrentUser = Depends(get_current_user),
) -> list[AddressResponse]:
    results = await service.get_addresses(user.profile_id)
    return [AddressResponse(**r.__dict__) for r in results]


@router.post("", response_model=AddressResponse, status_code=201)
@inject
async def create_address(
    data: CreateAddressRequest,
    service: FromDishka[AddressService],
    user: CurrentUser = Depends(get_current_user),
) -> AddressResponse:
    result = await service.create_address(
        user.profile_id,
        CreateAddressCommand(
            city=data.city,
            street=data.street,
            house=data.house,
            apartment=data.apartment,
            comment=data.comment,
            is_default=data.is_default,
        ),
    )
    return AddressResponse(**result.__dict__)


@router.patch("/{address_id}", response_model=AddressResponse)
@inject
async def update_address(
    address_id: uuid.UUID,
    data: UpdateAddressRequest,
    service: FromDishka[AddressService],
    user: CurrentUser = Depends(get_current_user),
) -> AddressResponse:
    result = await service.update_address(
        user.profile_id,
        address_id,
        UpdateAddressCommand(
            city=data.city,
            street=data.street,
            house=data.house,
            apartment=data.apartment,
            comment=data.comment,
            is_default=data.is_default,
        ),
    )
    return AddressResponse(**result.__dict__)


@router.delete("/{address_id}", status_code=204)
@inject
async def delete_address(
    address_id: uuid.UUID,
    service: FromDishka[AddressService],
    user: CurrentUser = Depends(get_current_user),
) -> None:
    await service.delete_address(user.profile_id, address_id)
