"""
角色菜单权限模型

定义角色与菜单权限的关联关系
"""

from sqlalchemy import Column, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class RoleMenuPermission(BaseModel):
    """
    角色菜单权限模型
    
    定义角色对特定菜单的权限：
    - 角色ID和菜单ID的关联
    - 权限类型列表（view, create, update, delete）
    """
    __tablename__ = "role_menu_permissions"
    
    # 角色ID，外键关联到 roles 表
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        comment="角色ID"
    )
    
    # 菜单ID，外键关联到 menus 表
    menu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.id", ondelete="CASCADE"),
        nullable=False,
        comment="菜单ID"
    )
    
    # 权限列表，使用 JSON 类型存储
    # 可能的权限类型：['view', 'create', 'update', 'delete']
    permissions = Column(
        JSON,
        nullable=False,
        default=list,
        comment="权限列表"
    )
    
    # 关系定义
    # 关联到角色表
    role = relationship(
        "Role",
        back_populates="menu_permissions",
        lazy="select"
    )
    
    # 关联到菜单表
    menu = relationship(
        "Menu",
        back_populates="role_permissions",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<RoleMenuPermission(role_id={self.role_id}, menu_id={self.menu_id}, permissions={self.permissions})>"
    
    def has_permission(self, permission_type):
        """
        检查是否有特定类型的权限
        
        Args:
            permission_type: 权限类型 ('view', 'create', 'update', 'delete')
            
        Returns:
            bool: 如果有权限返回 True
        """
        return permission_type in (self.permissions or [])
    
    def add_permission(self, permission_type):
        """
        添加权限
        
        Args:
            permission_type: 权限类型
        """
        if not self.permissions:
            self.permissions = []
            
        if permission_type not in self.permissions:
            self.permissions.append(permission_type)
    
    def remove_permission(self, permission_type):
        """
        移除权限
        
        Args:
            permission_type: 权限类型
        """
        if self.permissions and permission_type in self.permissions:
            self.permissions.remove(permission_type)
    
    def set_permissions(self, permission_list):
        """
        设置权限列表
        
        Args:
            permission_list: 权限类型列表
        """
        # 验证权限类型
        valid_permissions = {'view', 'create', 'update', 'delete'}
        filtered_permissions = [
            perm for perm in permission_list 
            if perm in valid_permissions
        ]
        
        self.permissions = filtered_permissions
    
    def get_permission_names(self):
        """
        获取权限的中文名称
        
        Returns:
            list: 权限的中文名称列表
        """
        permission_names = {
            'view': '查看',
            'create': '创建',
            'update': '更新',
            'delete': '删除'
        }
        
        return [
            permission_names.get(perm, perm)
            for perm in (self.permissions or [])
        ]
    
    @classmethod
    def get_all_permission_types(cls):
        """
        获取所有可用的权限类型
        
        Returns:
            list: 所有权限类型列表
        """
        return ['view', 'create', 'update', 'delete']
    
    @classmethod
    def get_permission_descriptions(cls):
        """
        获取权限类型的描述
        
        Returns:
            dict: 权限类型及其描述的字典
        """
        return {
            'view': '查看权限 - 可以查看菜单和数据',
            'create': '创建权限 - 可以创建新数据',
            'update': '更新权限 - 可以修改现有数据',
            'delete': '删除权限 - 可以删除数据'
        }