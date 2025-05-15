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

"""A module containing tokenizer fuctions."""

import tiktoken

from higoalutils.config.enums.model_enums import TokenizerType
from higoalutils.language_model.tokenizer.base import Tokenizer
from higoalutils.language_model.tokenizer.deepseek_v3_tokenizer.deepseek_tokenizer import deepseek_tokenizer
from higoalutils.language_model.tokenizer.dashscope_tokenizer.dashscope_tokenizer import dashscope_tokenizer


def get_tokenizer(encoding_name: str) -> Tokenizer:
    """返回统一封装的 Tokenizer 实例，包括 encode/decode/count_tokens 方法"""
    if encoding_name == TokenizerType.DeepSeekTokenizer:
        enc = deepseek_tokenizer
    elif encoding_name == TokenizerType.DashScopeTokenizer:
        enc = dashscope_tokenizer
    else:
        enc = tiktoken.get_encoding(encoding_name)

    def encode(text: str) -> list[int]:
        return enc.encode(str(text))

    def decode(tokens: list[int]) -> str:
        return enc.decode(tokens)

    def count_tokens(text: str) -> int:
        return len(encode(text))

    return Tokenizer(encode=encode, decode=decode, count_tokens=count_tokens)

