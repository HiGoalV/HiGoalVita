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

import os
from pathlib import Path
from string import Template
from typing import Any
from dotenv import load_dotenv
from higoalutils.config.defaults.sys_defaults import DEFAULT_ENV_FILE


def load_dotenv_file(config_dir: Path) -> None:
    """Load .env file from config_dir if exists."""
    dotenv_file = config_dir / DEFAULT_ENV_FILE
    if dotenv_file.exists():
        load_dotenv(dotenv_file)


def parse_env_variables(text: str) -> str:
    """Replace ${ENV_VAR} in YAML with actual env values."""
    return Template(text).safe_substitute(os.environ)


def apply_overrides(data: dict[str, Any], overrides: dict[str, Any]) -> None:
    """Apply CLI overrides in dot notation like 'a.b.c' = 1."""
    for key, value in overrides.items():
        keys = key.split(".")
        target = data
        current_path_parts = []
        for k in keys[:-1]:
            current_path_parts.append(k)
            target_obj = target.get(k, {})
            if not isinstance(target_obj, dict):
                raise TypeError(f"Cannot override non-dict value at {'.'.join(current_path_parts)}")
            target[k] = target_obj
            target = target[k]
        target[keys[-1]] = value