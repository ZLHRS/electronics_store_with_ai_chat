from app.config import Config
from app.infrastructure.di.auth_di import AuthProvider
from app.infrastructure.di.config_di import ConfigProvider
from app.infrastructure.di.db_di import DBProvider
from dishka import AsyncContainer, make_async_container

def setup_dishka_container(config: Config) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(config),
        DBProvider(),
        AuthProvider(),
    )