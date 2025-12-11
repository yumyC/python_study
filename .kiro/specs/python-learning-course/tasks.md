# Python 学习课程体系实施任务列表

- [x] 1. 创建课程基础结构和总览文档
  - 在 python_demo 文件夹中创建主目录结构
  - 编写课程总览 README.md，包含课程简介、五个阶段概述、前置知识要求和学习建议
  - 编写 LEARNING_PATH.md，使用 Mermaid 图表展示学习路径和阶段依赖关系
  - 创建 common 公共资源文件夹和故障排除指南
  - _需求: 1.1, 7.1, 7.4_

- [x] 2. 实现第一阶段：Python 基础
- [x] 2.1 创建环境搭建文档
  - 编写 Python 安装指南 (python_installation.md)
  - 编写 PyCharm 虚拟环境设置教程 (pycharm_setup.md)
  - 编写 VSCode 虚拟环境设置教程 (vscode_setup.md)
  - 编写虚拟环境使用指南 (virtual_env_guide.md)
  - _需求: 1.1, 1.2_

- [x] 2.2 编写 Python 基础教程示例代码
  - 创建变量和数据类型示例 (01_variables_and_types.py)，包含详细注释
  - 创建控制流示例 (02_control_flow.py)，演示 if/for/while 语句
  - 创建函数示例 (03_functions.py)，包含参数、返回值、装饰器
  - 创建类和对象示例 (04_classes_and_objects.py)，演示 OOP 概念
  - 创建模块和包示例 (05_modules_and_packages.py)
  - 创建文件操作示例 (06_file_operations.py)
  - _需求: 1.3, 8.1, 8.3_

- [x] 2.3 创建第一阶段实践项目
  - 实现计算器项目 (project1_calculator)，包含基本运算和错误处理
  - 实现待办事项列表项目 (project2_todo_list)，使用文件存储
  - 实现文件管理器项目 (project3_file_manager)，演示文件操作
  - 为每个项目编写 README.md，包含运行说明和学习要点
  - _需求: 1.4, 8.2_

- [x] 2.4 完成第一阶段文档
  - 编写阶段 README.md，说明学习目标和内容概览
  - 创建学习资源链接文档 (resources/links.md)
  - 编写知识点检查清单 (checklist.md)
  - _需求: 1.5, 7.2, 7.5_

- [-] 3. 实现第二阶段：Web 框架与数据库
- [x] 3.1 创建 FastAPI 学习模块
  - 编写 FastAPI 模块 README.md 和资源链接
  - 创建 Hello World 示例 (01_hello_world.py)
  - 创建路由示例 (02_routing.py)，演示路径参数和查询参数
  - 创建请求响应示例 (03_request_response.py)
  - 创建数据库集成示例 (04_database_integration.py)
  - 创建 ORM 模型示例 (05_orm_models.py)，使用 SQLAlchemy
  - _需求: 2.1, 2.6, 8.1_

- [x] 3.2 实现 FastAPI CRUD 示例项目
  - 创建项目结构 (app 文件夹、models、schemas、api)
  - 实现数据模型和数据库配置
  - 实现 CRUD API 端点（创建、读取、更新、删除）
  - 编写 requirements.txt 和项目 README.md
  - 创建 run.py 启动脚本
  - _需求: 2.3, 2.5, 8.2_

- [x] 3.3 创建 Flask 学习模块
  - 编写 Flask 模块 README.md 和资源链接
  - 创建 Hello World 示例 (01_hello_world.py)
  - 创建路由示例 (02_routing.py)
  - 创建模板示例 (03_templates.py)
  - 创建数据库集成示例 (04_database_integration.py)
  - 创建 ORM 模型示例 (05_orm_models.py)
  - _需求: 2.2, 2.6, 8.1_

- [x] 3.4 实现 Flask CRUD 示例项目
  - 创建项目结构 (app 文件夹、models、views、templates)
  - 实现数据模型和数据库配置
  - 实现 CRUD 路由和视图函数
  - 编写 requirements.txt 和项目 README.md
  - 创建 run.py 启动脚本
  - _需求: 2.4, 2.5, 8.2_

