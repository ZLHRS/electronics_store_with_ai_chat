from fastapi import APIRouter
from app.presentation.schema.health_schema import HealthResponse

router = APIRouter()

@router.get("/health_check", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse()