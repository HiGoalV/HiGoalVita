# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Parameterization settings for the default configuration."""

from pydantic import BaseModel, Field
from typing import List

from higoalcore.config.defaults.chunking_defaults import ChunkingConfigDefaults
from higoalcore.config.enums.index_enums import ChunkStrategyType
from higoalutils.config.enums.model_enums import TokenizerType


class ChunkingConfig(BaseModel):
    """Configuration section for chunking."""

    size: int = Field(
        description="The chunk size to use.",
        default=ChunkingConfigDefaults.size,
    )
    overlap: int = Field(
        description="The chunk overlap to use.",
        default=ChunkingConfigDefaults.overlap,
    )
    strategy: ChunkStrategyType = Field(
        description="The chunking strategy to use.",
        default=ChunkingConfigDefaults.strategy,
    )
    prepend_metadata: bool = Field(
        description="Prepend metadata into each chunk.",
        default=ChunkingConfigDefaults.prepend_metadata,
    )
    chunk_size_includes_metadata: bool = Field(
        description="Count metadata in max tokens.",
        default=ChunkingConfigDefaults.chunk_size_includes_metadata,
    )
    group_by_columns: List[str] = Field(
        description="The chunk by columns to use.",
        default=ChunkingConfigDefaults.group_by_columns,
    )
    default_encoding_model: TokenizerType = Field(
        description="The default encoding model to use.",
        default=ChunkingConfigDefaults.default_encoding_model,
    )