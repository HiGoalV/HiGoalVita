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

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Pattern
import re

from higoalcore.config.defaults.input_defaults import InputConfigDefaults
from higoalcore.config.enums.index_enums import InputFileType, InputType


class InputConfig(BaseModel):
    """输入配置"""
    model_config = ConfigDict(extra="ignore")
    
    type: InputType = Field(default=InputConfigDefaults.type, description="输入类型")
    root_dir: str = Field(
        default=InputConfigDefaults.root_dir,
        description="业务文件根目录"
    )
    file_type: List[InputFileType] = Field(
        default=InputConfigDefaults.file_type,
        description="支持的文件类型，例如 ['txt', 'csv']"
    )
    base_dir: str = Field(
        default=InputConfigDefaults.base_dir,
        description="基础目录"
    )
    file_encoding: str = Field(
        default=InputConfigDefaults.file_encoding,
        description="文件编码，比如utf-8"
    )
    
    text_file_pattern: str = Field(
        default=InputConfigDefaults.text_file_pattern,
        description="文本文件匹配模式（如果支持txt）"
    )

    csv_file_pattern: str = Field(
        default=InputConfigDefaults.csv_file_pattern,
        description="CSV文件匹配模式（如果支持csv）"
    )
    text_column: str = Field(
        default=InputConfigDefaults.text_column,
        description="CSV文件中的文本列列名"
    )
    title_column: Optional[str] = Field(
        default=InputConfigDefaults.title_column,
        description="CSV文件中的标题列列名"
    )

    @property
    def text_pattern(self) -> Pattern[str]:
        return re.compile(self.text_file_pattern)

    @property
    def csv_pattern(self) -> Pattern[str]:
        return re.compile(self.csv_file_pattern)

    @model_validator(mode="after")
    def validate_by_file_type(self) -> "InputConfig":
        """根据file_type内容动态校验相关字段"""
        if InputFileType.TEXT in self.file_type:
            assert self.text_file_pattern, "需要提供text_file_pattern来匹配txt文件。"

        if InputFileType.CSV in self.file_type:
            assert self.csv_file_pattern, "需要提供csv_file_pattern来匹配csv文件。"
            assert self.text_column, "需要提供text_column，指定CSV中的文本列。"
            assert self.title_column, "需要提供title_column，指定CSV中的标题列。"
        
        return self