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

"""支持句子策略的切片算法"""

import logging
from typing import Optional

from higoalutils.logger.progress import ProgressTicker
from higoalcore.config.models.chunking_config import ChunkingConfig
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalutils.language_model.tokenizer.base import Tokenizer
from higoalcore.index.text_splitting.chunk_text.sequential_id import DailySequentialIDGenerator
from higoalcore.index.text_splitting.splitter.split_sentences import split_sentences


log = logging.getLogger(__name__)

def validate_inputs(doc: dict) -> bool:
    """验证输入数据有效性"""
    if not isinstance(doc.get('text', ''), str):
        log.error("Invalid document text: expected string")
        return False
    return True


def extract_metadata(doc: dict) -> dict:
    """提取文档元数据"""
    return {
        'source_doc_id': doc.get('id', ''),
        'filename': doc.get('filename', ''),
        'title': doc.get('title', ''),
        'creation_date': doc.get('creation_date', '')
    }


def create_chunk(
    sentences: list[str],
    token_sizes: list[int],
    metadata_list: list[dict],
    generator: DailySequentialIDGenerator
) -> ChunkText:
    """创建新的文本块"""
    # 合并所有来源的title
    source_titles = list({m['title'] for m in metadata_list if m.get('title')})
    chunk_text = ''.join(sentences)
    total_size = sum(token_sizes)
    
    return ChunkText(
        id=generator.generate_id(key="default"),
        text=chunk_text,
        source_doc_id=metadata_list[0]['source_doc_id'],  # 使用第一个文档的ID
        filename=metadata_list[0]['filename'],
        attributes={
            "creation_date": metadata_list[0]['creation_date'],
            "title": source_titles,  # 所有来源title
            "chunk_size": total_size
        }
    )

def handle_overlap(
    current_chunk: list[str],
    current_sizes: list[int],
    overlap_limit: int
) -> tuple[list[str], list[int], int]:
    """处理块间重叠逻辑"""
    overlap_chunk = []
    overlap_sizes = []
    overlap_size = 0
    
    for sent, sent_size in zip(reversed(current_chunk), reversed(current_sizes)):
        if overlap_size + sent_size > overlap_limit:
            break
        overlap_chunk.insert(0, sent)
        overlap_sizes.insert(0, sent_size)
        overlap_size += sent_size
    
    return overlap_chunk, overlap_sizes, overlap_size


def split_single_text_on_sentences(
    config: ChunkingConfig,
    doc: dict,
    tokenizer: Tokenizer,
    tick: Optional[ProgressTicker] = None
) -> list[ChunkText]:
    """
    将单个文本按句子分割成块，支持重叠
    
    Args:
        config: 分块配置（size/overlap等）
        doc: 包含文本和元数据的字典
        tokenizer: 用于计算token长度的分词器
        tick: 进度回调（可选）
    
    Returns:
        List[ChunkText]: 生成的分块结果
    """
    # 输入验证
    if not validate_inputs(doc):
        return []
    
    # 元数据提取
    metadata = extract_metadata(doc)
    if not doc['text']:
        return []
    
    # 初始化
    generator = DailySequentialIDGenerator.get_instance(
        auto_persist_every=100,
        min_persist_interval=0.5
    )
    result = []
    
    try:
        # 分句并预计算token长度
        sentences = split_sentences(doc['text'], config)
        sentence_sizes = [len(tokenizer.encode(s)) for s in sentences]
        
        current_chunk = []      # 当前块的句子列表
        current_sizes = []      # 对应句子的token长度
        current_size = 0        # 当前块总token数
        
        for sent, sent_size in zip(sentences, sentence_sizes):
            # 正常添加句子到当前块
            if current_size + sent_size <= config.size:
                current_chunk.append(sent)
                current_sizes.append(sent_size)
                current_size += sent_size
            else:
                # 保存当前块
                if current_chunk:
                    result.append(create_chunk(
                        current_chunk, current_sizes, [metadata], generator
                    ))
                    log.info(f"current chunk saved: {current_size} tokens, and next sentence size is:{sent_size},the sum {current_size+sent_size} is lagger then {config.size}")
                
                # 处理重叠
                if config.overlap > 0:
                    (current_chunk, 
                     current_sizes, 
                     current_size) = handle_overlap(
                        current_chunk, current_sizes, config.overlap
                    )
                else:
                    current_chunk, current_sizes, current_size = [], [], 0
                
                # 添加新句子到新块
                current_chunk.append(sent)
                current_sizes.append(sent_size)
                current_size += sent_size
        
        # 处理最后一个块
        if current_chunk:
            result.append(create_chunk(
                current_chunk, current_sizes, [metadata], generator
            ))
            log.info(f"Current chunk is the last chunk, saved: {current_size} tokens.")
    except Exception as e:
        log.error(f"Chunking failed: {e}", exc_info=True)
        raise
    
    if tick:
        tick(1)
    
    log.debug(
        f"Processed document '{metadata['title']}': "
        f"{len(sentences)} sentences -> {len(result)} chunks"
    )
    return result

