import redis.asyncio as redis
from dishka import Provider, Scope, provide

from app.config import Config
from app.infrastructure.cache.permission_cache import PermissionCache


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_redis(self, config: Config) -> redis.Redis:
        return redis.from_url(config.redis.url, encoding="utf-8", decode_responses=True)

    @provide(scope=Scope.APP)
    def provide_permission_cache(self, client: redis.Redis) -> PermissionCache:
        return PermissionCache(client)
