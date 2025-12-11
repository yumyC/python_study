"""
菜单模型

定义系统菜单的数据模型，支持树形结构
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class Menu(BaseModel):
    """
    菜单模型
    
    支持树形结构的菜单管理：
    - 菜单名称和路径
    - 菜单图标和组件
    - 父子关系
    - 排序和可见性
    """
    __tablename__ = "menus"
    
    # 菜单名称
    name = Column(
        String(100), 
        nullable=False,
        comment="菜单名称"
    )
    
    # 菜单路径，用于前端路由
    path = Column(
        String(200), 
        nullable=False,
        comment="菜单路径"
    )
    
    # 菜单图标，通常是图标类名
    icon = Column(
        String(100),
        nullable=True,
        comment="菜单图标"
    )
    
    # 前端组件路径
    component = Column(
        String(200),
        nullable=True,
        comment="前端组件路径"
    )
    
    # 父菜单ID，自关联外键
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.id", ondelete="CASCADE"),
        nullable=True,
        comment="父菜单ID"
    )
    
    # 排序字段，数字越小越靠前
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序顺序"
    )
    
    # 是否可见
    is_visible = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否可见"
    )
    
    # 关系定义
    # 父菜单（多对一）
    parent = relationship(
        "Menu",
        remote_side="Menu.id",
        back_populates="children",
        lazy="select"
    )
    
    # 子菜单（一对多）
    children = relationship(
        "Menu",
        back_populates="parent",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Menu.sort_order"  # 按排序字段排序
    )
    
    # 菜单权限关联（一对多）
    role_permissions = relationship(
        "RoleMenuPermission",
        back_populates="menu",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Menu(name={self.name}, path={self.path})>"
    
    def get_breadcrumb(self):
        """
        获取菜单面包屑路径
        
        Returns:
            list: 从根菜单到当前菜单的路径列表
        """
        breadcrumb = [{"name": self.name, "path": self.path}]
        current = self.parent
        
        while current:
            breadcrumb.insert(0, {"name": current.name, "path": current.path})
            current = current.parent
            
        return breadcrumb
    
    def get_all_children(self):
        """
        获取所有子菜单（递归）
        
        Returns:
            list: 包含所有子菜单的列表
        """
        all_children = []
        
        for child in self.children.order_by(Menu.sort_order):
            all_children.append(child)
            all_children.extend(child.get_all_children())
            
        return all_children
    
    def to_tree_dict(self, include_children=True):
        """
        将菜单转换为树形字典结构
        
        Args:
            include_children: 是否包含子菜单
            
        Returns:
            dict: 树形结构的字典
        """
        result = {
            "id": str(self.id),
            "name": self.name,
            "path": self.path,
            "icon": self.icon,
            "component": self.component,
            "sort_order": self.sort_order,
            "is_visible": self.is_visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_children:
            result["children"] = [
                child.to_tree_dict(include_children=True)
                for child in self.children.order_by(Menu.sort_order)
                if child.is_visible
            ]
            
        return result
    
    def get_level(self):
        """
        获取菜单层级深度
        
        Returns:
            int: 菜单层级，根菜单为 0
        """
        level = 0
        current = self.parent
        
        while current:
            level += 1
            current = current.parent
            
        return level