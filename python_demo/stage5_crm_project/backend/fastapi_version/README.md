# FastAPI CRM 系统

这是一个完整的 CRM（客户关系管理）系统的 FastAPI 版本实现，包含员工管理、岗位管理、菜单管理、角色权限管理和工作日志等核心功能。

## 功能特性

- 🔐 **认证授权**: JWT Token 认证，基于角色的权限控制 (RBAC)
- 👥 **员工管理**: 员工信息管理，支持搜索、分页、状态管理
- 🏢 **岗位管理**: 层级结构的岗位管理，支持组织架构
- 📋 **菜单管理**: 树形菜单结构，动态权限控制
- 🎭 **角色管理**: 灵活的角色定义和权限分配
- 📝 **工作日志**: 员工工作记录，支持评分和统计
- 📊 **异步任务**: Celery 异步任务处理，支持文件导出
- 🔍 **监控日志**: 请求日志、错误处理、性能监控
- 🐳 **容器化**: Docker 容器化部署，支持一键启动
- 📚 **API 文档**: 自动生成的 OpenAPI 文档

## 项目结构

```
fastapi_version/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用主入口
│   ├── database.py             # 数据库配置和连接
│   ├── init_db.py             # 数据库初始化脚本
│   ├── models/                # 数据模型包
│   │   ├── __init__.py
│   │   ├── base.py            # 基础模型类
│   │   ├── employee.py        # 员工模型
│   │   ├── position.py        # 岗位模型
│   │   ├── menu.py            # 菜单模型
│   │   ├── role.py            # 角色模型
│   │   ├── role_menu_permission.py  # 角色菜单权限模型
│   │   └── work_log.py        # 工作日志模型
│   ├── schemas/               # Pydantic 数据模式
│   │   ├── __init__.py
│   │   ├── common.py          # 通用模式
│   │   └── employee.py        # 员工相关模式
│   ├── api/                   # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py            # 认证接口
│   │   ├── employees.py       # 员工管理接口
│   │   ├── positions.py       # 岗位管理接口
│   │   ├── menus.py           # 菜单管理接口
│   │   ├── roles.py           # 角色管理接口
│   │   ├── permissions.py     # 权限管理接口
│   │   ├── work_logs.py       # 工作日志接口
│   │   └── tasks.py           # 任务管理接口
│   ├── auth/                  # 认证授权模块
│   │   ├── __init__.py
│   │   ├── auth_service.py    # 认证服务
│   │   ├── jwt_handler.py     # JWT 处理
│   │   ├── dependencies.py    # 依赖注入
│   │   └── schemas.py         # 认证相关模式
│   ├── middleware/            # 中间件
│   │   ├── __init__.py
│   │   ├── request_logging.py # 请求日志中间件
│   │   ├── request_id.py      # Request ID 中间件
│   │   └── error_handler.py   # 错误处理中间件
│   └── tasks/                 # 异步任务
│       ├── __init__.py
│       ├── celery_app.py      # Celery 应用配置
│       └── work_log_tasks.py  # 工作日志相关任务
├── tests/                     # 测试文件
├── uploads/                   # 文件上传目录
├── logs/                      # 日志文件目录
├── requirements.txt           # 项目依赖
├── Dockerfile                 # Docker 镜像构建文件
├── docker-compose.yml         # 生产环境 Docker Compose
├── docker-compose.dev.yml     # 开发环境 Docker Compose
├── .env.example              # 环境变量示例
└── README.md                 # 项目说明
```

## 数据模型说明

### 1. BaseModel (基础模型)
- 所有模型的基类
- 包含公共字段：id、created_at、updated_at
- 提供通用方法：to_dict()、__repr__()

### 2. Employee (员工模型)
- 存储员工基本信息
- 支持用户名、邮箱登录
- 关联岗位和角色
- 员工状态管理（在职/离职）

### 3. Position (岗位模型)
- 支持层级结构的岗位管理
- 岗位编码和名称
- 岗位级别和描述
- 提供层级查询方法

### 4. Menu (菜单模型)
- 树形结构的菜单管理
- 支持前端路由配置
- 菜单图标和组件
- 排序和可见性控制

### 5. Role (角色模型)
- 角色定义和管理
- 角色编码和描述
- 权限管理方法

### 6. RoleMenuPermission (角色菜单权限)
- 角色与菜单的权限关联
- 支持细粒度权限控制（view、create、update、delete）
- JSON 格式存储权限列表

### 7. WorkLog (工作日志模型)
- 员工工作日志记录
- 工作内容和完成状态
- 自评和上级评分
- 统计分析方法

## 数据库关系

