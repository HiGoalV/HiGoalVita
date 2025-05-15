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

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, AsyncIterator


class MemoryStoreBase(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any: 
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, expire: int | None = None) -> None: 
        ...

    @abstractmethod
    async def has(self, key: str) -> bool: 
        ...

    @abstractmethod
    async def delete(self, *keys: str) -> None: 
        ...

    @abstractmethod
    async def clear(self) -> None: 
        ...

    @abstractmethod
    async def close(self) -> None: 
        ...

    @abstractmethod
    async def warmup(self) -> None: 
        ...
    
    @abstractmethod
    def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        ...
    
    @abstractmethod
    async def publish(self, channel: str, message: str) -> None:
        ...
    
    @abstractmethod
    def scan_iter(self, match: str) -> AsyncIterator[str]:
        ...