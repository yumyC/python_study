"""
FastAPI 授权控制示例

本示例演示如何实现基于角色的访问控制 (RBAC)，包括：
- 角色定义
- 权限检查
- 装饰器实现
- 资源级别权限控制

运行方式：
    uvicorn 02_authorization:app --reload

访问文档：
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from typing import Optional, List
from enum import Enum

app = FastAPI(title="FastAPI 授权控制示例")

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Basic 认证
security = HTTPBasic()


# ==================== 角色和权限定义 ====================

class Role(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"          # 管理员：所有权限
    MANAGER = "manager"      # 经理：管理权限
    USER = "user"            # 普通用户：基础权限
    GUEST = "guest"          # 访客：只读权限


class Permission(str, Enum):
    """权限枚举"""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE_USERS = "manage_users"


# 角色权限映射
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
        Permission.DELETE,
        Permission.MANAGE_USERS
    ],
    Role.MANAGER: [
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
        Permission.MANAGE_USERS
    ],
    Role.USER: [
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE
    ],
    Role.GUEST: [
        Permission.READ
    ]
}


# ==================== 数据模型 ====================

class UserInDB(BaseModel):
    """数据库中的用户模型"""
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    role: Role = Role.USER
    disabled: bool = False


class UserResponse(BaseModel):
    """用户响应模型"""
    username: str
    full_name: Optional[str] = None
    role: Role
    permissions: List[Permission]


class Article(BaseModel):
    """文章模型"""
    id: int
    title: str
    content: str
    author: str


# 模拟数据库
fake_users_db = {}
fake_articles_db = {}


# ==================== 辅助函数 ====================

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str) -> Optional[UserInDB]:
    """获取用户"""
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """认证用户"""
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def has_permission(user: UserInDB, permission: Permission) -> bool:
    """
    检查用户是否有指定权限
    
    Args:
        user: 用户对象
        permission: 要检查的权限
    
    Returns:
        bool: 是否有权限
    """
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    return permission in user_permissions


def has_role(user: UserInDB, required_role: Role) -> bool:
    """
    检查用户是否有指定角色
    
    Args:
        user: 用户对象
        required_role: 要求的角色
    
    Returns:
        bool: 是否有该角色
    """
    # 角色层级：ADMIN > MANAGER > USER > GUEST
    role_hierarchy = {
        Role.ADMIN: 4,
        Role.MANAGER: 3,
        Role.USER: 2,
        Role.GUEST: 1
    }
    return role_hierarchy.get(user.role, 0) >= role_hierarchy.get(required_role, 0)


# ==================== 依赖函数 ====================

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    """获取当前认证用户"""
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


def require_permission(permission: Permission):
    """
    权限检查依赖工厂
    
    Args:
        permission: 要求的权限
    
    Returns:
        依赖函数
    """
    def permission_checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {permission.value} 权限"
            )
        return current_user
    
    return permission_checker


def require_role(role: Role):
    """
    角色检查依赖工厂
    
    Args:
        role: 要求的角色
    
    Returns:
        依赖函数
    """
    def role_checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if not has_role(current_user, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {role.value} 角色或更高权限"
            )
        return current_user
    
    return role_checker


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "FastAPI 授权控制示例",
        "roles": [role.value for role in Role],
        "test_users": {
            "admin": "admin123 (管理员)",
            "manager": "manager123 (经理)",
            "user": "user123 (普通用户)",
            "guest": "guest123 (访客)"
        }
    }


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """获取当前用户信息"""
    permissions = ROLE_PERMISSIONS.get(current_user.role, [])
    return UserResponse(
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        permissions=permissions
    )


@app.get("/articles")
async def list_articles(
    current_user: UserInDB = Depends(require_permission(Permission.READ))
):
    """
    获取文章列表
    
    需要 READ 权限（所有角色都有）
    """
    return {
        "articles": list(fake_articles_db.values()),
        "user": current_user.username,
        "role": current_user.role
    }


@app.post("/articles", status_code=status.HTTP_201_CREATED)
async def create_article(
    article: Article,
    current_user: UserInDB = Depends(require_permission(Permission.CREATE))
):
    """
    创建文章
    
    需要 CREATE 权限（USER 及以上角色）
    """
    article.author = current_user.username
    fake_articles_db[article.id] = article.dict()
    return {
        "message": "文章创建成功",
        "article": article
    }


@app.put("/articles/{article_id}")
async def update_article(
    article_id: int,
    article: Article,
    current_user: UserInDB = Depends(require_permission(Permission.UPDATE))
):
    """
    更新文章
    
    需要 UPDATE 权限（USER 及以上角色）
    普通用户只能更新自己的文章，管理员和经理可以更新所有文章
    """
    if article_id not in fake_articles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    existing_article = fake_articles_db[article_id]
    
    # 资源级别权限检查：普通用户只能更新自己的文章
    if current_user.role == Role.USER and existing_article["author"] != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您只能更新自己的文章"
        )
    
    article.author = existing_article["author"]  # 保持原作者
    fake_articles_db[article_id] = article.dict()
    
    return {
        "message": "文章更新成功",
        "article": article
    }


@app.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    current_user: UserInDB = Depends(require_permission(Permission.DELETE))
):
    """
    删除文章
    
    需要 DELETE 权限（仅 ADMIN 角色）
    """
    if article_id not in fake_articles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    deleted_article = fake_articles_db.pop(article_id)
    
    return {
        "message": "文章删除成功",
        "article": deleted_article
    }


@app.get("/admin/users")
async def list_users(
    current_user: UserInDB = Depends(require_role(Role.MANAGER))
):
    """
    获取用户列表
    
    需要 MANAGER 或更高角色
    """
    users = [
        {
            "username": user["username"],
            "role": user["role"],
            "full_name": user.get("full_name")
        }
        for user in fake_users_db.values()
    ]
    return {
        "users": users,
        "total": len(users)
    }


@app.post("/admin/users/{username}/disable")
async def disable_user(
    username: str,
    current_user: UserInDB = Depends(require_permission(Permission.MANAGE_USERS))
):
    """
    禁用用户
    
    需要 MANAGE_USERS 权限（MANAGER 及以上角色）
    """
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己"
        )
    
    fake_users_db[username]["disabled"] = True
    
    return {
        "message": f"用户 {username} 已被禁用"
    }


# ==================== 初始化测试数据 ====================

def init_test_data():
    """初始化测试数据"""
    # 创建测试用户
    test_users = [
        {"username": "admin", "password": "admin123", "role": Role.ADMIN, "full_name": "管理员"},
        {"username": "manager", "password": "manager123", "role": Role.MANAGER, "full_name": "经理"},
        {"username": "user", "password": "user123", "role": Role.USER, "full_name": "普通用户"},
        {"username": "guest", "password": "guest123", "role": Role.GUEST, "full_name": "访客"},
    ]
    
    for user_data in test_users:
        user = UserInDB(
            username=user_data["username"],
            hashed_password=get_password_hash(user_data["password"]),
            role=user_data["role"],
            full_name=user_data["full_name"],
            disabled=False
        )
        fake_users_db[user.username] = user.dict()
    
    # 创建测试文章
    test_articles = [
        {"id": 1, "title": "FastAPI 入门", "content": "FastAPI 是一个现代化的 Python Web 框架", "author": "admin"},
        {"id": 2, "title": "Python 最佳实践", "content": "编写高质量 Python 代码的技巧", "author": "user"},
    ]
    
    for article in test_articles:
        fake_articles_db[article["id"]] = article


# 启动时初始化数据
init_test_data()


if __name__ == "__main__":
    print("测试用户：")
    print("  admin / admin123 (管理员 - 所有权限)")
    print("  manager / manager123 (经理 - 管理权限)")
    print("  user / user123 (普通用户 - 基础权限)")
    print("  guest / guest123 (访客 - 只读权限)")
    print("\n运行命令: uvicorn 02_authorization:app --reload")
    print("访问文档: http://127.0.0.1:8000/docs")
