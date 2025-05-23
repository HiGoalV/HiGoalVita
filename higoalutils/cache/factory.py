# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing create_cache method definition."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from higoalutils.cache.enums import CacheType
from higoalutils.storage.file_pipeline_storage import FilePipelineStorage

if TYPE_CHECKING:
    from higoalutils.cache.pipeline_cache import PipelineCache

from higoalutils.cache.json_pipeline_cache import JsonPipelineCache
from higoalutils.cache.memory_pipeline_cache import InMemoryCache
from higoalutils.cache.noop_pipeline_cache import NoopPipelineCache


class CacheFactory:
    """A factory class for cache implementations.

    Includes a method for users to register a custom cache implementation.

    Configuration arguments are passed to each cache implementation as kwargs (where possible)
    for individual enforcement of required/optional arguments.
    """

    cache_types: ClassVar[dict[str, type]] = {}

    @classmethod
    def register(cls, cache_type: str, cache: type):
        """Register a custom cache implementation."""
        cls.cache_types[cache_type] = cache

    @classmethod
    def create_cache(
        cls, cache_type: CacheType | str | None, root_dir: str, kwargs: dict
    ) -> PipelineCache:
        """Create or get a cache from the provided type."""
        if not cache_type:
            return NoopPipelineCache()
        match cache_type:
            case CacheType.none:
                return NoopPipelineCache()
            case CacheType.memory:
                return InMemoryCache()
            case CacheType.file:
                return JsonPipelineCache(
                    FilePipelineStorage(root_dir=root_dir).child(kwargs["base_dir"])
                )
            case _:
                if cache_type in cls.cache_types:
                    return cls.cache_types[cache_type](**kwargs)
                msg = f"Unknown cache type: {cache_type}"
                raise ValueError(msg)
