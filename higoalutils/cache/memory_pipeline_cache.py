# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'InMemoryCache' model."""

from typing import Any

from higoalutils.cache.pipeline_cache import PipelineCache


class InMemoryCache(PipelineCache):
    """In memory cache class definition."""

    _cache: dict[str, Any]

    def __init__(self, name: str | None = None):
        """Init method definition."""
        self._cache = {}
        self._prefix = name

    async def get(self, key: str) -> Any:
        """Get the value for the given key.

        Args:
            - key - The key to get the value for.
            - as_bytes - Whether or not to return the value as bytes.

        Returns
        -------
            - output - The value for the given key.
        """
        full_key = self.create_key(key, prefix=self._prefix)
        return self._cache.get(full_key)

    async def set(self, key: str, value: Any) -> None:
        """Set the value for the given key.

        Args:
            - key - The key to set the value for.
            - value - The value to set.
        """
        full_key = self.create_key(key, prefix=self._prefix)
        
        self._cache[full_key] = value

    async def has(self, key: str) -> bool:
        """Return True if the given key exists in the storage.

        Args:
            - key - The key to check for.

        Returns
        -------
            - output - True if the key exists in the storage, False otherwise.
        """
        full_key = self.create_key(key, prefix=self._prefix)
        return full_key in self._cache

    async def delete(self, key: str) -> None:
        """Delete the given key from the storage.

        Args:
            - key - The key to delete.
        """
        full_key = self.create_key(key, prefix=self._prefix)
        self._cache.pop(full_key, None)

    async def clear(self) -> None:
        """Clear the storage."""
        self._cache.clear()

    def child(self, name: str) -> PipelineCache:
        """Create a sub cache with the given name."""
        return InMemoryCache(name)
