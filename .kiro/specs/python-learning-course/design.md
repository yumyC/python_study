# Python 学习课程体系设计文档

## 概述

本设计文档描述了一个完整的 Python 学习课程体系的实现方案。该课程体系采用渐进式学习路径，从基础环境搭建到企业级项目实战，通过五个阶段帮助学员系统掌握 Python Web 开发技能。

课程体系将在 `python_demo` 文件夹中实现，采用模块化设计，每个阶段独立组织，便于学员按顺序学习和教师维护更新。

## 架构

### 整体架构

课程体系采用分层递进式架构，每个阶段建立在前一阶段的基础之上：

```
第一阶段：基础层 (Foundation Layer)
    ↓
第二阶段：框架层 (Framework Layer)
    ↓
第三阶段：企业特性层 (Enterprise Features Layer)
    ↓
第四阶段：工程化层 (Engineering Layer)
    ↓
第五阶段：实战层 (Practice Layer)
    ↓
进阶选学：专业方向层 (Advanced Specialization Layer)
```

### 目录结构设计

```
python_demo/
├── README.md                          # 课程总览和学习路径指南
├── LEARNING_PATH.md                   # 详细学习路径图
├── stage1_basics/                     # 第一阶段：Python 基础
│   ├── README.md
│   ├── setup/                         # 环境搭建
│   │   ├── python_installation.md
│   │   ├── pycharm_setup.md
│   │   ├── vscode_setup.md
│   │   └── virtual_env_guide.md
│   ├── tutorials/                     # 基础教程
│   │   ├── 01_variables_and_types.py
│   │   ├── 02_control_flow.py
│   │   ├── 03_functions.py
│   │   ├── 04_classes_and_objects.py
│   │   ├── 05_modules_and_packages.py
│   │   └── 06_file_operations.py
│   ├── projects/                      # 实践项目
│   │   ├── project1_calculator/
│   │   ├── project2_todo_list/
│   │   └── project3_file_manager/
│   ├── resources/                     # 学习资源
│   │   └── links.md
│   └── checklist.md                   # 知识点检查清单
│
├── stage2_frameworks/                 # 第二阶段：框架与数据库
│   ├── README.md
│   ├── fastapi/                       # FastAPI 学习模块
│   │   ├── README.md
│   │   ├── tutorials/
│   │   │   ├── 01_hello_world.py
│   │   │   ├── 02_routing.py
│   │   │   ├── 03_request_response.py
│   │   │   ├── 04_database_integration.py
│   │   │   └── 05_orm_models.py
│   │   ├── crud_project/              # CRUD 示例项目
│   │   │   ├── app/
│   │   │   ├── requirements.txt
│   │   │   ├── README.md
│   │   │   └── run.py
│   │   └── resources.md
│   ├── flask/                         # Flask 学习模块
│   │   ├── README.md
│   │   ├── tutorials/
│   │   │   ├── 01_hello_world.py
│   │   │   ├── 02_routing.py
│   │   │   ├── 03_templates.py
│   │   │   ├── 04_database_integration.py
│   │   │   └── 05_orm_models.py
│   │   ├── crud_project/              # CRUD 示例项目
│   │   │   ├── app/
│   │   │   ├── requirements.txt
│   │   │   ├── README.md
│   │   │   └── run.py
│   │   └── resources.md
│   ├── database/                      # 数据库学习模块
│   │   ├── sql_basics.md
│   │   ├── orm_guide.md
│   │   └── examples/
│   └── checklist.md
│
├── stage3_enterprise/                 # 第三阶段：企业特性
│   ├── README.md
│   ├── security/                      # 安全模块
│   │   ├── README.md
│   │   ├── fastapi_security/
│   │   │   ├── 01_authentication.py
│   │   │   ├── 02_authorization.py
│   │   │   ├── 03_jwt_tokens.py
│   │   │   └── 04_oauth2.py
│   │   ├── flask_security/
│   │   │   ├── 01_authentication.py
│   │   │   ├── 02_authorization.py
│   │   │   ├── 03_jwt_tokens.py
│   │   │   └── 04_session_management.py
│   │   └── resources.md
│   ├── middleware/                    # 中间件模块
│   │   ├── README.md
│   │   ├── 01_request_logging.py
│   │   ├── 02_error_handler.py
│   │   ├── 03_request_id_injection.py
│   │   ├── 04_cors_middleware.py
│   │   └── examples/
│   ├── observability/                 # 可观测性模块
│   │   ├── README.md
│   │   ├── 01_logging_setup.py
│   │   ├── 02_metrics_collection.py
│   │   ├── 03_tracing.py
│   │   └── integration_examples/
│   ├── async_tasks/                   # 异步任务模块
│   │   ├── README.md
│   │   ├── 01_celery_basics.py
│   │   ├── 02_task_queue.py
│   │   ├── 03_scheduled_tasks.py
│   │   └── examples/
│   └── checklist.md
│
├── stage4_cicd/                       # 第四阶段：测试与 CI/CD
│   ├── README.md
│   ├── testing/                       # 测试模块
│   │   ├── README.md
│   │   ├── 01_unit_testing.py
│   │   ├── 02_integration_testing.py
│   │   ├── 03_test_fixtures.py
│   │   ├── 04_mocking.py
│   │   └── examples/
│   ├── cicd/                          # CI/CD 模块
│   │   ├── README.md
│   │   ├── github_actions/
│   │   │   ├── basic_workflow.yml
│   │   │   ├── test_workflow.yml
│   │   │   ├── build_workflow.yml
│   │   │   └── deploy_workflow.yml
│   │   ├── video_tutorial.md
│   │   └── best_practices.md
│   ├── docker/                        # Docker 模块
│   │   ├── README.md
│   │   ├── Dockerfile.example
│   │   ├── docker-compose.yml.example
│   │   └── deployment_guide.md
│   └── checklist.md
│
├── stage5_crm_project/                # 第五阶段：CRM 实战项目
│   ├── README.md
│   ├── requirements.md                # 项目需求文档
│   ├── architecture.md                # 架构设计文档
│   ├── backend/                       # 后端项目
│   │   ├── fastapi_version/           # FastAPI 版本
│   │   │   ├── app/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py
│   │   │   │   ├── models/            # 数据模型
│   │   │   │   ├── schemas/           # Pydantic 模式
│   │   │   │   ├── api/               # API 路由
│   │   │   │   ├── services/          # 业务逻辑
│   │   │   │   ├── middleware/        # 中间件
│   │   │   │   ├── auth/              # 认证授权
│   │   │   │   └── tasks/             # 异步任务
│   │   │   ├── tests/
│   │   │   ├── requirements.txt
│   │   │   ├── Dockerfile
│   │   │   ├── docker-compose.yml
│   │   │   └── README.md
│   │   └── flask_version/             # Flask 版本
│   │       ├── app/
│   │       ├── tests/
│   │       ├── requirements.txt
│   │       ├── Dockerfile
│   │       ├── docker-compose.yml
│   │       └── README.md
│   ├── frontend/                      # 前端项目
│   │   ├── pure-admin-thin/
│   │   │   ├── src/
│   │   │   ├── public/
│   │   │   ├── package.json
│   │   │   └── README.md
│   │   └── integration_guide.md
│   ├── .github/                       # CI/CD 配置
│   │   └── workflows/
│   │       ├── backend_ci.yml
│   │       ├── frontend_ci.yml
│   │       └── deploy.yml
│   ├── docs/                          # 项目文档
│   │   ├── api_documentation.md
│   │   ├── database_schema.md
│   │   ├── deployment_guide.md
│   │   └── user_manual.md
│   └── checklist.md
│
├── advanced_topics/                   # 进阶选学内容
│   ├── README.md
│   ├── web_scraping/                  # 爬虫方向
│   │   ├── README.md
│   │   ├── basics/
│   │   ├── reverse_engineering/
│   │   ├── anti_scraping/
│   │   ├── projects/
│   │   └── resources.md
│   ├── data_processing/               # 数据处理方向
│   │   ├── README.md
│   │   ├── pandas_basics/
│   │   ├── big_data/
│   │   ├── data_analysis/
│   │   ├── projects/
│   │   └── resources.md
│   └── ai_frameworks/                 # AI 框架方向
│       ├── README.md
│       ├── langchain/
│       ├── llamaindex/
│       ├── projects/
│       └── resources.md
│
└── common/                            # 公共资源
    ├── templates/                     # 项目模板
    ├── utils/                         # 工具函数
    ├── configs/                       # 配置示例
    └── troubleshooting.md             # 故障排除指南
```

