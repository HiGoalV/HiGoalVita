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

"""中文句子的分割算法。注意，这个算法除了基本的文本切割成句子，还有一个参数split_text(..., need_merged=True)进行指定长度的合并成段。"""

import re
from typing import List, Optional


class ChineseSentenceSplitter:
    def __init__(
        self,
        separators: Optional[List[str]] = None,
        keep_separator: bool = True,
        is_separator_regex: bool = True,
        chunk_size: int = 400, # 这个参数的意图是按指定长度切割句子（切割时防止过小，可以按要求合并成段），不是document.chunk_size的概念
        chunk_overlap: int = 50,
    ) -> None:
        """中文句子分割器
        
        Args:
            separators: 分隔符列表，默认为中文常用的标点和换行符
            keep_separator: 是否保留分隔符
            is_separator_regex: 分隔符是否是正则表达式
            chunk_size: 最大块大小。此处是指切割时防止句子过小，可以按要求合并成段落。由split_text(..., need_merged=True)进行指定，默认为False
            chunk_overlap: 块之间的重叠大小
        """
        self._separators = separators or [
            r"\n\n|\n|\r\n|\r",      # 合并后的换行符规则（最高优先级）
            "。|！|？",               # 中文句子结束符
            r"\.\s|\!\s|\?\s",       # 英文句子结束符（后接空格）
            r"；|;\s",               # 分号（中英文）
            r"，|,\s"                # 逗号（中英文）
        ]
        self._keep_separator = keep_separator
        self._is_separator_regex = is_separator_regex
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def _split_text_with_regex(
        self, text: str, separator: str, keep_separator: bool
    ) -> List[str]:
        """使用正则表达式分割文本"""
        if separator:
            if keep_separator:
                # 保留分隔符
                _splits = re.split(f"({separator})", text)
                splits = ["".join(i) for i in zip(_splits[0::2], _splits[1::2])]
                if len(_splits) % 2 == 1:
                    splits += _splits[-1:]
            else:
                splits = re.split(separator, text)
        else:
            splits = list(text)
        return [s for s in splits if s != ""]

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """合并小片段，考虑重叠"""
        if not splits:
            return []
        
        merged = []
        current_chunk = []
        current_length = 0
        
        for s in splits:
            s_len = len(s)
            if current_length + s_len > self._chunk_size and current_chunk:
                merged_chunk = separator.join(current_chunk)
                merged.append(merged_chunk)
                
                # 处理重叠
                if self._chunk_overlap > 0:
                    # 从当前块末尾取重叠部分
                    overlap_start = max(0, len(current_chunk) - self._chunk_overlap)
                    current_chunk = current_chunk[overlap_start:]
                    current_length = sum(len(c) for c in current_chunk)
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(s)
            current_length += s_len
        
        if current_chunk:
            merged_chunk = separator.join(current_chunk)
            merged.append(merged_chunk)
        
        return merged

    def split_text(
        self, 
        text: str, 
        separators: Optional[List[str]] = None,
        need_merged: bool = False
    ) -> List[str]:
        """分割文本为句子
        
        Args:
            text: 要分割的文本
            separators: 可选的自定义分隔符列表
            need_merged: 是否需要合并小片段
            
        Returns:
            分割后的句子列表
        """
        if not text.strip():
            return []
            
        separators = separators or self._separators
        final_chunks = []
        
        # 获取合适的分隔符
        separator = separators[-1]
        new_separators = []
        
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1 :]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        
        splits = self._split_text_with_regex(text, _separator, self._keep_separator)
        
        if not need_merged:
            return [
                re.sub(r"\n{2,}", "\n", chunk.strip())
                for chunk in splits
                if chunk.strip() != ""
            ]

        # 递归处理长文本
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        
        for s in splits:
            if len(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self.split_text(s, new_separators)
                    final_chunks.extend(other_info)
        
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        
        # 清理结果：去除多余换行和空白
        return [
            re.sub(r"\n{2,}", "\n", chunk.strip())
            for chunk in final_chunks
            if chunk.strip() != ""
        ]