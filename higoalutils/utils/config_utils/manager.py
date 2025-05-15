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

from pathlib import Path
from typing import Any, Optional, Type, Generic
import yaml

from higoalutils.utils.config_utils.operation import load_dotenv_file, parse_env_variables, apply_overrides
from higoalutils.utils.config_utils.base import ConfigBase, T


class ConfigManager(ConfigBase[T], Generic[T]):
    def __init__(
        self,
        config_class: Type[T],
        config_dir: str,
        config_file: str,
        overrides: dict[str, Any] | None = None,
    ):
        self._config_class = config_class
        self._config_dir = config_dir
        self._config_file = config_file
        self._overrides = overrides or {}
        self._instance: Optional[T] = None

    def get_config(self) -> T:
        if self._instance is None:
            self._instance = self._load_config()
        return self._instance

    def reload(self) -> T:
        self._instance = self._load_config()
        return self._instance

    def _load_config(self) -> T:
        config_path = Path(self._config_dir)
        load_dotenv_file(config_path)

        file_path = config_path / self._config_file
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        config_text = file_path.read_text(encoding="utf-8")
        config_text = parse_env_variables(config_text)
        raw_data = yaml.safe_load(config_text)
        if self._overrides:
            apply_overrides(raw_data, self._overrides)

        return self._config_class(**raw_data)