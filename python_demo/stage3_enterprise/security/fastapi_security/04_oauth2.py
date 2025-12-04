"""
FastAPI OAuth2 集成示例

本示例演示如何实现 OAuth2 认证流程，包括：
- OAuth2 密码流程 (Password Flow)
- OAuth2 授权码流程 (Authorization Code Flow)
- 作用域 (Scopes) 权限控制
- 第三方登录集成思路

依赖安装：
    pip install python-jose[cryptography] passlib[bcrypt]

运行方式：
    uvicorn 04_oauth2:app --reload

访问文档：
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes
)
from pydantic import BaseModel, ValidationError
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os

app = FastAPI(title="FastAPI OAuth2 示例")

# ==================== 配置 ====================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 配置，支持作用域
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "me": "读取当前用户信息",
        "items:read": "读取项目",
        "items:write": "创建和修改项目",
        "items:delete": "删除项目",
        "admin": "管理员权限"
    }
)


# ==================== 数据模型 ====================

class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None
    scopes: List[str] = []


class User(BaseModel):
    """用户模型"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    scopes: List[str] = []


class UserInDB(User):
    """数据库中的用户模型"""
    hashed_password: str


class Item(BaseModel):
    """项目模型"""
    id: int
    name: str
    description: Optional[str] = None
    owner: str


# 模拟数据库
fake_users_db = {}
fake_items_db = {}


# ==================== 辅助函数 ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    """获取用户"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """认证用户"""
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 Access Token
    
    Args:
        data: 要编码的数据（包含 sub 和 scopes）
        expires_delta: 过期时间增量
    
    Returns:
        str: JWT 令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==================== 依赖函数 ====================

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户并验证作用域
    
    Args:
        security_scopes: 要求的安全作用域
        token: JWT 令牌
    
    Returns:
        User: 当前用户
    
    Raises:
        HTTPException: 认证失败或权限不足时抛出异常
    """
    # 构建认证错误信息
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # 解码令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # 获取令牌中的作用域
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # 获取用户
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    # 验证作用域权限
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return User(**user.dict())


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["me"])
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
    
    Returns:
        User: 活跃用户
    
    Raises:
        HTTPException: 用户被禁用时抛出异常
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


# ==================== API 端点 ====================

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 密码流程登录
    
    用户提供用户名、密码和请求的作用域，获取 Access Token
    
    Args:
        form_data: OAuth2 密码表单数据
    
    Returns:
        Token: Access Token
    
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证请求的作用域是否在用户允许的范围内
    requested_scopes = form_data.scopes
    user_scopes = user.scopes
    
    # 如果用户没有请求特定作用域，使用用户的所有作用域
    if not requested_scopes:
        granted_scopes = user_scopes
    else:
        # 只授予用户拥有的作用域
        granted_scopes = [scope for scope in requested_scopes if scope in user_scopes]
    
    # 创建 Access Token，包含授予的作用域
    access_token = create_access_token(
        data={"sub": user.username, "scopes": granted_scopes}
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息
    
    需要 'me' 作用域
    
    Args:
        current_user: 当前用户
    
    Returns:
        User: 用户信息
    """
    return current_user


@app.get("/users/me/items")
async def read_own_items(
    current_user: User = Security(get_current_user, scopes=["items:read"])
):
    """
    获取当前用户的项目列表
    
    需要 'items:read' 作用域
    
    Args:
        current_user: 当前用户
    
    Returns:
        dict: 用户的项目列表
    """
    user_items = [
        item for item in fake_items_db.values()
        if item["owner"] == current_user.username
    ]
    return {
        "items": user_items,
        "total": len(user_items)
    }


@app.get("/items")
async def read_all_items(
    current_user: User = Security(get_current_user, scopes=["items:read", "admin"])
):
    """
    获取所有项目列表
    
    需要 'items:read' 和 'admin' 作用域
    
    Args:
        current_user: 当前用户
    
    Returns:
        dict: 所有项目列表
    """
    return {
        "items": list(fake_items_db.values()),
        "total": len(fake_items_db)
    }


@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    item: Item,
    current_user: User = Security(get_current_user, scopes=["items:write"])
):
    """
    创建新项目
    
    需要 'items:write' 作用域
    
    Args:
        item: 项目信息
        current_user: 当前用户
    
    Returns:
        dict: 创建成功的项目
    """
    if item.id in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目 ID 已存在"
        )
    
    item.owner = current_user.username
    fake_items_db[item.id] = item.dict()
    
    return {
        "message": "项目创建成功",
        "item": item
    }


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    current_user: User = Security(get_current_user, scopes=["items:write"])
):
    """
    更新项目
    
    需要 'items:write' 作用域
    普通用户只能更新自己的项目，管理员可以更新所有项目
    
    Args:
        item_id: 项目 ID
        item: 更新的项目信息
        current_user: 当前用户
    
    Returns:
        dict: 更新后的项目
    """
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    existing_item = fake_items_db[item_id]
    
    # 检查权限：只有项目所有者或管理员可以更新
    if existing_item["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限更新此项目"
        )
    
    item.owner = existing_item["owner"]  # 保持原所有者
    fake_items_db[item_id] = item.dict()
    
    return {
        "message": "项目更新成功",
        "item": item
    }


@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Security(get_current_user, scopes=["items:delete"])
):
    """
    删除项目
    
    需要 'items:delete' 作用域
    
    Args:
        item_id: 项目 ID
        current_user: 当前用户
    
    Returns:
        dict: 删除成功消息
    """
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    existing_item = fake_items_db[item_id]
    
    # 检查权限：只有项目所有者或管理员可以删除
    if existing_item["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限删除此项目"
        )
    
    deleted_item = fake_items_db.pop(item_id)
    
    return {
        "message": "项目删除成功",
        "item": deleted_item
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "FastAPI OAuth2 示例",
        "scopes": {
            "me": "读取当前用户信息",
            "items:read": "读取项目",
            "items:write": "创建和修改项目",
            "items:delete": "删除项目",
            "admin": "管理员权限"
        },
        "test_users": {
            "admin": {
                "username": "admin",
                "password": "admin123",
                "scopes": ["me", "items:read", "items:write", "items:delete", "admin"]
            },
            "user": {
                "username": "user",
                "password": "user123",
                "scopes": ["me", "items:read", "items:write"]
            },
            "readonly": {
                "username": "readonly",
                "password": "readonly123",
                "scopes": ["me", "items:read"]
            }
        },
        "usage": "在 /docs 页面的 Authorize 按钮中选择需要的作用域进行登录"
    }


# ==================== 初始化测试数据 ====================

def init_test_data():
    """初始化测试数据"""
    # 创建测试用户
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "email": "admin@example.com",
            "full_name": "管理员",
            "scopes": ["me", "items:read", "items:write", "items:delete", "admin"]
        },
        {
            "username": "user",
            "password": "user123",
            "email": "user@example.com",
            "full_name": "普通用户",
            "scopes": ["me", "items:read", "items:write"]
        },
        {
            "username": "readonly",
            "password": "readonly123",
            "email": "readonly@example.com",
            "full_name": "只读用户",
            "scopes": ["me", "items:read"]
        }
    ]
    
    for user_data in test_users:
        password = user_data.pop("password")
        user = UserInDB(
            **user_data,
            hashed_password=get_password_hash(password),
            disabled=False
        )
        fake_users_db[user.username] = user.dict()
    
    # 创建测试项目
    test_items = [
        {"id": 1, "name": "项目 1", "description": "管理员的项目", "owner": "admin"},
        {"id": 2, "name": "项目 2", "description": "用户的项目", "owner": "user"},
    ]
    
    for item in test_items:
        fake_items_db[item["id"]] = item


# 启动时初始化数据
init_test_data()


if __name__ == "__main__":
    print("OAuth2 作用域示例")
    print("\n测试用户：")
    print("  admin / admin123 (所有权限)")
    print("  user / user123 (读写权限)")
    print("  readonly / readonly123 (只读权限)")
    print("\n使用说明：")
    print("  1. 访问 /docs 页面")
    print("  2. 点击 Authorize 按钮")
    print("  3. 选择需要的作用域（scopes）")
    print("  4. 输入用户名和密码登录")
    print("  5. 尝试访问不同的端点，体验作用域权限控制")
    print("\n运行命令: uvicorn 04_oauth2:app --reload")
    print("访问文档: http://127.0.0.1:8000/docs")
