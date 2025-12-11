"""
认证相关的 Pydantic 模式定义
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    """登录请求模式"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "password123"
            }
        }


class TokenData(BaseModel):
    """Token 数据模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒数


class LoginResponse(BaseModel):
    """登录响应模式"""
    user: "UserInfo"
    tokens: TokenData
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "admin",
                    "email": "admin@example.com",
                    "full_name": "管理员",
                    "role": {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "name": "系统管理员",
                        "code": "admin"
                    },
                    "position": {
                        "id": "123e4567-e89b-12d3-a456-426614174002", 
                        "name": "技术总监",
                        "code": "tech_director"
                    },
                    "permissions": ["user:view", "user:create", "user:update", "user:delete"]
                },
                "tokens": {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600
                }
            }
        }


class TokenRefreshRequest(BaseModel):
    """刷新 Token 请求模式"""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """刷新 Token 响应模式"""
    tokens: TokenData


class RoleInfo(BaseModel):
    """角色信息模式"""
    id: str
    name: str
    code: str
    description: Optional[str] = None


class PositionInfo(BaseModel):
    """岗位信息模式"""
    id: str
    name: str
    code: str
    description: Optional[str] = None
    level: int


class UserInfo(BaseModel):
    """用户信息模式"""
    id: str
    username: str
    email: EmailStr
    full_name: str
    role: Optional[RoleInfo] = None
    position: Optional[PositionInfo] = None
    permissions: List[str] = []
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PermissionCheck(BaseModel):
    """权限检查模式"""
    menu_path: str
    required_permission: str  # 'view', 'create', 'update', 'delete'


class MenuPermission(BaseModel):
    """菜单权限模式"""
    menu_id: str
    menu_name: str
    menu_path: str
    permissions: List[str]  # ['view', 'create', 'update', 'delete']


# 更新前向引用
LoginResponse.model_rebuild()