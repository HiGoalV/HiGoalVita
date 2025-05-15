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

from higoalutils.config.models.system_config import SystemConfig

class PreloadUtils:
    def __init__(self):
        pass
    async def start_up(self):
        self.load_system_config()
        await self.load_database()

    def load_system_config(self) -> SystemConfig:
        from higoalutils.config.load_config import get_config
        _config = get_config()
        return _config
    
    async def load_database(self):
        from higoalutils.database.memory_store.lifecycle import init_memory_stores
        from higoalutils.database.relational_database.lifecycle import init_relational_db
        await init_memory_stores()
        await init_relational_db()


    async def clean_up(self):
        from higoalutils.utils.singleton_utils.registry import shutdown_all
        await shutdown_all()

preload_utils = PreloadUtils()