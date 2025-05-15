# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Factory functions for creating loggers."""

from typing import ClassVar

from higoalutils.logger.base import ProgressLogger
from higoalutils.logger.null_progress import NullProgressLogger
from higoalutils.logger.print_progress import PrintProgressLogger
from higoalutils.logger.rich_progress import RichProgressLogger
from higoalutils.logger.types import LoggerType


class LoggerFactory:
    """A factory class for loggers."""

    logger_types: ClassVar[dict[str, type]] = {}

    @classmethod
    def register(cls, logger_type: str, logger: type):
        """Register a custom logger implementation."""
        cls.logger_types[logger_type] = logger

    @classmethod
    def create_logger(
        cls, logger_type: LoggerType | str, kwargs: dict | None = None
    ) -> ProgressLogger:
        """Create a logger based on the provided type."""
        if kwargs is None:
            kwargs = {}
        match logger_type:
            case LoggerType.RICH:
                return RichProgressLogger("RAG Indexer ")
            case LoggerType.PRINT:
                return PrintProgressLogger("RAG Indexer ")
            case LoggerType.NONE:
                return NullProgressLogger()
            case _:
                if logger_type in cls.logger_types:
                    return cls.logger_types[logger_type](**kwargs)
                return NullProgressLogger()
