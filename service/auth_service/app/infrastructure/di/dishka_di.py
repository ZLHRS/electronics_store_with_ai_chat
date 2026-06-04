from dishka import AsyncContainer, make_async_container

from app.config import Config
from app.infrastructure.di.auth_di import AuthProvider
from app.infrastructure.di.config_di import ConfigProvider
from app.infrastructure.di.db_di import DBProvider
from app.infrastructure.di.redis_di import RedisProvider


def setup_dishka_container(config: Config) -> AsyncContainer:
    return make_async_container(
        ConfigProvider(config),
        DBProvider(),
        RedisProvider(),
        AuthProvider(),
    )
