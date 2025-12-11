"""
岗位模型

定义岗位相关的数据模型，支持层级结构
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class Position(BaseModel):
    """
    岗位模型
    
    支持层级结构的岗位管理：
    - 岗位名称和编码
    - 岗位描述
    - 岗位级别
    - 上级岗位关联（自关联）
    """
    __tablename__ = "positions"
    
    # 岗位名称
    name = Column(
        String(100), 
        nullable=False,
        comment="岗位名称"
    )
    
    # 岗位编码，用于系统内部标识，必须唯一
    code = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="岗位编码"
    )
    
    # 岗位描述
    description = Column(
        Text,
        nullable=True,
        comment="岗位描述"
    )
    
    # 岗位级别，数字越小级别越高
    level = Column(
        Integer,
        nullable=False,
        default=1,
        comment="岗位级别"
    )
    
    # 上级岗位ID，自关联外键
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("positions.id", ondelete="SET NULL"),
        nullable=True,
        comment="上级岗位ID"
    )
    
    # 关系定义
    # 上级岗位（多对一）
    parent = relationship(
        "Position",
        remote_side="Position.id",  # 指定远程端的主键
        back_populates="children",
        lazy="select"
    )
    
    # 下级岗位（一对多）
    children = relationship(
        "Position",
        back_populates="parent",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    # 该岗位的员工（一对多）
    employees = relationship(
        "Employee",
        back_populates="position",
        lazy="dynamic"
    )
    
    def __repr__(self):
        return f"<Position(code={self.code}, name={self.name}, level={self.level})>"
    
    def get_full_path(self):
        """
        获取岗位的完整路径
        
        Returns:
            str: 从根岗位到当前岗位的完整路径，用 " > " 分隔
        """
        path = [self.name]
        current = self.parent
        
        while current:
            path.insert(0, current.name)
            current = current.parent
            
        return " > ".join(path)
    
    def get_all_children(self):
        """
        获取所有下级岗位（递归）
        
        Returns:
            list: 包含所有下级岗位的列表
        """
        all_children = []
        
        for child in self.children:
            all_children.append(child)
            all_children.extend(child.get_all_children())
            
        return all_children
    
    def is_ancestor_of(self, other_position):
        """
        检查当前岗位是否是另一个岗位的上级
        
        Args:
            other_position: 要检查的岗位
            
        Returns:
            bool: 如果是上级岗位返回 True
        """
        current = other_position.parent
        
        while current:
            if current.id == self.id:
                return True
            current = current.parent
            
        return False