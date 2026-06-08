import uuid
from decimal import Decimal

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query, Request

from app.application.dto.product_dto import (
    AttributeItemCommand,
    CreateProductCommand,
    ImageItemCommand,
    UpdateProductCommand,
)
from app.application.service.product_service import ProductService
from app.domain.entity.product_entity import ProductFilter
from app.domain.permissions import P
from app.presentation.deps import require_permission
from app.presentation.limiters import products_read_limiter, products_write_limiter
from app.presentation.schema.product_schema import (
    CreateProductRequest,
    ProductListResponse,
    ProductResponse,
    UpdateProductRequest,
)

router = APIRouter(prefix="/products")


@router.get("", response_model=ProductListResponse, dependencies=[Depends(products_read_limiter)])
@inject
async def list_products(
    request: Request,
    service: FromDishka[ProductService],
    category: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    min_price: Decimal | None = Query(default=None),
    max_price: Decimal | None = Query(default=None),
    search: str | None = Query(default=None),
    status: str | None = Query(default="active"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> ProductListResponse:
    attributes = {
        k[len("attribute_") :]: v
        for k, v in request.query_params.items()
        if k.startswith("attribute_")
    }
    result = await service.list_products(
        ProductFilter(
            category_slug=category,
            brand_slug=brand,
            min_price=min_price,
            max_price=max_price,
            search=search,
            attributes=attributes,
            status=status,
            page=page,
            limit=limit,
        )
    )
    return ProductListResponse(
        items=[_to_response(p) for p in result.items],
        total=result.total,
        page=result.page,
        limit=result.limit,
    )


@router.get(
    "/{product_id}", response_model=ProductResponse, dependencies=[Depends(products_read_limiter)]
)
@inject
async def get_product(
    product_id: uuid.UUID,
    service: FromDishka[ProductService],
) -> ProductResponse:
    result = await service.get_product(product_id)
    return _to_response(result)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
    dependencies=[Depends(products_write_limiter)],
)
@inject
async def create_product(
    data: CreateProductRequest,
    service: FromDishka[ProductService],
    _: object = Depends(require_permission(P.PRODUCTS_CREATE)),
) -> ProductResponse:
    result = await service.create_product(
        CreateProductCommand(
            name=data.name,
            price=data.price,
            slug=data.slug,
            description=data.description,
            category_id=data.category_id,
            brand_id=data.brand_id,
            status=data.status,
            images=[ImageItemCommand(i.image_url, i.sort_order) for i in data.images],
            attributes=[AttributeItemCommand(a.name, a.value) for a in data.attributes],
        )
    )
    return _to_response(result)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(products_write_limiter)],
)
@inject
async def update_product(
    product_id: uuid.UUID,
    data: UpdateProductRequest,
    service: FromDishka[ProductService],
    _: object = Depends(require_permission(P.PRODUCTS_UPDATE)),
) -> ProductResponse:
    result = await service.update_product(
        product_id,
        UpdateProductCommand(
            name=data.name,
            slug=data.slug,
            description=data.description,
            price=data.price,
            category_id=data.category_id,
            brand_id=data.brand_id,
            status=data.status,
            images=(
                [ImageItemCommand(i.image_url, i.sort_order) for i in data.images]
                if data.images is not None
                else None
            ),
            attributes=(
                [AttributeItemCommand(a.name, a.value) for a in data.attributes]
                if data.attributes is not None
                else None
            ),
        ),
    )
    return _to_response(result)


@router.delete(
    "/{product_id}",
    status_code=204,
    dependencies=[Depends(products_write_limiter)],
)
@inject
async def delete_product(
    product_id: uuid.UUID,
    service: FromDishka[ProductService],
    _: object = Depends(require_permission(P.PRODUCTS_DELETE)),
) -> None:
    await service.delete_product(product_id)


def _to_response(result) -> ProductResponse:
    from app.presentation.schema.product_schema import AttributeResponse, ImageResponse

    return ProductResponse(
        id=result.id,
        name=result.name,
        slug=result.slug,
        description=result.description,
        price=result.price,
        category_id=result.category_id,
        brand_id=result.brand_id,
        status=result.status,
        created_at=result.created_at,
        updated_at=result.updated_at,
        images=[
            ImageResponse(
                id=i.id, product_id=i.product_id, image_url=i.image_url, sort_order=i.sort_order
            )
            for i in result.images
        ],
        attributes=[
            AttributeResponse(id=a.id, product_id=a.product_id, name=a.name, value=a.value)
            for a in result.attributes
        ],
    )
