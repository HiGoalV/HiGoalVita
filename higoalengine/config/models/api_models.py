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

from pydantic import BaseModel
from typing import Optional

from higoalengine.config.enums.task_type import TaskStatusType, ResponseType


class EmptyModel(BaseModel):
    pass

class ResponseBase(BaseModel):
    code: int
    status: int
    message: str
    data: Optional[dict] = None

class MessageResponse(BaseModel):
    type: ResponseType
    task_id: Optional[str] = None
    status: Optional[TaskStatusType] = None
    content: Optional[str] = None


class WSCreateRequest(BaseModel):
    type: str = "create"
    query: str
    user_id: str = "default"
    model: int
    stream: bool = False
    model_config = {
        "extra": "ignore"
    }


class WSCancelRequest(BaseModel):
    type: str = "cancel"
    task_id: str
    model_config = {
        "extra": "ignore"
    }


class WSChunkResponse(BaseModel):
    type: ResponseType = ResponseType.CHUNK
    task_id: str
    chunk_index: int
    content: str
    is_final: bool


class SubmitRequest(BaseModel):
    query: str
    user_id: str = "default"
    model: Optional[str] = None


class PollRequest(BaseModel):
    task_id: str
    model_config = {
        "extra": "ignore"
    }

class CancelRequest(BaseModel):
    task_id: str
