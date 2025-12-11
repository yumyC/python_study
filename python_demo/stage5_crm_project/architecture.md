# CRM 项目架构设计文档

## 1. 架构概述

本 CRM 系统采用前后端分离的架构设计，后端提供 RESTful API 服务，前端使用现代化的单页应用（SPA）框架。系统设计遵循分层架构原则，确保各层职责清晰、低耦合、高内聚。

### 1.1 架构风格

- **前后端分离**: 前端和后端独立开发、部署和扩展
- **RESTful API**: 使用标准的 HTTP 方法和状态码
- **微服务友好**: 模块化设计，便于未来拆分为微服务
- **事件驱动**: 异步任务使用消息队列

### 1.2 技术栈

**后端（FastAPI 版本）**
- FastAPI 0.100+: Web 框架
- SQLAlchemy 2.0+: ORM
- Pydantic 2.0+: 数据验证
- Alembic: 数据库迁移
- Celery: 异步任务
- Redis: 缓存和消息队列
- PostgreSQL: 关系数据库
- python-jose: JWT 处理
- passlib: 密码加密

**后端（Flask 版本）**
- Flask 2.3+: Web 框架
- Flask-SQLAlchemy: ORM 集成
- Flask-Migrate: 数据库迁移
- Flask-JWT-Extended: JWT 认证
- Marshmallow: 序列化
- Celery: 异步任务
- Redis: 缓存和消息队列
- PostgreSQL: 关系数据库

**前端**
- Vue 3: 前端框架
- PureAdminThin: 管理后台模板
- TypeScript: 类型安全
- Vite: 构建工具
- Pinia: 状态管理
- Vue Router: 路由管理
- Axios: HTTP 客户端

**基础设施**
- Docker: 容器化
- Docker Compose: 本地开发环境
- GitHub Actions: CI/CD
- Nginx: 反向代理和静态文件服务


## 2. 系统架构图

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                         客户端层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web 浏览器   │  │  移动浏览器   │  │   API 客户端  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                      负载均衡 / 反向代理                       │
│                         Nginx                                │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ↓                       ↓
┌──────────────────────┐    ┌──────────────────────┐
│    前端静态资源       │    │     后端 API 服务     │
│   (Vue 3 SPA)        │    │   (FastAPI/Flask)    │
└──────────────────────┘    └──────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │   PostgreSQL     │ │      Redis       │ │  Celery Worker   │
        │   (主数据库)      │ │  (缓存/队列)     │ │   (异步任务)      │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 2.2 后端分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                        API 层 (Presentation)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  路由定义     │  │  请求验证     │  │  响应序列化   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     中间件层 (Middleware)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  认证中间件   │  │  日志中间件   │  │  错误处理     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     业务逻辑层 (Business)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  服务类       │  │  业务规则     │  │  权限验证     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     数据访问层 (Data Access)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Repository  │  │  ORM 模型     │  │  数据库操作   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        数据库层 (Database)                    │
