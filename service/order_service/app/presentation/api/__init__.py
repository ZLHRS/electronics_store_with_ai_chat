from fastapi import APIRouter

from app.presentation.api.health_api import router as health_router
from app.presentation.api.order_api import router as order_router

main_router = APIRouter(prefix="/api/v1")

routers = [
    health_router,
    order_router,
]

for router in routers:
    main_router.include_router(router)
