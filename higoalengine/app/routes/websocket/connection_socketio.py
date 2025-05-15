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

from typing import Callable, Any, Type, Optional, Awaitable
import json, time
from pydantic import BaseModel

from higoalengine.config.models.api_models import *


class SocketIOConnection:
    def __init__(
        self, sid: str, 
        emit_func: Callable[[str, Any], Awaitable[None]], 
        disconnect_func: Optional[Callable[[], Awaitable[None]]] = None
    ):
        self.sid = sid
        self.emit_func = emit_func
        self.disconnect_func = disconnect_func
        self.last_heartbeat = time.time()
        self.closed = False

    async def send_json(self, data: Any, code: int = 200, message: str = "", model: Optional[Type[BaseModel]] = None) -> None:
        payload = await self._prepare_payload(data, model)
        await self.emit_func("message", ResponseBase(code=code, status=1, message=message, data=payload).model_dump())

    async def send_error(self, message: str, code: int = 500) -> None:
        await self.emit_func("message", ResponseBase(code=code, status=0, message=message).model_dump())


    async def receive_json(self, raw: Optional[dict] = None) -> dict:
        self.last_heartbeat = time.time()
        return raw or {}

    async def close(self, reason: str = "socket.io disconnect") -> None:
        self.closed = True
        if self.disconnect_func:
            print("❌ 主动断开连接")
            await self.disconnect_func()

    async def _prepare_payload(self, data: Any, model: Optional[Type[BaseModel]] = None) -> dict:
        if isinstance(data, BaseModel):
            payload = data.model_dump()
        elif isinstance(data, dict):
            payload = data
        elif isinstance(data, str):
            payload = json.loads(data)
        else:
            raise TypeError(f"不支持类型: {type(data)}")
        if model:
            return model.model_validate(payload).model_dump()
        return payload