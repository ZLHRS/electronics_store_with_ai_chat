from fastapi import APIRouter

from app.presentation.api.brand_api import router as brand_router
from app.presentation.api.category_api import router as category_router
from app.presentation.api.health_api import router as health_router
from app.presentation.api.product_api import router as product_router

main_router = APIRouter(prefix="/api/v1")

routers = [
    health_router,
    product_router,
    category_router,
    brand_router,
]

for router in routers:
    main_router.include_router(router)
