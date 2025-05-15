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


class TaskStatusType(str, Enum):
    """The status of the task."""

    PENDING = "pending"
    """The pending status of the task."""
    PROCESSING = "processing"
    """The processing status of the task."""
    OUTPUTTING = "outputting"
    """The outputting status of the task."""
    SUCCEEDED = "succeeded"
    """The completed status of the task."""
    INTERRUPTED = "interrupted"
    """The interrupted status of the task."""
    FAILED = "failed"
    """The failed status of the task."""
    CANCELLED = "cancelled"
    """The cancelled status of the task."""
    UNKNOWN = "unknown"
    """The unknown status of the task."""

    def __repr__(self):
        """Get a stringrepresentation."""
        return f'"{self.value}"'

class ResponseType(str, Enum):
    """The type of the message."""

    STATUS = "status"
    """The status message."""
    CHUNK = "chunk"
    """The chunk message."""
    STREAM_START = "stream_start"
    """The stream_start message."""
    RESULT = "result"
    """The result message."""
    ERROR = "error"
    """The error message."""