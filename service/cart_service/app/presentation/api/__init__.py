from fastapi import APIRouter

from app.presentation.api.cart_api import router as cart_router
from app.presentation.api.health_api import router as health_router

main_router = APIRouter(prefix="/api/v1")

routers = [
    health_router,
    cart_router,
]

for router in routers:
    main_router.include_router(router)