def split_multiple_texts_on_sentences(
    config: ChunkingConfig,
    texts: list[dict], 
    tokenizer: Tokenizer, 
    tick: ProgressTicker | None = None
) -> list[ChunkText]:
    """
    将多个文本按句子分割成块，支持重叠和跨文本合并
    
    Args:
        config: 分块配置（size/overlap等）
        texts: 包含多个文本和元数据的字典列表
        tokenizer: 用于计算token长度的分词器
        tick: 进度回调（可选）
    
    Returns:
        List[ChunkText]: 生成的分块结果
    """
    if not texts:
        return []
    
    # 初始化
    generator = DailySequentialIDGenerator.get_instance(
        auto_persist_every=100,
        min_persist_interval=0.5
    )
    result = []
    
    current_chunk = []      # 当前块的句子列表
    current_sizes = []      # 对应句子的token长度
    current_size = 0        # 当前块总token数
    current_metadata_list = []  # 块的元数据
    
    try:
        for doc in texts:
            # 输入验证
            if not validate_inputs(doc):
                continue
                
            # 元数据提取
            metadata = extract_metadata(doc)
            if not doc['text']:
                continue
                
            if not current_metadata_list:  # 初始化
                current_metadata_list.append(metadata)
                
            # 分句并预计算token长度
            sentences = split_sentences(doc['text'], config)
            sentence_sizes = [len(tokenizer.encode(s)) for s in sentences]
            
            # 检查整个文本是否适合当前块
            total_text_size = sum(sentence_sizes)
            
            # 情况1: 整个文本可以放入当前块
            if current_size + total_text_size <= config.size:
                current_chunk.extend(sentences)
                current_sizes.extend(sentence_sizes)
                current_size += total_text_size
                current_metadata_list.append(metadata)  # 记录合并的元数据
                continue
                
            # 情况2: 文本太大需要拆分
            for sent, sent_size in zip(sentences, sentence_sizes):
                # 正常添加句子到当前块
                if current_size + sent_size <= config.size:
                    current_chunk.append(sent)
                    current_sizes.append(sent_size)
                    current_size += sent_size
                    current_metadata_list.append(metadata)  # 记录当前句子来源
                else:
                    # 保存当前块
                    if current_chunk:
                        result.append(create_chunk(
                            current_chunk, current_sizes, current_metadata_list, generator
                        ))
                    
                    # 处理重叠
                    if config.overlap > 0:
                        overlap_chunk, overlap_sizes, overlap_size = handle_overlap(
                            current_chunk, current_sizes, config.overlap
                        )
                        # 根据重叠的句子数量截取元数据
                        overlap_meta_count = len(overlap_sizes)
                        current_metadata_list = current_metadata_list[-overlap_meta_count:]

                        current_chunk, current_sizes = overlap_chunk, overlap_sizes
                        current_size = overlap_size
                    else:
                        current_chunk, current_sizes, current_size = [], [], 0
                        current_metadata_list = []
                    
                    # 添加新句子到新块
                    current_chunk.append(sent)
                    current_sizes.append(sent_size)
                    current_size += sent_size
                    current_metadata_list.append(metadata)
        
        # 处理最后一个块
        if current_chunk:
            result.append(create_chunk(
                current_chunk, current_sizes, current_metadata_list, generator # type: ignore
            ))
            
    except Exception as e:
        log.error(f"Chunking failed: {e}", exc_info=True)
        raise
    
    if tick:
        tick(len(texts))
    
    log.debug(
        f"Processed {len(texts)} documents -> {len(result)} chunks"
    )
    return result