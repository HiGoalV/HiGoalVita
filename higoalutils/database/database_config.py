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

from typing import Optional
from pydantic import BaseModel, model_validator

from higoalutils.database.memory_store.enums import MemoryDatabaseType
from higoalutils.database.memory_store.models import *
from higoalutils.database.relational_database.enums import RelationDatabaseType
from higoalutils.database.relational_database.models import *
from higoalutils.database.vector_store.enums import VectorDatabaseType
from higoalutils.database.vector_store.models import *


class DatabaseConfig(BaseModel):
    memery_database_config: MemoryDatabaseConfig
    relation_database_config: RelationDatabaseConfig
    vector_database_config: VectorDatabaseConfig

    redis_config: Optional[RedisConfig] = None
    mysql_config: Optional[MysqlConfig] = None
    oceanbase_relational_config: Optional[OBReConfig] = None
    sqlite_config: Optional[SqliteConfig] = None
    lancedb_config: Optional[LancedbConfig] = None
    oceanbase_vector_config: Optional[OBVeConfig] = None


    @model_validator(mode="after")
    def validate_selected_config(self) -> "DatabaseConfig":

        # 检查 memory_database_config
        if self.memery_database_config:
            if self.memery_database_config.type == MemoryDatabaseType.REDIS:
                assert self.redis_config is not None, "REDIS 配置缺失"

        # 检查 relation_database_config
        if self.relation_database_config:
            if self.relation_database_config.type == RelationDatabaseType.MYSQL:
                assert self.mysql_config is not None, "MySQL 配置缺失"
            elif self.relation_database_config.type == RelationDatabaseType.SQLITE:
                assert self.sqlite_config is not None, "Sqlite 配置缺失"
            elif self.relation_database_config.type == RelationDatabaseType.OCEANBASE:
                assert self.oceanbase_relational_config is not None, "OceanBase 配置缺失"

        # 检查 vector_database_config
        if self.vector_database_config:
            if self.vector_database_config.type == VectorDatabaseType.LANCEDB:
                assert self.lancedb_config is not None, "LanceDB 配置缺失"
            elif self.relation_database_config.type == VectorDatabaseType.OCEANBASE:
                assert self.oceanbase_vector_config is not None, "OceanBase 配置缺失"
        
        return self