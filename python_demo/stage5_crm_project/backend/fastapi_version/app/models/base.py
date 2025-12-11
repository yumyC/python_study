"""
基础模型类

定义所有数据模型的公共字段和方法
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class BaseModel(Base):
    """
    基础模型类
    
    包含所有数据表的公共字段：
    - id: 主键，使用 UUID
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __abstract__ = True  # 标记为抽象类，不会创建对应的数据表
    
    # 主键，使用 UUID 类型
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment="主键ID"
    )
    
    # 创建时间，自动设置为当前时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    # 更新时间，每次更新时自动更新
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    def to_dict(self):
        """
        将模型实例转换为字典
        
        Returns:
            dict: 包含所有字段的字典
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        """
        返回模型的字符串表示
        """
        return f"<{self.__class__.__name__}(id={self.id})>"