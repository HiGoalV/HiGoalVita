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

from typing import Optional, List
from pydantic import BaseModel, Field, model_validator
from higoalutils.config.enums.model_enums import PlatformType, ObjectType


class ModelRegistryItem(BaseModel):
    id: int
    type: ObjectType
    platform: PlatformType
    model_name: str
    readable_name: Optional[str] = None
    enabled: bool = Field(default=True)

    # 仅远程平台需要
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    local_path: Optional[str] = None

    @property
    def display_name(self) -> str:
        return self.readable_name or self.model_name


class ModelRegistryConfig(BaseModel):
    model_registry: List[ModelRegistryItem]

    @model_validator(mode="after")
    def check_duplicates_and_fill_defaults(self):
        seen_ids = set()
        for item in self.model_registry:
            if item.id is not None:
                if item.id in seen_ids:
                    raise ValueError(f"Duplicate model id detected: {item.id}")
                seen_ids.add(item.id)
    
            if not item.readable_name:
                item.readable_name = item.model_name
        
        self.model_registry = [
            item for item in self.model_registry if item.enabled
        ]

        return self

    def get_by_model_name(self, model_name: str) -> ModelRegistryItem:
        for item in self.model_registry:
            if item.enabled and item.model_name == model_name:
                return item
        raise ValueError(f"模型名称 '{model_name}' 不存在或已被禁用")


    def get_by_id(self, model_id: int) -> ModelRegistryItem:
        for item in self.model_registry:
            if item.enabled and item.id == model_id:
                return item
        raise ValueError(f"模型名称 '{model_id}' 不存在或已被禁用")


    def get_chat_models(self) -> List[ModelRegistryItem]:
        return [item for item in self.model_registry if item.type == ObjectType.CHAT]