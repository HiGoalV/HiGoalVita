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

"""HuggingFaceEmbeddings model definition."""

import os
from typing import Union
from huggingface_hub import snapshot_download
from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore

os.environ["TOKENIZERS_PARALLELISM"] = "false"

DEFAULT_MODEL = "BAAI/bge-large-zh-v1.5"

def sanitize_model_dir(model_name: str) -> str:
    """将 HuggingFace 模型名转换为合法的本地目录名"""
    return model_name.replace("/", "__")

def get_embeddings(modelname: Union[str, None], device: str = "cpu") -> HuggingFaceEmbeddings:
    """
    加载或自动下载 HuggingFace 模型用于向量嵌入。
    
    参数:
        modelname (str): 模型名称，例如 'BAAI/bge-large-zh-v1.5'，可为 None（使用默认模型）
        device (str): 运行设备，支持 'cpu', 'cuda', 'mps' 等

    返回:
        HuggingFaceEmbeddings 实例
    """
    if modelname is None:
        modelname = DEFAULT_MODEL

    # 指定本地缓存路径（你可根据项目统一管理模型路径）
    cache_root = os.path.abspath("models/hf_models")
    local_dir = os.path.join(cache_root, sanitize_model_dir(modelname))

    # 如果不存在就下载
    if not os.path.exists(os.path.join(local_dir, "config.json")):
        print(f"[INFO] Downloading model: {modelname} to {local_dir}")
        snapshot_download(
            repo_id=modelname,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
        )

    # 设置 sentence_transformers 缓存路径（可选）
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = cache_root

    return HuggingFaceEmbeddings(
        model_name=local_dir,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )
