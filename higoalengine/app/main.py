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

from fastapi import FastAPI
import socketio
from contextlib import asynccontextmanager
from pyprojroot import here
import sys
sys.path.append(str(here()))

from higoalengine.app.preload_manager import preload_manager
from higoalengine.app.routes import router as all_routes
from higoalengine.app.cors_config import apply_cors


# build lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    await preload_manager.preload_all()
    yield
    await preload_manager.clean_up()

app = FastAPI(lifespan=lifespan)

apply_cors(app)

app.include_router(all_routes)



from higoalengine.app.routes.websocket.connection_socketio import SocketIOConnection
from higoalengine.app.routes.websocket.handler import dispatcher

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    print(f"✅ 客户端连接: {sid}")

@sio.event
async def disconnect(sid):
    print(f"❌ 客户端断开: {sid}")


@sio.event
async def message(sid, data):
    print(f"📥 收到原始消息: {data}")
    conn = SocketIOConnection(
        sid=sid,
        emit_func=lambda event, payload: sio.emit(event, payload, to=sid),
        disconnect_func=lambda: sio.disconnect(sid)
    )
    await dispatcher.dispatch(conn, data=data) # type: ignore

app.mount("/", socketio.ASGIApp(sio))