│                         PostgreSQL                           │
└─────────────────────────────────────────────────────────────┘
```


## 3. 核心模块设计

### 3.1 认证授权模块 (Auth Module)

**职责**: 处理用户认证和授权

**组件**:
- `auth/jwt.py`: JWT Token 生成和验证
- `auth/password.py`: 密码加密和验证
- `auth/dependencies.py`: 认证依赖注入
- `auth/permissions.py`: 权限验证装饰器

**流程**:
1. 用户提交用户名和密码
2. 验证用户凭证
3. 生成 JWT Access Token 和 Refresh Token
4. 客户端在请求头中携带 Token
5. 中间件验证 Token 有效性
6. 从 Token 中提取用户信息
7. 验证用户权限

**安全措施**:
- 密码使用 bcrypt 加密
- Token 包含过期时间
- Token 使用密钥签名
- 支持 Token 刷新机制
- 登录失败次数限制

### 3.2 员工管理模块 (Employee Module)

**职责**: 管理员工信息

**组件**:
- `models/employee.py`: 员工数据模型
- `schemas/employee.py`: 员工数据验证
- `services/employee_service.py`: 员工业务逻辑
- `api/employees.py`: 员工 API 路由

**核心功能**:
- CRUD 操作
- 搜索和筛选
- 分页查询
- 密码管理
- 状态管理

### 3.3 岗位管理模块 (Position Module)

**职责**: 管理组织架构和岗位信息

**组件**:
- `models/position.py`: 岗位数据模型
- `schemas/position.py`: 岗位数据验证
- `services/position_service.py`: 岗位业务逻辑
- `api/positions.py`: 岗位 API 路由

**核心功能**:
- 岗位 CRUD
- 岗位层级关系
- 树形结构查询
- 岗位编码管理

**数据结构**:
- 自引用关系（parent_id）
- 层级字段（level）
- 支持多级岗位结构

### 3.4 菜单管理模块 (Menu Module)

**职责**: 管理系统菜单和路由

**组件**:
- `models/menu.py`: 菜单数据模型
- `schemas/menu.py`: 菜单数据验证
- `services/menu_service.py`: 菜单业务逻辑
- `api/menus.py`: 菜单 API 路由

**核心功能**:
- 菜单 CRUD
- 树形结构
- 菜单排序
- 可见性控制
- 用户菜单查询

### 3.5 角色权限模块 (Role & Permission Module)

**职责**: 管理角色和权限

**组件**:
- `models/role.py`: 角色数据模型
- `models/role_menu_permission.py`: 权限绑定模型
- `schemas/role.py`: 角色数据验证
- `services/role_service.py`: 角色业务逻辑
- `services/permission_service.py`: 权限业务逻辑
- `api/roles.py`: 角色 API 路由
- `api/permissions.py`: 权限 API 路由

**核心功能**:
- 角色 CRUD
- 权限分配
- 权限查询
- 权限验证

**权限模型**:
- 基于角色的访问控制（RBAC）
- 菜单级别权限
- 操作级别权限（view, create, update, delete）

### 3.6 工作日志模块 (WorkLog Module)

**职责**: 管理员工工作日志

**组件**:
- `models/worklog.py`: 工作日志数据模型
- `schemas/worklog.py`: 工作日志数据验证
- `services/worklog_service.py`: 工作日志业务逻辑
- `api/worklogs.py`: 工作日志 API 路由
- `tasks/export_tasks.py`: 导出异步任务

**核心功能**:
- 日志 CRUD
- 自评和上级评分
- 日志查询和筛选
- 异步导出 Excel
- 任务状态追踪

**业务规则**:
- 每天一条日志
- 权限控制（员工/主管/管理员）
- 评分后限制修改


## 4. 数据库设计

### 4.1 数据库选择

**推荐**: PostgreSQL 13+

**理由**:
- 开源免费
- 功能强大（支持 JSON、全文搜索等）
- 性能优秀
- 社区活跃
- 企业级可靠性

**备选**: MySQL 8+

### 4.2 核心表结构

详见 [数据库设计文档](docs/database_schema.md)

### 4.3 数据库设计原则

1. **规范化**: 遵循第三范式，减少数据冗余
2. **索引优化**: 为常用查询字段添加索引
3. **外键约束**: 使用外键保证数据完整性
4. **软删除**: 重要数据使用软删除（deleted_at 字段）
5. **审计字段**: 所有表包含 created_at 和 updated_at
6. **UUID 主键**: 使用 UUID 作为主键，便于分布式扩展

### 4.4 数据库迁移

使用 Alembic（FastAPI）或 Flask-Migrate（Flask）管理数据库版本：

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 5. API 设计

### 5.1 RESTful 规范

**资源命名**:
- 使用复数名词: `/api/employees`, `/api/roles`
- 使用小写字母和连字符: `/api/work-logs`
- 避免动词: 使用 HTTP 方法表示操作

**HTTP 方法**:
- GET: 查询资源
- POST: 创建资源
- PUT: 完整更新资源
- PATCH: 部分更新资源
- DELETE: 删除资源

**状态码**:
- 200 OK: 成功
- 201 Created: 创建成功
- 204 No Content: 删除成功
- 400 Bad Request: 请求参数错误
- 401 Unauthorized: 未认证
- 403 Forbidden: 无权限
- 404 Not Found: 资源不存在
- 422 Unprocessable Entity: 验证失败
- 500 Internal Server Error: 服务器错误

### 5.2 API 版本控制

使用 URL 路径版本控制:
```
/api/v1/employees
/api/v2/employees
```

### 5.3 请求格式

**请求头**:
```
Content-Type: application/json
Authorization: Bearer <access_token>
X-Request-ID: <uuid>
```

**请求体**:
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "full_name": "张三",
  "position_id": "uuid",
  "role_id": "uuid"
}
```

