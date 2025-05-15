# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

from enum import Enum


class CacheType(str, Enum):
    """The cache configuration type for the pipeline."""

    file = "file"
    """The file cache configuration type."""
    memory = "memory"
    """The memory cache configuration type."""
    none = "none"
    """The none cache configuration type."""