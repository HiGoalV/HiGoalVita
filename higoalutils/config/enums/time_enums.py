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


class TimeGranularity(str, Enum):
    """The time granularity for the pipeline."""
    YEAR = "year"
    """The year granularity."""
    MONTH = "month"
    """The month granularity."""
    DAY = "day"
    """The day granularity."""
    HOUR = "hour"
    """The hour granularity."""
    MINUTE = "minute"
    """The minute granularity."""
    SECOND = "second"
    """The second granularity."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'




class DatetimeFormat(str, Enum):
    """The datetime format for the pipeline."""
    date = "date"
    """The date format."""
    datetime = "datetime"
    """The datetime format."""
    month = "month"
    """The month format."""
    year = "year"
    """The year format."""
    timezone = "timezone"
    """The timezone format."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


class TimeType(str, Enum):
    """The time type for the pipeline."""
    READABLE = "readable"
    """The readable time type."""
    UTC = "utc"
    """The UTC time type."""
    TIMESTAMP = "timestamp"
    """The timestamp time type."""
    NATURAL = "natural"
    """The natural time type."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'
