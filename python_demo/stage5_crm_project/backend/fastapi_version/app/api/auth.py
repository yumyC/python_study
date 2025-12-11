"""
认证相关的 API 路由

提供登录、刷新令牌、获取用户信息等接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.auth import (
    AuthService, 
    LoginRequest, 
    LoginResponse, 
    TokenRefreshRequest, 
    TokenRefreshResponse,
    UserInfo,
    get_current_user,
    get_current_active_user
)

# 创建认证路由器
router = APIRouter(
    prefix="/auth",
    tags=["认证"],
    responses={
        401: {"description": "认证失败"},
        403: {"description": "权限不足"}
    }
)


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    支持用户名或邮箱登录，返回用户信息和访问令牌
    
    Args:
        login_data: 登录请求数据
        db: 数据库会话
        
    Returns:
        登录响应，包含用户信息和令牌
        
    Raises:
        HTTPException: 登录失败时返回 401 错误
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data.username, login_data.password)


@router.post("/refresh", response_model=TokenRefreshResponse, summary="刷新访问令牌")
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌接口
    
    使用刷新令牌获取新的访问令牌
    
    Args:
        refresh_data: 刷新令牌请求数据
        db: 数据库会话
        
    Returns:
        新的令牌数据
        
    Raises:
        HTTPException: 刷新失败时返回 401 错误
    """
    auth_service = AuthService(db)
    tokens = auth_service.refresh_token(refresh_data.refresh_token)
    return TokenRefreshResponse(tokens=tokens)


@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息接口
    
    返回当前认证用户的详细信息，包括角色、岗位和权限
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        用户详细信息
    """
    auth_service = AuthService(db)
    return auth_service._build_user_info(current_user)


@router.get("/permissions", summary="获取当前用户权限")
async def get_current_user_permissions(
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户权限列表接口
    
    返回用户的所有权限和可访问的菜单
    
    Args:
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        用户权限和菜单信息
    """
    auth_service = AuthService(db)
    
    # 获取权限列表
    permissions = auth_service.get_user_permissions(current_user)
    
    # 获取菜单权限
    menu_permissions = auth_service.get_user_menu_permissions(current_user)
    
    return {
        "user_id": str(current_user.id),
        "username": current_user.username,
        "role": {
            "id": str(current_user.role.id) if current_user.role else None,
            "name": current_user.role.name if current_user.role else None,
            "code": current_user.role.code if current_user.role else None
        },
        "permissions": permissions,
        "menu_permissions": menu_permissions
    }


@router.post("/check-permission", summary="检查用户权限")
async def check_user_permission(
    menu_path: str,
    permission: str,
    current_user: Employee = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    检查用户权限接口
    
    检查当前用户是否有指定菜单的特定权限
    
    Args:
        menu_path: 菜单路径
        permission: 权限类型 ('view', 'create', 'update', 'delete')
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        权限检查结果
    """
    auth_service = AuthService(db)
    has_permission = auth_service.check_permission(current_user, menu_path, permission)
    
    return {
        "user_id": str(current_user.id),
        "menu_path": menu_path,
        "permission": permission,
        "has_permission": has_permission
    }


@router.post("/logout", summary="用户登出")
async def logout(
    current_user: Employee = Depends(get_current_user)
):
    """
    用户登出接口
    
    注意：由于使用 JWT，实际的登出需要在客户端删除令牌
    这个接口主要用于记录登出日志或执行其他清理操作
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        登出成功消息
    """
    # 在实际应用中，这里可以：
    # 1. 记录登出日志
    # 2. 将令牌加入黑名单（需要额外的存储）
    # 3. 执行其他清理操作
    
    return {
        "message": "登出成功",
        "user_id": str(current_user.id),
        "username": current_user.username
    }


@router.get("/validate-token", summary="验证令牌")
async def validate_token(
    current_user: Employee = Depends(get_current_user)
):
    """
    验证令牌接口
    
    检查当前令牌是否有效
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        令牌验证结果
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "status": current_user.status.value
    }