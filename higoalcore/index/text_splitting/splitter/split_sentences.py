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

"""将一个文本块切成句子，支持中、英文两种语言。"""

from higoalcore.config.models.chunking_config import ChunkingConfig
from higoalutils.utils.language_utils.detect_language import detect_language
from higoalutils.config.enums.sys_enums import LanguageCode

def split_sentences(
    text: str, _config: ChunkingConfig
) -> list:
    """Chunks text into multiple parts by sentence."""
    if detect_language(text) == LanguageCode.English:
        import nltk
        from higoalcore.index.text_splitting.chunk_text.bootstrap import bootstrap
        bootstrap() # 加载nltk的分句模块
        sentences = nltk.sent_tokenize(text)
    else:
        from higoalcore.index.text_splitting.splitter.chinese_recursive_text_splitter import ChineseSentenceSplitter
        splitter = ChineseSentenceSplitter(
            chunk_size=_config.size,  # 这里设置 chunk_size
        )
        sentences = splitter.split_text(text) # 调用中文分句函数
    return sentences
