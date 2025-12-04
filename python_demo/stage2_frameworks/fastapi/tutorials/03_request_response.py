"""
FastAPI 请求和响应示例

演示如何使用 Pydantic 模型处理请求体和响应，包括数据验证、
状态码处理和响应模型定义。

运行方式:
    uvicorn 03_request_response:app --reload

访问文档:
    http://127.0.0.1:8000/docs
"""

from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field, EmailStr, validator

app = FastAPI(title="请求响应示例 API", version="1.0.0")


# ============ 1. 定义 Pydantic 模型 ============

class User(BaseModel):
    """用户模型"""
    id: Optional[int] = None
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名，3-50 个字符"
    )
    email: EmailStr = Field(..., description="用户邮箱")
    full_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄，0-150")
    is_active: bool = Field(True, description="账户是否激活")
    created_at: Optional[datetime] = None
    
    # 自定义验证器
    @validator('username')
    def username_alphanumeric(cls, v):
        """验证用户名只包含字母数字和下划线"""
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "age": 30,
                "is_active": True
            }
        }


class UserCreate(BaseModel):
    """创建用户的请求模型（不包含 id 和 created_at）"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    password: str = Field(..., min_length=8, description="密码，至少 8 个字符")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "jane_doe",
                "email": "jane@example.com",
                "full_name": "Jane Doe",
                "age": 25,
                "password": "securepassword123"
            }
        }


class UserUpdate(BaseModel):
    """更新用户的请求模型（所有字段都是可选的）"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """用户响应模型（不包含敏感信息）"""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    age: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # 允许从 ORM 模型创建


class Message(BaseModel):
    """通用消息响应"""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: str
    status_code: int


# 模拟数据库
fake_users_db: List[User] = []
next_user_id = 1


# ============ 2. POST 请求 - 创建资源 ============

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新用户",
    description="创建一个新用户账户",
    tags=["用户管理"]
)
def create_user(user: UserCreate):
    """
    创建新用户
    
    - **username**: 用户名（必需，3-50 字符）
    - **email**: 邮箱地址（必需）
    - **full_name**: 全名（可选）
    - **age**: 年龄（可选，0-150）
    - **password**: 密码（必需，至少 8 字符）
    """
    global next_user_id
    
    # 检查用户名是否已存在
    if any(u.username == user.username for u in fake_users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"用户名 '{user.username}' 已存在"
        )
    
    # 检查邮箱是否已存在
    if any(u.email == user.email for u in fake_users_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"邮箱 '{user.email}' 已被使用"
        )
    
    # 创建新用户（实际应用中密码需要加密）
    new_user = User(
        id=next_user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        age=user.age,
        is_active=True,
        created_at=datetime.now()
    )
    
    fake_users_db.append(new_user)
    next_user_id += 1
    
    return new_user


# ============ 3. GET 请求 - 读取资源 ============

@app.get(
    "/users",
    response_model=List[UserResponse],
    summary="获取用户列表",
    tags=["用户管理"]
)
def get_users(
    skip: int = 0,
    limit: int = 10,
    active_only: bool = False
):
    """
    获取用户列表
    
    支持分页和过滤
    """
    users = fake_users_db
    
    # 过滤激活用户
    if active_only:
        users = [u for u in users if u.is_active]
    
    # 分页
    return users[skip:skip + limit]


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="获取单个用户",
    tags=["用户管理"],
    responses={
        200: {"description": "成功返回用户信息"},
        404: {"description": "用户不存在", "model": ErrorResponse}
    }
)
def get_user(user_id: int):
    """
    通过 ID 获取用户信息
    """
    user = next((u for u in fake_users_db if u.id == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    return user


# ============ 4. PUT 请求 - 更新资源 ============

@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="更新用户信息",
    tags=["用户管理"]
)
def update_user(user_id: int, user_update: UserUpdate):
    """
    更新用户信息
    
    只更新提供的字段，未提供的字段保持不变
    """
    user = next((u for u in fake_users_db if u.id == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    # 更新字段（只更新提供的字段）
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 检查用户名冲突
    if 'username' in update_data:
        if any(u.username == update_data['username'] and u.id != user_id 
               for u in fake_users_db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"用户名 '{update_data['username']}' 已存在"
            )
    
    # 检查邮箱冲突
    if 'email' in update_data:
        if any(u.email == update_data['email'] and u.id != user_id 
               for u in fake_users_db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"邮箱 '{update_data['email']}' 已被使用"
            )
    
    # 应用更新
    for field, value in update_data.items():
        setattr(user, field, value)
    
    return user


# ============ 5. DELETE 请求 - 删除资源 ============

@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    tags=["用户管理"]
)
def delete_user(user_id: int):
    """
    删除用户
    
    返回 204 No Content 状态码
    """
    global fake_users_db
    
    user = next((u for u in fake_users_db if u.id == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    fake_users_db = [u for u in fake_users_db if u.id != user_id]
    
    # 204 响应不应该有响应体
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============ 6. PATCH 请求 - 部分更新 ============

@app.patch(
    "/users/{user_id}/activate",
    response_model=UserResponse,
    summary="激活/停用用户",
    tags=["用户管理"]
)
def toggle_user_activation(user_id: int, activate: bool):
    """
    激活或停用用户账户
    """
    user = next((u for u in fake_users_db if u.id == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    user.is_active = activate
    
    return user


# ============ 7. 自定义响应 ============

@app.get(
    "/users/{user_id}/export",
    summary="导出用户数据",
    tags=["用户管理"]
)
def export_user(user_id: int):
    """
    导出用户数据为 JSON
    
    演示自定义响应头
    """
    user = next((u for u in fake_users_db if u.id == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 ID {user_id} 不存在"
        )
    
    # 创建响应并添加自定义头
    response = Response(
        content=user.model_dump_json(),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=user_{user_id}.json",
            "X-Custom-Header": "CustomValue"
        }
    )
    
    return response


# ============ 8. 批量操作 ============

class BulkUserCreate(BaseModel):
    """批量创建用户请求"""
    users: List[UserCreate]


class BulkCreateResponse(BaseModel):
    """批量创建响应"""
    created: int
    failed: int
    users: List[UserResponse]
    errors: List[str]


@app.post(
    "/users/bulk",
    response_model=BulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="批量创建用户",
    tags=["用户管理"]
)
def bulk_create_users(bulk_request: BulkUserCreate):
    """
    批量创建多个用户
    
    返回创建成功和失败的统计信息
    """
    global next_user_id
    
    created_users = []
    errors = []
    
    for user_data in bulk_request.users:
        try:
            # 检查重复
            if any(u.username == user_data.username for u in fake_users_db):
                errors.append(f"用户名 '{user_data.username}' 已存在")
                continue
            
            if any(u.email == user_data.email for u in fake_users_db):
                errors.append(f"邮箱 '{user_data.email}' 已被使用")
                continue
            
            # 创建用户
            new_user = User(
                id=next_user_id,
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                age=user_data.age,
                is_active=True,
                created_at=datetime.now()
            )
            
            fake_users_db.append(new_user)
            created_users.append(new_user)
            next_user_id += 1
            
        except Exception as e:
            errors.append(f"创建用户失败: {str(e)}")
    
    return BulkCreateResponse(
        created=len(created_users),
        failed=len(errors),
        users=created_users,
        errors=errors
    )


"""
学习要点:

