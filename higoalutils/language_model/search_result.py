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

"""Base classes for search algos.HiGoal重新做了结构调整。"""

import json
import pandas as pd
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SearchResult:
    """A Structured Search Result."""
    response: str | dict[str, Any] | list[dict[str, Any]] | None
    context_data: str | list[pd.DataFrame] | dict[str, pd.DataFrame] | None
    # actual text strings that are in the context window, built from context_data
    prompt:str
    context_text: str | list[str] | dict[str, str] | None
    exception: str | None
    completion_time: float
    # total LLM calls and token usage
    llm_calls: int
    prompt_tokens: int
    output_tokens: int

def pretty_print_search_result(result: SearchResult) -> str:
    """将SearchResult转换为文本输出。"""
    result_dict = asdict(result)
    
    # 处理可能包含DataFrame的字段
    if result_dict['context_data'] is not None:
        if isinstance(result_dict['context_data'], list):
            result_dict['context_data'] = [df.to_dict() for df in result_dict['context_data']]
        elif isinstance(result_dict['context_data'], dict):
            result_dict['context_data'] = {k: v.to_dict() for k, v in result_dict['context_data'].items()}
    
    # 使用json模块格式化输出
    return json.dumps(result_dict, indent=4, ensure_ascii=False)
