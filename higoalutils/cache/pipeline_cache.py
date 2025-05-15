# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'PipelineCache' model."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any


class PipelineCache(ABC):
    """Provide a cache interface for the pipeline."""

    __cache_strategy_version__: int = 2
    @abstractmethod
    async def get(self, key: str) -> Any:
        """Get the value for the given key.

        Args:
            - key - The key to get the value for.
            - as_bytes - Whether or not to return the value as bytes.

        Returns
        -------
            - output - The value for the given key.
        """

    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """Set the value for the given key.

        Args:
            - key - The key to set the value for.
            - value - The value to set.
        """

    @abstractmethod
    async def has(self, key: str) -> bool:
        """Return True if the given key exists in the cache.

        Args:
            - key - The key to check for.

        Returns
        -------
            - output - True if the key exists in the cache, False otherwise.
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete the given key from the cache.

        Args:
            - key - The key to delete.
        """

    @abstractmethod
    async def clear(self) -> None:
        """Clear the cache."""

    @abstractmethod
    def child(self, name: str) -> PipelineCache:
        """Create a child cache with the given name.

        Args:
            - name - The name to create the sub cache with.
        """
    def create_key(self, data: Any, *, prefix: str | None = None) -> str:
        """Create a custom key by hashing the data. Returns `{data_hash}_v{strategy_version}` or `{prefix}_{data_hash}_v{strategy_version}`."""
        data_hash = _hash(json.dumps(data, sort_keys=True))

        if prefix is not None:
            return f"{prefix}_{data_hash}_v{self.__cache_strategy_version__}"

        return f"{data_hash}_v{self.__cache_strategy_version__}"


def _hash(_input: str) -> str:
    """Use a deterministic hashing approach."""
    return hashlib.sha256(_input.encode()).hexdigest()