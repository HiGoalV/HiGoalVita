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

from dataclasses import dataclass
from pydantic import Field
from typing import List

from higoalcore.config.enums.index_enums import ChunkStrategyType
from higoalutils.config.enums.model_enums import TokenizerType


@dataclass
class ChunkingConfigDefaults:
    """Default values for chunks."""
    size: int = 1200
    overlap: int = 100
    strategy = ChunkStrategyType.TOKENS
    prepend_metadata: bool = False
    chunk_size_includes_metadata: bool = False
    group_by_columns: List[str] = Field(default_factory=lambda: ["id"])
    default_encoding_model: TokenizerType = TokenizerType.DeepSeekTokenizer