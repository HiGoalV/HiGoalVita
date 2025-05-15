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

import re
import pytz
from datetime import datetime, timedelta, timezone, date
from typing import Any, Literal
from dateutil.parser import parse as dateutil_parse

from higoalutils.config.load_config import get_config
from higoalutils.config.enums.time_enums import TimeGranularity, TimeType

TIME_ZONE = get_config().base_config.time_zone
TZ = pytz.timezone(TIME_ZONE)


class TimeUtils:
    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def now_local() -> datetime:
        return TimeUtils.now_utc().astimezone(TZ)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=TZ).astimezone(timezone.utc)
        return dt.astimezone(timezone.utc)
    

    @staticmethod
    def from_utc_to_readable(utc_str: str, granularity: TimeGranularity = TimeGranularity.SECOND) -> str:
        try:
            dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
            return TimeUtils.format_with_granularity(dt.astimezone(TZ), granularity)
        except Exception as e:
            raise ValueError(f"Invalid UTC datetime format: {utc_str}") from e

    @staticmethod
    def get_time_bundle(time_type: TimeType = TimeType.UTC) -> str | int:
        dt = TimeUtils.now_local()
        match time_type:
            case TimeType.UTC:
                return dt.astimezone(timezone.utc).isoformat()
            case TimeType.READABLE:
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            case TimeType.TIMESTAMP:
                return int(dt.timestamp())
            case _:
                raise ValueError(f"Unsupported time type: {time_type}")

    @staticmethod
    def parse_to_utc(value: str | int | float, kind: TimeType) -> datetime:
        if kind == TimeType.READABLE:
            return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ).astimezone(timezone.utc)
        elif kind == TimeType.TIMESTAMP:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        elif kind == TimeType.UTC:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
        elif kind == TimeType.NATURAL:
            return TimeUtils._parse_natural_language(str(value))
        raise ValueError(f"Unsupported kind: {kind}")

    @staticmethod
    def _parse_natural_language(value: str) -> datetime:
        from dateutil.relativedelta import relativedelta
        value = value.strip().lower()
        today = TimeUtils.now_local()

        if value in {"今天", "今日", "now", "today"}:
            return today.astimezone(timezone.utc)
        if value in {"昨天", "yesterday"}:
            return (today - timedelta(days=1)).astimezone(timezone.utc)
        if value in {"前天", "the day before yesterday"}:
            return (today - timedelta(days=2)).astimezone(timezone.utc)
        if "天前" in value or "days ago" in value:
            num = int(re.findall(r'\d+', value)[0])
            return (today - timedelta(days=num)).astimezone(timezone.utc)
        if "月前" in value or "months ago" in value:
            num = int(re.findall(r'\d+', value)[0])
            return (today - relativedelta(months=num)).astimezone(timezone.utc)
        if "年前" in value or "years ago" in value:
            num = int(re.findall(r'\d+', value)[0])
            return (today - relativedelta(years=num)).astimezone(timezone.utc)

        try:
            dt = dateutil_parse(value)
            return TimeUtils.to_utc(dt)
        except Exception:
            raise ValueError(f"Unrecognized natural date string: {value}")

    @staticmethod
    def format_with_granularity(dt: datetime, granularity: TimeGranularity) -> str:
        formats = {
            TimeGranularity.YEAR: "%Y",
            TimeGranularity.MONTH: "%Y-%m",
            TimeGranularity.DAY: "%Y-%m-%d",
            TimeGranularity.HOUR: "%Y-%m-%d %H",
            TimeGranularity.MINUTE: "%Y-%m-%d %H:%M",
            TimeGranularity.SECOND: "%Y-%m-%d %H:%M:%S"
        }
        return dt.strftime(formats[granularity])
    
    @staticmethod
    def get_now_local_readable(granularity: TimeGranularity = TimeGranularity.SECOND) -> str:
        return TimeUtils.format_with_granularity(TimeUtils.now_local(), granularity)

    @staticmethod
    def is_leap_year(year: int) -> bool:
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def get_last_day_of_month(year: int, month: int) -> datetime:
        if month == 12:
            return datetime(year + 1, 1, 1) - timedelta(days=1)
        return datetime(year, month + 1, 1) - timedelta(days=1)

    @staticmethod
    def replace_prompt_dates(prompt: str) -> str:
        today = TimeUtils.now_local().date()
        year = today.year
        weekday = ["一", "二", "三", "四", "五", "六", "日"][today.weekday()]
        fd_this_month = today.replace(day=1)
        fd_last_month = (fd_this_month - timedelta(days=1)).replace(day=1)
        start_this_week = today - timedelta(days=today.weekday())
        start_last_week = start_this_week - timedelta(days=7)
        date_map = {
            "today": today,
            "year": year,
            "weekday": weekday,
            "yesterday": today - timedelta(days=1),
            "day_before_yesterday": today - timedelta(days=2),
            "this_week_start": start_this_week,
            "this_week_end": today,
            "last_week_start": start_last_week,
            "last_week_end": start_last_week + timedelta(days=6),
            "this_month_start": fd_this_month,
            "this_month_end": today,
            "last_month_start": fd_last_month,
            "last_month_end": fd_this_month - timedelta(days=1),
            "this_year_start": datetime(today.year, 1, 1).date(),
            "this_year_end": today,
        }
        for key, val in date_map.items():
            prompt = prompt.replace(f"{{{key}}}", val.strftime("%Y-%m-%d") if isinstance(val, (datetime, date)) else str(val))
        return prompt
