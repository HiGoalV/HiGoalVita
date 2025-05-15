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

from typing import List, Optional

from higoalcore.config.enums.index_enums import InputFileType, InputType


class InputConfigDefaults:
    type: InputType = InputType.file
    root_dir: str = "appdata"
    base_dir: str = "input"
    file_encoding: str = "utf-8"
    file_type: List[InputFileType] = [InputFileType.TEXT, InputFileType.CSV]

    text_file_pattern: str = InputFileType.text_file_pattern
    
    csv_file_pattern: str = InputFileType.csv_file_pattern
    text_column: str = "text"
    title_column: Optional[str]= None

    
    
    
    
    