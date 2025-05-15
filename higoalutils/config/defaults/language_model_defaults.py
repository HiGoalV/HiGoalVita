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
from higoalutils.config.enums.sys_enums import AsyncType
from higoalutils.config.enums.model_enums import TokenizerType


@dataclass
class LanguageModelDefaults:
    """Default values for language model."""

    default_model: str = ""
    default_encoding_model: TokenizerType = TokenizerType.DeepSeekTokenizer
    api_key: None = None
    encoding_model: str = ""
    device: str = "cpu"
    max_tokens: int = 8192 # 如果是openai 此处值为 4000
    temperature: float = 0
    top_p: float = 1
    request_timeout: float = 180.0
    api_base: None = None
    model_supports_json: None = None
    tokens_per_minute: int = 50_000
    requests_per_minute: int = 1_000
    retry_strategy: str = "native"
    max_retries: int = 10
    max_retry_wait: float = 10.0
    concurrent_requests: int = 25
    responses: None = None
    async_mode: AsyncType = AsyncType.THREADED