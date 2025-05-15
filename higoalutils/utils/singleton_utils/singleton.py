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

from typing import TypeVar, Type, cast
from higoalutils.utils.singleton_utils.registry import get_instance

T = TypeVar("T")

def singleton(cls: Type[T]) -> Type[T]:
    class SingletonWrapper(cls):
        def __new__(cls, *args, **kwargs):
            return get_instance(cls, *args, **kwargs)

    SingletonWrapper.__name__ = cls.__name__
    SingletonWrapper.__qualname__ = cls.__qualname__
    return cast(Type[T], SingletonWrapper)