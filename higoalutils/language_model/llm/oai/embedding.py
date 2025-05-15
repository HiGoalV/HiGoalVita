# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""OpenAI Embedding model implementation."""

import asyncio
from typing import Any

import numpy as np
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from higoalutils.language_model.llm.base import BaseTextEmbedding
from higoalutils.language_model.llm.oai.base import OpenAILLMImpl
from higoalutils.language_model.llm.oai.typing import (
    OPENAI_RETRY_ERROR_TYPES,
    OpenaiApiType,
)
from higoalutils.language_model.llm.oai.text_utils import chunk_text


class OpenAIEmbedding(BaseTextEmbedding, OpenAILLMImpl):
    """Wrapper for OpenAI Embedding models."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "text-embedding-3-small",
        api_base: str | None = None,
        api_type: OpenaiApiType = OpenaiApiType.OpenAI,
        encoding_name: str = "cl100k_base",
        max_tokens: int = 8191,
        max_retries: int = 10,
        request_timeout: float = 180.0,
        retry_error_types: tuple[type[BaseException]] = OPENAI_RETRY_ERROR_TYPES,  # type: ignore
    ):
        OpenAILLMImpl.__init__(
            self=self,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,  # type: ignore
            max_retries=max_retries,
            request_timeout=request_timeout,
        )

        self.model = model
        self.encoding_name = encoding_name
        self.max_tokens = max_tokens
        self.retry_error_types = retry_error_types

    def embed(self, text: str | list[str], **kwargs: Any) -> list[list[float]]:
        """
        Embed text using OpenAI Embedding's sync function. 此处 text:str | list[str] 仅为兼容,注意返回值改为list[list[float]]

        For text longer than max_tokens, chunk texts into max_tokens, embed each chunk, then combine using weighted average.
        Please refer to: https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb
        """
        if isinstance(text, list):
            text = text[0]
        token_chunks = chunk_text(
            text=text, tokenizer_name=self.encoding_name, max_tokens=self.max_tokens
        )
        chunk_embeddings = []
        chunk_lens = []
        for chunk in token_chunks:
            try:
                embedding, chunk_len = self._embed_with_retry(chunk, **kwargs)
                chunk_embeddings.append(embedding)
                chunk_lens.append(chunk_len)
            # TODO: catch a more specific exception
            except Exception as e:  # noqa BLE001
                # self._reporter.error(
                #     message="Error embedding chunk",
                #     details={self.__class__.__name__: str(e)},
                # )

                continue
        chunk_embeddings = np.average(chunk_embeddings, axis=0, weights=chunk_lens)
        chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings)
        return [chunk_embeddings.tolist()]

    async def aembed(self, text: str | list[str], **kwargs: Any) -> list[list[float]]:
        """
        Embed text using OpenAI Embedding's async function. 此处 text:str | list[str] 仅为兼容,注意返回值改为list[list[float]]

        For text longer than max_tokens, chunk texts into max_tokens, embed each chunk, then combine using weighted average.
        """
        if isinstance(text, list):
            text = text[0]

        token_chunks = chunk_text(
            text=text, tokenizer_name=self.encoding_name, max_tokens=self.max_tokens
        )
        chunk_embeddings = []
        chunk_lens = []
        embedding_results = await asyncio.gather(*[
            self._aembed_with_retry(chunk, **kwargs) for chunk in token_chunks
        ])
        embedding_results = [result for result in embedding_results if result[0]]
        chunk_embeddings = [result[0] for result in embedding_results]
        chunk_lens = [result[1] for result in embedding_results]
        chunk_embeddings = np.average(chunk_embeddings, axis=0, weights=chunk_lens)  # type: ignore
        chunk_embeddings = chunk_embeddings / np.linalg.norm(chunk_embeddings)
        return [chunk_embeddings.tolist()]

    def _embed_with_retry(
        self, text: str | tuple, **kwargs: Any
    ) -> tuple[list[float], int]:
        try:
            retryer = Retrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                retry=retry_if_exception_type(self.retry_error_types),
            )
            for attempt in retryer:
                with attempt:
                    embedding = (
                        self.sync_client.embeddings.create(  # type: ignore
                            input=text,
                            model=self.model,
                            **kwargs,  # type: ignore
                        )
                        .data[0]
                        .embedding
                        or []
                    )
                    return (embedding, len(text))
        except RetryError as e:
            # self._reporter.error(
            #     message="Error at embed_with_retry()",
            #     details={self.__class__.__name__: str(e)},
            # )
            return ([], 0)
        else:
            # TODO: why not just throw in this case?
            return ([], 0)

    async def _aembed_with_retry(
        self, text: str | tuple, **kwargs: Any
    ) -> tuple[list[float], int]:
        try:
            retryer = AsyncRetrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                retry=retry_if_exception_type(self.retry_error_types),
            )
            async for attempt in retryer:
                with attempt:
                    embedding = (
                        await self.async_client.embeddings.create(  # type: ignore
                            input=text,
                            model=self.model,
                            **kwargs,  # type: ignore
                        )
                    ).data[0].embedding or []
                    return (embedding, len(text))
        except RetryError as e:
            # self._reporter.error(
            #     message="Error at embed_with_retry()",
            #     details={self.__class__.__name__: str(e)},
            # )
            return ([], 0)
        else:
            # TODO: why not just throw in this case?
            return ([], 0)
