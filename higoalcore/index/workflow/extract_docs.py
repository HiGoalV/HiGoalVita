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

"""工作流：加载文件、切片，并存入向量数据库。"""

from typing import List
import asyncio

from higoalcore.config.models.core_config import CoreConfig
from higoalcore.index.text_splitting.chunking_maker import ChunkingFactory
from higoalutils.database.relational_database.manager import DBEngineManager
from higoalcore.database.kgdataloader import KGDataLoader
from higoalcore.database.kg_vector_store import KGVectorStore
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalutils.logger.base import ProgressLogger
from higoalutils.utils.time_utils.date_uitility import DateUtility
from higoalutils.config.models.system_config import SystemConfig
from higoalutils.logger.progress import ProgressTicker


async def extract_docs(
    sys_config: SystemConfig,
    core_config: CoreConfig,
    progress_reporter: ProgressLogger | None = None,
) -> None:
    
    # 获取chunks
    chunking_logger = progress_reporter.child("📥 Loading & Chunking") if progress_reporter else None
    chunk_loader = ChunkingFactory(core_config.input_config, core_config.chunk_config, chunking_logger)
    chunks = await chunk_loader.run()

    # 将chunks写入到向量数据库
    vectordb_logger = progress_reporter.child("📦 Writing to VectorDB", transient=False) if progress_reporter else None
    ticker_v = ProgressTicker(vectordb_logger, num_total=1)
    vector_store = KGVectorStore(sys_config.embedding_config)
    await vector_store.chunk_operator.upsert_chunk(chunks)
    ticker_v()
    ticker_v.done()

    # 将chunks写入到关系型数据库
    rdb_logger = progress_reporter.child("🗃️ Writing to RDB", transient=False) if progress_reporter else None
    ticker_r = ProgressTicker(rdb_logger, num_total=1)
    await _store_docs_chunks_to_rdb(chunks)
    ticker_r()
    ticker_r.done()
    await asyncio.sleep(0.1)
    

async def _store_docs_chunks_to_rdb(chunks: List[ChunkText]):
    """将documents与chunks写入到关系型数据库"""
    utils_datetime = DateUtility()
    records = []
    documents = []
    doc_id = ""
    for chunk in chunks:
        title = chunk.attributes.get("title", "")
        if isinstance(title, list):
            title = ', '.join(title)
        if doc_id != chunk.source_doc_id:
            document = {
                "id": chunk.source_doc_id,
                "filename": chunk.filename,
                "title": title,
                "creation_date": chunk.attributes.get("creation_date", ""),
                "extracted_date": utils_datetime.now_timezone(),
            }
            documents.append(document)
            doc_id = chunk.source_doc_id

        record = {
            "id": chunk.id,
            "text": chunk.text,
            "source_doc_id": chunk.source_doc_id,
            "filename": chunk.filename,
            "title": title,
            "filename": chunk.filename, 
            "creation_date": chunk.attributes.get("creation_date", ""),
        }
        records.append(record)
    sessionmaker = DBEngineManager().get_sessionmaker()
    data_loader = KGDataLoader(sessionmaker)
    await data_loader.write_all(documents, records)