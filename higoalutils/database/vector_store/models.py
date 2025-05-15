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

from higoalutils.database.vector_store.enums import VectorDatabaseType


class VectorDatabaseConfig(BaseModel):
    type: VectorDatabaseType


class LancedbConfig(BaseModel):
    path: str
    overwrite: bool
    container_name: str
    default_top_k: int
    default_similarity_threshold: float

class OBVeConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str
    overwrite: bool
    container_name: str
    default_top_k: int
    default_similarity_threshold: float