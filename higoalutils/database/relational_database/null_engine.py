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
from higoalutils.database.relational_database.base import DatabaseEngineBase
from sqlalchemy.orm import DeclarativeMeta


class NullDatabaseEngine(DatabaseEngineBase):

    def get_engine(self) -> AsyncEngine:
        raise NotImplementedError("NullDatabaseEngine has no engine.")

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        raise NotImplementedError("NullDatabaseEngine has no sessionmaker.")
    
    def get_base(self) -> DeclarativeMeta:
        raise NotImplementedError("NullDatabaseEngine has no base.")

    async def warmup(self) -> None:
        pass

    async def close(self) -> None:
        pass