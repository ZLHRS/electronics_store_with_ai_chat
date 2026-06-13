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
