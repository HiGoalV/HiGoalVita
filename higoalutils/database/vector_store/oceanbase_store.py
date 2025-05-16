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
from typing import List
from sqlalchemy import Column, String, Text, JSON as SQL_JSON, func
from pyobvector import ObVecClient, VECTOR
import time

from higoalutils.database.vector_store.base import (
    VectorStoreBase, VectorStoreDocument, VectorStoreSearchResult
)
from higoalutils.config.load_config import get_config
from higoalutils.database.vector_store.utils  import normalize_vector



class OBVectorStore(VectorStoreBase):
    """OceanBase 向量数据库实现（基于 pyobvector）"""

    def __init__(self):
        ob_cfg = get_config().database_config.oceanbase_vector_config
        self.container = ob_cfg.container_name  # type: ignore
        self.top_k = ob_cfg.default_top_k  # type: ignore
        self.similarity_threshold = ob_cfg.default_similarity_threshold  # type: ignore
        self.overwrite = ob_cfg.overwrite  # type: ignore
        self.database = ob_cfg.database # type: ignore

        self.client = ObVecClient(
            uri=f"{ob_cfg.host}:{ob_cfg.port}",  # type: ignore
            user=ob_cfg.user,  # type: ignore
            password=ob_cfg.password,  # type: ignore
            db_name=ob_cfg.database  # type: ignore
        )

    def warmup(self) -> None:
        self.client.perform_raw_text_sql("SHOW TABLES")  # type: ignore

    def close(self) -> None:
        pass  # ObVecClient 无需关闭

    def get_full_table_name(self, simple_name: str) -> str:
        return f"{self.container}_{simple_name}"

    def _get_columns(self) -> List[Column]:
        return [
            Column("id", String(64), primary_key=True),
            Column("source_doc_id", String(64)),
            Column("text", Text),
            Column("vector", VECTOR(1024)),
            Column("metadata", SQL_JSON),
        ]

    def load_documents(self, documents: List[VectorStoreDocument], table_name: str, overwrite: bool | None = None) -> None:
        overwrite = overwrite if overwrite is not None else self.overwrite

        self.client.perform_raw_text_sql(f"USE {self.database}")

        if overwrite:
            self.client.perform_raw_text_sql(f"DROP TABLE IF EXISTS `{table_name}`")

        # 创建表结构
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id VARCHAR(255) PRIMARY KEY,
            source_doc_id VARCHAR(255),
            text TEXT,
            vector VECTOR(1024),
            metadata JSON,
            VECTOR INDEX `{table_name}_vector_index` (vector) WITH (distance=cosine, type=hnsw)
        )
        """
        self.client.perform_raw_text_sql(create_table_sql)

        data = []
        for doc in documents:
            if doc.vector is not None:
                normalized_vector = normalize_vector(doc.vector)
                data.append({
                    "id": doc.id,
                    "source_doc_id": doc.source_doc_id,
                    "text": doc.text,
                    "vector": normalized_vector,
                    "metadata": doc.metadata,
                })
        
        # print(f"📝 准备写入 OceanBase，文档数量: {len(data)}")

        if data:
            self.client.insert(table_name, data=data)

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
        top_k = top_k if top_k is not None else self.top_k
        sim_t = similarity_threshold if similarity_threshold is not None else self.similarity_threshold
        
        res = self.client.ann_search(
            table_name=table_name,
            vec_data=normalize_vector(vector),
            vec_column_name="vector",
            distance_func=func.cosine_distance,
            topk=top_k * 3,
            with_dist=True,
            output_column_names=["id", "source_doc_id", "text", "vector", "metadata"],
            metric="cosine"
        )
        results = []
        for i, row in enumerate(res):
            *fields, distance = row
            score = 1 - float(distance)

            if sim_t > 0 and score < sim_t:
                continue
            
            id_, source_doc_id, text, vector_data, metadata_json = fields
            metadata = metadata_json if isinstance(metadata_json, dict) else json.loads(metadata_json)

            # print(f"🔹 第{i+1}个结果 Score: {score:.4f} - ID: {id_}", metadata)

            results.append(VectorStoreSearchResult(
                document=VectorStoreDocument(
                    id=id_,
                    source_doc_id=source_doc_id,
                    text=text,
                    vector=vector_data,
                    metadata=metadata,
                ),
                score=score
            ))
        t2 = time.time()
        print(f"✅ 查询 Oceanbase 向量数据库 共 {len(results)} 个结果通过相似度过滤，返回 Top {top_k}，耗时 {t2 - t1} 秒")
        return results[:top_k]

    def search_by_id(self, table_name: str, id: str) -> VectorStoreDocument:
        query = self.client.select(  # type: ignore
            table_name=table_name,
            where=f"id = '{id}'",
            output_column_names=["id", "source_doc_id", "text", "vector", "metadata"]
        )
        if not query:
            return VectorStoreDocument(id=id, source_doc_id=None, text=None, vector=None)
        doc = query[0]
        return VectorStoreDocument(
            id=doc["id"],
            source_doc_id=doc.get("source_doc_id"),
            text=doc.get("text"),
            vector=doc.get("vector"),
            metadata=doc.get("metadata", {}),
        )