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

from enum import Enum

class AsyncType(str, Enum):
    """Enum for the type of async to use."""

    ASYNCIO = "asyncio"
    THREADED = "threaded"


class DeviceType(str, Enum):
    """The device type for the pipeline."""

    CPU = "cpu"
    """The CPU device type."""
    CUDA = "cuda"
    """The CUDA device type."""
    MPS = "mps"
    """The MPS device type."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


class LanguageCode(str, Enum):
    """Language class definition."""

    Chinese = "zh"
    English = "en"

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


class EmbeddingType(str, Enum):
    """Embedding type class definition."""

    OpenAI = "openai_embedding"
    HuggingFace = "huggingface_embedding"

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'