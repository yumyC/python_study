"""
员工相关的 Pydantic 模式
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class EmployeeBase(BaseModel):
    """员工基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: str = Field(..., min_length=2, max_length=100, description="员工姓名")
    position_id: Optional[str] = Field(None, description="岗位ID")
    role_id: Optional[str] = Field(None, description="角色ID")


class EmployeeCreateRequest(EmployeeBase):
    """创建员工请求模式"""
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "zhangsan",
                "email": "zhangsan@example.com",
                "password": "password123",
                "full_name": "张三",
                "position_id": "uuid",
                "role_id": "uuid"
            }
        }


class EmployeeUpdateRequest(BaseModel):
    """更新员工请求模式"""
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="员工姓名")
    position_id: Optional[str] = Field(None, description="岗位ID")
    role_id: Optional[str] = Field(None, description="角色ID")
    status: Optional[str] = Field(None, regex="^(active|inactive)$", description="员工状态")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "full_name": "新姓名",
                "position_id": "new-uuid",
                "role_id": "new-uuid",
                "status": "active"
            }
        }


class EmployeeResponse(BaseModel):
    """员工响应模式"""
    id: str = Field(description="员工ID")
    username: str = Field(description="用户名")
    email: str = Field(description="邮箱地址")
    full_name: str = Field(description="员工姓名")
    status: str = Field(description="员工状态")
    position_name: Optional[str] = Field(None, description="岗位名称")
    role_name: Optional[str] = Field(None, description="角色名称")
    created_at: Optional[str] = Field(None, description="创建时间")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "uuid",
                "username": "zhangsan",
                "email": "zhangsan@example.com",
                "full_name": "张三",
                "status": "active",
                "position_name": "软件工程师",
                "role_name": "员工",
                "created_at": "2023-12-11T10:00:00Z"
            }
        }


class EmployeeListResponse(BaseModel):
    """员工列表响应模式"""
    id: str = Field(description="员工ID")
    username: str = Field(description="用户名")
    full_name: str = Field(description="员工姓名")
    email: str = Field(description="邮箱地址")
    status: str = Field(description="员工状态")
    position_name: Optional[str] = Field(None, description="岗位名称")
    role_name: Optional[str] = Field(None, description="角色名称")
    
    class Config:
        from_attributes = True