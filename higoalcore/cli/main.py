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

"""HiGoal Graph RAG Cli 主程序入口"""
import asyncio
from typing import Annotated
import typer

from higoalcore.index.workflow.extract_docs import extract_docs
from higoalcore.config.load_config import get_core_config
from higoalutils.config.load_config import get_config
from higoalutils.callbacks.record_query_callbacks import RecordQueryCallbacks
from higoalcore.config.enums.query_enums import SearchMethod
from higoalcore.query.query import basic_search
from higoalutils.language_model.tokenizer.get_tokenizer import get_tokenizer
from higoalutils.logger.factory import LoggerFactory
from higoalutils.logger.types import LoggerType


app = typer.Typer(
    help="HiGoalRAG: A graph-based retrieval-augmented generation (RAG) system.",
    no_args_is_help=True,
)

@app.command("index")
def _index_cli(
    logger: Annotated[
        bool, typer.Option(help="The progress logger to use.")
    ] =  True
):
    """Build a knowledge graph index."""
    core_cfg = get_core_config()
    sys_config = get_config()
    progress_logger = LoggerFactory.create_logger(LoggerType.RICH) if logger else None
    asyncio.run(
        extract_docs(
            sys_config=sys_config,
            core_config=core_cfg,
            progress_reporter=progress_logger
        )
    )

@app.command("query")
def _query_cli(
    query: Annotated[
        str, typer.Option(help="The user question to search.")
    ],
    method: Annotated[
        SearchMethod, typer.Option(help="The searching method to use.")
    ] = SearchMethod.BASIC,
    model: Annotated[
        str, typer.Option(help="The searching model to use.")
    ] = "deepseek-chat"
):
    """A knowledge graph RAG 检索"""

    sys_cfg = get_config()
    tokenizer = get_tokenizer(sys_cfg.language_model_config.default_encoding_model)
    callbacks = []
    callbacks.append(RecordQueryCallbacks(tokenizer.count_tokens))
    match method:
        case SearchMethod.BASIC:
            asyncio.run(
                basic_search(
                    query=query,
                    system_config=sys_cfg,
                    embedding_config=sys_cfg.embedding_config,
                    callbacks=callbacks,
                    model_name=model
                ) 
            )