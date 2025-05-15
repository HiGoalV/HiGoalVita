# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Chat-based OpenAI LLM implementation."""

import time
from collections.abc import AsyncGenerator, Callable, Generator
from operator import call
from typing import Any, Optional, Dict
import asyncio

from sympy import comp
from tenacity import (
    AsyncRetrying,
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from higoalutils.language_model.llm.oai.text_utils import num_tokens
from higoalutils.logger.base import StatusLogger
from higoalutils.language_model.llm.base import BaseLLM, BaseLLMCallback
from higoalutils.language_model.llm.oai.base import OpenAILLMImpl
from higoalutils.language_model.llm.oai.typing import (
    OPENAI_RETRY_ERROR_TYPES,
    OpenaiApiType,
)
import logging
log = logging.getLogger(__name__)

_MODEL_REQUIRED_MSG = "model is required"


class ChatOpenAI(BaseLLM, OpenAILLMImpl):
    """Wrapper for OpenAI ChatCompletion models."""

    def __init__(
        self,
        encoding_model: str,
        api_key: str | None = None,
        model: str | None = None,
        api_base: str | None = None,
        api_type: OpenaiApiType = OpenaiApiType.OpenAI,
        max_retries: int = 10,
        request_timeout: float = 180.0,
        retry_error_types: tuple[type[BaseException]] = OPENAI_RETRY_ERROR_TYPES,  # type: ignore
        logger: StatusLogger | None = None,
    ):
        OpenAILLMImpl.__init__(
            self=self,
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,  # type: ignore
            max_retries=max_retries,
            request_timeout=request_timeout,
            logger=logger,
        )
        self.model = model
        self.retry_error_types = retry_error_types
        self.encoding_model = encoding_model

    def generate(
        self,
        messages: str | list[Any],
        streaming: bool = True,
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text."""
        try:
            retryer = Retrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                retry=retry_if_exception_type(self.retry_error_types),
            )
            for attempt in retryer:
                with attempt:
                    return self._generate(
                        messages=messages,
                        streaming=streaming,
                        callbacks=callbacks,
                        **kwargs,
                    )
        except RetryError as e:
            self._reporter.error(
                message="Error at generate()", details={self.__class__.__name__: str(e)}
            )
            return ""
        else:
            # TODO: why not just throw in this case?
            return ""

    def stream_generate(
        self,
        messages: str | list[Any],
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        """Generate text with streaming."""
        try:
            retryer = Retrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                retry=retry_if_exception_type(self.retry_error_types),
            )
            for attempt in retryer:
                with attempt:
                    generator = self._stream_generate(
                        messages=messages,
                        callbacks=callbacks,
                        **kwargs,
                    )
                    yield from generator

        except RetryError as e:
            self._reporter.error(
                message="Error at stream_generate()",
                details={self.__class__.__name__: str(e)},
            )
            return
        else:
            return

    async def agenerate(
        self,
        messages: str | list[Any],
        streaming: bool = True,
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text asynchronously."""
        t1 = time.time()
        try:
            retryer = AsyncRetrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                retry=retry_if_exception_type(self.retry_error_types),  # type: ignore
            )
            async for attempt in retryer:
                with attempt:
                    return await self._agenerate(
                        num_tokens=num_tokens,
                        messages=messages,
                        streaming=streaming,
                        callbacks=callbacks,
                        **kwargs,
                    )
        except RetryError as e:
            self._reporter.error(f"Error at agenerate(): {e}")
            log.error(f"Victor Wu: Error at agenerate(): {e}")
            t2 = time.time()
            completion_time = time.time() - t1
            if callbacks:
                if isinstance(messages, list):
                    prompt = '\n'.join([message["content"] for message in messages if "content" in message])
                else:
                    prompt = messages if isinstance(messages, str) else ""
                for callback in callbacks:
                    await callback.on_llm_query(
                        prompt=prompt,
                        exception=f"Error at agenerate(): {e}",
                        completion_time=completion_time,
                        llm_calls=1,
                    )
            return ""
        else:
            # TODO: why not just throw in this case?
            t2 = time.time()
            completion_time = time.time() - t1
            error_msg = "Unexpected error in agenerate()"

            self._reporter.error(error_msg)
            log.error(f"Victor Wu: {error_msg}")
            if callbacks:
                if isinstance(messages, list):
                    prompt = '\n'.join([message["content"] for message in messages if "content" in message])
                else:
                    prompt = messages if isinstance(messages, str) else ""
                for callback in callbacks:
                    await callback.on_llm_query(
                        prompt=prompt,
                        exception=f"Error at agenerate(): {error_msg}",
                        completion_time=completion_time,
                        llm_calls=1,
                    )
            return ""

    async def astream_generate( #  type: ignore
        self,
        messages: str | list[Any],
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Generate text asynchronously with streaming."""
        try:
            retryer = AsyncRetrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential_jitter(max=10),
                reraise=True,
                retry=retry_if_exception_type(self.retry_error_types),  # type: ignore
            )
            async for attempt in retryer:
                with attempt:
                    inner_generator = self._astream_generate(
                        messages=messages,
                        callbacks=callbacks,
                        **kwargs,
                    )
                    async for response in inner_generator:
                        yield response
        except RetryError as e:
            self._reporter.error(f"Error at astream_generate(): {e}")
            return
        else:
            return

    async def _generate(
        self,
        messages: str | list[Any],
        streaming: bool = False,
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> str:
        model = self.model
        if not model:
            raise ValueError(_MODEL_REQUIRED_MSG)
        isJson = kwargs.get("isJson", False)
        if isJson and not kwargs.get("response_format", {}):
            response = self.sync_client.chat.completions.create(  # type: ignore
                model=model,
                messages=messages,  # type: ignore
                stream=streaming,
                response_format={'type': 'json_object'},
                **kwargs,
            )  # type: ignore
        else:
            response = self.sync_client.chat.completions.create(  # type: ignore
                model=model,
                messages=messages,  # type: ignore
                stream=streaming,
                **kwargs,
            )  # type: ignore
        if streaming:
            full_response = ""
            while True:
                try:
                    chunk = response.__next__()  # type: ignore
                    if not chunk or not chunk.choices:
                        continue

                    delta = (
                        chunk.choices[0].delta.content
                        if chunk.choices[0].delta and chunk.choices[0].delta.content
                        else ""
                    )  # type: ignore

                    full_response += delta
                    if callbacks:
                        for callback in callbacks:
                            await callback.on_llm_new_token(delta)
                    if chunk.choices[0].finish_reason == "stop":  # type: ignore
                        break
                except StopIteration:
                    break
            return full_response
        return response.choices[0].message.content or ""  # type: ignore

    def _stream_generate(
        self,
        messages: str | list[Any],
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        model = self.model
        if not model:
            raise ValueError(_MODEL_REQUIRED_MSG)
        response = self.sync_client.chat.completions.create(  # type: ignore
            model=model,
            messages=messages,  # type: ignore
            stream=True,
            **kwargs,
        )
        for chunk in response:
            if not chunk or not chunk.choices:
                continue

            delta = (
                chunk.choices[0].delta.content
                if chunk.choices[0].delta and chunk.choices[0].delta.content
                else ""
            )

            yield delta

            if callbacks:
                for callback in callbacks:
                    callback.on_llm_new_token(delta)

    async def _agenerate(
        self,
        messages: str | list[Any],
        streaming: bool = True,
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> str:
        t1 = time.time()
        model = self.model
        if not model:
            raise ValueError(_MODEL_REQUIRED_MSG)

        allowed_kwargs = {
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "response_format",
            "isJson",
        }

        invalid_kwargs = set(kwargs.keys()) - allowed_kwargs
        if invalid_kwargs:
            log.warning(f"Victor Wu: Ignoring invalid kwargs: {invalid_kwargs}")
            kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}

        isJson = kwargs.get("isJson", False)
        if isJson and not kwargs.get("response_format", None):
            kwargs["response_format"] = {"type": "json_object"}
        kwargs.pop("isJson", None)

        log.info(f"Victor Wu: _agenerate(): isJson={isJson}, streaming={streaming}, response_format={kwargs.get('response_format', {})}")
        response = await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=streaming,
            **kwargs,
        )

        if streaming:
            full_response = ""
            try:
                async for chunk in response:
                    if not chunk or not chunk.choices:
                        continue

                    delta = (
                        chunk.choices[0].delta.content
                        if chunk.choices[0].delta and chunk.choices[0].delta.content
                        else ""
                    )
                    full_response += delta

                    if callbacks:
                        for callback in callbacks:
                            fn = getattr(callback, "on_llm_new_token", None)
                            if fn:
                                if callable(fn) and asyncio.iscoroutinefunction(fn):
                                    await fn(delta)
                                elif callable(fn):
                                    fn(delta)

                    if chunk.choices[0].finish_reason == "stop":
                        break
            except StopAsyncIteration:
                pass

            completion_time = time.time() - t1
            if callbacks:
                if isinstance(messages, list):
                    prompt = '\n'.join([m["content"] for m in messages if "content" in m])
                else:
                    prompt = messages if isinstance(messages, str) else ""
                for callback in callbacks:
                    await callback.on_llm_query(
                        prompt=prompt,
                        response=full_response,
                        completion_time=completion_time,
                        llm_calls=1,
                    )
            return full_response

        result = response.choices[0].message.content or ""
        completion_time = time.time() - t1
        if callbacks:
            if isinstance(messages, list):
                prompt = '\n'.join([m["content"] for m in messages if "content" in m])
            else:
                prompt = messages if isinstance(messages, str) else ""
            for callback in callbacks:
                await callback.on_llm_query(
                    prompt=prompt,
                    response=result,
                    completion_time=completion_time,
                    llm_calls=1,
                    prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                    output_tokens=response.usage.completion_tokens if response.usage else 0
                )
        return result

    async def _astream_generate(
        self,
        messages: str | list[Any],
        callbacks: list[BaseLLMCallback] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        model = self.model
        if not model:
            raise ValueError(_MODEL_REQUIRED_MSG)
        response = await self.async_client.chat.completions.create(  # type: ignore
            model=model,
            messages=messages,  # type: ignore
            stream=True,
            **kwargs,
        )
        async for chunk in response:
            if not chunk or not chunk.choices:
                continue

            delta = (
                chunk.choices[0].delta.content
                if chunk.choices[0].delta and chunk.choices[0].delta.content
                else ""
            )  # type: ignore

            yield delta

            if callbacks:
                for callback in callbacks:
                    callback.on_llm_new_token(delta)
