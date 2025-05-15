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

from pydantic import BaseModel

from higoalutils.database.memory_store.enums import MemoryDatabaseType


class MemoryDatabaseConfig(BaseModel):
    type: MemoryDatabaseType

class RedisConfig(BaseModel):
    host: str
    port: int
    password: str
    db: int = 0
    max_connections: int = 10
    pool_recycle: int = 3600