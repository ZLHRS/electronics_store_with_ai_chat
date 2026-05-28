import uvicorn
from app.config import setup_config
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from typing import AsyncIterator
from contextlib import asynccontextmanager
from app.infrastructure.di.dishka_di import setup_dishka_container
from app.logging import setup_logging
from app.presentation.api import main_router

def create_lifespan(dishka_container):
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await dishka_container.close()
    return lifespan

def create_app() -> FastAPI:
    config = setup_config()
    dishka_container = setup_dishka_container(config)
    setup_logging(config.logging.level)
    app = FastAPI(lifespan=create_lifespan(dishka_container))
    app.include_router(main_router)
    setup_dishka(dishka_container, app)
    return app

app = create_app()

if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)