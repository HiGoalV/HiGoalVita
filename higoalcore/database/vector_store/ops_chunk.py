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

"""业务层操作模块"""
import logging
from typing import List, Dict

from higoalcore.config.enums.index_enums import VectorTable
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalcore.database.vector_store.ikg_operator import IKGOperator
from higoalutils.database.vector_store.base import VectorStoreBase, VectorStoreDocument
from higoalutils.language_model.llm.base import BaseTextEmbedding


log = logging.getLogger(__name__)

class ChunkOperator(IKGOperator):
    """文本块操作模块"""
    
    def __init__(self, adapter: VectorStoreBase, embedder: BaseTextEmbedding):
        super().__init__(adapter, embedder)
    
    async def upsert_chunk(self, 
        chunks: List[ChunkText] | List[Dict], 
        overwrite: bool = True
    ) -> int:
        """
        插入或更新文本块
        args:
            chunks: List[ChunkText] | List[Dict]
            overwrite: bool = True
        """
        # 生成所有chunk的向量文档
        if isinstance(chunks[0], dict):
            try:
                chunks = [ChunkText(**chunk) for chunk in chunks] # type: ignore
            except Exception as e:
                log.error(f"Failed to convert chunks to ChunkText: {e}")
                raise e
    
        docs = [self._chunk_to_vector_doc(chunk) for chunk in chunks] # type: ignore
        
        table_name = self.adapter.get_full_table_name(
            simple_name=VectorTable.CHUNKS.value,
        )

        self.adapter.load_documents(
            documents=docs,
            overwrite=overwrite,
            table_name=table_name
        )
        log.info(f"Upserted {len(docs)} chunks to {table_name}")
        return len(docs)
    
    async def semantic_search(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        filter_column: str | None = None,
        filter_ids: List[str] | None = None
    ) -> List[Dict]:
        """语义搜索关系"""
        return await self._semantic_search(
            query=query,
            simple_table_name=VectorTable.CHUNKS,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            filter_column=filter_column,
            filter_ids=filter_ids
        )
    
    def _chunk_to_vector_doc(self, chunk: ChunkText) -> VectorStoreDocument:
            """将单个ChunkText转换为VectorStoreDocument"""
            # 使用embedder生成向量
            vector = None
            if chunk.text:
                vector = self.embedder.embed(chunk.text)[0]
            
            # 构建metadata
            metadata = chunk.attributes.copy()
            if chunk.filename:
                metadata["filename"] = chunk.filename
            
            return VectorStoreDocument(
                id=chunk.id,
                source_doc_id=chunk.source_doc_id,
                text=chunk.text,
                vector=vector,
                metadata=metadata
            )