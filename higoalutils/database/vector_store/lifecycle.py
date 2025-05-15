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

from higoalutils.database.vector_store.factory import VectorStoreFactory
from higoalutils.utils.singleton_utils.registry import destroy_instance

store_instance = None

def init_vector_store():
    global store_instance
    store_instance = VectorStoreFactory().get_store()
    store_instance.warmup()

def shutdown_vector_store():
    if store_instance:
        store_instance.close()
        destroy_instance(store_instance)