## 组件和接口

### 1. 文档组件

#### 课程总览文档 (README.md)
- **职责**: 提供课程体系的整体介绍和快速导航
- **内容**:
  - 课程简介和学习目标
  - 五个阶段的概述
  - 前置知识要求
  - 学习建议和时间规划
  - 快速开始指南

#### 学习路径文档 (LEARNING_PATH.md)
- **职责**: 展示详细的学习路径和知识图谱
- **内容**:
  - Mermaid 流程图展示学习路径
  - 每个阶段的学习目标和产出
  - 阶段间的依赖关系
  - 预计学习时间

#### 阶段 README 文档
- **职责**: 每个阶段的详细说明
- **内容**:
  - 阶段学习目标
  - 前置知识要求
  - 学习内容概览
  - 实践项目说明
  - 学习资源链接
  - 下一步建议

#### 知识点检查清单 (checklist.md)
- **职责**: 帮助学员自我评估学习成果
- **内容**:
  - 核心知识点列表
  - 技能掌握程度评估
  - 实践项目完成情况
  - 进入下一阶段的准备度检查

### 2. 代码示例组件

#### 教程示例代码
- **职责**: 演示特定概念或技术的使用
- **特点**:
  - 单文件或小型示例
  - 详细的代码注释
  - 清晰的输出说明
  - 可独立运行

