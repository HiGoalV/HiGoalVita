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

"""Date time related functions."""

import re
from  datetime import datetime,timezone
from datetime import timedelta
from typing import Any
import pytz

from higoalutils.config.enums.time_enums import DatetimeFormat, TimeType
from higoalutils.config.load_config import get_config


TIME_ZONE = get_config().base_config.time_zone


def get_internet_datetime(time_zone: str = TIME_ZONE) -> datetime:
    """
    返回指定时区的当前 datetime 对象（非字符串）
    """
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(pytz.timezone(time_zone))

def get_internet_time(type: DatetimeFormat = DatetimeFormat.date, time_zone: str = TIME_ZONE):
    """
    获取指定时区的互联网时间。
    
    :param type: 日期格式，分为'date'、'datetime'、'timezone'。默认为'datetime'。
    :return: 指定时区的当前时间。
    """
    # 获取UTC时间
    utc_now = datetime.now(timezone.utc)
    
    # 设置时区
    timezone_here = pytz.timezone(time_zone)
    
    # 将UTC时间转换为指定时区的时间
    local_time = utc_now.replace(tzinfo=pytz.utc).astimezone(timezone_here)
    result = local_time.strftime('%Y-%m-%d %H:%M:%S')
    if type == 'date':
        result = local_time.strftime('%Y-%m-%d')
    elif type == 'datetime':
        result = local_time.strftime('%Y-%m-%d %H:%M:%S')
    elif type == 'month':
        result = local_time.strftime('%Y-%m')
    elif type == 'year':
        result = local_time.strftime('%Y')
    elif type == 'timezone':
        result = "北京时间: " + local_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    return result
# 格式化日期字符串
def format_date(datestr):
    """格式化日期字符串，将2位数年份转换为4位数年份,最后的格式是YYYY-MM-DD 或 YYYY-MM"""
    if not bool(re.match(r'^\d{4}', datestr)):
        tmp_date = get_internet_time(DatetimeFormat.date)
        datestr = f"{tmp_date}-{datestr}"
    # 将日期转化为YYYY-MM-DD格式
    pattern = r'(\d{4}[年.-]\d{1,2}[月.-]\d{1,2})'
    match = re.search(pattern, datestr)
    if match:
        # 根据匹配到的日期字符串转换为YYYY-MM-DD格式
        date_part = match.group(1)
        date_part = re.sub(r'[年月]', '-', date_part)  # 替换中文年月为短横线
        date_part = re.sub(r'\.', '-', date_part)      # 替换点号为短横线
        date_part = date_part[:10]
        return date_part
    raise AssertionError(f"Invalid date format: {datestr}")

# 获取日期信息列表
def get_normal_dates(prompt_message):
    today_str = get_internet_time(DatetimeFormat.date)
    today = datetime.strptime(today_str, '%Y-%m-%d').date()
    year = today_str[:4]
    weekday = ["一", "二", "三", "四", "五", "六", "日"][today.weekday()]
    first_day_of_this_year = today.replace(month=1, day=1)
    first_day_of_this_month = today.replace(day=1)
    first_day_of_last_month = (first_day_of_this_month - timedelta(days=1)).replace(day=1)
    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - timedelta(weeks=1)
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)
    end_of_this_week = start_of_this_week + timedelta(days=6)
    end_of_last_week = start_of_last_week + timedelta(days=6)
    date_formats = {
        'today': today_str,
        'year': year,
        'weekday': weekday,
        'last_week_start': start_of_last_week.strftime('%Y-%m-%d'),
        'last_week_end': end_of_last_week.strftime('%Y-%m-%d'),
        'this_week_start': start_of_this_week.strftime('%Y-%m-%d'),
        'this_week_end': today.strftime('%Y-%m-%d'),
        'yesterday': yesterday.strftime('%Y-%m-%d'),
        'day_before_yesterday': day_before_yesterday.strftime('%Y-%m-%d'),
        'this_month_start': first_day_of_this_month.strftime('%Y-%m-%d'),
        'this_month_end': today.strftime('%Y-%m-%d'),
        'last_month_start': first_day_of_last_month.strftime('%Y-%m-%d'),
        'last_month_end': (first_day_of_this_month - timedelta(days=1)).strftime('%Y-%m-%d'),
        'this_year_start': first_day_of_this_year.strftime('%Y-%m-%d'),
        'this_year_end': today.strftime('%Y-%m-%d')
    }
    for key, value in date_formats.items():
        prompt_message = prompt_message.replace(f'{{{key}}}', value)
    return prompt_message

