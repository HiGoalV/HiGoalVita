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

from enum import Enum
import re


class ChunkStrategyType(str, Enum):
    """ChunkStrategy class definition."""

    TOKENS = "tokens"
    SENTENCES = "sentences"

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'

class InputFileType(str, Enum):
    """The input file type for the pipeline."""

    CSV = "csv"
    """The CSV input type."""
    csv_file_pattern = re.compile(r"(?P<title>[^\\/]).csv$")
    """The CSV file pattern."""
    TEXT = "text"
    """The text input type."""
    text_file_pattern = re.compile(r"(?P<title>[^\\/]).txt$")

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'


class InputType(str, Enum):
    """The input type for the pipeline."""

    file = "file"
    """The file storage type."""

    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'

class VectorTable(str, Enum):
    """VectorTable class definition.暂时先这么用，后续有更复杂的表的时候再去改"""
    DOCUMENTS = "kg_documents_vector"
    CHUNKS = "kg_chunks_vector"
    ENTITIES = "kg_entities_vector"
    RELATIONS = "kg_relations_vector"
    CLAIMS = "kg_claims_vector"
    COMMUNITIES = "kg_communities_vector"
    def __repr__(self):
        """Get a string representation."""
        return f'"{self.value}"'