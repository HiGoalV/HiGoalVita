# Copyright 2025 HiGoal Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import inspect
from typing import Any, AsyncGenerator, AsyncIterator
from redis.asyncio import Redis

from higoalutils.database.memory_store.base import MemoryStoreBase
from higoalutils.config.load_config import get_config
from higoalutils.utils.singleton_utils.singleton import singleton


@singleton
class RedisMemoryStore(MemoryStoreBase):
    def __init__(self):
        redis_cfg = get_config().database_config.redis_config
        self._redis = Redis(
            host=redis_cfg.host, # type: ignore
            port=redis_cfg.port, # type: ignore
            db=redis_cfg.db, # type: ignore
            password=redis_cfg.password, # type: ignore
            decode_responses=True,
            max_connections=getattr(redis_cfg, "max_connections", 10)
        )

    async def get(self, key: str):
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, expire: int | None = None):
        await self._redis.set(key, json.dumps(value), ex=expire)

    async def has(self, key: str) -> bool:
        return await self._redis.exists(key) == 1

    async def delete(self, *keys: str) -> None:
        await self._redis.delete(*keys)

    async def clear(self) -> None:
        async for key in self._redis.scan_iter("*"):
            await self._redis.delete(key)

    async def warmup(self) -> None:
        await self._redis.ping()

    async def close(self) -> None:
        await self._redis.close()
        result = self._redis.connection_pool.disconnect()
        if inspect.isawaitable(result):
            await result
    
    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for msg in pubsub.listen():
                if msg["type"] == "message" and msg["data"]:
                    yield msg["data"]
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
    
    async def publish(self, channel: str, message: str) -> None:
        await self._redis.publish(channel, message)
    
    async def scan_iter(self, match: str = "*") -> AsyncIterator[str]:
        async for key in self._redis.scan_iter(match=match):
            yield key