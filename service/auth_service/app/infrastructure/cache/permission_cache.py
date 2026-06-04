import json
import uuid

import redis.asyncio as redis


class PermissionCache:
    def __init__(self, client: redis.Redis):
        self._client = client

    def _key(self, user_id: uuid.UUID) -> str:
        return f"permissions:user:{user_id}"

    async def get(self, user_id: uuid.UUID) -> frozenset[str] | None:
        raw = await self._client.get(self._key(user_id))
        if raw is None:
            return None
        return frozenset(json.loads(raw))

    async def set(self, user_id: uuid.UUID, permissions: frozenset[str], ttl_seconds: int) -> None:
        await self._client.set(
            self._key(user_id),
            json.dumps(sorted(permissions)),
            ex=ttl_seconds,
        )

    async def delete(self, user_id: uuid.UUID) -> None:
        await self._client.delete(self._key(user_id))
