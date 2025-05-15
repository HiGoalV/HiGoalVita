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

from fastapi import APIRouter
import time
from fastapi.responses import JSONResponse

from higoalengine.config.models.api_models import *
from higoalutils.config.load_model_info import get_model_info


router = APIRouter()

@router.get("/getModel", summary="获取 Chat 模型列表", tags=["模型管理"])
async def get_model():
    chat_models = get_model_info().get_chat_models()

    response_data = [
        {
            "key": model.id,
            "value": model.display_name
        }
        for model in chat_models
    ]

    return JSONResponse(content={
        "status": 1,
        "data": response_data,
        "msg": "操作成功",
        "timestamps": int(time.time() * 1000)
    })

