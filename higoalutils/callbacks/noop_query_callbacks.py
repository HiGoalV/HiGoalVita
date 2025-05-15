# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""No-op Query Callbacks."""

from typing import Any

from higoalutils.callbacks.query_callbacks import QueryCallbacks
from higoalutils.language_model.search_result import SearchResult


class NoopQueryCallbacks(QueryCallbacks):
    """A no-op implementation of QueryCallbacks."""

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

    def on_llm_new_token(self, token):
        """Handle when a new token is generated."""

    def add_tokens(self, prompt_tokens: int | None, output_tokens: int | None):
        """Caculate the number of tokens used."""
        
    def add_llm_call(self, llm_calls:int = 1):
        """Add a LLM call."""