### 5.4 响应格式

**成功响应**:
```json
{
  "data": {
    "id": "uuid",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "full_name": "张三",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**列表响应**:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

**错误响应**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "验证失败",
    "details": {
      "email": ["邮箱格式不正确"]
    },
    "request_id": "uuid"
  }
}
```

### 5.5 分页参数

```
GET /api/employees?page=1&page_size=20
```

### 5.6 搜索和筛选

```
GET /api/employees?search=张三&position_id=uuid&status=active
```

### 5.7 排序

```
GET /api/employees?sort=-created_at,full_name
```
（`-` 表示降序）


## 6. 中间件设计

### 6.1 认证中间件 (Authentication Middleware)

**职责**: 验证请求的 JWT Token

**流程**:
1. 从请求头获取 Authorization
2. 提取 Bearer Token
3. 验证 Token 签名和有效期
4. 解析用户信息
5. 将用户信息注入到请求上下文

**实现**:
```python
# FastAPI 版本
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    # 验证 Token
    # 返回用户信息
    pass
```

### 6.2 请求日志中间件 (Request Logging Middleware)

**职责**: 记录所有 API 请求

**记录内容**:
- Request ID
- 请求方法和路径
- 请求参数
- 响应状态码
- 响应时间
- 用户信息

**实现**:
```python
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 注入 request_id
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # 记录日志
        duration = time.time() - start_time
        logger.info(f"Request completed", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration
        })
        
        return response
```

### 6.3 错误处理中间件 (Error Handler Middleware)

**职责**: 统一处理异常

**处理的异常**:
- 验证错误
- 认证错误
- 权限错误
- 业务逻辑错误
- 数据库错误
- 未知错误

**实现**:
```python
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "request_id": request.state.request_id
            }
        }
    )
```

### 6.4 CORS 中间件 (CORS Middleware)

**职责**: 处理跨域请求

**配置**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 7. 异步任务设计

### 7.1 任务队列架构

```
API 服务 → Redis (Broker) → Celery Worker → 结果存储
```

### 7.2 Celery 配置

**Broker**: Redis
**Backend**: Redis
**序列化**: JSON

**配置示例**:
```python
# celery_config.py
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/1'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Shanghai'
enable_utc = True
```

### 7.3 工作日志导出任务

**任务定义**:
```python
from celery import Task

@celery_app.task(bind=True)
def export_worklogs_task(self, employee_id, start_date, end_date):
    # 查询数据
    # 生成 Excel
    # 保存文件
    # 返回文件路径
    pass
```

**任务调用**:
```python
# API 端点
@router.post("/worklogs/export")
async def export_worklogs(params: ExportParams):
    task = export_worklogs_task.delay(
        params.employee_id,
        params.start_date,
        params.end_date
    )
    return {"task_id": task.id}
```

**任务状态查询**:
```python
@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

### 7.4 任务监控

使用 Flower 监控 Celery 任务:
```bash
celery -A app.tasks flower
```


## 8. 安全设计

### 8.1 认证安全

**密码策略**:
- 最小长度 8 位
- 必须包含大小写字母和数字
- 使用 bcrypt 加密存储
- 密码加盐（salt）

**Token 安全**:
- JWT 使用 HS256 或 RS256 算法
- Access Token 有效期 2 小时
- Refresh Token 有效期 7 天
- Token 包含过期时间和签名
- 支持 Token 黑名单（可选）

**登录保护**:
- 登录失败 5 次锁定 30 分钟
- 记录登录日志
- 异常登录告警

### 8.2 授权安全

**RBAC 模型**:
- 用户 → 角色 → 权限
- 最小权限原则
- 权限继承（可选）

**权限验证**:
```python
from functools import wraps

