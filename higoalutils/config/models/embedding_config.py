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

from pydantic import BaseModel, Field, model_validator
from typing import Optional

from higoalutils.config.enums.sys_enums import AsyncType, EmbeddingType, DeviceType
from higoalutils.config.defaults.embedding_defaults import HuggingFaceEmbeddingDefaults, OpenAIEmbeddingDefaults


class EmbeddingModelConfig(BaseModel):
    type: EmbeddingType

class HuggingFaceEmbeddingConfig(BaseModel):
    default_model: str = Field(default=HuggingFaceEmbeddingDefaults.model)
    device: DeviceType = Field(default=HuggingFaceEmbeddingDefaults.device)
    parallelization_num_threads: int = Field(default=HuggingFaceEmbeddingDefaults.parallelization_num_threads)
    parallelization_stagger: float = Field(default=HuggingFaceEmbeddingDefaults.parallelization_stagger)
    async_mode: AsyncType = Field(default=HuggingFaceEmbeddingDefaults.async_mode)


class OpenAIEmbeddingConfig(BaseModel):
    default_model: str = Field(default=OpenAIEmbeddingDefaults.model)
    request_timeout: float = Field(default=OpenAIEmbeddingDefaults.request_timeout)
    retry_strategy: str = Field(default=OpenAIEmbeddingDefaults.retry_strategy)
    max_retries: int = Field(default=OpenAIEmbeddingDefaults.max_retries)
    max_retry_wait: float = Field(default=OpenAIEmbeddingDefaults.max_retry_wait)
    async_mode: AsyncType = Field(default=OpenAIEmbeddingDefaults.async_mode)


class EmbeddingConfig(BaseModel):
    embedding_model_config: EmbeddingModelConfig
    huggingface_embedding_config: Optional[HuggingFaceEmbeddingConfig] = None
    openai_embedding_config: Optional[OpenAIEmbeddingConfig] = None

    @model_validator(mode="after")
    def validate_active_model(self):
        model_type = self.embedding_model_config.type

        if model_type == EmbeddingType.HuggingFace:
            if self.huggingface_embedding_config is None:
                raise ValueError("huggingface_embedding_config is required for huggingface_embedding")
        elif model_type == EmbeddingType.OpenAI:
            if self.openai_embedding_config is None:
                raise ValueError("openai_embedding_config is required for openai_embedding")
        else:
            raise ValueError(f"Unsupported embedding model type: {model_type}")

        return self