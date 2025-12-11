"""
员工模型

定义员工相关的数据模型
"""

from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import BaseModel


class EmployeeStatus(enum.Enum):
    """员工状态枚举"""
    ACTIVE = "active"      # 在职
    INACTIVE = "inactive"  # 离职


class Employee(BaseModel):
    """
    员工模型
    
    存储员工的基本信息，包括：
    - 用户名和邮箱（用于登录）
    - 密码哈希值
    - 姓名
    - 岗位和角色关联
    - 员工状态
    """
    __tablename__ = "employees"
    
    # 用户名，用于登录，必须唯一
    username = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="用户名"
    )
    
    # 邮箱地址，必须唯一
    email = Column(
        String(100), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="邮箱地址"
    )
    
    # 密码哈希值，不存储明文密码
    password_hash = Column(
        String(255), 
        nullable=False,
        comment="密码哈希值"
    )
    
    # 员工姓名
    full_name = Column(
        String(100), 
        nullable=False,
        comment="员工姓名"
    )
    
    # 岗位ID，外键关联到 positions 表
    position_id = Column(
        UUID(as_uuid=True),
        ForeignKey("positions.id", ondelete="SET NULL"),
        nullable=True,
        comment="岗位ID"
    )
    
    # 角色ID，外键关联到 roles 表
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        comment="角色ID"
    )
    
    # 员工状态
    status = Column(
        Enum(EmployeeStatus),
        default=EmployeeStatus.ACTIVE,
        nullable=False,
        comment="员工状态"
    )
    
    # 关系定义
    # 关联到岗位表
    position = relationship(
        "Position", 
        back_populates="employees",
        lazy="select"  # 延迟加载
    )
    
    # 关联到角色表
    role = relationship(
        "Role", 
        back_populates="employees",
        lazy="select"
    )
    
    # 关联到工作日志表（一对多）
    work_logs = relationship(
        "WorkLog", 
        back_populates="employee",
        lazy="dynamic",  # 动态加载，返回查询对象
        cascade="all, delete-orphan"  # 级联删除
    )
    
    def __repr__(self):
        return f"<Employee(username={self.username}, full_name={self.full_name})>"
    
    def is_active(self):
        """检查员工是否在职"""
        return self.status == EmployeeStatus.ACTIVE