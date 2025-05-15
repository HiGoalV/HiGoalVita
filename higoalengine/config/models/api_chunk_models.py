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

from pydantic import BaseModel, Field
from higoalutils.utils.time_utils.get_datetime import get_internet_datetime
from higoalengine.config.enums.task_type import ResponseType


class StreamChunk(BaseModel):
    task_id: str
    chunk_index: int
    content: str
    is_final: bool = False
    timestamp: str = Field(default_factory=lambda: get_internet_datetime().isoformat())

    def to_memory(self) -> dict:
        """转成 dict 保存到内存中"""
        return self.model_dump()

    @classmethod
    def from_memory(cls, data: dict) -> "StreamChunk":
        """从内存中的 dict 还原 BaseModel"""
        return cls.model_validate(data)

    def to_frontend(self) -> dict:
        """转成发送给前端的 dict：增加 type 字段"""
        data = self.model_dump(exclude={"timestamp"})  # ⬅️ 发送给前端不带 timestamp
        data["type"] = ResponseType.CHUNK
        return data


class FullResult(BaseModel):
    task_id: str
    content: str
    timestamp: str = Field(default_factory=lambda: get_internet_datetime().isoformat())

    def to_memory(self) -> dict:
        """转成 dict 保存到内存中"""
        return self.model_dump()

    def to_frontend(self) -> dict:
        """发送给前端：增加 type，去掉 timestamp"""
        data = self.model_dump(exclude={"timestamp"})
        data["type"] = ResponseType.RESULT
        return data
    
    @classmethod
    def from_memory(cls, data: str) -> "FullResult":
        """从内存读取"""
        return cls.model_validate(data)