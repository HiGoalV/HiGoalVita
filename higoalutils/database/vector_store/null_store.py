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

from typing import Any, List
from higoalutils.database.vector_store.base import (
    VectorStoreBase,
    VectorStoreDocument,
    VectorStoreSearchResult,
)

class NullVectorStore(VectorStoreBase):
    """无操作的向量数据库实现，用于禁用或调试场景"""


    def _open_table(self, **kwargs: Any) -> Any:
        return None

    def load_documents(self, documents: List[VectorStoreDocument], table_name: str, overwrite: bool | None = None) -> None:
        pass

    def close(self) -> None:
        pass

    def warmup(self) -> None:
        pass

    def _filter_by_id(self, include_ids: list[str] | list[int]) -> Any:
        return None

    def _filter_by_doc_id(self, include_doc_ids: list[str] | list[int]) -> Any:
        return None

    def similarity_search_by_vector(
        self,
        vector: list[float],
        table_name: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        filter_column: str | None = None,
        filter_values: list[str] | None = None
    ) -> List[VectorStoreSearchResult]:
       return []

    def search_by_id(self, table_name: str, id: str) -> VectorStoreDocument:
        return VectorStoreDocument(id=id, source_doc_id=None, text=None,  vector=None)

    def get_full_table_name(self, simple_name: str) -> str:
        return f"null_{simple_name}"