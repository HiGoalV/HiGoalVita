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

from typing import Optional
from higoalutils.language_model.llm.get_client import get_text_embedder
from higoalutils.language_model.llm.base import BaseTextEmbedding
from higoalutils.config.models.embedding_config import EmbeddingConfig
import threading


class EmbeddingModelSingleton:
    """
    文本嵌入模型单例管理器
    确保全局只有一个嵌入模型实例
    """
    
    _instance: Optional[BaseTextEmbedding] = None
    _lock = threading.Lock()
    _config: Optional[EmbeddingConfig] = None
    
    @classmethod
    def get_instance(cls, config: Optional[EmbeddingConfig] = None) -> BaseTextEmbedding:
        """
        获取全局唯一的嵌入模型实例
        
        参数:
            config: 模型配置(第一次调用时必须提供)
            
        返回:
            BaseTextEmbedding实例
            
        异常:
            ValueError: 如果第一次调用时未提供配置
        """
        if cls._instance is None:
            with cls._lock:
                # 再次检查，防止多线程环境下重复创建
                if cls._instance is None:
                    if config is None:
                        raise ValueError("首次调用必须提供模型配置")
                    cls._config = config
                    cls._instance = get_text_embedder(config)
        elif config is not None and config != cls._config:
            raise ValueError("嵌入模型配置已初始化，不允许更改")
            
        return cls._instance
    
    @classmethod
    def clear_instance(cls) -> None:
        """
        清除当前实例(主要用于测试)
        """
        with cls._lock:
            cls._instance = None
            cls._config = None