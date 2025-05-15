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
from typing import List, Pattern

from higoalcore.config.models.input_config import InputConfig
from higoalcore.config.models.chunking_config import ChunkingConfig
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalutils.storage.pipeline_storage import PipelineStorage
from higoalutils.logger.base import ProgressLogger


class BaseChunkLoader(ABC):
    """每种输入类型的ChunkLoader应实现此接口，返回 List[ChunkText]"""

    def __init__(self, pattern: Pattern[str], input_type: str):
        self.pattern: Pattern[str] = pattern
        self.input_type = input_type

    @abstractmethod
    async def load_and_chunk(
        self,
        input_config: InputConfig,
        chunk_config: ChunkingConfig,
        storage: PipelineStorage,
        progress: ProgressLogger | None
    ) -> List[ChunkText]:
        ...