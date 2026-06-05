from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import redis.asyncio as redis
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from app.config import setup_config
from app.infrastructure.di.dishka_di import setup_dishka_container
from app.logging import setup_logging
from app.presentation.api import main_router
from app.presentation.exception import register_exception_handlers
from app.presentation.middleware import request_id_middleware


def create_app() -> FastAPI:
    config = setup_config()
    setup_logging(config.logging.level)

    dishka_container = setup_dishka_container(config)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        redis_client = redis.from_url(config.redis.url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
        try:
            yield
        finally:
            await FastAPILimiter.close()
            await dishka_container.close()

    application = FastAPI(lifespan=lifespan)
    application.middleware("http")(request_id_middleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(main_router)
    setup_dishka(dishka_container, application)
    register_exception_handlers(application)
    return application
