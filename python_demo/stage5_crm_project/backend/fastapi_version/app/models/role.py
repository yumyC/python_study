"""
角色模型

定义系统角色的数据模型
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Role(BaseModel):
    """
    角色模型
    
    定义系统中的角色：
    - 角色名称和编码
    - 角色描述
    - 与员工和权限的关联
    """
    __tablename__ = "roles"
    
    # 角色名称
    name = Column(
        String(100), 
        nullable=False,
        comment="角色名称"
    )
    
    # 角色编码，用于系统内部标识，必须唯一
    code = Column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="角色编码"
    )
    
    # 角色描述
    description = Column(
        Text,
        nullable=True,
        comment="角色描述"
    )
    
    # 关系定义
    # 该角色的员工（一对多）
    employees = relationship(
        "Employee",
        back_populates="role",
        lazy="dynamic"
    )
    
    # 角色菜单权限（一对多）
    menu_permissions = relationship(
        "RoleMenuPermission",
        back_populates="role",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Role(code={self.code}, name={self.name})>"
    
    def get_permissions(self):
        """
        获取角色的所有权限
        
        Returns:
            dict: 以菜单ID为键，权限列表为值的字典
        """
        permissions = {}
        
        for permission in self.menu_permissions:
            permissions[str(permission.menu_id)] = permission.permissions
            
        return permissions
    
    def has_permission(self, menu_id, permission_type):
        """
        检查角色是否有特定菜单的特定权限
        
        Args:
            menu_id: 菜单ID
            permission_type: 权限类型 ('view', 'create', 'update', 'delete')
            
        Returns:
            bool: 如果有权限返回 True
        """
        permission = self.menu_permissions.filter_by(menu_id=menu_id).first()
        
        if not permission:
            return False
            
        return permission_type in permission.permissions
    
    def get_accessible_menus(self):
        """
        获取角色可访问的所有菜单
        
        Returns:
            list: 可访问的菜单列表
        """
        from .menu import Menu
        
        menu_ids = [
            permission.menu_id 
            for permission in self.menu_permissions
            if 'view' in permission.permissions
        ]
        
        return Menu.query.filter(Menu.id.in_(menu_ids)).all()
    
    def add_menu_permission(self, menu_id, permissions):
        """
        为角色添加菜单权限
        
        Args:
            menu_id: 菜单ID
            permissions: 权限列表
        """
        from .role_menu_permission import RoleMenuPermission
        
        # 检查是否已存在权限记录
        existing = self.menu_permissions.filter_by(menu_id=menu_id).first()
        
        if existing:
            existing.permissions = permissions
        else:
            new_permission = RoleMenuPermission(
                role_id=self.id,
                menu_id=menu_id,
                permissions=permissions
            )
            self.menu_permissions.append(new_permission)
    
    def remove_menu_permission(self, menu_id):
        """
        移除角色的菜单权限
        
        Args:
            menu_id: 菜单ID
        """
        permission = self.menu_permissions.filter_by(menu_id=menu_id).first()
        
        if permission:
            self.menu_permissions.remove(permission)