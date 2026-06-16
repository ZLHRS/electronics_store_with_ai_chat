import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.product_dto import CreateCategoryCommand, UpdateCategoryCommand
from app.application.service.category_service import CategoryService
from app.domain.permissions import P
from app.presentation.deps import require_permission
from app.presentation.schema.category_schema import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)

router = APIRouter(prefix="/categories")


@router.get("", response_model=list[CategoryResponse])
@inject
async def list_categories(service: FromDishka[CategoryService]) -> list[CategoryResponse]:
    results = await service.list_categories()
    return [
        CategoryResponse(id=r.id, name=r.name, slug=r.slug, parent_id=r.parent_id) for r in results
    ]


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
    return CategoryResponse(
        id=result.id, name=result.name, slug=result.slug, parent_id=result.parent_id
    )


@router.patch("/{category_id}", response_model=CategoryResponse)
@inject
async def update_category(
    category_id: uuid.UUID,
    data: UpdateCategoryRequest,
    service: FromDishka[CategoryService],
    _: object = Depends(require_permission(P.PRODUCTS_UPDATE)),
) -> CategoryResponse:
    result = await service.update_category(
        category_id, UpdateCategoryCommand(name=data.name, slug=data.slug)
    )
    return CategoryResponse(
        id=result.id, name=result.name, slug=result.slug, parent_id=result.parent_id
    )


@router.delete("/{category_id}", status_code=204)
@inject
async def delete_category(
    category_id: uuid.UUID,
    service: FromDishka[CategoryService],
    _: object = Depends(require_permission(P.PRODUCTS_DELETE)),
) -> None:
    await service.delete_category(category_id)
