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

import asyncio

from higoalutils.database.memory_store.base import MemoryStoreBase
from higoalengine.config.models.api_models import *
from higoalengine.app.routes.websocket.connection_socketio import SocketIOConnection
from higoalengine.config.models.api_chunk_models import StreamChunk, FullResult
from higoalengine.app.routes.websocket.utils import cleanup_task_cache_except_result_and_status


class TaskStreamer:
    def __init__(
        self,
        memory_store: MemoryStoreBase,
        task_id: str,
        wsconn: SocketIOConnection,
        stream: bool = False,
        poll_interval: float = 0.5,
        timeout: float = 30.0,
    ):
        self.store = memory_store
        self.task_id = task_id
        self.wsconn = wsconn
        self.stream = stream
        self.poll_interval = poll_interval
        self.timeout = timeout

        self.chunk_key = lambda i: f"task:{task_id}:chunk:{i}"
        self.max_key = f"task:{task_id}:chunk:max"
        self.status_key = f"task:{task_id}:status"
        self.result_key = f"task:{task_id}:result"

    async def streaming(self):
        """统一处理流式与非流式推送"""
        if self.stream:
            await self._stream_chunks()
        else:
            await self._stream_result()

    async def _stream_chunks(self):
        """流式推送模式"""
        index = 1
        try:
            while True:
                if self.wsconn.closed:
                    raise RuntimeError("WebSocket 已关闭")

                cached = await self.store.get(self.chunk_key(index))
                if cached:
                    chunk = StreamChunk.from_memory(cached)
                    if chunk.chunk_index != index:
                        raise RuntimeError(f"Chunk 序号不连续，期望 {index}，但收到 {chunk.chunk_index}")

                    await self.wsconn.send_json(code=200, data=chunk.to_frontend())
                    index += 1

                    if chunk.is_final:
                        print(f"✅ 任务 task_id={self.task_id} 流式完成")
                        break
                else:
                    await asyncio.sleep(self.poll_interval)

        except Exception as e:
            print(f"⚠️ 流式推送中断: {e}")
            try:
                await self.wsconn.send_error(
                    message="流式推送异常中断，请重试",
                    code=500
                )
            except Exception:
                pass
        finally:
            await cleanup_task_cache_except_result_and_status(self.store, self.task_id)

    async def _stream_result(self):
        """非流式推送模式"""
        elapsed = 0.0

        try:
            while elapsed < self.timeout:
                if self.wsconn.closed:
                    print(f"⚡️ WebSocket 已关闭，终止任务 {self.task_id}")
                    return

                status = await self.store.get(self.status_key)

                if not status:
                    await self.wsconn.send_error(
                        message="任务不存在或状态丢失",
                        code=404
                    )
                    return

                match status:
                    case TaskStatusType.SUCCEEDED:
                        result = await self.store.get(self.result_key)
                        if result:
                            full_result = FullResult.from_memory(result)
                            await self.wsconn.send_json(
                                data=full_result.to_frontend(),
                                code=200,
                                message="任务已完成"
                            )
                        else:
                            await self.wsconn.send_error(
                                message="任务已完成但结果缺失",
                                code=500
                            )
                        return

                    case TaskStatusType.CANCELLED | TaskStatusType.FAILED:
                        await self.wsconn.send_error(
                            message=f"任务已{status}，无法获取结果",
                            code=500
                        )
                        return

                    case TaskStatusType.PROCESSING | TaskStatusType.PENDING | TaskStatusType.OUTPUTTING:
                        await asyncio.sleep(self.poll_interval)
                        elapsed += self.poll_interval

                    case _:
                        await self.wsconn.send_error(
                            message=f"未知任务状态: {status}",
                            code=500
                        )
                        return

            await self.wsconn.send_error(
                message="查询超时，请稍后重试",
                code=504
            )

        except Exception as e:
            print(f"⚠️ 非流式推送中断: {e}")
            try:
                await self.wsconn.send_error(
                    message="非流式推送异常中断，请重试",
                    code=500
                )
            except Exception:
                pass
        finally:
            await cleanup_task_cache_except_result_and_status(self.store, self.task_id)