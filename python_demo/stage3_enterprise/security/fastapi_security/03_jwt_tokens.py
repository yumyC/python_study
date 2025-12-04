"""
FastAPI JWT 令牌认证示例

本示例演示如何使用 JWT (JSON Web Token) 实现无状态认证，包括：
- JWT 令牌生成
- Access Token 和 Refresh Token
- 令牌验证和解析
- 令牌过期处理

依赖安装：
    pip install python-jose[cryptography] passlib[bcrypt]

运行方式：
    uvicorn 03_jwt_tokens:app --reload

访问文档：
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

app = FastAPI(title="FastAPI JWT 认证示例")

# ==================== 配置 ====================

# JWT 配置（生产环境应从环境变量读取）
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Access Token 15 分钟过期
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Refresh Token 7 天过期

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ==================== 数据模型 ====================

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None
    token_type: Optional[str] = None  # "access" 或 "refresh"


class User(BaseModel):
    """用户模型"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False


class UserInDB(User):
    """数据库中的用户模型"""
    hashed_password: str


class UserRegister(BaseModel):
    """用户注册模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


# 模拟数据库
fake_users_db = {}

# 存储已撤销的令牌（生产环境应使用 Redis）
revoked_tokens = set()


# ==================== 密码处理 ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


# ==================== 用户操作 ====================

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


# ==================== JWT 令牌操作 ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 Access Token
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        str: JWT 令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "token_type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建 Refresh Token
    
    Args:
        data: 要编码的数据
    
    Returns:
        str: JWT 令牌
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "token_type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    解码并验证令牌
    
    Args:
        token: JWT 令牌
    
    Returns:
        TokenData: 令牌数据
    
    Raises:
        HTTPException: 令牌无效时抛出异常
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("token_type")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username, token_type=token_type)
        return token_data
    
    except JWTError:
        raise credentials_exception


# ==================== 依赖函数 ====================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    获取当前用户（从 Access Token）
    
    Args:
        token: JWT 令牌
    
    Returns:
        User: 当前用户
    
    Raises:
        HTTPException: 令牌无效或用户不存在时抛出异常
    """
    # 检查令牌是否已被撤销
    if token in revoked_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已被撤销",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = decode_token(token)
    
    # 验证令牌类型
    if token_data.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌类型",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(**user.dict())


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
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

@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """
    用户注册
    
    Args:
        user: 用户注册信息
    
    Returns:
        User: 注册成功的用户信息
    """
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        disabled=False
    )
    
    fake_users_db[user.username] = user_in_db.dict()
    
    return User(**user_in_db.dict())


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录，获取 JWT 令牌
    
    Args:
        form_data: OAuth2 密码表单数据
    
    Returns:
        Token: Access Token 和 Refresh Token
    
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
    
    # 创建 Access Token
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    # 创建 Refresh Token
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@app.post("/token/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    使用 Refresh Token 刷新 Access Token
    
    Args:
        refresh_token: Refresh Token
    
    Returns:
        Token: 新的 Access Token 和 Refresh Token
    
    Raises:
        HTTPException: Refresh Token 无效时抛出异常
    """
    # 检查令牌是否已被撤销
    if refresh_token in revoked_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已被撤销",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = decode_token(refresh_token)
    
    # 验证令牌类型
    if token_data.token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌类型",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建新的令牌
    new_access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    
    # 撤销旧的 Refresh Token
    revoked_tokens.add(refresh_token)
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@app.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_active_user)
):
    """
    用户登出，撤销令牌
    
    Args:
        token: 当前 Access Token
        current_user: 当前用户
    
    Returns:
        dict: 登出成功消息
    """
    # 将令牌加入撤销列表
    revoked_tokens.add(token)
    
    return {"message": "登出成功"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
    
    Returns:
        User: 用户信息
    """
    return current_user


@app.get("/items")
async def read_items(current_user: User = Depends(get_current_active_user)):
    """
    获取项目列表（需要认证）
    
    Args:
        current_user: 当前用户
    
    Returns:
        dict: 项目列表
    """
    return {
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
        ],
        "user": current_user.username
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "FastAPI JWT 认证示例",
        "endpoints": {
            "register": "POST /register",
            "login": "POST /token",
            "refresh": "POST /token/refresh",
            "logout": "POST /logout",
            "me": "GET /users/me (需要认证)",
            "items": "GET /items (需要认证)"
        },
        "test_user": {
            "username": "testuser",
            "password": "testpass123"
        }
    }


# ==================== 初始化测试数据 ====================

def init_test_data():
    """初始化测试数据"""
    test_user = UserInDB(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="测试用户",
        disabled=False
    )
    fake_users_db["testuser"] = test_user.dict()


# 启动时初始化数据
init_test_data()


if __name__ == "__main__":
    print("JWT 认证示例")
    print("\n测试用户：")
    print("  用户名: testuser")
    print("  密码: testpass123")
    print("\n使用流程：")
    print("  1. POST /token 登录获取令牌")
    print("  2. 使用 Access Token 访问受保护的端点")
    print("  3. Access Token 过期后使用 Refresh Token 刷新")
    print("  4. POST /logout 登出撤销令牌")
    print("\n运行命令: uvicorn 03_jwt_tokens:app --reload")
    print("访问文档: http://127.0.0.1:8000/docs")
