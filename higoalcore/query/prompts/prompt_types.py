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

"""该模块定义了各个功能提示词的枚举类"""

from enum import Enum


class BasicSearch(str, Enum):
    """Basic query prompts的枚举类"""

    file = "basic_search"
    """prompt所在的文件名，扩展名统一为yaml"""
    prompt = "answer"
    """answer场景下的prompt"""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'
    
