# FastAPI 认证授权系统

本模块实现了完整的 JWT 认证和基于角色的访问控制 (RBAC) 系统，适用于企业级 CRM 应用。

## 功能特性

- **JWT 认证**: 使用 JSON Web Token 进行用户认证
- **RBAC 权限控制**: 基于角色的访问控制系统
- **菜单权限**: 细粒度的菜单级权限控制
- **密码安全**: 使用 bcrypt 进行密码哈希
- **Token 刷新**: 支持访问令牌的自动刷新
- **灵活的权限检查**: 提供多种权限验证方式

## 核心组件

### 1. JWT 处理器 (`jwt_handler.py`)

负责 JWT Token 的生成、验证和密码处理：

```python
from app.auth.jwt_handler import jwt_handler

# 生成访问令牌
access_token = jwt_handler.create_access_token({"sub": user_id})

# 生成刷新令牌
refresh_token = jwt_handler.create_refresh_token({"sub": user_id})

# 验证令牌
payload = jwt_handler.verify_token(token, "access")

# 密码哈希和验证
hashed = jwt_handler.hash_password("password")
is_valid = jwt_handler.verify_password("password", hashed)
```

### 2. 认证服务 (`auth_service.py`)

提供用户认证和权限验证的业务逻辑：

```python
from app.auth import AuthService

auth_service = AuthService(db)

# 用户登录
login_response = auth_service.login("username", "password")

# 刷新令牌
new_tokens = auth_service.refresh_token(refresh_token)

# 获取当前用户
user = auth_service.get_current_user(access_token)

# 检查权限
has_permission = auth_service.check_permission(user, "/employees", "view")
```

### 3. 依赖注入 (`dependencies.py`)

提供 FastAPI 依赖注入的认证和授权函数：

```python
from app.auth import get_current_user, require_permission, get_permission_checker

# 基础认证
@app.get("/protected")
async def protected_route(current_user: Employee = Depends(get_current_user)):
    return {"user": current_user.username}

# 权限控制
@app.get("/employees")
async def get_employees(
    current_user: Employee = Depends(require_permission("/employees", "view"))
):
    return employees

# 灵活权限检查
@app.put("/employees/{id}")
async def update_employee(
    id: str,
    checker: PermissionChecker = Depends(get_permission_checker)
):
    # 自定义权限逻辑
    if id == str(checker.current_user.id):
        checker.require_permission("/employees", "view")  # 更新自己
    else:
        checker.require_permission("/employees", "update")  # 更新他人
```

## API 端点

### 认证相关接口

#### 1. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

响应：
```json
{
    "user": {
        "id": "uuid",
        "username": "admin",
        "email": "admin@crm.com",
        "full_name": "系统管理员",
        "role": {
            "id": "uuid",
            "name": "系统管理员",
            "code": "ADMIN"
        },
        "permissions": ["employees:view", "employees:create", ...]
    },
    "tokens": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 1800
    }
}
```

#### 2. 刷新令牌
```http
POST /api/auth/refresh
Content-Type: application/json

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. 获取用户信息
```http
GET /api/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 4. 获取用户权限
```http
GET /api/auth/permissions
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 5. 检查权限
```http
POST /api/auth/check-permission?menu_path=/employees&permission=view
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 权限系统设计

### 权限模型

系统采用 RBAC (Role-Based Access Control) 模型：

```
用户 (Employee) → 角色 (Role) → 权限 (RoleMenuPermission) → 菜单 (Menu)
```

### 权限类型

每个菜单支持四种基本权限：
- `view`: 查看权限
- `create`: 创建权限  
- `update`: 更新权限
- `delete`: 删除权限

### 权限格式

权限以字符串形式存储，格式为 `menu_path:permission`：
- `/employees:view` - 员工管理查看权限
- `/employees:create` - 员工管理创建权限
- `/work-logs:update` - 工作日志更新权限

## 使用示例

### 1. 基础认证保护

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/profile")
async def get_profile(current_user: Employee = Depends(get_current_active_user)):
    return {"user_id": current_user.id, "name": current_user.full_name}
