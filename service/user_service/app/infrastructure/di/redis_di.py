import redis.asyncio as redis
from dishka import Provider, Scope, provide

from app.config import Config


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_redis(self, config: Config) -> redis.Redis:
        return redis.from_url(config.redis.url, encoding="utf-8", decode_responses=True)
