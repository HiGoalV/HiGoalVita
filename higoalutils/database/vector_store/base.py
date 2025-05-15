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

from abc import ABC, abstractmethod
from typing import Any, List
from dataclasses import dataclass, field
from enum import Enum


class FilterColumn(str, Enum):
    """Enum for the column of vector store to filter."""

    DOCID = "source_doc_id"
    """Column name for the source document id."""
    ID = "id"
    """Column name for the chunk id."""


@dataclass
class VectorStoreDocument:
    id: str
    source_doc_id: str | None
    text: str | None
    vector: list[float] | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorStoreSearchResult:
    document: VectorStoreDocument
    score: float


class VectorStoreBase(ABC):
    """统一向量数据库接口基类"""

    @abstractmethod
    def warmup(self) -> None:
        """连接预热"""
        ...

    @abstractmethod
    def close(self) -> None:
        """关闭连接"""
        ...

    @abstractmethod
    def load_documents(self, documents: List[VectorStoreDocument], table_name: str, overwrite: bool | None = None) -> None:
        """向量入库"""
        ...

    @abstractmethod
    def similarity_search_by_vector(
        self,
        vector: list[float],
        table_name: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        filter_column: str | None = None,
        filter_values: list[str] | None = None
    ) -> List[VectorStoreSearchResult]:
        """向量相似度检索"""
        ...

    @abstractmethod
    def search_by_id(self, table_name: str, id: str) -> VectorStoreDocument:
        """通过ID精确查找"""
        ...

    @abstractmethod
    def get_full_table_name(self, simple_name: str) -> str:
        """根据逻辑表名获取完整表名"""
        ...