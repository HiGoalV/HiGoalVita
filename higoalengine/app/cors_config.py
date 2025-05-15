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

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from higoalengine.config.load_config import get_engine_config

def apply_cors(app: FastAPI):
    cfg = get_engine_config().web_config
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allow_origins or ["*"],
        allow_credentials=cfg.allow_credentials or True,
        allow_methods=cfg.allow_methods or ["*"],
        allow_headers=cfg.allow_headers or ["*"],
    )