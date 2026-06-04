from fastapi import APIRouter

from app.presentation.api.address_api import router as address_router
from app.presentation.api.favorite_api import router as favorite_router
from app.presentation.api.health_api import router as health_router
from app.presentation.api.preferences_api import router as preferences_router
from app.presentation.api.user_api import router as user_router
from app.presentation.api.view_history_api import router as view_history_router

main_router = APIRouter(prefix="/api/v1")

routers = [
    health_router,
    user_router,
    address_router,
    favorite_router,
    view_history_router,
    preferences_router,
]

for router in routers:
    main_router.include_router(router)
