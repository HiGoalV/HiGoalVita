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

"""关系型数据库ORM模型设计"""

import pytz
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

Base = declarative_base()


class ClaimStatus(PyEnum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    SUSPECTED = "SUSPECTED"

class KGDocument(Base):
    """文档存储表"""
    __tablename__ = 'kg_documents'

    id = Column(String(256), primary_key=True, comment='文档唯一ID')
    filename = Column(String(512), unique=True, comment='文件名')
    title = Column(String(512), default='', comment='文档标题')
    author = Column(String(128), default='', comment='作者')
    source = Column(String(512), default='', comment='文章来源')
    creation_date = Column(DateTime, comment='创建日期')
    extracted_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')), 
                         comment='提取入库时间')
    raw_data = Column(JSON, comment='元数据')

    chunks = relationship("KGChunk", back_populates="document", cascade="all, delete-orphan")

class KGChunk(Base):
    """文本块存储表"""
    __tablename__ = 'kg_chunks'

    id = Column(String(64), primary_key=True, comment='文本块唯一ID')
    text = Column(Text, comment='文本内容')
    source_doc_id = Column(String(256), ForeignKey('kg_documents.id', ondelete="CASCADE"), index=True, comment='关联文档ID')
    title = Column(String(512), default='', comment='文档标题')
    raw_data = Column(JSON, comment='元数据')

    document = relationship("KGDocument", back_populates="chunks")