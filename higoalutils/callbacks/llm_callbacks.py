# Copyright (c) 2025 HiGoal Corporation.
# Licensed under the Private License

"""LLM 回调函数，用于记录每次LLM查询的结果."""

import pandas as pd
from typing import Protocol, Any
from higoalutils.language_model.search_result import SearchResult

class BaseLLMCallback(Protocol):
    """Base class for LLM callbacks."""

    async def on_llm_new_token(self, token: str):
        """Handle when a new token is generated."""
        ...

    def add_tokens(self, prompt_tokens: int | None, output_tokens: int | None):
        """Caculate the number of tokens used."""
        ...

    def add_llm_call(self, llm_calls: int= 1):
        """Add a LLM call."""
        ...
    
    def on_llm_response(self, search_result: SearchResult) -> None:
        """Handle the LLM response."""
        ...
    
    async def on_llm_query(
            self, 
            prompt: str,
            context: str | None = None,
            context_data: str | list[pd.DataFrame] | dict[str, pd.DataFrame] | None = None,
            response: str | dict[str, Any] | list[dict[str, Any]] | None = None,
            exception: str | None = None,
            completion_time: float = 0,
            llm_calls: int = 1,
            prompt_tokens: int = 0,
            output_tokens: int = 0
    ) -> None:
        """Handle the LLM query."""
        ...
    
    def dumps(self) -> str:
        """Dump the callback to a string."""
        ...