def require_permission(menu_path: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前用户
            # 检查权限
            # 如果有权限，执行函数
            # 否则返回 403
            pass
        return wrapper
    return decorator

@router.post("/employees")
@require_permission("/employees", "create")
async def create_employee(data: EmployeeCreate):
    pass
```

### 8.3 数据安全

**SQL 注入防护**:
- 使用 ORM 参数化查询
- 避免拼接 SQL 语句
- 输入验证

**XSS 防护**:
- 前端输入验证
- 输出转义
- Content-Security-Policy 头

**CSRF 防护**:
- 使用 Token 验证
- SameSite Cookie 属性

**敏感数据**:
- 密码不记录到日志
- API 响应不返回密码字段
- 敏感字段加密存储

### 8.4 通信安全

**HTTPS**:
- 生产环境强制 HTTPS
- TLS 1.2+
- 证书有效性检查

**API 安全**:
- 请求频率限制
- IP 白名单（可选）
- API Key 验证（可选）

## 9. 性能优化

### 9.1 数据库优化

**索引优化**:
- 为常用查询字段添加索引
- 复合索引优化多条件查询
- 避免过多索引影响写入性能

**查询优化**:
- 使用 select_related 和 joinedload 减少查询次数
- 避免 N+1 查询问题
- 分页查询大数据集
- 使用数据库连接池

**示例**:
```python
# 优化前（N+1 查询）
employees = session.query(Employee).all()
for emp in employees:
    print(emp.position.name)  # 每次都查询数据库

# 优化后（一次查询）
employees = session.query(Employee).options(
    joinedload(Employee.position)
).all()
for emp in employees:
    print(emp.position.name)  # 不再查询数据库
```

### 9.2 缓存策略

**Redis 缓存**:
- 用户信息缓存（登录后）
- 菜单树缓存
- 权限信息缓存
- 热点数据缓存

**缓存模式**:
- Cache-Aside: 先查缓存，未命中查数据库
- Write-Through: 写入时同时更新缓存
- 设置合理的过期时间

**示例**:
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache(key_prefix: str, expire: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{args[0]}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 缓存未命中，执行函数
            result = await func(*args, **kwargs)
            
            # 写入缓存
            redis_client.setex(
                cache_key,
                expire,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator
```

### 9.3 异步处理

**异步 I/O**:
- 使用 async/await
- 异步数据库驱动
- 异步 HTTP 客户端

**后台任务**:
- 耗时操作使用 Celery
- 邮件发送
- 文件导出
- 数据统计

### 9.4 响应优化

**数据压缩**:
- Gzip 压缩响应
- 减少响应体大小

**分页**:
- 大数据集必须分页
- 默认每页 20 条
- 最大每页 100 条

**字段过滤**:
- 支持指定返回字段
- 减少不必要的数据传输


## 10. 可观测性

### 10.1 日志系统

**日志级别**:
- DEBUG: 调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

**结构化日志**:
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "user_login",
    user_id=user.id,
    username=user.username,
    ip_address=request.client.host,
    request_id=request.state.request_id
)
```

**日志内容**:
- 时间戳
- 日志级别
- Request ID
- 用户信息
- 操作描述
- 错误堆栈（如果有）

### 10.2 监控指标

**应用指标**:
- 请求数量
- 响应时间
- 错误率
- 并发用户数

**系统指标**:
- CPU 使用率
- 内存使用率
- 磁盘 I/O
- 网络流量

**业务指标**:
- 活跃用户数
- 日志创建数
- 导出任务数

### 10.3 追踪系统

**Request ID**:
- 每个请求生成唯一 ID
- 在日志中记录
- 在响应头中返回
- 用于追踪请求链路

**分布式追踪**:
- 使用 OpenTelemetry（可选）
- 追踪跨服务调用
- 性能分析

### 10.4 健康检查

**健康检查端点**:
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "checks": {
            "database": check_database(),
            "redis": check_redis(),
            "celery": check_celery()
        }
    }
```

## 11. 测试策略

### 11.1 单元测试

**测试范围**:
- 业务逻辑函数
- 数据验证
- 工具函数

**测试框架**: pytest

**示例**:
```python
def test_password_hash():
    password = "Test123456"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
```

### 11.2 集成测试

**测试范围**:
- API 端点
- 数据库操作
- 认证流程

**测试数据库**: 使用独立的测试数据库

