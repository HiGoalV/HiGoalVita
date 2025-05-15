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

import logging
from pathlib import Path
from typing import List

from higoalcore.index.text_splitting.splitter.text_splitter import create_chunks
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalcore.config.models.chunking_config import ChunkingConfig
from higoalcore.config.models.input_config import InputConfig
from higoalutils.storage.pipeline_storage import PipelineStorage
from higoalutils.logger.base import ProgressLogger
from higoalutils.utils.code_utils.hashing import gen_sha512_hash
from higoalcore.index.text_splitting.loaders.loader_base import BaseChunkLoader
from higoalutils.logger.progress import ProgressTicker


log = logging.getLogger(__name__)

class TextChunkLoader(BaseChunkLoader):
    async def load_and_chunk(
        self,
        input_config: InputConfig,
        chunk_config: ChunkingConfig,
        storage: PipelineStorage,
        progress: ProgressLogger | None
    ) -> List[ChunkText]:
        chunks = []
        log.info("[ChunkingFactory] Loading TEXT files...")
        files = list(storage.find(self.pattern, progress=progress))
        if not files:
            log.warning(f"No text files found in {input_config.base_dir}")
            return []

        log.info(f"Found {len(files)} text files in {input_config.base_dir}")
        ticker = ProgressTicker(progress, num_total=len(files))

        for file, group in files:
            try:
                text = await storage.get(file, encoding=input_config.file_encoding)
                item = {**group, "text": text}
                doc = {
                    **group,
                    "text": text,
                    "id": gen_sha512_hash(item, item.keys()),
                    "filename": str(Path(file).name),
                    "creation_date": await storage.get_creation_date(file),
                }
                doc_chunks = create_chunks(chunk_config, input=doc, ticker=None)
                chunks.extend(doc_chunks)
                log.info("Loaded %d chunks from text file: %s", len(doc_chunks), file)
            except Exception as e:
                log.warning("Error loading text file %s: %s", file, str(e))
            finally:
                ticker()

        log.info("Completed loading. Total text files: %d, total chunks: %d", len(files), len(chunks))
        ticker.done()
        return chunks