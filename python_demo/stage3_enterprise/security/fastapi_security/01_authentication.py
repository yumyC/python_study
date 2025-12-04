"""
FastAPI 基础认证示例

本示例演示如何实现基础的用户认证系统，包括：
- 用户注册
- 密码哈希存储
- 用户登录
- 密码验证

运行方式：
    uvicorn 01_authentication:app --reload

访问文档：
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from typing import Optional
import secrets

app = FastAPI(title="FastAPI 基础认证示例")

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Basic 认证
security = HTTPBasic()

# 模拟数据库（实际项目中应使用真实数据库）
fake_users_db = {}


# ==================== 数据模型 ====================

class UserRegister(BaseModel):
    """用户注册模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码")
    full_name: Optional[str] = Field(None, description="全名")


class UserInDB(BaseModel):
    """数据库中的用户模型"""
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    disabled: bool = False


class UserResponse(BaseModel):
    """用户响应模型（不包含密码）"""
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False


# ==================== 密码处理函数 ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
    
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
    
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


# ==================== 用户操作函数 ====================

def get_user(username: str) -> Optional[UserInDB]:
    """
    从数据库获取用户
    
    Args:
        username: 用户名
    
    Returns:
        Optional[UserInDB]: 用户对象，不存在则返回 None
    """
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    认证用户
    
    Args:
        username: 用户名
        password: 密码
    
    Returns:
        Optional[UserInDB]: 认证成功返回用户对象，失败返回 None
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ==================== 依赖函数 ====================

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    """
    获取当前认证用户（使用 HTTP Basic 认证）
    
    Args:
        credentials: HTTP Basic 认证凭据
    
    Returns:
        UserInDB: 当前用户对象
    
    Raises:
        HTTPException: 认证失败时抛出 401 错误
    """
    user = authenticate_user(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    return user


def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
    
    Returns:
        UserInDB: 活跃用户对象
    
    Raises:
        HTTPException: 用户被禁用时抛出 400 错误
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


# ==================== API 端点 ====================

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """
    用户注册
    
    Args:
        user: 用户注册信息
    
    Returns:
        UserResponse: 注册成功的用户信息
    
    Raises:
        HTTPException: 用户名已存在时抛出 400 错误
    """
    # 检查用户名是否已存在
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        disabled=False
    )
    
    # 保存到"数据库"
    fake_users_db[user.username] = user_in_db.dict()
    
    return UserResponse(**user_in_db.dict())


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    """
    获取当前用户信息
    
    需要 HTTP Basic 认证
    
    Args:
        current_user: 当前认证用户
    
    Returns:
        UserResponse: 当前用户信息
    """
    return UserResponse(**current_user.dict())


@app.get("/users/{username}", response_model=UserResponse)
async def read_user(
    username: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    获取指定用户信息（需要认证）
    
    Args:
        username: 要查询的用户名
        current_user: 当前认证用户
    
    Returns:
        UserResponse: 用户信息
    
    Raises:
        HTTPException: 用户不存在时抛出 404 错误
    """
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserResponse(**user.dict())


@app.get("/")
async def root():
    """根路径（无需认证）"""
    return {
        "message": "欢迎使用 FastAPI 认证系统",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /register",
            "me": "GET /users/me (需要认证)",
            "user": "GET /users/{username} (需要认证)"
        }
    }


# ==================== 测试数据 ====================

# 创建一个测试用户
if __name__ == "__main__":
    # 添加测试用户
    test_user = UserInDB(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="测试用户",
        disabled=False
    )
    fake_users_db["testuser"] = test_user.dict()
    
    print("测试用户已创建：")
    print("  用户名: testuser")
    print("  密码: testpass123")
    print("\n运行命令: uvicorn 01_authentication:app --reload")
    print("访问文档: http://127.0.0.1:8000/docs")
