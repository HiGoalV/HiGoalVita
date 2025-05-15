# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

from enum import Enum

class OutputType(str, Enum):
    """The output type for the pipeline."""

    file = "file"
    """The file output type."""
    memory = "memory"
    """The memory output type."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'