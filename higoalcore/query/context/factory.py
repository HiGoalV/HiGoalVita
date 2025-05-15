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

"""生成上下文的工厂模块"""

from higoalcore.config.enums.query_enums import SearchMethod
from higoalutils.config.models.embedding_config import EmbeddingConfig
from higoalcore.database.kg_vector_store import KGVectorStore


async def create_context(
    query: str,
    embedding_config: EmbeddingConfig,
    search_method: SearchMethod = SearchMethod.BASIC,
    callbacks: list = [],
) -> str:
    """
    根据查询和搜索方法生成上下文。
    """
    result = ""
    match search_method:
        case SearchMethod.BASIC:
            result = await create_basic_search_context(
                query=query,
                embedding_config=embedding_config,
            )
    for callback in callbacks:
        callback.on_context(result)
    return result
        
async def create_basic_search_context(
    query: str,
    embedding_config: EmbeddingConfig,
    top_k: int | None = None,
    similarity_threshold: float | None = None,
) -> str:
    """
    根据查询生成基本搜索上下文。
    """
    vector_store = KGVectorStore(embedding_config=embedding_config)
    
    results: list[dict] = await vector_store.chunk_operator.semantic_search(
        query=query,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )

    final_result = ""

    # 处理搜索结果
    for result in results:
        final_result += f"文档ID: {result["id"]}\n" 
        final_result += f"title: {result.get("metadata",{}).get("title","no title")}\n"
        final_result += f"内容: {result.get("text","")}\n"
        final_result += f"相似度分数: {result.get("score",0):.4f}\n"

    return  final_result