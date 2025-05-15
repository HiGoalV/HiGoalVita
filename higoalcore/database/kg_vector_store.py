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

"""向量存储入口模块"""

from higoalcore.database.vector_store import ChunkOperator
from higoalutils.config.models.embedding_config import EmbeddingConfig
from higoalutils.database.vector_store.factory import VectorStoreFactory
from higoalutils.language_model.llm.embedding_model_singleton import EmbeddingModelSingleton 


class KGVectorStore:
    """向量存储统一入口"""
    def __init__(self, embedding_config: EmbeddingConfig):
        self.embedder = EmbeddingModelSingleton.get_instance(embedding_config)
        self._init_components()
    
    def _init_components(self):
        """初始化各组件"""
        adapter = VectorStoreFactory().get_store()
        self.chunk_operator = ChunkOperator(adapter, self.embedder)
    