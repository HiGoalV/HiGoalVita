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

"""HiGoalRAG的检索入口模块"""

from higoalcore.query.context.factory import create_context
from higoalcore.query.prompts.construct_prompt import get_prompt_template, complete_prompt
from higoalcore.config.enums.query_enums import SearchMethod
from higoalutils.config.models.system_config import SystemConfig
from higoalutils.config.models.embedding_config import EmbeddingConfig
from higoalutils.language_model.llm.get_client import get_llm


async def basic_search(
    query: str,
    system_config: SystemConfig,
    embedding_config: EmbeddingConfig,
    callbacks: list = [],
    model_name: str | None = None,
) -> None:
    # 获取上下文
    context = await create_context(
        query=query,
        embedding_config=embedding_config,
        search_method=SearchMethod.BASIC,
        callbacks=callbacks,
    )
    
    prompt = await get_prompt_template(
        query_text=query,
        search_method=SearchMethod.BASIC,
    )

    messages = complete_prompt(
        query=query,
        prompt=prompt,
        context=context,
    )

    # 获取LLM客户端
    llm_client = get_llm(system_config.language_model_config, model_name)
    response = await llm_client.agenerate(messages, callbacks=callbacks)
    
    print("-----------------------------------\n")
    print(f"提问：{query}\n")
    print(response)
    print(f"LLM 访问 {callbacks[-1].llm_calls} 次, 用时: {callbacks[-1].completion_time} 秒。")
    print("-----------------------------------")