#### 项目示例代码
- **职责**: 提供完整的实践项目
- **特点**:
  - 多文件项目结构
  - 完整的功能实现
  - README 文档说明
  - requirements.txt 依赖管理
  - 运行和测试说明

### 3. CRM 项目组件

#### 核心模块

**员工管理模块 (Employee Management)**
- 数据模型: Employee
- API 端点: /api/employees
- 功能: CRUD 操作、搜索、分页

**岗位管理模块 (Position Management)**
- 数据模型: Position
- API 端点: /api/positions
- 功能: CRUD 操作、岗位层级

**菜单管理模块 (Menu Management)**
- 数据模型: Menu
- API 端点: /api/menus
- 功能: CRUD 操作、树形结构

**角色管理模块 (Role Management)**
- 数据模型: Role
- API 端点: /api/roles
- 功能: CRUD 操作、权限绑定

**权限管理模块 (Permission Management)**
- 数据模型: RoleMenuPermission
- API 端点: /api/permissions
- 功能: 角色-菜单权限绑定

**工作日志模块 (Work Log Management)**
- 数据模型: WorkLog
- API 端点: /api/worklogs
- 功能: CRUD 操作、评分、导出

#### 认证授权组件

**JWT 认证**
- 登录接口: /api/auth/login
- Token 刷新: /api/auth/refresh
- 用户信息: /api/auth/me

**权限控制**
- 基于角色的访问控制 (RBAC)
- 装饰器/依赖注入实现
- 菜单权限验证

#### 异步任务组件

**工作日志导出任务**
- 任务队列: Celery + Redis
- 导出格式: Excel (xlsx)
- 任务状态追踪
- 下载链接生成

#### 中间件组件

**请求日志中间件**
- 记录请求信息
- 响应时间统计
- 错误追踪

**Request ID 中间件**
- 生成唯一请求 ID
- 注入到日志和响应头
- 分布式追踪支持

**错误处理中间件**
- 统一错误响应格式
- 错误日志记录
- 友好的错误信息

## 数据模型

### CRM 项目数据模型

