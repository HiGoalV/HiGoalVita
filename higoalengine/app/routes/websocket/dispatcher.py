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

import inspect
from typing import Dict, Any, Optional, Type, get_origin, get_args, Annotated

from pydantic import BaseModel, ValidationError
from higoalengine.app.routes.websocket.connection_socketio import SocketIOConnection
from higoalengine.app.routes.websocket.types import HandlerType, WSDepends


class WSDispatcher:
    def __init__(self):
        self._handlers: Dict[str, Dict[str, Any]] = {}
        self._default_handler: Optional[HandlerType] = None

    def register(
        self,
        type_: str,
        *,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
    ):
        def decorator(func: HandlerType):
            if type_ in self._handlers:
                raise ValueError(f"消息类型 {type_} 已注册")
            self._handlers[type_] = {
                "handler": func,
                "request_model": request_model,
                "response_model": response_model
            }
            return func
        return decorator

    def set_default(self, func: HandlerType):
        self._default_handler = func

    async def dispatch(self, wsconn: SocketIOConnection, **extra_params: Any):

        try:
            if "data" in extra_params:
                
                raw_msg = await wsconn.receive_json(extra_params["data"])
                print(f"🔍 raw_msg = {raw_msg}")
            else:
                raise ValueError("Socket.IO 消息缺少 'data' 参数")

            msg_type = raw_msg.get("type", "__default__")

            if msg_type == "ping":
                await wsconn.send_json({"type": "pong"})
                return

            config = self._handlers.get(msg_type)
            if not config:
                if self._default_handler:
                    await self._default_handler(wsconn, raw_msg)
                return

            await self._handle_message(wsconn, config, raw_msg, extra_params)

        except Exception as e:
            await wsconn.send_error(f"处理消息失败: {e}")


    async def _handle_message(
        self,
        wsconn: SocketIOConnection,
        config: Dict[str, Any],
        raw_msg: dict,
        extra_params: dict,
    ) -> None:
        try:
            request_model: Optional[Type[BaseModel]] = config.get("request_model")
            response_model: Optional[Type[BaseModel]] = config.get("response_model")
            handler: HandlerType = config["handler"]

            parsed_req = (
                request_model.model_construct(**raw_msg)
                if request_model else raw_msg
            )

            inject_kwargs = await self._build_injection(handler, wsconn, parsed_req, extra_params)
            result = await handler(**inject_kwargs)

            if result:
                await wsconn.send_json(result, model=response_model)

        except ValidationError as e:
            await wsconn.send_error(f"数据验证失败: {e}", code=422)
        except Exception as e:
            await wsconn.send_error(f"处理失败: {e}", code=500)

    async def _build_injection(
        self,
        handler: HandlerType,
        wsconn: SocketIOConnection,
        req: BaseModel | dict,
        extra_params: dict,
    ):
        sig = inspect.signature(handler)
        inject_kwargs = {}

        for name, param in sig.parameters.items():
            ann = param.annotation
            default = param.default

            if name == "wsconn":
                inject_kwargs[name] = wsconn
            elif name == "req":
                inject_kwargs[name] = req
            elif name in extra_params:
                inject_kwargs[name] = extra_params[name]
            elif get_origin(ann) is Annotated:
                real_type, depends_info = get_args(ann)
                if not isinstance(depends_info, WSDepends):
                    raise ValueError(f"依赖 {name} 注解错误，必须是 WSDepends")
                dep_func = depends_info.dependency
                value = dep_func()
                if inspect.isasyncgen(value):
                    try:
                        value = await value.__anext__()
                    except StopAsyncIteration:
                        raise ValueError(f"依赖 {name} 没有正确 yield 出对象")
                elif inspect.isawaitable(value):
                    value = await value
                inject_kwargs[name] = value
            elif isinstance(default, WSDepends):
                dep_func = default.dependency
                value = dep_func()
                if inspect.isasyncgen(value):
                    try:
                        value = await value.__anext__()
                    except StopAsyncIteration:
                        raise ValueError(f"依赖 {name} 没有正确 yield 出对象")
                elif inspect.isawaitable(value):
                    value = await value
                inject_kwargs[name] = value
            elif default is not inspect.Parameter.empty:
                inject_kwargs[name] = default
            else:
                raise ValueError(f"缺少必要参数: {name}")

        return inject_kwargs