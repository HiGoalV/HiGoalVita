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

"""用于时间的公共函数"""

import re
import pytz
from datetime import datetime, timedelta, timezone
from typing import Any

from higoalutils.config.load_config import get_config


TIME_ZONE = get_config().base_config.time_zone

class DateUtility:
    @staticmethod
    def is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    
    @staticmethod
    def get_last_day_of_month(year, month):
        if month == 12:
            return datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            return datetime(year, month + 1, 1) - timedelta(days=1)
        
    @staticmethod
    def format_date(date_str):
        date_str = date_str.replace(" ", "").strip() # 处理空格和换行符
        try:
            # 处理YYYY年MM月DD日
            if "年" in date_str and "日" in date_str:
                date_str = date_str.replace("日", "").replace("年", "-").replace("月", "-")
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            
            # 处理YYYY年MM月
            if "年" in date_str and "月" in date_str and "日" not in date_str:
                year, month = re.findall(r"\d+", date_str)
                return f"{year}-{int(month):02d}"
            
            # 处理MM月DD日（自动推断年份）
            if "月" in date_str and "日" in date_str:
                today = datetime.today()
                month, day = re.findall(r"\d+", date_str)
                month = int(month)
                day = int(day)
                year = today.year - 1 if (month > today.month) or (month == today.month and day > today.day) else today.year
                return f"{year}-{month:02d}-{day:02d}"
            
            # 处理分隔符为.或-的日期，YYYY-MM-DD、YYYY.MM.DD、YYYY-MM、YYYY.MM、MM-DD
            for sep in [".", "-"]:
                if sep in date_str:
                    parts = date_str.split(sep)
                    if len(parts) == 3:  # YYYY-MM-DD
                        return datetime.strptime(date_str, f"%Y{sep}%m{sep}%d").strftime("%Y-%m-%d")
                    elif len(parts) == 2:  # YYYY-MM 或 MM-DD
                        if len(parts[0]) == 2:  # MM-DD
                            today = datetime.today()
                            month = int(parts[0])
                            day = int(parts[1])
                            year = today.year - 1 if (month > today.month) or (month == today.month and day > today.day) else today.year
                            return f"{year}-{month:02d}-{day:02d}"
                        else: # YYYY-MM
                            year = int(parts[0])
                            return f"{year}-{int(parts[1]):02d}"
            
        except Exception as e:
            print(f"日期格式化错误: {date_str} - {str(e)}")
        return date_str  # 无法解析时返回原字符串
    @staticmethod
    def safe_convert_to_utc(dt: datetime):
        """安全转换为UTC时区，用于时间排序，比如取min / max 值"""
        if not isinstance(dt, datetime):
            return datetime.now().astimezone(timezone.utc)
        if dt.tzinfo is None:  # 无时区的datetime
            return dt.replace(tzinfo=timezone.utc)
        else:  # 有时区的datetime
            return dt.astimezone(timezone.utc)
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime | None:
        """将日期字符串解析为datetime对象"""
        if not date_str or date_str.upper() == "NONE":
            return None
        # 尝试解析带时区的格式（如 "2024-05-06 22:21:10 +0008"）
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            pass
        
        # 尝试解析简单日期格式（如 "2024-05-06"）
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None
        
    @staticmethod
    def now_timezone(time_zone: str = TIME_ZONE) -> datetime:
        return datetime.now(pytz.timezone(time_zone))