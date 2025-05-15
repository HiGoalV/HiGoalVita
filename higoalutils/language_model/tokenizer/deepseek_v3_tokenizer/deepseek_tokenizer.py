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

"""DeepSeek V3 Tokenizer."""

import sys
from pyprojroot import here
sys.path.append(str(here()))

import transformers 

chat_tokenizer_dir = "higoalutils/language_model/tokenizer/deepseek_v3_tokenizer"

deepseek_tokenizer = transformers.AutoTokenizer.from_pretrained( # type: ignore
    chat_tokenizer_dir, trust_remote_code=True
)
