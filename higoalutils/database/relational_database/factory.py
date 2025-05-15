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
from higoalutils.database.relational_database.enums import RelationDatabaseType
from higoalutils.database.relational_database.base import DatabaseEngineBase
from higoalutils.database.relational_database.mysql_engine import MysqlEngine
from higoalutils.database.relational_database.oceanbase_engine import OceanBaseEngine
from higoalutils.database.relational_database.sqlite_engine import SqliteEngine
from higoalutils.database.relational_database.null_engine import NullDatabaseEngine


def create_engine_instance() -> DatabaseEngineBase:
    db_type = get_config().database_config.relation_database_config.type
    match db_type:
        case RelationDatabaseType.MYSQL:
            return MysqlEngine()
        case RelationDatabaseType.OCEANBASE:
            return OceanBaseEngine()
        case RelationDatabaseType.SQLITE:
            return SqliteEngine()
        case RelationDatabaseType.NONE:
            return NullDatabaseEngine()
        case _:
            return NullDatabaseEngine()