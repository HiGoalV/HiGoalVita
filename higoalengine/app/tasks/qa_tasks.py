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

from higoalengine.config.enums.task_type import TaskStatusType
from higoalengine.config.load_config import get_engine_config
from higoalutils.database.memory_store.factory import MemoryStoreFactory
from higoalutils.database.relational_database.manager import DBEngineManager
from higoalcore.query.query import basic_search
from higoalutils.language_model.tokenizer.get_tokenizer import get_tokenizer
from higoalutils.config.load_config import get_config
from higoalutils.callbacks.record_query_callbacks import RecordQueryCallbacks


cfg = get_engine_config().memory_config

async def generate_answer(task_id: str, query: str, model: str):
    memory_store = MemoryStoreFactory.get_store()
    sessionmaker = DBEngineManager().get_sessionmaker()

    await memory_store.set(f"task:{task_id}:status", TaskStatusType.PROCESSING, expire=cfg.result_retention_time)

    try:
        sys_cfg = get_config()
        tokenizer = get_tokenizer(sys_cfg.language_model_config.default_encoding_model)
        callbacks = [
            RecordQueryCallbacks(
                tokenizer.count_tokens, 
                stream_to_redis=True, 
                task_id=task_id, 
                memory_store=memory_store,
                sessionmaker=sessionmaker
            )
        ]
        try:
            await basic_search(
                query=query,
                system_config=sys_cfg,
                embedding_config=sys_cfg.embedding_config,
                callbacks=callbacks,
                model_name=model
            ) 
        except asyncio.CancelledError:
            print(f"⚠️ 推理中断：任务 {task_id} 被主动取消")
            await memory_store.set(f"task:{task_id}:status", TaskStatusType.CANCELLED)
            return

        
    except Exception as e:
        print(f"❌ 任务执行失败：{e}")
        await memory_store.set(f"task:{task_id}:status", TaskStatusType.FAILED, expire=cfg.result_retention_time)