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

"""HuggingFaceEmbeddings model implementation."""

from typing import Any
import numpy as np

from higoalutils.language_model.llm.base import BaseTextEmbedding
from higoalutils.language_model.llm.huggingface_embedding.bge_embeddings import get_embeddings


class HuggingFaceEmbedding(BaseTextEmbedding):
    """Wrapper for HuggingFaceEmbedding models."""

    def __init__(
        self,
        model: str,
        device: str = "cpu",
        max_tokens: int = 524288, # 512K tokens
    ):
        self.max_tokens = max_tokens
        self.embeddings = get_embeddings(model, device)
    def embed(self, text: str | list[str], **kwargs: Any) -> list[list[float]]:
        """
        Embed text using HuggingFaceEmbedding sync function.
        """
        if isinstance(text, str):
            text = [text]
        chunk_embeddings = np.array(self.embeddings.embed_documents(text)).tolist()
        return chunk_embeddings

    async def aembed(self, text: str | list[str], **kwargs: Any) -> list[list[float]]:
        """
        Embed text using OpenAI Embedding's async function.
        """
        if isinstance(text, str):
            text = [text]
        chunk_embeddings = np.array(await self.embeddings.aembed_documents(text)).tolist()
        return chunk_embeddings
