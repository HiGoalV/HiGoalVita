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

"""文档和块数据加载模块"""
import logging
import uuid
from collections import defaultdict
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import insert, select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from higoalcore.database.models.graph_tables import KGDocument, KGChunk
from higoalutils.utils.time_utils.date_uitility import DateUtility
from higoalutils.utils.time_utils.time_utils import TimeUtils

log = logging.getLogger(__name__)


class DocumentLoader:
    def __init__(self, sql_pool: async_sessionmaker[AsyncSession]):
        self.sql_pool = sql_pool
    
    async def check_file_processed(
        self,
        filename: str
    ) -> Dict[str, Any]:
        """检查文件是否已处理过"""
        async with self.sql_pool() as session:
            # 查询文档是否存在
            stmt = select(
                KGDocument.id,
                KGDocument.extracted_date,
                func.count(KGChunk.id).label('chunk_count')
            ).outerjoin(
                KGChunk, KGDocument.id == KGChunk.source_doc_id
            ).where(
                KGDocument.filename == filename
            ).group_by(KGDocument.id)

            result = await session.execute(stmt)
            doc = result.first()

            if not doc:
                return {
                    'processed': False,
                    'extracted_date': None,
                    'chunk_count': 0,
                    'document_id': None
                }

            return {
                'processed': doc.chunk_count > 0,
                'extracted_date': doc.extracted_date,
                'chunk_count': doc.chunk_count,
                'document_id': doc.id
            }

    
    async def load_documents(
        self,
        documents: List[Dict],
        cleanup_empty: bool = True
    ) -> Dict[str, List[str]]:
        """加载文档数据"""
        if not documents:
            return {'inserted_ids': [], 'deleted_ids': []}
        
        utils_date = DateUtility()

        async with self.sql_pool() as session:
            # 1. 先清理可能存在的空文档
            deleted_ids = []
            if cleanup_empty:
                # 找出没有chunks的文档
                stmt = select(
                    KGDocument.id
                ).outerjoin(
                    KGChunk, KGDocument.id == KGChunk.source_doc_id
                ).group_by(
                    KGDocument.id
                ).having(
                    func.count(KGChunk.id) == 0
                )

                result = await session.execute(stmt)
                empty_doc_ids = [str(doc) for doc in result.scalars()]

                if empty_doc_ids:
                    # 删除这些空文档
                    delete_stmt = delete(KGDocument).where(
                        KGDocument.id.in_(empty_doc_ids)
                    )
                    await session.execute(delete_stmt)
                    deleted_ids = empty_doc_ids

            # 2. 插入新文档（使用ON DUPLICATE KEY UPDATE避免重复）
            to_insert = []
            extracted_date = TimeUtils.now_local()
            for doc in documents:
                creation_date = utils_date._parse_date(doc.get('creation_date',""))
                to_insert.append({
                    'id': doc.get('id', str(uuid.uuid4())),
                    'filename': doc['filename'],
                    'title': doc.get('title', ''),
                    'author': doc.get('author', ''),
                    'source': doc.get('source', ''),
                    'creation_date': creation_date,
                    'extracted_date': extracted_date,
                    'raw_data': {
                        'original_data': doc.get('raw_data', {})
                    }
                })

            if to_insert:
                dialect = session.bind.dialect.name

                if dialect in ("mysql",) or dialect.startswith("oceanbase"):
                    from sqlalchemy.dialects.mysql import insert as mysql_insert

                    stmt = mysql_insert(KGDocument).values(to_insert)
                    stmt = stmt.on_duplicate_key_update(
                        title=stmt.inserted.title,
                        author=stmt.inserted.author,
                        source=stmt.inserted.source,
                        extracted_date=stmt.inserted.extracted_date,
                        raw_data=stmt.inserted.raw_data
                    )

                elif dialect == "sqlite":
                    from sqlalchemy.dialects.sqlite import insert as sqlite_insert

                    stmt = sqlite_insert(KGDocument).values(to_insert)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["id"],  # 主键冲突处理
                        set_={
                            "title": stmt.excluded.title,
                            "author": stmt.excluded.author,
                            "source": stmt.excluded.source,
                            "extracted_date": stmt.excluded.extracted_date,
                            "raw_data": stmt.excluded.raw_data,
                        }
                    )

                else:
                    raise NotImplementedError(f"Unsupported database dialect: {dialect}")

                await session.execute(stmt)

            await session.commit()

            return {
                'inserted_ids': [doc['id'] for doc in to_insert],
                'deleted_ids': deleted_ids
            }

    
    async def load_chunks(
        self,
        chunks: List[Dict],
        cleanup_existing: bool = True
    ) -> Dict[str, List[str]]:
        """加载文本块数据"""
        if not chunks:
            return {'inserted_ids': [], 'deleted_ids': []}

        async with self.sql_pool() as session:
            # 按文档分组
            doc_chunks = defaultdict(list)
            for chunk in chunks:
                doc_id = chunk.get('source_doc_id')
                if doc_id:
                    doc_chunks[doc_id].append(chunk)

            inserted_ids = []
            deleted_ids = []

            for doc_id, doc_chunk_list in doc_chunks.items():
                # 检查文档是否存在
                if not await self._check_document_exists(session, doc_id):
                    log.warning(f"Document {doc_id} not found, skipping chunks")
                    continue

                # 清理该文档现有的chunks（如果需要）
                if cleanup_existing:
                    delete_stmt = delete(KGChunk).where(
                        KGChunk.source_doc_id == doc_id)
                    result = await session.execute(delete_stmt)
                    if result.rowcount > 0:
                        deleted_ids.append(doc_id)

                # 准备插入数据
                to_insert = []
                for chunk in doc_chunk_list:
                    raw_data = {
                        'filename': chunk.get('filename'),
                        'creation_date': chunk.get('creation_date'),
                        **chunk.get('raw_data', {})
                    }
                    
                    to_insert.append({
                        'id': chunk.get('id', str(uuid.uuid4())),
                        'text': chunk.get('text', ''),
                        'source_doc_id': doc_id,
                        'title': chunk.get('title', ''),
                        'raw_data': raw_data
                    })

                if to_insert:
                    await session.execute(insert(KGChunk), to_insert)
                    inserted_ids.extend([chunk['id'] for chunk in to_insert])

            await session.commit()

            return {
                'inserted_ids': inserted_ids,
                'deleted_ids': deleted_ids
            }


    async def _check_document_exists(
        self,
        session: AsyncSession,
        doc_id: str
    ) -> bool:
        """检查文档是否存在"""
        stmt = select(KGDocument).where(KGDocument.id == doc_id)
        result = await session.execute(stmt)
        return result.scalar() is not None