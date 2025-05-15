# Copyright (c) 2025 HiGoal Corporation.
# Licensed under the Private License

"""LLM Query Callbacks."""
import pandas as pd
from typing import Any

from higoalutils.callbacks.llm_callbacks import BaseLLMCallback
from higoalutils.language_model.search_result import SearchResult


class QueryCallbacks(BaseLLMCallback):
    """Callbacks used during query execution."""

    def on_context(self, context: Any) -> None:
        """Handle when context data is constructed."""

    def on_map_response_start(self, map_response_contexts: list[str]) -> None:
        """Handle the start of map operation."""

    def on_map_response_end(self, map_response_outputs: list[SearchResult]) -> None:
        """Handle the end of map operation."""

    def on_reduce_response_start(
        self, reduce_response_context: str | dict[str, Any]
    ) -> None:
        """Handle the start of reduce operation."""

    def on_reduce_response_end(self, reduce_response_output: str) -> None:
        """Handle the end of reduce operation."""

    def on_llm_response(self, search_result: SearchResult) -> None:
        """Handle the LLM response."""
    
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
    
    def dumps(self) -> str:
        """Dump the callback to a string."""
        return ""