# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Base classes for LLM and Embedding models."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from openai import AsyncOpenAI, OpenAI

from higoalutils.logger.base import StatusLogger
from higoalutils.logger.console import ConsoleReporter
from higoalutils.language_model.llm.base import BaseTextEmbedding
from higoalutils.language_model.llm.oai.typing import OpenaiApiType


class BaseOpenAILLM(ABC):
    """The Base OpenAI LLM implementation."""

    _async_client: AsyncOpenAI
    _sync_client: OpenAI

    def __init__(self):
        self._create_openai_client()

    @abstractmethod
    def _create_openai_client(self):
        """Create a new synchronous and asynchronous OpenAI client instance."""

    def set_clients(
        self,
        sync_client: OpenAI,
        async_client: AsyncOpenAI,
    ):
        """
        Set the synchronous and asynchronous clients used for making API requests.

        Args:
            sync_client (OpenAI): The sync client object.
            async_client (AsyncOpenAI): The async client object.
        """
        self._sync_client = sync_client
        self._async_client = async_client

    @property
    def async_client(self) -> AsyncOpenAI | None:
        """
        Get the asynchronous client used for making API requests.

        Returns
        -------
            AsyncOpenAI: The async client object.
        """
        return self._async_client

    @property
    def sync_client(self) -> OpenAI | None:
        """
        Get the synchronous client used for making API requests.

        Returns
        -------
            AsyncOpenAI: The async client object.
        """
        return self._sync_client

    @async_client.setter
    def async_client(self, client: AsyncOpenAI):
        """
        Set the asynchronous client used for making API requests.

        Args:
            client (AsyncOpenAI): The async client object.
        """
        self._async_client = client

    @sync_client.setter
    def sync_client(self, client: OpenAI):
        """
        Set the synchronous client used for making API requests.

        Args:
            client (OpenAI): The sync client object.
        """
        self._sync_client = client


class OpenAILLMImpl(BaseOpenAILLM):
    """Orchestration OpenAI LLM Implementation."""

    _reporter: StatusLogger = ConsoleReporter()

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        api_type: OpenaiApiType = OpenaiApiType.OpenAI,
        max_retries: int = 10,
        request_timeout: float = 180.0,
        logger: StatusLogger | None = None,
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.api_type = api_type
        self.max_retries = max_retries
        self.request_timeout = request_timeout
        self.logger = logger or ConsoleReporter()

        try:
            # Create OpenAI sync and async clients
            super().__init__()
        except Exception as e:
            self._reporter.error(
                message="Failed to create OpenAI client",
                details={self.__class__.__name__: str(e)},
            )
            raise

    def _create_openai_client(self):
        """Create a new OpenAI client instance."""
        if self.api_type == OpenaiApiType.OpenAI:
            sync_client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                # Retry Configuration
                timeout=self.request_timeout,
                max_retries=self.max_retries,
            )

            async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base,
                # Retry Configuration
                timeout=self.request_timeout,
                max_retries=self.max_retries,
            )
            self.set_clients(sync_client=sync_client, async_client=async_client)


class OpenAITextEmbeddingImpl(BaseTextEmbedding):
    """Orchestration OpenAI Text Embedding Implementation."""

    _reporter: StatusLogger | None = None

    def _create_openai_client(self, api_type: OpenaiApiType):
        """Create a new synchronous and asynchronous OpenAI client instance."""
