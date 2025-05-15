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

"""A module containing the 'Tokenizer' model and splitting functions."""

import logging

from higoalutils.logger.progress import ProgressTicker
from higoalcore.config.models.chunking_config import ChunkingConfig
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalutils.language_model.tokenizer.base import Tokenizer
from higoalcore.index.text_splitting.chunk_text.sequential_id import DailySequentialIDGenerator


log = logging.getLogger(__name__)

def split_single_text_on_tokens(
    config: ChunkingConfig,
    doc:dict, 
    tokenizer: Tokenizer, 
    tick: ProgressTicker | None = None
) -> list[ChunkText]:
    """Split a single text and return chunks using the tokenizer."""
    result = []
    if not doc.get('text',''):
        return result
    
    input_ids = tokenizer.encode(doc['text'])

    # 初始化一个ID生成器，默认key＝'default'
    generator = DailySequentialIDGenerator.get_instance(
        auto_persist_every=100,
        min_persist_interval=0.5
    )

    source_doc_title = doc.get('title','')
    source_doc_filename = doc.get('filename','')
    creation_date = doc.get('creation_date','')
    source_doc_id = doc.get('id','')
    if tick:
        tick(1)
    
    start_idx = 0
    cur_idx = min(start_idx + config.size, len(input_ids))
    chunk_ids = input_ids[start_idx:cur_idx]

    while start_idx < len(input_ids):
        chunk_text = tokenizer.decode(list(chunk_ids))
        #result.append(chunk_text)  # Append chunked text as string
        chunk = ChunkText(
            id=generator.generate_id(key="default"),
            text=chunk_text,
            source_doc_id=source_doc_id,
            filename=source_doc_filename,
            attributes={
                "creation_date": creation_date,
                "source_doc": [source_doc_title],
                "chunk_size": len(chunk_ids)
            },
        )
        result.append(chunk)
        start_idx += config.size - config.overlap
        cur_idx = min(start_idx + config.size, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]

    return result
def split_multiple_texts_on_tokens(
    config: ChunkingConfig,
    texts: list[dict], 
    tokenizer: Tokenizer, 
    tick: ProgressTicker | None = None
) -> list[ChunkText]:
    """Split multiple texts and return chunks with metadata using the tokenizer."""
    result = []
    mapped_ids = []

    if not texts:
        return result

    # 初始化一个ID生成器，默认key＝'default'
    generator = DailySequentialIDGenerator.get_instance(
        auto_persist_every=100,
        min_persist_interval=0.5
    )

    for doc in texts:
        encoded = tokenizer.encode(doc['text'])
        if tick:
            tick(1)  # Track progress if tick callback is provided
        source_doc_title = doc.get('title','')
        mapped_ids.append((source_doc_title, encoded))

    input_ids = [
        (source_doc_title, id) for source_doc_title, ids in mapped_ids for id in ids
    ]

    start_idx = 0
    cur_idx = min(start_idx + config.size, len(input_ids))
    chunk_ids = input_ids[start_idx:cur_idx]
    source_doc_filename = texts[0].get('filename','')
    creation_date = texts[0].get('creation_date','')
    source_doc_id = texts[0].get('id','')
    while start_idx < len(input_ids):
        chunk_text = tokenizer.decode([id for _, id in chunk_ids])
        doc_indices = list({source_doc_title for source_doc_title, _ in chunk_ids})
        #result.append(TextChunk(chunk_text, doc_indices, len(chunk_ids)))
        chunk = ChunkText(
            id=generator.generate_id(key="default"),
            text=chunk_text,
            source_doc_id=source_doc_id,
            filename=source_doc_filename,
            attributes={
                "creation_date": creation_date,
                "source_doc": doc_indices,
                "chunk_size": len(chunk_ids)
            },
        )
        result.append(chunk)
        start_idx += config.size - config.overlap
        cur_idx = min(start_idx + config.size, len(input_ids))
        chunk_ids = input_ids[start_idx:cur_idx]

    return result
