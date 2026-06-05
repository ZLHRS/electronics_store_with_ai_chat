from fastapi import APIRouter

from app.presentation.api.health_api import router as health_router
from app.presentation.api.payment_api import router as payment_router
from app.presentation.api.webhook_api import router as webhook_router

main_router = APIRouter(prefix="/api/v1")

routers = [
    health_router,
    payment_router,
    webhook_router,
]

for router in routers:
    main_router.include_router(router)
