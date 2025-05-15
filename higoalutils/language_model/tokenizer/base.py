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

from dataclasses import dataclass
from higoalutils.language_model.tokenizer.types import (
    TextTokenizerDecoder, TextTokenizerEncoder, TextTokenizerCounter
)

@dataclass(frozen=True)
class Tokenizer:
    """Tokenizer data class."""

    decode: TextTokenizerDecoder
    """ Function to decode a list of token ids to a string"""
    encode: TextTokenizerEncoder
    """ Function to encode a string to a list of token ids"""
    count_tokens: TextTokenizerCounter
    """ Function to count the number of tokens in a string"""