```
Employee ──┬── Position (多对一)
           ├── Role (多对一)
           └── WorkLog (一对多)

Role ────── RoleMenuPermission (一对多)
Menu ────── RoleMenuPermission (一对多)

Position ── Position (自关联，父子关系)
Menu ────── Menu (自关联，父子关系)
```

## 快速开始

### 方式一：Docker Compose（推荐）

1. **克隆项目并进入目录**
```bash
cd study/python_demo/stage5_crm_project/backend/fastapi_version
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（可选，使用默认配置即可快速启动）
vim .env
```

3. **启动所有服务**
```bash
# 启动生产环境（包含 Nginx、PostgreSQL、Redis、Celery）
docker-compose up -d

# 或启动开发环境（仅启动 Redis 和 PostgreSQL）
docker-compose -f docker-compose.dev.yml up -d
```

4. **访问应用**
- API 文档：http://localhost:8000/docs
- 交互式文档：http://localhost:8000/redoc
- Celery 监控：http://localhost:5555
- 健康检查：http://localhost:8000/health

### 方式二：本地开发环境

1. **环境要求**
- Python 3.9+
- PostgreSQL 或 SQLite
- Redis（用于异步任务）

2. **安装依赖**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 升级 pip 并安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

3. **配置数据库**
```bash
# 使用 SQLite（默认，无需额外配置）
export DATABASE_URL="sqlite:///./crm_fastapi.db"

# 或使用 PostgreSQL
export DATABASE_URL="postgresql://crm_user:crm_password@localhost/crm_db"
```

4. **初始化数据库**
```bash
# 运行数据库初始化脚本
python -m app.init_db
```

5. **启动服务**
```bash
# 启动 FastAPI 应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动 Celery Worker（新终端）
celery -A app.tasks.celery_app worker --loglevel=info

# 启动 Celery Beat 定时任务（可选，新终端）
celery -A app.tasks.celery_app beat --loglevel=info
```

### 方式三：快速开发脚本

```bash
# 使用提供的开发脚本
chmod +x start_dev.sh
./start_dev.sh
```

## 默认账户

数据库初始化后会创建以下默认账户：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 系统管理员 | 拥有所有权限 |
| manager | manager123 | 部门经理 | 部门管理权限 |
| employee | employee123 | 普通员工 | 基础员工权限 |

## 环境变量配置

创建 `.env` 文件并配置以下变量：

```bash
# 数据库配置
DATABASE_URL=postgresql://crm_user:crm_password@localhost:5432/crm_db

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用配置
APP_NAME=CRM System
APP_VERSION=1.0.0
DEBUG=false

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

## API 接口概览

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新 Token
- `GET /api/auth/me` - 获取当前用户信息

### 员工管理
- `GET /api/employees` - 获取员工列表（支持搜索、分页）
- `POST /api/employees` - 创建员工
- `GET /api/employees/{id}` - 获取员工详情
- `PUT /api/employees/{id}` - 更新员工信息
- `DELETE /api/employees/{id}` - 删除员工

### 岗位管理
- `GET /api/positions` - 获取岗位列表（支持树形结构）
- `POST /api/positions` - 创建岗位
- `PUT /api/positions/{id}` - 更新岗位
- `DELETE /api/positions/{id}` - 删除岗位

### 菜单管理
- `GET /api/menus` - 获取菜单列表
- `GET /api/menus/user` - 获取用户权限菜单
- `POST /api/menus` - 创建菜单
- `PUT /api/menus/{id}` - 更新菜单
- `DELETE /api/menus/{id}` - 删除菜单

### 角色管理
- `GET /api/roles` - 获取角色列表
- `POST /api/roles` - 创建角色
- `PUT /api/roles/{id}` - 更新角色
- `DELETE /api/roles/{id}` - 删除角色

### 权限管理
- `POST /api/permissions/assign` - 分配角色权限
- `GET /api/permissions/role/{role_id}` - 查询角色权限

### 工作日志
- `GET /api/worklogs` - 获取工作日志列表
- `POST /api/worklogs` - 创建工作日志
- `PUT /api/worklogs/{id}` - 更新工作日志
- `POST /api/worklogs/{id}/rate` - 上级评分
- `POST /api/worklogs/export` - 导出工作日志

### 任务管理
- `GET /api/tasks/{task_id}` - 查询任务状态
- `GET /api/tasks/{task_id}/download` - 下载任务结果

### 系统监控
- `GET /health` - 健康检查
- `GET /` - API 信息

> 详细的 API 文档请访问：http://localhost:8000/docs

## 模型特性演示

### 1. 层级关系查询

```python
# 获取岗位的完整路径
position = db.query(Position).first()
full_path = position.get_full_path()  # "CEO > 技术总监 > 高级开发工程师"

