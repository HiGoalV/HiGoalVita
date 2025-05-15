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

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import asyncio

from higoalutils.database.relational_database.dependencies import get_db_session_ws
from higoalutils.database.memory_store.dependencies import get_store_dep_ws
from higoalutils.database.memory_store.base import MemoryStoreBase
from higoalutils.utils.code_utils.uuid import gen_uuid
from higoalengine.database.models import UserQATask, UserQuery
from higoalengine.app.tasks.qa_tasks import generate_answer
from higoalengine.config.enums.task_type import TaskStatusType, ResponseType
from higoalengine.app.routes.websocket.dispatcher import WSDispatcher
from higoalengine.app.routes.websocket.utils import cleanup_task_cache_except_result_and_status
from higoalengine.app.routes.websocket.streamer import TaskStreamer
from higoalengine.config.models.api_models import *
from higoalengine.app.routes.websocket.connection_socketio import SocketIOConnection
from higoalengine.app.routes.websocket.types import WSDepends
from higoalutils.config.load_model_info import get_model_info


dispatcher = WSDispatcher()

@dispatcher.register(
    "create",
    request_model=WSCreateRequest
)
async def handle_create(
    wsconn: SocketIOConnection,
    req: WSCreateRequest,
    memory_store: Annotated[MemoryStoreBase, WSDepends(get_store_dep_ws)],
    session: Annotated[AsyncSession, WSDepends(get_db_session_ws)] # 当前写法需要手动关闭连接池，到时候统一成fastapi的写法
):
    task_id = gen_uuid()

    print(req)

    async with session.begin():
        session.add(UserQATask(task_id=task_id, user_id=req.user_id, status=TaskStatusType.PENDING))
        session.add(UserQuery(task_id=task_id, query_text=req.query))

    await memory_store.set(f"task:{task_id}:status", TaskStatusType.PENDING)

    model_name = get_model_info().get_by_id(req.model).model_name
    
    asyncio.create_task(generate_answer(task_id, req.query, model_name))

    await wsconn.send_json(
        MessageResponse(
            type=ResponseType.STATUS,
            task_id=task_id,
            status=TaskStatusType.PENDING
        ), code=200,message="AI正在思考中...")
    
    streamer = TaskStreamer(
        memory_store=memory_store,
        task_id=task_id,
        wsconn=wsconn,
        stream=req.stream,
    )
    await streamer.streaming()

@dispatcher.register(
    "cancel",
    request_model=WSCancelRequest
)
async def handle_cancel(
    wsconn: SocketIOConnection, 
    req: WSCancelRequest,
    memory_store: Annotated[MemoryStoreBase, WSDepends(get_store_dep_ws)],
    session: Annotated[AsyncSession, WSDepends(get_db_session_ws)]
):
    task_id = req.task_id

    await memory_store.set(f"task:{task_id}:status", TaskStatusType.CANCELLED)
    try:
        async with session.begin():
            task = await session.get(UserQATask, task_id)
            if task:
                task.status = TaskStatusType.CANCELLED
            else:
                print(f"⚠️ 数据库中未找到任务 {task_id}，跳过更新")
    except Exception as e:
        print(f"⚠️ 数据库更新失败: {e}")

    await cleanup_task_cache_except_result_and_status(memory_store, task_id)

    await wsconn.send_json(
        MessageResponse(
            type=ResponseType.STATUS,
            task_id=task_id,
            status=TaskStatusType.CANCELLED
        ), code=200,message="任务已取消")

