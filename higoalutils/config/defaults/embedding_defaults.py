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

from higoalutils.config.enums.sys_enums import DeviceType, AsyncType


class EmbeddingDefaultBase:
    """通用嵌入模型默认配置基类"""
    async_mode = AsyncType.THREADED


class HuggingFaceEmbeddingDefaults(EmbeddingDefaultBase):
    """默认配置：HuggingFace 本地嵌入模型"""
    model: str = "BAAI/bge-large-zh-v1.5"
    device: DeviceType = DeviceType.CPU
    parallelization_num_threads = 50
    parallelization_stagger = 0.3


class OpenAIEmbeddingDefaults(EmbeddingDefaultBase):
    """默认配置：OpenAI / DashScope 等远程嵌入模型"""
    model: str = "text-embedding-v3"
    request_timeout = 30.0
    retry_strategy = "exponential"
    max_retries = 3
    max_retry_wait = 10.0