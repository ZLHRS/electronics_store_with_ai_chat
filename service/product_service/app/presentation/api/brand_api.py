import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.product_dto import CreateBrandCommand, UpdateBrandCommand
from app.application.service.brand_service import BrandService
from app.domain.permissions import P
from app.presentation.deps import require_permission
from app.presentation.schema.brand_schema import (
    BrandResponse,
    CreateBrandRequest,
    UpdateBrandRequest,
)

router = APIRouter(prefix="/brands")


@router.get("", response_model=list[BrandResponse])
@inject
async def list_brands(service: FromDishka[BrandService]) -> list[BrandResponse]:
    results = await service.list_brands()
    return [BrandResponse(id=r.id, name=r.name, slug=r.slug) for r in results]


@router.post("", response_model=BrandResponse, status_code=201)
@inject
async def create_brand(
    data: CreateBrandRequest,
    service: FromDishka[BrandService],
    _: object = Depends(require_permission(P.PRODUCTS_CREATE)),
) -> BrandResponse:
    result = await service.create_brand(CreateBrandCommand(name=data.name, slug=data.slug))
    return BrandResponse(id=result.id, name=result.name, slug=result.slug)


@router.patch("/{brand_id}", response_model=BrandResponse)
@inject
async def update_brand(
    brand_id: uuid.UUID,
    data: UpdateBrandRequest,
    service: FromDishka[BrandService],
    _: object = Depends(require_permission(P.PRODUCTS_UPDATE)),
) -> BrandResponse:
    result = await service.update_brand(
        brand_id, UpdateBrandCommand(name=data.name, slug=data.slug)
    )
    return BrandResponse(id=result.id, name=result.name, slug=result.slug)


@router.delete("/{brand_id}", status_code=204)
@inject
async def delete_brand(
    brand_id: uuid.UUID,
    service: FromDishka[BrandService],
    _: object = Depends(require_permission(P.PRODUCTS_DELETE)),
) -> None:
    await service.delete_brand(brand_id)
