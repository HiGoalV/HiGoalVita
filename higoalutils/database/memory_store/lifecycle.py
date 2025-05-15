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

from higoalutils.database.memory_store.factory import MemoryStoreFactory
from higoalutils.utils.singleton_utils.registry import destroy_instance

async def init_memory_stores() -> None:
    store = MemoryStoreFactory.get_store()
    await store.warmup()

async def shutdown_memory_stores() -> None:
    store = MemoryStoreFactory.get_store()
    await store.close()
    destroy_instance(store)