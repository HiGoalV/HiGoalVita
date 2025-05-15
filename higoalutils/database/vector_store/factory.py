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

from higoalutils.config.load_config import get_config
from higoalutils.database.vector_store.lancedb_store import LanceDBStore
from higoalutils.database.vector_store.oceanbase_store import OBVectorStore
from higoalutils.database.vector_store.null_store import NullVectorStore
from higoalutils.database.vector_store.base import VectorStoreBase
from higoalutils.database.vector_store.enums import VectorDatabaseType
from higoalutils.utils.singleton_utils.singleton import singleton


@singleton
class VectorStoreFactory:
    """统一的向量数据库工厂（返回单例连接实例）"""

    def __init__(self):
        self._store: VectorStoreBase | None = None
        self._initialized = False

    def get_store(self) -> VectorStoreBase:
        if self._store:
            return self._store

        config = get_config()
        db_type = config.database_config.vector_database_config.type

        match db_type:
            case VectorDatabaseType.LANCEDB:
                self._store = LanceDBStore()
            case VectorDatabaseType.OCEANBASE:
                self._store = OBVectorStore()
            case _:
                self._store = NullVectorStore()

        return self._store