**示例**:
```python
def test_create_employee(client, auth_headers):
    response = client.post(
        "/api/employees",
        json={
            "username": "test",
            "email": "test@example.com",
            "password": "Test123456",
            "full_name": "测试用户"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["data"]["username"] == "test"
```

### 11.3 测试覆盖率

**目标**: 核心业务逻辑 80% 以上

**工具**: pytest-cov

```bash
pytest --cov=app --cov-report=html
```

### 11.4 测试数据

**使用 Factory**:
```python
import factory

class EmployeeFactory(factory.Factory):
    class Meta:
        model = Employee
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    full_name = factory.Faker("name", locale="zh_CN")
```

## 12. 部署架构

### 12.1 开发环境

**Docker Compose**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/crm
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=crm
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6
    ports:
      - "6379:6379"
  
  celery:
    build: .
    command: celery -A app.tasks worker -l info
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

### 12.2 生产环境

**容器编排**: Docker Compose 或 Kubernetes

**架构**:
```
Internet
    ↓
Nginx (反向代理 + SSL)
    ↓
API 服务 (多实例)
    ↓
PostgreSQL (主从复制)
Redis (哨兵模式)
Celery Worker (多实例)
```

**高可用**:
- API 服务多实例 + 负载均衡
- 数据库主从复制
- Redis 哨兵模式
- 自动重启机制

### 12.3 CI/CD 流程

**GitHub Actions**:
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t crm-api .
      - name: Push to registry
        run: docker push crm-api
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh user@server "docker pull crm-api && docker-compose up -d"
```

## 13. 配置管理

### 13.1 环境变量

**必需配置**:
```bash
# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/crm

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 13.2 配置文件

**config.py**:
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 14. 错误处理

### 14.1 自定义异常

```python
class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

class ValidationError(AppException):
    def __init__(self, message: str, details: dict = None):
        super().__init__("VALIDATION_ERROR", message, 422)
        self.details = details

class AuthenticationError(AppException):
    def __init__(self, message: str = "认证失败"):
        super().__init__("AUTHENTICATION_ERROR", message, 401)

class PermissionError(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__("PERMISSION_ERROR", message, 403)
```

### 14.2 全局异常处理

```python
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": getattr(exc, "details", None),
                "request_id": request.state.request_id
            }
        }
    )
```

## 15. 最佳实践

### 15.1 代码组织

- 按功能模块组织代码
- 保持文件和函数简短
- 使用有意义的命名
- 遵循 PEP 8 规范

### 15.2 依赖注入

使用 FastAPI 的依赖注入系统:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/employees")
async def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()
```

### 15.3 数据验证

使用 Pydantic 模型:
```python
from pydantic import BaseModel, EmailStr, validator

class EmployeeCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少 8 位')
        return v
```

### 15.4 文档注释

```python
async def create_employee(data: EmployeeCreate, db: Session) -> Employee:
    """
    创建新员工
    
    Args:
        data: 员工创建数据
        db: 数据库会话
    
    Returns:
        创建的员工对象
    
    Raises:
        ValidationError: 数据验证失败
        DuplicateError: 用户名或邮箱已存在
    """
    pass
```

## 16. 扩展性考虑

### 16.1 微服务拆分

当系统规模增长时，可以拆分为微服务:
- 用户服务
- 权限服务
- 工作日志服务
- 通知服务

### 16.2 消息队列

引入消息队列（RabbitMQ/Kafka）:
- 服务间异步通信
- 事件驱动架构
- 解耦服务依赖

### 16.3 API 网关

使用 API 网关统一入口:
- 路由转发
- 认证授权
- 限流熔断
- 日志监控

### 16.4 服务发现

使用服务发现（Consul/Eureka）:
- 动态服务注册
- 健康检查
- 负载均衡

## 17. 总结

本 CRM 系统采用现代化的架构设计，具有以下特点:

1. **分层清晰**: API、业务逻辑、数据访问分离
2. **安全可靠**: 完善的认证授权和数据安全机制
3. **高性能**: 缓存、异步、数据库优化
4. **可观测**: 日志、监控、追踪完整
5. **易维护**: 模块化、测试覆盖、文档完善
6. **可扩展**: 支持水平扩展和微服务拆分

通过学习和实现这个项目，你将掌握企业级 Web 应用开发的核心技能。
