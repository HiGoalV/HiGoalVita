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

"""Knowledge Graph Data Loader to MySQL Module."""

import logging
from typing import List

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from higoalcore.database.relationaldb import DocumentLoader

log = logging.getLogger(__name__)


class KGDataLoader:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self.loader = DocumentLoader(sessionmaker)

    async def write_all(self, documents: List[dict], chunks: List[dict]):
        await self.loader.load_documents(documents, cleanup_empty=True)
        await self.loader.load_chunks(chunks, cleanup_existing=True)