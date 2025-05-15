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

"""Knowledge Graph Elements vector store 接口模块"""

from abc import abstractmethod
from typing import List, Dict

from higoalcore.config.enums.index_enums import VectorTable
from higoalutils.database.vector_store.base import VectorStoreBase, FilterColumn, VectorStoreSearchResult
from higoalutils.language_model.llm.base import BaseTextEmbedding


class IKGOperator():
    """
    命名实体操作模块，纯业务逻辑，不依赖具体数据库
    """
    
    def __init__(self, adapter: VectorStoreBase, embedder: BaseTextEmbedding):
        self.adapter = adapter
        self.embedder = embedder
    
    @abstractmethod
    async def upsert(
        self, 
        insert_ids: List[str] | None = None,
        update_ids: List[str] | None = None
    ) -> int:
        """upsert graph elements"""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        filter_column: str | None = None,
        filter_ids: List[str] | None = None
    ) -> List[Dict]:
        """定义文本检索"""
        ...

    async def _semantic_search(
        self,
        query: str,
        simple_table_name: VectorTable,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        filter_column: str | None = None,
        filter_ids: List[str] | None = None
    ) -> List[Dict]:
        """
        语义检索
        args:
            query: 检索的文本
            simple_table_name: 检索的表名
            top_k: 最多返回的记录数,默认为空（即取系统配置的默认值）
            similarity_threshold: 相似度阈值,默认为空（即取系统配置的默认值）
            filter_column: 过滤字段,默认为空（可以是id或doc_id）
            filter_ids: 过滤字段值列表,默认为空（即取系统配置的默认值）
        returns:
            List[Dict]: 检索结果
        """
        if not simple_table_name or simple_table_name not in set(VectorTable):
            raise ValueError(f"Invalid table_name: {simple_table_name}. Table name must be one of {set(VectorTable)}")
        
        table_name = simple_table_name.value if isinstance(simple_table_name, VectorTable) else simple_table_name
        
        query_vector = self.embedder.embed(query)[0]

        # 参数处理
        params = {}
        if filter_column and filter_ids:
            if filter_column not in [FilterColumn.DOCID.value]:
                raise ValueError(f"Invalid filter_column: {filter_column}")
            params["filter_column"] = filter_column
            params["filter_values"] = filter_ids

        full_table_name = self.adapter.get_full_table_name(
            simple_name=table_name
        )

        results = self.adapter.similarity_search_by_vector(
            vector=query_vector,
            table_name=full_table_name,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            **params
        )
        return self._process_search_results(results)
    
    def _process_search_results(self, results: List[VectorStoreSearchResult]) -> List[Dict]:
        """处理搜索结果"""
        processed = []
        for r in results:
            result_item = {
                "id": r.document.id,
                "score": r.score,
                "text": r.document.text,
                "doc_id": r.document.source_doc_id,
                "metadata": r.document.metadata
            }
            
            processed.append(result_item)
        return processed
