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

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text, Float
from datetime import datetime

from higoalengine.config.enums.task_type import TaskStatusType
from higoalutils.database.relational_database.manager import DBEngineManager
from higoalutils.utils.time_utils.get_datetime import get_internet_datetime


Base = DBEngineManager().get_base()

class UserQATask(Base):
    __tablename__ = "user_qa_tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_role: Mapped[str] = mapped_column(String(50))
    company: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))
    subcategory: Mapped[str] = mapped_column(String(50))
    permissions: Mapped[str] = mapped_column(String(500))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[TaskStatusType] = mapped_column(String(50), default=TaskStatusType.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_internet_datetime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_internet_datetime, onupdate=get_internet_datetime)


class UserQuery(Base):
    __tablename__ = "user_queries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_internet_datetime)


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text)
    answer_image: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_internet_datetime)