- [x] 3.5 创建数据库学习模块和阶段文档
  - 编写 SQL 基础教程 (sql_basics.md)
  - 编写 ORM 使用指南 (orm_guide.md)
  - 创建数据库示例代码
  - 编写阶段 README.md 和知识点检查清单
  - _需求: 2.6, 7.2, 7.5_

- [-] 4. 实现第三阶段：企业特性
- [x] 4.1 创建安全模块
  - 编写安全模块 README.md 和资源文档
  - 实现 FastAPI 认证示例 (01_authentication.py)
  - 实现 FastAPI 授权示例 (02_authorization.py)
  - 实现 FastAPI JWT 令牌示例 (03_jwt_tokens.py)
  - 实现 FastAPI OAuth2 示例 (04_oauth2.py)
  - 实现 Flask 认证、授权、JWT 和会话管理示例
  - _需求: 3.1, 3.2, 3.3, 8.1_

- [x] 4.2 创建中间件模块
  - 编写中间件模块 README.md
  - 实现请求日志中间件 (01_request_logging.py)
  - 实现错误处理中间件 (02_error_handler.py)
  - 实现 Request ID 注入中间件 (03_request_id_injection.py)
  - 实现 CORS 中间件 (04_cors_middleware.py)
  - 创建中间件集成示例
  - _需求: 3.4, 3.5, 8.1_

- [x] 4.3 创建可观测性模块
  - 编写可观测性模块 README.md
  - 实现日志配置示例 (01_logging_setup.py)，使用 structlog
  - 实现指标收集示例 (02_metrics_collection.py)
  - 实现追踪示例 (03_tracing.py)
  - 创建可观测性工具集成示例
  - _需求: 3.7, 8.1_

- [x] 4.4 创建异步任务模块和阶段文档
  - 编写异步任务模块 README.md 和相关文档
  - 实现 Celery 基础示例 (01_celery_basics.py)
  - 实现任务队列示例 (02_task_queue.py)
  - 实现定时任务示例 (03_scheduled_tasks.py)
  - 创建异步任务完整示例
  - 编写阶段 README.md 和知识点检查清单
  - _需求: 3.6, 7.2, 7.5_

- [x] 5. 实现第四阶段：测试与 CI/CD
- [x] 5.1 创建测试模块
  - 编写测试模块 README.md
  - 实现单元测试示例 (01_unit_testing.py)，使用 pytest
  - 实现集成测试示例 (02_integration_testing.py)
  - 实现测试夹具示例 (03_test_fixtures.py)
  - 实现 Mock 示例 (04_mocking.py)
  - 创建完整的测试示例项目
  - _需求: 4.1, 8.1_

- [x] 5.2 创建 CI/CD 模块
  - 编写 CI/CD 模块 README.md
  - 创建基础工作流配置 (basic_workflow.yml)
  - 创建测试工作流配置 (test_workflow.yml)
  - 创建构建工作流配置 (build_workflow.yml)
  - 创建部署工作流配置 (deploy_workflow.yml)
  - 编写视频教程说明文档和最佳实践指南
  - _需求: 4.2, 4.3, 4.4_

- [x] 5.3 创建 Docker 模块和阶段文档
  - 编写 Docker 模块 README.md
  - 创建 Dockerfile 示例
  - 创建 docker-compose.yml 示例
  - 编写部署指南文档
  - 编写阶段 README.md 和知识点检查清单
  - _需求: 4.5, 7.2, 7.5_

- [-] 6. 实现第五阶段：CRM 实战项目
- [x] 6.1 创建 CRM 项目基础结构和文档
  - 创建项目目录结构（backend、frontend、docs、.github）
  - 编写项目需求文档 (requirements.md)
  - 编写架构设计文档 (architecture.md)
  - 编写项目总览 README.md
  - 编写数据库模式文档 (database_schema.md)
  - _需求: 5.1, 7.2_

- [x] 6.2 实现 FastAPI 版本的数据模型
  - 创建 Employee 模型（员工管理）
  - 创建 Position 模型（岗位管理）
  - 创建 Menu 模型（菜单管理）
  - 创建 Role 模型（角色管理）
  - 创建 RoleMenuPermission 模型（权限绑定）
  - 创建 WorkLog 模型（工作日志）
  - 配置数据库连接和迁移
  - _需求: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 6.3 实现 FastAPI 版本的认证授权系统
  - 实现 JWT 认证逻辑
  - 实现登录、刷新令牌、获取用户信息接口
  - 实现 RBAC 权限控制装饰器
  - 实现菜单权限验证逻辑
  - _需求: 5.6, 3.3_

