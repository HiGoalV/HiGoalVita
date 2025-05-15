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
from typing import Any, Dict, Type

_singleton_instances: Dict[str, Any] = {}

def get_instance(cls: Type[Any], *args, **kwargs) -> Any:
    """Get or create a singleton instance of the given class."""
    name = cls.__qualname__
    if name not in _singleton_instances:
        instance = super(cls, cls).__new__(cls, *args, **kwargs)
        _singleton_instances[name] = instance
    return _singleton_instances[name]

def destroy_instance(obj: Any):
    """Destroy the singleton instance of the given class."""
    name = obj.__class__.__qualname__
    _singleton_instances.pop(name, None)

def reset_instance(cls: type):
    """Reset the singleton instance of the given class."""
    name = cls.__qualname__
    _singleton_instances.pop(name, None)
    return cls()

async def shutdown_all():
    """Close and destroy all singleton instances."""
    for name, instance in list(_singleton_instances.items()):
        close_fn = getattr(instance, "close", None)
        if callable(close_fn):
            result = close_fn()
            if inspect.isawaitable(result):
                await result
        del _singleton_instances[name]