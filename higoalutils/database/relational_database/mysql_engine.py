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

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeMeta

from higoalutils.database.relational_database.base import DatabaseEngineBase
from higoalutils.config.load_config import get_config


class MysqlEngine(DatabaseEngineBase):
    def __init__(self):
        cfg = get_config().database_config.mysql_config
        uri = f"mysql+asyncmy://{cfg.user}:{cfg.password}@{cfg.host}:{cfg.port}/{cfg.database}" # type: ignore
        self._Base = declarative_base()
        self._engine = create_async_engine(uri, future=True)
        self._sessionmaker = async_sessionmaker(bind=self._engine, class_=AsyncSession)

    def get_engine(self) -> AsyncEngine:
        return self._engine

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self._sessionmaker

    def get_base(self) -> DeclarativeMeta:
        return self._Base

    async def warmup(self) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

    async def close(self) -> None:
        await self._engine.dispose()