1. Pydantic 模型
   - 使用 BaseModel 定义数据模型
   - Field() 添加验证规则和元数据
   - 自动进行数据验证和类型转换
   - 支持自定义验证器 (@validator)

2. 请求体 (Request Body)
   - POST/PUT/PATCH 请求使用请求体传递数据
   - 自动解析 JSON 并验证
   - 验证失败返回 422 错误

3. 响应模型 (Response Model)
   - response_model 参数指定响应模型
   - 自动过滤不在模型中的字段
   - 确保响应数据的一致性

4. HTTP 状态码
   - 200: 成功 (默认)
   - 201: 创建成功
   - 204: 成功但无内容
   - 400: 客户端错误
   - 404: 资源不存在
   - 422: 验证错误

5. 异常处理
   - HTTPException 抛出 HTTP 错误
   - 自动返回正确的状态码和错误信息
   - 可以自定义错误响应模型

6. 不同的请求方法
   - POST: 创建资源
   - GET: 读取资源
   - PUT: 完整更新资源
   - PATCH: 部分更新资源
   - DELETE: 删除资源

7. 数据验证
   - 自动验证数据类型
   - 字段约束（长度、范围等）
   - 邮箱格式验证
   - 自定义验证逻辑

8. API 文档
   - summary: 端点简短描述
   - description: 详细描述
   - tags: 分组标签
   - responses: 可能的响应定义

实践练习:
1. 创建一个博客文章的 CRUD API
2. 添加文章分类和标签功能
3. 实现文章搜索和过滤
4. 添加评论功能
5. 实现文章点赞功能
6. 添加更多的数据验证规则
"""
