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
from higoalutils.database.memory_store.redis_store import RedisMemoryStore
from higoalutils.database.memory_store.base import MemoryStoreBase
from higoalutils.database.memory_store.enums import MemoryDatabaseType
from higoalutils.database.memory_store.null_store import NullMemoryStore


class MemoryStoreFactory:
    @staticmethod
    def get_store() -> MemoryStoreBase:
        config = get_config()
        store_type: MemoryDatabaseType = config.database_config.memery_database_config.type
        match store_type:
            case MemoryDatabaseType.REDIS:
                return RedisMemoryStore()
            case MemoryDatabaseType.NONE:
                return NullMemoryStore()
            case _:
                return NullMemoryStore()