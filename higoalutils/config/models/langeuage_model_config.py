# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""Language model configuration."""
from pydantic import BaseModel, Field

from higoalutils.config.defaults.language_model_defaults import LanguageModelDefaults
from higoalutils.config.enums.sys_enums import AsyncType

class LanguageModelConfig(BaseModel):
    """Language model configuration."""

    default_model: str = Field(
        description="The LLM model to use.",
        default=LanguageModelDefaults.default_model,
    )

    default_encoding_model: str = Field(
        description="The encoding model to use",
        default=LanguageModelDefaults.default_encoding_model,
    )
    model_supports_json: bool | None = Field(
        description="Whether the model supports JSON output mode.",
        default=LanguageModelDefaults.model_supports_json,
    )
    request_timeout: float = Field(
        description="The request timeout to use.",
        default=LanguageModelDefaults.request_timeout,
    )
    tokens_per_minute: int = Field(
        description="The number of tokens per minute to use for the LLM service.",
        default=LanguageModelDefaults.tokens_per_minute,
    )
    requests_per_minute: int = Field(
        description="The number of requests per minute to use for the LLM service.",
        default=LanguageModelDefaults.requests_per_minute,
    )
    retry_strategy: str = Field(
        description="The retry strategy to use for the LLM service.",
        default=LanguageModelDefaults.retry_strategy,
    )
    max_retries: int = Field(
        description="The maximum number of retries to use for the LLM service.",
        default=LanguageModelDefaults.max_retries,
    )
    max_retry_wait: float = Field(
        description="The maximum retry wait to use for the LLM service.",
        default=LanguageModelDefaults.max_retry_wait,
    )
    parallelization_num_threads: int = Field(
        default=1, 
        description="Number of parallel threads")
    parallelization_stagger: float = Field(
        default=0.0, 
        description="Stagger time for parallelization")

    async_mode: AsyncType = Field(
        description="The async mode to use.", default=LanguageModelDefaults.async_mode
    )
    responses: list[str | BaseModel] | None = Field(
        default=LanguageModelDefaults.responses,
        description="Static responses to use in mock mode.",
    )
    max_tokens: int = Field(
        description="The maximum number of tokens to generate.",
        default=LanguageModelDefaults.max_tokens,
    )
    temperature: float = Field(
        description="The temperature to use for token generation.",
        default=LanguageModelDefaults.temperature,
    )
    top_p: float = Field(
        description="The top-p value to use for token generation.",
        default=LanguageModelDefaults.top_p,
    )