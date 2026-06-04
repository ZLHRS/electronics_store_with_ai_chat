from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.product_dto import CreateBrandCommand
from app.application.service.brand_service import BrandService
from app.domain.permissions import P
from app.presentation.deps import require_permission
from app.presentation.schema.brand_schema import BrandResponse, CreateBrandRequest

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
