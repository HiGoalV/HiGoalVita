# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Factory functions for creating storage."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from higoalutils.storage.enums import OutputType
from higoalutils.storage.file_pipeline_storage import create_file_storage
from higoalutils.storage.memory_pipeline_storage import MemoryPipelineStorage

if TYPE_CHECKING:
    from higoalutils.storage.pipeline_storage import PipelineStorage


class StorageFactory:
    """A factory class for storage implementations.

    Includes a method for users to register a custom storage implementation.

    Configuration arguments are passed to each storage implementation as kwargs
    for individual enforcement of required/optional arguments.
    """

    storage_types: ClassVar[dict[str, type]] = {}

    @classmethod
    def register(cls, storage_type: str, storage: type):
        """Register a custom storage implementation."""
        cls.storage_types[storage_type] = storage

    @classmethod
    def create_storage(
        cls, storage_type: OutputType | str, kwargs: dict
    ) -> PipelineStorage:
        """Create or get a storage object from the provided type."""
        match storage_type:
            case OutputType.file:
                return create_file_storage(**kwargs)
            case OutputType.memory:
                return MemoryPipelineStorage()
            case _:
                if storage_type in cls.storage_types:
                    return cls.storage_types[storage_type](**kwargs)
                msg = f"Unknown storage type: {storage_type}"
                raise ValueError(msg)
