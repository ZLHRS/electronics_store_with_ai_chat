from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.presentation.schema.health_schema import HealthResponse

router = APIRouter()


@router.get("/health_check", response_model=HealthResponse)
@inject
async def health_check(session: FromDishka[AsyncSession]) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return HealthResponse()
