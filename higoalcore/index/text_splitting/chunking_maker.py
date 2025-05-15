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

from typing import List
from pathlib import Path
import logging

from higoalcore.config.models.chunking_config import ChunkingConfig
from higoalcore.config.models.input_config import InputConfig
from higoalcore.index.text_splitting.chunk_text.chunk_text import ChunkText
from higoalutils.logger.base import ProgressLogger
from higoalutils.logger.null_progress import NullProgressLogger
from higoalutils.storage.pipeline_storage import PipelineStorage
from higoalutils.storage.file_pipeline_storage import FilePipelineStorage
from higoalcore.index.text_splitting.loaders.csv_loader import CSVChunkLoader
from higoalcore.index.text_splitting.loaders.text_loader import TextChunkLoader
from higoalcore.config.enums.index_enums import InputFileType


log = logging.getLogger(__name__)

class ChunkingFactory:
    def __init__(
        self,
        input_config: InputConfig,
        chunk_config: ChunkingConfig,
        progress_reporter: ProgressLogger | None = None
    ):
        self.input_config = input_config
        self.chunk_config = chunk_config
        self.progress = progress_reporter or NullProgressLogger()
        file_path = Path(input_config.root_dir) / input_config.base_dir
        self.storage: PipelineStorage = FilePipelineStorage(root_dir=str(file_path))

    async def run(self) -> List[ChunkText]:
        chunks = []

        if InputFileType.TEXT in self.input_config.file_type:
            text_logger = self.progress.child("📄 Text Files", transient=False) if self.progress else None
            loader = TextChunkLoader(pattern=self.input_config.text_pattern, input_type="text")
            chunks += await loader.load_and_chunk(self.input_config, self.chunk_config, self.storage, text_logger)

        if InputFileType.CSV in self.input_config.file_type:
            csv_logger = self.progress.child("🧾 CSV Files", transient=False) if self.progress else None
            loader = CSVChunkLoader(pattern=self.input_config.csv_pattern, input_type="csv")
            chunks += await loader.load_and_chunk(self.input_config, self.chunk_config, self.storage, csv_logger)

        return chunks