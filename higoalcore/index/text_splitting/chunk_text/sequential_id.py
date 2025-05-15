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

"""生成连续性ID的生成器，带文件锁和进程锁机制，全局唯一实例控制。用于切片等ID生成场景。支持多key=value对"""

import time
import os
import sys
import atexit
from threading import RLock
from pathlib import Path
from typing import Dict, Optional
import pytz
from datetime import datetime
from contextlib import contextmanager


# 根据操作系统选择文件锁定方式
if sys.platform == "win32":
    import msvcrt
    LOCK_EX = 0x1  # 独占锁
    LOCK_UN = 0x0  # 解锁
else:
    import fcntl
    LOCK_EX = fcntl.LOCK_EX
    LOCK_UN = fcntl.LOCK_UN

DEFAULT_STORAGE_PATH = "datavolume/config/sequential_id.dat"
DEFAULT_TIMEZONE = "Asia/Shanghai"
_SINGLETON_INSTANCE: Optional['DailySequentialIDGenerator'] = None
_SINGLETON_LOCK = RLock()

class DailySequentialIDGenerator:
    def __init__(self, 
                storage_path: str = DEFAULT_STORAGE_PATH,
                time_zone: str = DEFAULT_TIMEZONE,
                auto_persist_every: int = 100,
                min_persist_interval: float = 1.0):
        """
        初始化ID生成器
        
        :param storage_path: 存储文件路径
        :param time_zone: 时区(如"Asia/Shanghai")
        :param auto_persist_every: 自动持久化间隔(每N次)
        :param min_persist_interval: 最小持久化间隔(秒)
        """
        self._storage = Path(storage_path)
        self._counters: Dict[str, int] = {}
        self._last_dates: Dict[str, str] = {}
        self._lock = RLock()
        self._time_zone = pytz.timezone(time_zone)
        self._auto_persist_every = auto_persist_every
        self._min_persist_interval = min_persist_interval
        self._last_persist_time = 0.0
        
        self._init_counters()
        atexit.register(self._safe_persist)

    @staticmethod
    def _file_lock(file):
        """跨平台文件锁定"""
        try:
            if sys.platform == "win32":
                msvcrt.locking(file.fileno(), LOCK_EX, 1)
            else:
                fcntl.flock(file, LOCK_EX | fcntl.LOCK_NB)
        except (OSError, IOError) as e:
            raise RuntimeError(f"文件锁定失败: {str(e)}")

    @staticmethod
    def _file_unlock(file):
        """跨平台文件解锁"""
        try:
            if sys.platform == "win32":
                if os.path.exists(file.name):  # 检查文件是否存在
                    msvcrt.locking(file.fileno(), LOCK_UN, 1)
            else:
                fcntl.flock(file, LOCK_UN)
        except (OSError, IOError):
            pass  # 解锁失败不影响主要逻辑

    @classmethod
    def get_instance(cls, 
                   storage_path: str = DEFAULT_STORAGE_PATH,
                   **kwargs) -> 'DailySequentialIDGenerator':
        """获取全局唯一实例"""
        global _SINGLETON_INSTANCE, _SINGLETON_LOCK
        
        if _SINGLETON_INSTANCE is not None:
            return _SINGLETON_INSTANCE

        with _SINGLETON_LOCK:
            if _SINGLETON_INSTANCE is None:
                lockfile = Path(storage_path).with_suffix('.lock')
                lockfile.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    with open(lockfile, 'wb+') as f:  # 使用二进制模式避免编码问题
                        try:
                            cls._file_lock(f)
                            _SINGLETON_INSTANCE = cls(storage_path, **kwargs)
                        finally:
                            cls._file_unlock(f)
                except Exception as e:
                    raise RuntimeError(f"初始化ID生成器失败: {str(e)}")
        
        return _SINGLETON_INSTANCE

    def _init_counters(self):
        """初始化计数器"""
        try:
            if not self._storage.exists():
                self._storage.parent.mkdir(parents=True, exist_ok=True)
                with open(self._storage, 'w'):
                    return
            
            with open(self._storage, 'rb+') as f:  # 二进制模式读取
                self._file_lock(f)
                try:
                    content = f.read().decode('utf-8').strip()
                    if content:
                        for item in content.split(","):
                            if "=" in item:
                                key, values = item.split("=")
                                date_str, counter_str = values.split("|")
                                self._counters[key] = int(counter_str)
                                self._last_dates[key] = date_str
                finally:
                    self._file_unlock(f)
        except Exception as e:
            raise RuntimeError(f"初始化计数器失败: {str(e)}")

    def _do_persist(self):
        """执行持久化(假设已持有锁)"""
        current_time = time.time()
        if current_time - self._last_persist_time < self._min_persist_interval:
            return
        
        try:
            temp_path = self._storage.with_suffix('.tmp')

            with open(temp_path, 'wb') as f:  # 先写入临时文件
                items = [
                    f"{k}={self._last_dates[k]}|{self._counters[k]}".encode('utf-8')
                    for k in self._counters
                ]
                f.write(b",".join(items))
            # 原子性替换文件
            if sys.platform == "win32":
                # Windows需要先删除原文件
                if self._storage.exists():
                    os.unlink(self._storage)
            temp_path.replace(self._storage)
            
            self._last_persist_time = current_time
        except Exception as e:
            if temp_path.exists(): # type: ignore[union-attr]
                temp_path.unlink() # type: ignore[union-attr]
            raise RuntimeError(f"持久化失败: {str(e)}")

    def _safe_persist(self):
        """安全的持久化方法"""
        with self._lock:
            try:
                self._do_persist()
            except Exception as e:
                pass

    def _get_current_date(self) -> str:
        """获取当前日期(yyMMdd)"""
        return datetime.now(self._time_zone).strftime("%y%m%d")

    def generate_id(self, key: str = "default") -> str:
        """
        生成唯一ID(自动持久化保障)
        格式: 6位日期 + 9位序列号 = 15位
        """
        with self._lock:
            current_date = self._get_current_date()
            
            # 必须持久化的场景
            must_persist = (
                key not in self._counters or 
                current_date != self._last_dates.get(key)
            )
            
            if must_persist:
                self._counters[key] = 0
                self._last_dates[key] = current_date
            
            self._counters[key] += 1
            
            if self._counters[key] > 999_999_999:
                raise ValueError(f"序列号超过最大值 (key: {key}, date: {current_date})")
            
            # 自动持久化条件
            if must_persist or self._counters[key] % self._auto_persist_every == 0:
                self._safe_persist()
            
            return f"{current_date}{self._counters[key]:09d}"

    @contextmanager
    def batch_mode(self):
        """
        批量操作上下文管理器
        退出时自动持久化，期间减少持久化频率
        """
        original_interval = self._auto_persist_every
        self._auto_persist_every = sys.maxsize
        
        try:
            yield
        finally:
            self._auto_persist_every = original_interval
            self._safe_persist()

    def persist_now(self):
        """立即持久化"""
        self._safe_persist()

    def __del__(self):
        """对象销毁时自动持久化"""
        self._safe_persist()

if __name__ == "__main__":
    try:
        # 获取实例
        generator = DailySequentialIDGenerator.get_instance(
            auto_persist_every=100,
            min_persist_interval=0.5
        )
        
        # 测试生成ID
        print("生成的ID示例:")
        for _ in range(5):
            print(generator.generate_id())
        
        # 测试新key
        print("\n测试新key:")
        print(generator.generate_id(key="test_key"))
        
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)