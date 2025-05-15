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

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from higoalutils.utils.singleton_utils.singleton import singleton
from higoalutils.database.relational_database.factory import create_engine_instance
from higoalutils.database.relational_database.base import DatabaseEngineBase


@singleton
class DBEngineManager:

    def __init__(self):
        self._impl: DatabaseEngineBase = create_engine_instance()

    def get_engine(self) -> AsyncEngine:
        return self._impl.get_engine()

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self._impl.get_sessionmaker()
    
    def get_base(self) -> DeclarativeMeta:
        return self._impl.get_base()

    async def warmup(self) -> None:
        await self._impl.warmup()

    async def close(self) -> None:
        await self._impl.close()