# 检查年份
def check_year(query):
    current_year = int(get_internet_time(DatetimeFormat.date)[:4])
    chinese_to_arabic = { '零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7', '八': '8', '九': '9' }
    for chinese, arabic in chinese_to_arabic.items():
        query = query.replace(chinese, arabic)
    match = re.search(r'(\d{4})年|(\d{2})年', query)
    if match:
        if match.group(1):
            return int(match.group(1))
        elif match.group(2):
            return 2000 + int(match.group(2))
        elif match.group(3):
            return int(match.group(3))

    if "去年" in query or "上年" in query or "前一年" in query or "上一年" in query or "昨年" in query:
        return current_year - 1 
    elif "今年" in query or "本年" in query:
        return current_year
    elif "前年" in query or "上上年" in query:
        return current_year - 2 
    
    return current_year

def check_month_end(fromdate, todate):
    small_months = ['04','06','09','11']
    big_months = ['01','03','05','07','08','10','12']
    if todate[5:7] == '02' and is_leap_year(int(todate[0:4])) and todate[8:10] == '29':
        return True
    elif todate[5:7] == '02' and todate[8:10] == '28':
        return True
    elif todate[5:7] in small_months and todate[8:10] == '30':
        return True
    elif todate[5:7] in big_months and todate[8:10] == '31':
        return True
    else:
        return False
def is_leap_year(year):
    if year % 4 == 0 and year % 100 != 0:
        return True
    elif year % 400 == 0:
        return True
    else:
        return False
def convert_date_or_month(date_str):
    """
    日期或月度转换格式。将一个任意字符串，判断是否是日期或月度。如是，转换为YYYY-MM-DD or YYYY-MM格式，否则报错退出。引用时，需要加报错处理，请注意。
    
    :param date_str: 待转换的字符串。
    :return: 转换后的日期或月度字符串。转换为YYYY-MM-DD or YYYY-MM格式
    :raises ValueError: 如果输入的字符串不是有效的日期或月度格式。
    """
    # 定义正则表达式匹配模式
    patterns = [
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y-%m-%d'),  # 1999年2月13日
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y-%m-%d'),  # 2002年11月5日
        (r'(\d{4})年(\d{1,2})月', '%Y-%m'),                # 2024年9月
        (r'(\d{4})\.(\d{1,2})\.(\d{1,2})', '%Y-%m-%d'),    # 2024.9.13
        (r'(\d{4})年(.*?)月', '%Y-%m'),                    # 2024年八月份
        (r'(\d{4})\.(\d{1,2})', '%Y-%m'),                  # 2029.08 或 2029.8
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d')       # 2009-1-15
    ]
    
    # 中文月份映射
    chinese_month = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
        '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12
    }
    
    for pattern, date_format in patterns:
        match = re.match(pattern, date_str)
        if match:
            # 提取匹配的组
            groups = match.groups()
            year = int(groups[0])
            
            # 处理中文月份
            if len(groups) > 1 and groups[1] in chinese_month:
                month = chinese_month[groups[1]]
            else:
                month = int(groups[1]) if len(groups) > 1 else 1
            
            # 如果有日部分
            if len(groups) > 2:
                day = int(groups[2])
                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            else:
                date_obj = datetime(year, month, 1)
                return date_obj.strftime('%Y-%m')
    
    # 如果没有匹配到任何模式，报错返回
    raise ValueError("输入的字符串不是有效的日期格式")

def get_timestamp_now(seconds: bool = True) -> int:
    dt = get_internet_datetime()
    ts = dt.timestamp()
    return int(ts) if seconds else int(ts * 1000)