```

### 2. 权限控制

```python
from app.auth import require_permission

@router.get("/employees")
async def list_employees(
    current_user: Employee = Depends(require_permission("/employees", "view"))
):
    # 只有拥有员工查看权限的用户才能访问
    return employees
```

### 3. 角色控制

```python
from app.auth import require_role

@router.post("/system/backup")
async def create_backup(
    current_user: Employee = Depends(require_role("ADMIN"))
):
    # 只有管理员角色才能访问
    return {"message": "备份已创建"}
```

### 4. 灵活权限检查

```python
from app.auth import get_permission_checker, PermissionChecker

@router.put("/employees/{employee_id}")
async def update_employee(
    employee_id: str,
    data: EmployeeUpdateRequest,
    checker: PermissionChecker = Depends(get_permission_checker)
):
    # 自定义权限逻辑
    if employee_id == str(checker.current_user.id):
        # 更新自己的信息，只需要基础权限
        checker.require_permission("/employees", "view")
    else:
        # 更新他人信息，需要管理权限
        checker.require_permission("/employees", "update")
    
    # 修改敏感字段需要管理员权限
    if data.role_id is not None:
        checker.require_role("ADMIN")
    
    # 执行更新逻辑...
```

### 5. 可选认证

```python
from app.auth import optional_auth

@router.get("/public-data")
async def get_public_data(
    current_user: Optional[Employee] = Depends(optional_auth)
):
    # 根据是否登录返回不同的数据
    if current_user:
        return {"data": "详细数据", "user": current_user.username}
    else:
        return {"data": "公开数据"}
```

## 环境配置

在 `.env` 文件中配置相关参数：

```env
# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 数据库配置
DATABASE_URL=sqlite:///./crm.db
```

## 默认账户

系统初始化时会创建以下默认账户：

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| admin | admin123 | 系统管理员 | 所有权限 |
| manager | manager123 | 部门经理 | 部分管理权限 |
| employee | employee123 | 普通员工 | 基础权限 |

## 安全注意事项

1. **密钥安全**: 生产环境必须使用强密钥并定期更换
2. **HTTPS**: 生产环境必须使用 HTTPS 传输
3. **Token 过期**: 合理设置 Token 过期时间
4. **权限最小化**: 遵循最小权限原则
5. **日志记录**: 记录所有认证和授权操作
6. **输入验证**: 严格验证所有用户输入

## 扩展功能

### 1. Token 黑名单

可以实现 Token 黑名单功能来支持真正的登出：

```python
# 在 Redis 中维护黑名单
def add_to_blacklist(token: str, expire_time: int):
    redis_client.setex(f"blacklist:{token}", expire_time, "1")

def is_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklist:{token}")
```

### 2. 权限缓存

对于高频访问的权限检查，可以使用缓存：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_permissions_cached(user_id: str) -> List[str]:
    # 缓存用户权限
    pass
```

### 3. 审计日志

记录所有权限相关操作：

```python
def log_permission_check(user_id: str, menu_path: str, permission: str, result: bool):
    # 记录权限检查日志
    pass
```

## 测试

系统包含完整的测试用例，可以运行：

```bash
# 运行认证相关测试
pytest tests/test_auth.py -v

# 运行权限相关测试  
pytest tests/test_permissions.py -v
```

## 故障排除

### 常见问题

1. **Token 无效**: 检查 JWT_SECRET_KEY 是否正确
2. **权限不足**: 确认用户角色和菜单权限配置
3. **密码错误**: 确认密码哈希算法一致性
4. **Token 过期**: 检查系统时间和过期时间设置

### 调试技巧

1. 启用详细日志记录
2. 使用 `/api/auth/validate-token` 检查 Token 状态
3. 使用 `/api/auth/permissions` 查看用户权限
4. 检查数据库中的角色权限配置

这个认证授权系统为 CRM 应用提供了企业级的安全保障，支持灵活的权限控制和扩展。