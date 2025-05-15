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

import json
from typing import List, Optional
import lancedb
import pyarrow as pa
import time

from higoalutils.database.vector_store.base import (
    VectorStoreBase, VectorStoreDocument, VectorStoreSearchResult
)
from higoalutils.config.load_config import get_config
from higoalutils.database.vector_store.utils  import normalize_vector


class LanceDBStore(VectorStoreBase):
    """LanceDB 向量数据库实现（余弦相似度版本）"""

    def __init__(self):
        lancedb_cfg = get_config().database_config.lancedb_config
        self.container = lancedb_cfg.container_name # type: ignore
        self.top_k = lancedb_cfg.default_top_k # type: ignore
        self.similarity_threshold = lancedb_cfg.default_similarity_threshold # type: ignore
        self.overwrite = lancedb_cfg.overwrite # type: ignore
        self.db_connection = lancedb.connect(lancedb_cfg.path) # type: ignore

    def warmup(self) -> None:
        self.db_connection.table_names()

    def close(self) -> None:
        pass

    def _open_table(self, table_name: str):
        return self.db_connection.open_table(table_name)

    def get_full_table_name(self, simple_name: str) -> str:
        return f"{self.container}_{simple_name}"

    def load_documents(self, documents: List[VectorStoreDocument], table_name: str, overwrite: bool | None = None) -> None:
        overwrite = overwrite if overwrite is not None else self.overwrite
        data = [
            {
                "id": doc.id,
                "source_doc_id": doc.source_doc_id,
                "text": doc.text,
                "vector": normalize_vector(doc.vector),
                "metadata": json.dumps(doc.metadata),
            }
            for doc in documents if doc.vector is not None
        ]

        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("source_doc_id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32())),
            pa.field("metadata", pa.string()),
        ])

        # print(f"📝 准备写入 LanceDB，文档数量: {len(data)}")

        if overwrite:
            if data:
                self.db_connection.create_table(
                    table_name,
                    data=data,
                    mode="overwrite"
                )
            else:
                self.db_connection.create_table(
                    table_name,
                    schema=schema,
                    mode="overwrite"
                )
        else:
            table = self._open_table(table_name)
            if data:
                table.add(data, mode="append")

    def _build_filter(self, column: str, values: List[str]) -> Optional[str]:
        if not values:
            return None
        quoted = ", ".join(f"'{v}'" for v in values)
        return f"{column} in ({quoted})"

    def similarity_search_by_vector(
        self,
        vector: list[float],
        table_name: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        filter_column: str | None = None,
        filter_values: list[str] | None = None
    ) -> List[VectorStoreSearchResult]:
        t1 = time.time()
        top_k = top_k if top_k else self.top_k
        sim_t = similarity_threshold if similarity_threshold else self.similarity_threshold

        table = self._open_table(table_name)
        query_vector = normalize_vector(vector)
        
        # 明确使用余弦相似度搜索
        res = table.search(query_vector, vector_column_name="vector") # .metric("cosine")

        if filter_column and filter_values:
            query_filter = self._build_filter(filter_column, filter_values)
            if query_filter:
                res = res.where(query_filter, prefilter=True)

        docs = res.limit(top_k * 3).to_list()  # 获取更多结果以便后续过滤

        results = []
        for i, doc in enumerate(docs):
            raw_score = float(doc["_distance"])
            normalized_score = 1 - 0.5 * raw_score
            if sim_t > 0 and normalized_score < sim_t:
                continue
            results.append(VectorStoreSearchResult(
                document=VectorStoreDocument(
                    id=doc["id"],
                    text=doc["text"],
                    source_doc_id=doc["source_doc_id"],
                    vector=doc["vector"],
                    metadata=json.loads(doc["metadata"]),
                ),
                score=normalized_score,  # 使用归一化后的分数
            ))
        t2 = time.time()
        print(f"✅ 查询 LanceDB 向量数据库 共 {len(results)} 个结果通过相似度过滤，返回 Top {top_k}，耗时 {t2 - t1} 秒")
        return results[:top_k]

    def search_by_id(self, table_name: str, id: str) -> VectorStoreDocument:
        table = self._open_table(table_name)
        docs = table.search().where(f"id == '{id}'", prefilter=True).to_list()
        if not docs:
            return VectorStoreDocument(id=id, source_doc_id=None, text=None, vector=None)
        doc = docs[0]
        return VectorStoreDocument(
            id=doc["id"],
            text=doc["text"],
            source_doc_id=doc["source_doc_id"],
            vector=doc["vector"],
            metadata=json.loads(doc["metadata"]),
        )