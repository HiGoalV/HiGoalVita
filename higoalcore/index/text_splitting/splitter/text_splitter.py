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

"""HiGoal Graph RAG 切处理器."""

from typing import Any, Callable

from higoalcore.config.models.chunking_config import ChunkingConfig
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalutils.language_model.tokenizer.base import Tokenizer
from higoalutils.logger.progress import ProgressTicker
from higoalcore.config.enums.index_enums import ChunkStrategyType
from higoalcore.index.text_splitting.splitter.text_splitting_tokens import (
    split_single_text_on_tokens,
    split_multiple_texts_on_tokens,
)
from higoalcore.index.text_splitting.splitter.text_splitting_sentences import (
    split_single_text_on_sentences,
    split_multiple_texts_on_sentences
)
from higoalutils.language_model.tokenizer.get_tokenizer import get_tokenizer
from higoalutils.config.enums.model_enums import TokenizerType


def create_chunks(
    config: ChunkingConfig,
    input: dict[str, Any] | list[dict[str, Any]],
    ticker: ProgressTicker | None = None,
    encoding_model: TokenizerType | None = None,
) -> list[ChunkText]:
    """Create chunks from input based on configured strategy and input type."""
    encoding_model = encoding_model or config.default_encoding_model
    tokenizer = get_tokenizer(encoding_model)

    is_list_input = isinstance(input, list)

    # Dispatch table
    strategy_dispatch: dict[ChunkStrategyType, dict[bool, Callable]] = {
        ChunkStrategyType.TOKENS: {
            True: split_multiple_texts_on_tokens,
            False: split_single_text_on_tokens,
        },
        ChunkStrategyType.SENTENCES: {
            True: split_multiple_texts_on_sentences,
            False: split_single_text_on_sentences,
        },
    }

    try:
        split_fn = strategy_dispatch[config.strategy][is_list_input]
    except KeyError:
        raise ValueError(f"Unsupported chunking strategy: {config.strategy}")

    return split_fn(config, input, tokenizer, ticker)