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


class RelationDatabaseType(str, Enum):
    """Enum for the type of relation databse to use."""

    MYSQL = "mysql"
    """The MySQL database"""
    SQLITE = "sqlite"
    """The SQLite database"""
    OCEANBASE = "oceanbase"
    """The OceanBase database"""
    NONE = "none"
    """No relation database"""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'