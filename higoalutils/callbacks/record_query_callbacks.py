# Copyright 2025 HiGoal Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""用于 Query Callbacks, 记录LLM调用次数、消耗Tokens以及报错信息"""

import pandas as pd
from typing import Any
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
import asyncio

from higoalutils.callbacks.query_callbacks import QueryCallbacks
from higoalutils.language_model.search_result import SearchResult, pretty_print_search_result
from higoalutils.language_model.tokenizer.types import TextTokenizerEncoder,TextTokenizerDecoder,TextTokenizerCounter
from higoalutils.database.memory_store.base import MemoryStoreBase
from higoalengine.database.models import UserAnswer, UserQATask
from higoalengine.config.enums.task_type import TaskStatusType
from higoalengine.config.models.api_chunk_models import StreamChunk, FullResult
from higoalengine.config.load_config import get_engine_config


async def save_and_publish_fragment_with_status(
    *,
    task_id: str,
    chunk_index: int,
    content: str,
    is_final: bool,
    sessionmaker: async_sessionmaker[AsyncSession] | None = None,
    memory_store: MemoryStoreBase | None = None,
) -> None:
    cfg = get_engine_config().memory_config

    chunk = StreamChunk(
        task_id=task_id,
        chunk_index=chunk_index,
        content=content,
        is_final=is_final
    )
    print(chunk)

    if memory_store is None:
        raise ValueError("memory_store is None")

    if chunk_index == 1:
        await memory_store.set(f"task:{task_id}:status", TaskStatusType.OUTPUTTING, expire=cfg.result_retention_time)
    await memory_store.set(f"task:{task_id}:chunk:{chunk_index}", chunk.to_memory(), expire=cfg.task_timeout)
    await memory_store.set(f"task:{task_id}:chunk:max", chunk_index, expire=cfg.task_timeout)

    if is_final:
        full_content = ""
        for i in range(1, chunk_index + 1):
            cached = await memory_store.get(f"task:{task_id}:chunk:{i}")
            if cached:
                full_content += cached["content"]
        full_result = FullResult(
            task_id=task_id,
            content=full_content
        )
        await memory_store.set(f"task:{task_id}:result", full_result.to_memory(), expire=cfg.result_retention_time)
        
        if sessionmaker is None:
            raise RuntimeError("sessionmaker is None")
        
        async with sessionmaker() as session:
            async with session.begin():
                result = await session.execute(select(UserAnswer).where(UserAnswer.task_id == task_id))
                answer = result.scalar_one_or_none()

                if answer:
                    answer.answer_text = full_content
                else:
                    session.add(UserAnswer(
                        task_id=task_id,
                        answer_text=full_content
                    ))

                result = await session.execute(select(UserQATask).where(UserQATask.task_id == task_id))
                task = result.scalar_one()
                task.status = TaskStatusType.SUCCEEDED

        await memory_store.set(f"task:{task_id}:status", TaskStatusType.SUCCEEDED, expire=cfg.result_retention_time)




class RecordQueryCallbacks(QueryCallbacks):
    """A no-op implementation of QueryCallbacks."""
    def __init__(self, 
            num_tokens: TextTokenizerCounter,
            task_id: str | None = None,
            stream_to_redis: bool = False,
            memory_store: MemoryStoreBase | None = None,
            sessionmaker: async_sessionmaker[AsyncSession] | None = None,
        ) -> None:
        """Initialize the RecordQueryCallbacks."""
        self.context_data = {} # 用于向上兼容，过往版本
        self.llm_calls = 0
        self.prompt_tokens: int = 0
        self.output_tokens: int = 0
        self.completion_time: float = 0
        self.search_results: list[SearchResult] = []
        self.num_tokens = num_tokens
        self.stream_to_redis = stream_to_redis
        self.task_id = task_id
        self.memory_store = memory_store
        self.sessionmaker = sessionmaker
        self.chunk_index = 1
        self.buffer = ""
        

    def on_context(self, context: Any) -> None:
        """Handle when context data is constructed."""
        self.context_data = context

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

    async def on_llm_new_token(self, token):
        if self.stream_to_redis and self.task_id and self.memory_store:
            # ✅ 取消检查逻辑（每次 token 推送前都检查）
            status = await self.memory_store.get(f"task:{self.task_id}:status")
            if status == TaskStatusType.CANCELLED:
                print(f"❌ Task {self.task_id} 被取消，中止推理")
                raise asyncio.CancelledError(f"Task {self.task_id} was cancelled.")

            self.buffer += token
            if len(self.buffer) >= 10 or token in ('.', '。', '\n'):
                await save_and_publish_fragment_with_status(
                    task_id=self.task_id,
                    chunk_index=self.chunk_index,
                    content=self.buffer,
                    is_final=False,
                    sessionmaker=self.sessionmaker,
                    memory_store=self.memory_store,
                )
                self.chunk_index += 1
                self.buffer = ""

    def add_tokens(self, prompt_tokens: int | None, output_tokens: int | None):
        """Caculate the number of tokens used."""
        self.prompt_tokens += prompt_tokens or 0
        self.output_tokens += output_tokens or 0
    
    def add_llm_call(self, llm_calls:int = 1):
        """Add a LLM call."""
        self.llm_calls += llm_calls
    
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
        """记录LLM查询结果。可以是查询前，或者查询后."""
        search_result = SearchResult(
            response=response,
            context_data=context_data,
            prompt=prompt,
            context_text=context,
            exception=exception,
            completion_time=completion_time,
            llm_calls=llm_calls,
            prompt_tokens=prompt_tokens if prompt_tokens !=0 else self.num_tokens(prompt),
            output_tokens=output_tokens if output_tokens !=0 else self.num_tokens(str(response)) if response else 0,
        )
        self.search_results.append(search_result)
        self.add_tokens(search_result.prompt_tokens, search_result.output_tokens)
        self.add_llm_call(search_result.llm_calls)
        self.completion_time += completion_time
        if self.stream_to_redis and self.buffer and self.task_id:
            await save_and_publish_fragment_with_status(
                task_id=self.task_id,
                chunk_index=self.chunk_index,
                content=self.buffer,
                is_final=True,
                sessionmaker=self.sessionmaker,
                memory_store=self.memory_store,
            )
            self.buffer = ""
    
    def dumps(self) -> str:
        """Dump the callback to a string."""
        outstr = f"Total {self.llm_calls} LLM calls, take {"{:.2f}".format(self.completion_time)} seconds,\n"
        outstr += f" and used {self.prompt_tokens} prompt tokens and {self.output_tokens} output tokens."
        if self.search_results:
            outstr += f"Details of the LLM calls are as follows:\n"
            for search_result in self.search_results:
                outstr += pretty_print_search_result(search_result) + "\n"
        return outstr