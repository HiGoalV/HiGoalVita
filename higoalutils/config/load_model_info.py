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

from higoalutils.utils.config_utils.factory import ConfigFactory
from higoalutils.config.models.model_config import ModelRegistryConfig
from higoalutils.config.load_config import get_config


cfg = get_config()
ModelConfigManager = ConfigFactory(
    config_class=ModelRegistryConfig, 
    config_dir= f"{cfg.base_config.root_dir}/{cfg.base_config.config_dir}", 
    config_file=cfg.config_file_config.config_file_for_model
)

def get_model_info() -> ModelRegistryConfig:
    return ModelConfigManager.get_config()