# 获取所有下级岗位
children = position.get_all_children()
```

### 2. 树形菜单结构

```python
# 获取菜单树形结构
menu = db.query(Menu).filter_by(parent_id=None).first()
tree_dict = menu.to_tree_dict(include_children=True)
```

### 3. 权限检查

```python
# 检查角色权限
role = db.query(Role).first()
has_permission = role.has_permission(menu_id, 'create')

# 获取可访问菜单
accessible_menus = role.get_accessible_menus()
```

### 4. 工作日志统计

```python
# 获取评分统计
stats = WorkLog.get_rating_statistics(
    session=db,
    employee_id=employee_id,
    start_date=start_date,
    end_date=end_date
)
```

## 部署指南

### Docker 生产部署

1. **构建镜像**
```bash
docker build -t crm-fastapi:latest .
```

2. **使用 Docker Compose 部署**
```bash
# 生产环境部署
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

3. **扩展服务**
```bash
# 扩展 API 服务实例
docker-compose up -d --scale app=3

# 扩展 Celery Worker
docker-compose up -d --scale celery_worker=2
```

### 传统部署

1. **安装系统依赖**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv postgresql redis-server nginx

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql-server redis nginx
```

2. **配置服务**
```bash
# 配置 PostgreSQL
sudo -u postgres createuser crm_user
sudo -u postgres createdb crm_db -O crm_user

# 启动 Redis
sudo systemctl start redis
sudo systemctl enable redis

# 配置 Nginx（参考 nginx.conf）
sudo cp nginx.conf /etc/nginx/sites-available/crm
sudo ln -s /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

3. **部署应用**
```bash
# 使用 Gunicorn 部署
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 使用 Supervisor 管理进程
sudo apt-get install supervisor
# 配置 supervisor 配置文件
```

### 监控和维护

1. **日志管理**
```bash
# 查看应用日志
tail -f logs/app.log

# 查看 Docker 日志
docker-compose logs -f

# 日志轮转配置
# 配置 logrotate 或使用 Docker 日志驱动
```

2. **性能监控**
```bash
# 查看 Celery 任务
celery -A app.tasks.celery_app inspect active

# 监控 Redis
redis-cli monitor

# 数据库性能
# 使用 pg_stat_statements 等工具
```

3. **备份策略**
```bash
# 数据库备份
pg_dump crm_db > backup_$(date +%Y%m%d).sql

# 文件备份
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

## 开发说明

### 代码规范
- 遵循 PEP 8 编码规范
- 使用 black 进行代码格式化
- 使用 mypy 进行类型检查

### 模型设计原则
1. 使用 UUID 作为主键，避免 ID 冲突
2. 所有模型继承 BaseModel，统一公共字段
3. 合理使用外键约束和级联操作
4. 提供业务相关的便捷方法
5. 支持软删除和状态管理

### 性能优化
1. 合理使用 lazy loading 策略
2. 为常用查询字段添加索引
3. 使用 relationship 的 back_populates 双向关联
4. 避免 N+1 查询问题

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行测试并显示详细输出
pytest -v -s
```

### 测试数据

项目提供了多个测试脚本：

```bash
# 测试认证系统
python test_auth_system.py

# 测试核心 API
python test_core_apis.py

# 测试数据模型
python test_models.py

# 测试异步中间件
python test_async_middleware.py

# 简单 API 测试
python simple_api_test.py
```

## 故障排除

### 常见问题

1. **数据库连接失败**
```bash
# 检查数据库服务状态
sudo systemctl status postgresql

# 检查连接字符串
echo $DATABASE_URL
```

2. **Redis 连接失败**
```bash
# 检查 Redis 服务
redis-cli ping

# 检查 Celery 连接
celery -A app.tasks.celery_app inspect ping
```

3. **权限问题**
```bash
# 检查文件权限
ls -la uploads/ logs/

# 修复权限
chmod 755 uploads/ logs/
```

4. **端口占用**
```bash
# 查看端口占用
netstat -tlnp | grep :8000

# 杀死占用进程
kill -9 <PID>
```

### 性能优化

1. **数据库优化**
- 添加适当的索引
- 使用连接池
- 优化查询语句

2. **缓存策略**
- Redis 缓存热点数据
- 使用 CDN 缓存静态资源

3. **异步处理**
- 耗时操作使用 Celery
- 合理设置 Worker 数量

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 使用 black 进行代码格式化
- 使用 mypy 进行类型检查
- 编写单元测试
- 更新文档

## 许可证

本项目仅用于学习和教学目的。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件
- 参与讨论

---

**注意**: 这是一个教学项目，主要用于学习 FastAPI 和现代 Python Web 开发技术。生产环境使用前请进行充分的安全评估和性能测试。