#### Employee (员工)
```python
{
    "id": "UUID",
    "username": "string",
    "email": "string",
    "password_hash": "string",
    "full_name": "string",
    "position_id": "UUID",
    "role_id": "UUID",
    "status": "enum(active, inactive)",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Position (岗位)
```python
{
    "id": "UUID",
    "name": "string",
    "code": "string",
    "description": "string",
    "level": "integer",
    "parent_id": "UUID (nullable)",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Menu (菜单)
```python
{
    "id": "UUID",
    "name": "string",
    "path": "string",
    "icon": "string",
    "component": "string",
    "parent_id": "UUID (nullable)",
    "sort_order": "integer",
    "is_visible": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### Role (角色)
```python
{
    "id": "UUID",
    "name": "string",
    "code": "string",
    "description": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### RoleMenuPermission (角色菜单权限)
```python
{
    "id": "UUID",
    "role_id": "UUID",
    "menu_id": "UUID",
    "permissions": "array[string]",  # ['view', 'create', 'update', 'delete']
    "created_at": "datetime"
}
```

#### WorkLog (工作日志)
```python
{
    "id": "UUID",
    "employee_id": "UUID",
    "log_date": "date",
    "work_content": "text",
    "completion_status": "enum(completed, in_progress, pending)",
    "problems_encountered": "text",
    "tomorrow_plan": "text",
    "self_rating": "integer (1-5)",
    "supervisor_rating": "integer (1-5, nullable)",
    "supervisor_comment": "text (nullable)",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### 数据库关系

```
Employee ──┬── Position (many-to-one)
           ├── Role (many-to-one)
           └── WorkLog (one-to-many)

Role ────── RoleMenuPermission (one-to-many)

Menu ────── RoleMenuPermission (one-to-many)

Position ── Position (self-referencing, parent-child)

Menu ────── Menu (self-referencing, parent-child)
```

## 错误处理

### 错误分类

1. **客户端错误 (4xx)**
   - 400 Bad Request: 请求参数错误
   - 401 Unauthorized: 未认证
   - 403 Forbidden: 无权限
   - 404 Not Found: 资源不存在
   - 422 Unprocessable Entity: 验证失败

2. **服务器错误 (5xx)**
   - 500 Internal Server Error: 服务器内部错误
   - 503 Service Unavailable: 服务不可用

### 错误响应格式

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {},
        "request_id": "uuid"
    }
}
```

### 错误处理策略

1. **全局异常处理器**: 捕获所有未处理的异常
2. **自定义异常类**: 定义业务相关的异常
3. **错误日志记录**: 记录详细的错误信息和堆栈
4. **用户友好提示**: 返回清晰的错误信息

## 测试策略

### 测试层次

1. **单元测试**
   - 测试独立的函数和类
   - 使用 pytest 框架
   - Mock 外部依赖
   - 覆盖率目标: 80%+

2. **集成测试**
   - 测试 API 端点
   - 测试数据库交互
   - 使用测试数据库
   - 测试认证和授权流程

3. **端到端测试**
   - 测试完整的用户流程
   - 模拟真实场景
   - 验证业务逻辑

### 测试工具

- **pytest**: 测试框架
- **pytest-cov**: 代码覆盖率
- **pytest-asyncio**: 异步测试支持
- **httpx**: API 测试客户端
- **factory_boy**: 测试数据工厂

### CI/CD 测试流程

1. 代码提交触发 CI
2. 运行代码质量检查 (flake8, black, mypy)
3. 运行单元测试
4. 运行集成测试
5. 生成覆盖率报告
6. 测试通过后构建 Docker 镜像
7. 部署到测试环境

## 技术栈

### 第一阶段
- Python 3.9+
- PyCharm / VSCode
- venv / virtualenv

### 第二阶段
- FastAPI 0.100+
- Flask 2.3+
- SQLAlchemy 2.0+
- Pydantic 2.0+
- PostgreSQL / MySQL

### 第三阶段
- JWT (python-jose)
- Celery 5.3+
- Redis 4.5+
- Prometheus (可观测性)
- Structlog (日志)

### 第四阶段
- pytest 7.4+
- GitHub Actions
- Docker 24+
- Docker Compose

### 第五阶段
- 所有前述技术
- PureAdminThin (Vue 3)
- Nginx (反向代理)

### 进阶选学
- Scrapy (爬虫)
- Pandas / Polars (数据处理)
- LangChain / LlamaIndex (AI)

## 部署架构

### 开发环境
```
本地开发机
├── Python 虚拟环境
├── 本地数据库
└── 本地 Redis
```

### 生产环境
```
Docker 容器化部署
├── Nginx 容器 (反向代理)
├── 后端 API 容器 (多实例)
├── Celery Worker 容器
├── PostgreSQL 容器
├── Redis 容器
└── 前端静态文件 (Nginx 服务)
```

## 设计决策

### 1. 为什么同时提供 FastAPI 和 Flask 版本？

**决策**: 在第二阶段和 CRM 项目中同时提供两个框架的实现

**理由**:
- FastAPI 是现代异步框架，性能优秀，适合新项目
- Flask 是成熟稳定的框架，生态丰富，企业应用广泛
- 学员可以对比学习，理解不同框架的设计理念
- 增加就业竞争力，适应不同公司的技术栈

### 2. 为什么采用渐进式学习路径？

**决策**: 将课程分为五个递进阶段

**理由**:
- 降低学习曲线，避免一开始就接触复杂概念
- 每个阶段都有明确的学习目标和产出
- 便于学员自我评估和调整学习节奏
- 支持不同基础的学员从适合的阶段开始

### 3. 为什么 CRM 项目包含完整的 RBAC 权限系统？

**决策**: 实现基于角色的访问控制系统

**理由**:
- RBAC 是企业应用的标准权限模型
- 涵盖认证、授权、权限管理等核心概念
- 提供真实的企业级开发经验
- 为学员就业提供可展示的项目经验

### 4. 为什么强调异步任务和可观测性？

**决策**: 在第三阶段专门讲解这些企业特性

**理由**:
- 异步任务是处理耗时操作的标准方案
- 可观测性是生产环境必备能力
- 这些是初级和中级开发者的分水岭
- 提升学员的工程化思维

### 5. 为什么包含 CI/CD 和容器化部署？

**决策**: 第四阶段专注于工程化实践

**理由**:
- DevOps 能力是现代开发者的必备技能
- 自动化测试和部署提高开发效率
- Docker 是主流的部署方案
- 完整的开发到部署流程体验

## 实施注意事项

1. **代码质量**: 所有示例代码必须遵循 PEP 8 规范，使用 black 格式化
2. **文档完整性**: 每个项目必须包含 README 和运行说明
3. **依赖管理**: 使用 requirements.txt 明确列出所有依赖及版本
4. **注释规范**: 关键代码必须有中文注释说明
5. **错误处理**: 示例代码应展示正确的错误处理方式
6. **安全性**: 不在代码中硬编码敏感信息，使用环境变量
7. **可运行性**: 所有示例项目必须能够直接运行，提供测试数据
8. **版本兼容**: 明确 Python 版本要求（建议 3.9+）
