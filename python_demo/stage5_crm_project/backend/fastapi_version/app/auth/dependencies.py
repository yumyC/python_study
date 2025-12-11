"""
认证依赖项

提供 FastAPI 依赖注入的认证和授权函数
"""

from typing import Optional, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from .auth_service import AuthService


# HTTP Bearer token 安全方案
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Employee:
    """
    获取当前认证用户的依赖项
    
    Args:
        credentials: HTTP Bearer 凭据
        db: 数据库会话
        
    Returns:
        当前用户的 Employee 对象
        
    Raises:
        HTTPException: 认证失败时抛出 401 异常
    """
    auth_service = AuthService(db)
    return auth_service.get_current_user(credentials.credentials)


def get_current_active_user(
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    """
    获取当前活跃用户的依赖项
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前活跃用户的 Employee 对象
        
    Raises:
        HTTPException: 用户未激活时抛出 400 异常
    """
    if not current_user.is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user


def require_permission(menu_path: str, permission: str) -> Callable:
    """
    权限检查装饰器工厂
    
    Args:
        menu_path: 菜单路径
        permission: 所需权限 ('view', 'create', 'update', 'delete')
        
    Returns:
        权限检查依赖项函数
    """
    def permission_checker(
        current_user: Employee = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> Employee:
        """
        权限检查依赖项
        
        Args:
            current_user: 当前用户
            db: 数据库会话
            
        Returns:
            通过权限检查的用户
            
        Raises:
            HTTPException: 权限不足时抛出 403 异常
        """
        auth_service = AuthService(db)
        
        # 检查用户权限
        if not auth_service.check_permission(current_user, menu_path, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {menu_path} 的 {permission} 权限"
            )
        
        return current_user
    
    return permission_checker


def require_role(role_code: str) -> Callable:
    """
    角色检查装饰器工厂
    
    Args:
        role_code: 所需角色代码
        
    Returns:
        角色检查依赖项函数
    """
    def role_checker(
        current_user: Employee = Depends(get_current_active_user)
    ) -> Employee:
        """
        角色检查依赖项
        
        Args:
            current_user: 当前用户
            
        Returns:
            通过角色检查的用户
            
        Raises:
            HTTPException: 角色不匹配时抛出 403 异常
        """
        if not current_user.role or current_user.role.code != role_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {role_code} 角色"
            )
        
        return current_user
    
    return role_checker


def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[Employee]:
    """
    可选认证依赖项
    
    如果提供了 token 则验证，否则返回 None
    
    Args:
        credentials: 可选的 HTTP Bearer 凭据
        db: 数据库会话
        
    Returns:
        认证用户或 None
    """
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        return auth_service.get_current_user(credentials.credentials)
    except HTTPException:
        return None


class PermissionChecker:
    """
    权限检查器类
    
    提供更灵活的权限检查方式
    """
    
    def __init__(self, db: Session, current_user: Employee):
        self.db = db
        self.current_user = current_user
        self.auth_service = AuthService(db)
    
    def has_permission(self, menu_path: str, permission: str) -> bool:
        """
        检查是否有指定权限
        
        Args:
            menu_path: 菜单路径
            permission: 权限类型
            
        Returns:
            是否有权限
        """
        return self.auth_service.check_permission(self.current_user, menu_path, permission)
    
    def has_role(self, role_code: str) -> bool:
        """
        检查是否有指定角色
        
        Args:
            role_code: 角色代码
            
        Returns:
            是否有角色
        """
        return self.current_user.role and self.current_user.role.code == role_code
    
    def has_any_permission(self, menu_path: str, permissions: list) -> bool:
        """
        检查是否有任意一个权限
        
        Args:
            menu_path: 菜单路径
            permissions: 权限列表
            
        Returns:
            是否有任意权限
        """
        return any(
            self.has_permission(menu_path, perm) 
            for perm in permissions
        )
    
    def has_all_permissions(self, menu_path: str, permissions: list) -> bool:
        """
        检查是否有所有权限
        
        Args:
            menu_path: 菜单路径
            permissions: 权限列表
            
        Returns:
            是否有所有权限
        """
        return all(
            self.has_permission(menu_path, perm) 
            for perm in permissions
        )
    
    def require_permission(self, menu_path: str, permission: str) -> None:
        """
        要求指定权限，没有权限时抛出异常
        
        Args:
            menu_path: 菜单路径
            permission: 权限类型
            
        Raises:
            HTTPException: 权限不足时抛出异常
        """
        if not self.has_permission(menu_path, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {menu_path} 的 {permission} 权限"
            )
    
    def require_role(self, role_code: str) -> None:
        """
        要求指定角色，没有角色时抛出异常
        
        Args:
            role_code: 角色代码
            
        Raises:
            HTTPException: 角色不匹配时抛出异常
        """
        if not self.has_role(role_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {role_code} 角色"
            )


def get_permission_checker(
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> PermissionChecker:
    """
    获取权限检查器的依赖项
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        权限检查器实例
    """
    return PermissionChecker(db, current_user)