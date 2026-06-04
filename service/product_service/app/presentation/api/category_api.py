from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.product_dto import CreateCategoryCommand
from app.application.service.category_service import CategoryService
from app.domain.permissions import P
from app.presentation.deps import require_permission
from app.presentation.schema.category_schema import CategoryResponse, CreateCategoryRequest

router = APIRouter(prefix="/categories")


@router.get("", response_model=list[CategoryResponse])
@inject
async def list_categories(service: FromDishka[CategoryService]) -> list[CategoryResponse]:
    results = await service.list_categories()
    return [CategoryResponse(id=r.id, name=r.name, slug=r.slug, parent_id=r.parent_id) for r in results]


@router.post("", response_model=CategoryResponse, status_code=201)
@inject
async def create_category(
    data: CreateCategoryRequest,
    service: FromDishka[CategoryService],
    _: object = Depends(require_permission(P.PRODUCTS_CREATE)),
) -> CategoryResponse:
    result = await service.create_category(
        CreateCategoryCommand(name=data.name, slug=data.slug, parent_id=data.parent_id)
    )
    return CategoryResponse(id=result.id, name=result.name, slug=result.slug, parent_id=result.parent_id)
