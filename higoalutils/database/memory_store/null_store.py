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

from typing import Any, AsyncGenerator, AsyncIterator
from higoalutils.database.memory_store.base import MemoryStoreBase


class NullMemoryStore(MemoryStoreBase):

    async def get(self, key: str):
        return None

    async def set(self, key: str, value: Any, expire: int | None = None):
        pass

    async def has(self, key: str) -> bool:
        return False

    async def delete(self, *keys: str):
        pass

    async def clear(self):
        pass

    async def warmup(self):
        pass

    async def close(self):
        pass

    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        if False:
            yield ""
        raise NotImplementedError("This memory store does not support subscribe.")

    async def publish(self, channel: str, message: str) -> None:
        return
    
    async def scan_iter(self, match: str = "*") -> AsyncIterator[str]:
        if False:
            yield ""
        raise NotImplementedError("This memory store does not support scan_iter.")