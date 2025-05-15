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

from pydantic import BaseModel

from pathlib import Path
from pydantic import BaseModel, Field, model_validator
from higoalutils.config.defaults.base_defaults import BaseConfigDefault


class BaseConfig(BaseModel):
    """The default configuration section for Reporting."""

    root_dir: str = Field(
        description="The root directory for the system.",
        default=BaseConfigDefault.root_dir,
    )
    config_dir: str = Field(
        description="The directory for configuration files.",
        default=BaseConfigDefault.config_dir,
    )
    log_dir: str = Field(
        description="The directory for log files.",
        default=BaseConfigDefault.log_dir,
    )
    output_dir: str = Field(
        description="The directory for output files.",
        default=BaseConfigDefault.output_dir,
    )
    file_encoding: str = Field(
        description="The encoding to use for file reporting.",
        default=BaseConfigDefault.file_encoding,
    )
    time_zone: str = Field(
        description="The time zone for the system.",
        default=BaseConfigDefault.time_zone,
    )

    def _validate_root_dir(self) -> None:
        """Validate the root directory."""
        if self.root_dir.strip() == "":
            self.root_dir = str(Path.cwd())

        root_dir = Path(self.root_dir).resolve()
        if not root_dir.is_dir():
            msg = f"Invalid root directory: {self.root_dir} is not a directory."
            raise FileNotFoundError(msg)
        self.root_dir = str(root_dir)

    @model_validator(mode="after")
    def _validate_model(self):
        """Validate the model configuration."""
        self._validate_root_dir()
        return self