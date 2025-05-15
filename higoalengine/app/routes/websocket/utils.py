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

from higoalutils.database.memory_store.base import MemoryStoreBase
from higoalengine.config.load_config import get_engine_config


cfg = get_engine_config().memory_config

async def cleanup_task_cache_except_result_and_status(memory_store: MemoryStoreBase, task_id: str):
    """清理除 result 和 status 以外的所有 task缓存"""
    prefix = f"task:{task_id}:"
    preserve_keys = {f"{prefix}status", f"{prefix}result"}
    keys_to_delete = []

    async for key in memory_store.scan_iter(match=f"{prefix}*"):
        if key not in preserve_keys:
            keys_to_delete.append(key)

    if keys_to_delete:
        await memory_store.delete(*keys_to_delete)
        print(f"🧹 清理完成，删除 {len(keys_to_delete)} 个键: {keys_to_delete}")
    else:
        print("ℹ️ 无需清理：无临时键")