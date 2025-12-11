# Flask CRM 系统

基于 Flask 的客户关系管理系统，包含完整的认证授权功能和异步任务处理。

## 功能特性

- **用户认证**: JWT 令牌认证，支持登录、注册、令牌刷新
- **权限控制**: 基于角色的访问控制 (RBAC)，支持菜单级权限管理
- **员工管理**: 员工信息的 CRUD 操作，支持搜索和分页
- **岗位管理**: 支持层级结构的岗位管理
- **菜单管理**: 树形结构的菜单管理
- **角色管理**: 角色的创建和权限分配
- **工作日志**: 员工工作日志记录和评分系统
- **异步任务**: 基于 Celery 的异步任务处理，支持工作日志导出
- **中间件**: 请求日志、Request ID、错误处理中间件

## 技术栈

- **Web 框架**: Flask 3.0
- **数据库 ORM**: SQLAlchemy
- **数据库迁移**: Flask-Migrate
- **认证**: Flask-JWT-Extended
- **跨域**: Flask-CORS
- **异步任务**: Celery + Redis
- **Excel 导出**: openpyxl
- **数据库**: SQLite (默认) / PostgreSQL / MySQL

## 项目结构

```
flask_version/
├── app/                        # 应用主目录
│   ├── __init__.py            # 应用工厂
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py           # 基础模型
│   │   ├── employee.py       # 员工模型
│   │   ├── position.py       # 岗位模型
│   │   ├── menu.py           # 菜单模型
│   │   ├── role.py           # 角色模型
│   │   ├── role_menu_permission.py  # 权限模型
│   │   └── work_log.py       # 工作日志模型
│   ├── api/                   # API 蓝图
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证 API
│   │   ├── employees.py      # 员工 API
│   │   ├── positions.py      # 岗位 API
│   │   ├── menus.py          # 菜单 API
│   │   ├── roles.py          # 角色 API
│   │   ├── permissions.py    # 权限 API
│   │   ├── work_logs.py      # 工作日志 API
│   │   └── tasks.py          # 任务 API
│   ├── auth/                  # 认证模块
│   │   ├── __init__.py
│   │   ├── auth_service.py   # 认证服务
│   │   ├── jwt_handler.py    # JWT 处理
│   │   └── decorators.py     # 认证装饰器
│   ├── middleware/            # 中间件
│   │   ├── __init__.py
│   │   ├── request_logging.py # 请求日志
│   │   ├── request_id.py     # Request ID
│   │   └── error_handler.py  # 错误处理
│   └── tasks/                 # 异步任务
│       ├── __init__.py
│       ├── celery_app.py     # Celery 配置
│       └── work_log_tasks.py # 工作日志任务
├── app.py                     # 应用入口
├── requirements.txt           # 依赖列表
├── .env.example              # 环境变量示例
└── README.md                 # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，修改相应配置
```

### 3. 初始化数据库

```bash
# 初始化数据库
flask init-db

# 创建示例数据
flask create-sample-data
```

### 4. 启动应用

```bash
# 启动 Flask 应用
python app.py

# 或使用 Flask CLI
flask run --host=0.0.0.0 --port=5000
```

### 5. 启动 Celery Worker (可选)

如果需要使用异步任务功能：

```bash
# 启动 Redis (需要先安装 Redis)
redis-server

# 启动 Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info

# 启动 Celery Beat (定时任务)
celery -A app.tasks.celery_app beat --loglevel=info
```

## API 文档

### 认证相关

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/change-password` - 修改密码
- `POST /api/auth/register` - 用户注册（演示用）

### 员工管理

- `GET /api/employees` - 获取员工列表
- `POST /api/employees` - 创建员工
- `GET /api/employees/{id}` - 获取员工详情
- `PUT /api/employees/{id}` - 更新员工信息
- `DELETE /api/employees/{id}` - 删除员工

### 岗位管理

- `GET /api/positions` - 获取岗位列表
- `POST /api/positions` - 创建岗位
- `PUT /api/positions/{id}` - 更新岗位
- `DELETE /api/positions/{id}` - 删除岗位

### 菜单管理

- `GET /api/menus` - 获取菜单树
- `POST /api/menus` - 创建菜单
- `PUT /api/menus/{id}` - 更新菜单
- `DELETE /api/menus/{id}` - 删除菜单

### 角色管理

- `GET /api/roles` - 获取角色列表
- `POST /api/roles` - 创建角色
- `PUT /api/roles/{id}` - 更新角色
- `DELETE /api/roles/{id}` - 删除角色

### 权限管理

- `GET /api/permissions/roles/{role_id}` - 获取角色权限
- `POST /api/permissions/roles/{role_id}/menus/{menu_id}` - 分配权限
- `DELETE /api/permissions/roles/{role_id}/menus/{menu_id}` - 移除权限

### 工作日志

- `GET /api/work-logs` - 获取工作日志列表
- `POST /api/work-logs` - 创建工作日志
- `POST /api/work-logs/{id}/rating` - 为日志评分
- `GET /api/work-logs/statistics` - 获取统计信息

### 异步任务

- `POST /api/tasks/export-work-logs` - 启动导出任务
- `GET /api/tasks/{task_id}/status` - 获取任务状态
- `GET /api/tasks/{task_id}/download` - 下载任务结果

## 演示接口

应用提供了一些无需认证的演示接口：

- `GET /` - API 信息
- `GET /health` - 健康检查
- `GET /demo/employees` - 演示员工数据
- `GET /demo/positions` - 演示岗位数据
- `GET /demo/menus` - 演示菜单数据
- `GET /demo/work-logs` - 演示工作日志数据
- `GET /demo/statistics` - 演示统计数据

## 默认账号

创建示例数据后，可以使用以下账号登录：

- 用户名: `admin`
- 密码: `admin123`

## 数据库配置

### SQLite (默认)

```
DATABASE_URL=sqlite:///crm_flask.db
```

### PostgreSQL

```
DATABASE_URL=postgresql://username:password@localhost:5432/crm_flask
```

### MySQL

```
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/crm_flask
```

## 部署

### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 开发说明

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 遵循 PEP 8 编码规范

### 测试

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app
```

### 数据库迁移

```bash
# 初始化迁移
flask db init

# 生成迁移文件
flask db migrate -m "描述信息"

# 应用迁移
flask db upgrade
```

## 注意事项

1. **安全性**: 生产环境中请修改默认的密钥和密码
2. **数据库**: 生产环境建议使用 PostgreSQL 或 MySQL
3. **Redis**: 异步任务功能需要 Redis 支持
4. **日志**: 生产环境中配置适当的日志级别
5. **CORS**: 根据前端域名配置 CORS 策略

## 许可证

本项目仅用于学习和演示目的。