- [x] 6.4 实现 FastAPI 版本的核心业务模块
  - 实现员工管理 API（CRUD、搜索、分页）
  - 实现岗位管理 API（CRUD、层级关系）
  - 实现菜单管理 API（CRUD、树形结构）
  - 实现角色管理 API（CRUD）
  - 实现权限管理 API（角色-菜单绑定）
  - 实现工作日志 API（CRUD、评分）
  - _需求: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 6.5 实现 FastAPI 版本的异步任务和中间件
  - 配置 Celery 和 Redis
  - 实现工作日志异步导出任务（Excel 格式）
  - 实现任务状态追踪和下载接口
  - 实现请求日志中间件
  - 实现 Request ID 中间件
  - 实现错误处理中间件
  - _需求: 5.8, 3.4, 3.5_

- [x] 6.6 完成 FastAPI 版本的配置和文档
  - 编写 requirements.txt
  - 创建 Dockerfile 和 docker-compose.yml
  - 编写项目 README.md，包含安装和运行说明
  - 编写 API 文档 (api_documentation.md)
  - _需求: 5.9, 8.2_

- [x] 6.7 实现 Flask 版本的 CRM 项目
  - 创建 Flask 项目结构
  - 实现所有数据模型（与 FastAPI 版本相同）
  - 实现认证授权系统
  - 实现所有核心业务模块
  - 实现异步任务和中间件
  - 编写配置文件和项目文档
  - _需求: 5.1, 5.2-5.8_

- [x] 6.8 创建前端项目集成
  - 创建 PureAdminThin 前端项目结构
  - 配置前端路由和菜单
  - 实现登录页面和认证逻辑
  - 实现员工管理页面
  - 实现岗位、菜单、角色管理页面
  - 实现工作日志管理和导出功能
  - 编写前端集成指南文档
  - _需求: 5.9, 5.10_

- [x] 6.9 创建 CRM 项目的 CI/CD 配置
  - 创建后端 CI 工作流 (backend_ci.yml)
  - 创建前端 CI 工作流 (frontend_ci.yml)
  - 创建部署工作流 (deploy.yml)
  - 配置 Docker 镜像构建和推送
  - 编写部署指南文档
  - _需求: 5.11, 5.12_

- [x] 6.10 完成 CRM 项目文档和检查清单
  - 编写用户手册 (user_manual.md)
  - 完善部署指南
  - 创建项目演示数据和初始化脚本
  - 编写知识点检查清单
  - _需求: 7.5, 8.2_

- [-] 7. 实现进阶选学内容
- [x] 7.1 创建爬虫方向学习模块
  - 编写爬虫模块 README.md 和资源文档
  - 创建爬虫基础教程和示例
  - 创建逆向工程示例
  - 创建反爬破解示例
  - 实现至少一个完整的爬虫项目
  - _需求: 6.1, 6.4_

- [x] 7.2 创建数据处理方向学习模块
  - 编写数据处理模块 README.md 和资源文档
  - 创建 Pandas 基础教程和示例
  - 创建大数据处理示例
  - 创建数据分析示例
  - 实现至少一个完整的数据分析项目
  - _需求: 6.2, 6.4_

- [x] 7.3 创建 AI 框架方向学习模块
  - 编写 AI 框架模块 README.md 和资源文档
  - 创建 LangChain 教程和示例
  - 创建 LlamaIndex 教程和示例
  - 实现至少一个完整的 AI 应用项目
  - 提供社区资源链接
  - _需求: 6.3, 6.4, 6.5_

- [x] 8. 最终审查和优化
  - 检查所有代码是否遵循 PEP 8 规范
  - 确保所有文档完整且格式统一
  - 检查所有 requirements.txt 文件的依赖版本
  - 添加常见问题解答到故障排除指南
  - 验证所有学习路径和检查清单的准确性
  - _需求: 8.1, 8.2, 8.3, 8.4, 8.5_
