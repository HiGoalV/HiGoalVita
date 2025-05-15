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

"""HiGoal Graph RAG 检查一段文本是中文还是英文"""

from higoalutils.config.enums.sys_enums import LanguageCode
def detect_language(text: str, chinese_threshold: float = 0.3) -> LanguageCode:
    """
    判断文本是中文（zh）还是英文（en）。
    
    Args:
        text: 输入文本
        chinese_threshold: 汉字占比阈值（默认 30%）
    
    Returns:
        "zh" (中文) 或 "en" (英文)
    """
    total_chars = 0
    chinese_chars = 0
    
    for char in text:
        # 只统计有效字符（忽略空格、标点、数字等）
        if char.isalpha():
            total_chars += 1
            # 判断是否为汉字（Unicode 范围：\u4e00-\u9fff）
            if '\u4e00' <= char <= '\u9fff':
                chinese_chars += 1
    
    # 如果没有有效字符，默认返回英文
    if total_chars == 0:
        return LanguageCode.Chinese
    
    # 计算汉字占比
    ratio = chinese_chars / total_chars
    
    # 根据阈值判断语言
    return LanguageCode.Chinese if ratio >= chinese_threshold else LanguageCode.English