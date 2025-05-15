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
from typing import Type
from higoalutils.utils.config_utils.manager import ConfigManager
from higoalutils.config.defaults.sys_defaults import DEFAULT_CONFIG_FILES, DEFAULT_ROOT_DIR, DEFAULT_CONFIG_DIR

_config_registry: dict[tuple[str, str], ConfigManager] = {}

def ConfigFactory(
    config_class: Type,
    config_dir: str = f"{DEFAULT_ROOT_DIR}/{DEFAULT_CONFIG_DIR}",
    config_file: str = DEFAULT_CONFIG_FILES,
    overrides: dict[str, str] | None = None,
) -> ConfigManager:
    key = (config_class.__name__, str(Path(config_dir).resolve()))
    if key not in _config_registry:
        _config_registry[key] = ConfigManager(
            config_class=config_class,
            config_dir=config_dir,
            config_file=config_file,
            overrides=overrides,
        )
    return _config_registry[key]
