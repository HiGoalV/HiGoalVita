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

from typing import Sequence, Union
import numpy as np
import torch


VectorLike = Union[Sequence[float], np.ndarray]

def normalize_vector(vec: VectorLike) -> list[float]:
    """通用归一化函数，支持 List / ndarray / Tensor，输出 float32 list"""
    # 处理 torch.Tensor
    if isinstance(vec, torch.Tensor):
        vec = vec.detach().cpu().numpy()

    # 转为 numpy 数组（float32）
    arr = np.array(vec, dtype=np.float32)

    # 计算 L2 范数并归一化
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr.tolist()

    return (arr / norm).tolist()