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

"""用于向量存储的Document格式."""

from pydantic import BaseModel, Field
from typing import Any


class ChunkText(BaseModel):
    """Configuration section for chunking."""

    id: str = Field(
        description="The chunk size to use.",
    )
    text: str | None = Field(
        description="The chunk overlap to use.",
    )
    source_doc_id: str = Field(
        description="The source document id.",
    )
    filename: str | None = Field(
        description="Prepend metadata into each chunk.",
    )
    attributes: dict[str, Any] = Field(
        description="Prepend metadata into each chunk.",
    )
    