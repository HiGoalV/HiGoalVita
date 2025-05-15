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

class PlatformType(str, Enum):
    """Platform type"""

    openai = "openai"
    """OpenAI"""
    huggingface = "huggingface"
    """HuggingFace"""
    deepseek = "deepseek"
    """DeepSeek"""
    dashscope = "dashscope"
    """DashScope"""
    nltk = "nltk"
    """NLTK"""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'

class ObjectType(str, Enum):
    """Object type"""

    CHAT = "chat"
    """Chat"""
    EMBEDDING = "embedding"
    """Embedding"""
    SENTENCE_SPLITTER = "sentence_splitter"
    """Sentence Splitter"""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'

class TokenizerType(str, Enum):
    """Tokenizer type"""
    OpenAITokenizer = "cl100k_base"
    """OpenAI tokenizer"""
    DeepSeekTokenizer = "deepseek_tokenizer"
    """DeepSeek tokenizer"""
    DashScopeTokenizer = "dashscope_tokenizer"
    """DashScope tokenizer"""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'

