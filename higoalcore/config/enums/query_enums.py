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

from enum import Enum

class SearchMethod(str, Enum):
    """The type of search to run."""

    BASIC = "basic"

    def __str__(self):
        """Return the string representation of the enum value."""
        return self.value

class PromptFileType(str, Enum):
    """Prompt存储的文件格式枚举类"""

    YAML = ".yaml"
    """prompt以yaml格式存储，扩展名为.yaml"""
    TXT = ".txt"
    """prompt以txt格式存储，扩展名为.txt"""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'