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

from typing import Any, Union

class SafeRequest:
    """一个可以用点（.）或者下标（[]）访问的轻量级请求对象"""
    
    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError("SafeRequest 只能初始化自 dict 类型")
        self._data = data

    def __getattr__(self, name: str) -> Any:
        """支持 req.xxx 访问"""
        value = self._data.get(name)
        return self._wrap(value)

    def __getitem__(self, key: str) -> Any:
        """支持 req["xxx"] 访问"""
        value = self._data.get(key)
        return self._wrap(value)

    def _wrap(self, value: Any) -> Any:
        """内部方法：把 dict 自动包装成 SafeRequest，list 里面的 dict 也包装"""
        if isinstance(value, dict):
            return SafeRequest(value)
        elif isinstance(value, list):
            return [SafeRequest(v) if isinstance(v, dict) else v for v in value]
        else:
            return value

    def dict(self) -> Union[dict, list]:
        """取出原始结构（递归展开 SafeRequest -> dict）"""
        def unwrap(obj: Any) -> Union[dict, list, Any]:
            if isinstance(obj, SafeRequest):
                return {k: unwrap(v) for k, v in obj._data.items()}
            elif isinstance(obj, list):
                return [unwrap(i) for i in obj]
            else:
                return obj

        return unwrap(self)