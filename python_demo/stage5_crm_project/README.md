# 第五阶段：CRM 实战项目

## 项目简介

本阶段通过一个完整的 CRM（客户关系管理）系统项目，综合运用前四个阶段学到的所有知识，包括 Web 框架、数据库、安全认证、中间件、异步任务、测试和 CI/CD 等企业级开发技能。

CRM 项目采用前后端分离架构，提供 FastAPI 和 Flask 两个后端版本供学员选择学习，前端基于 PureAdminThin 框架（Vue 3）。

## 学习目标

完成本阶段学习后，你将能够：

- ✅ 独立设计和实现完整的企业级 Web 应用
- ✅ 掌握前后端分离架构的开发模式
- ✅ 实现基于 RBAC 的权限管理系统
- ✅ 使用异步任务处理耗时操作
- ✅ 集成中间件实现日志、追踪等功能
- ✅ 编写自动化测试保证代码质量
- ✅ 使用 Docker 容器化部署应用
- ✅ 配置 CI/CD 实现自动化构建和部署

## 前置知识

在开始本阶段学习前，你应该已经掌握：

- ✅ Python 基础语法和面向对象编程（第一阶段）
- ✅ FastAPI 或 Flask 框架的使用（第二阶段）
- ✅ 数据库设计和 ORM 操作（第二阶段）
- ✅ JWT 认证和权限控制（第三阶段）
- ✅ 中间件和异步任务（第三阶段）
- ✅ 单元测试和集成测试（第四阶段）
- ✅ Docker 和 CI/CD 基础（第四阶段）

## 项目功能

### 核心模块

1. **员工管理**
   - 员工信息的增删改查
   - 员工搜索和分页
   - 员工状态管理

2. **岗位管理**
   - 岗位信息维护
   - 岗位层级关系
   - 岗位编码管理

3. **菜单管理**
   - 菜单树形结构
   - 菜单路由配置
   - 菜单图标和组件

4. **角色管理**
   - 角色信息维护
   - 角色编码管理
   - 角色描述

5. **权限管理**
   - 角色与菜单权限绑定
   - 细粒度权限控制（查看、创建、更新、删除）
   - 权限验证

6. **工作日志**
   - 日志记录（工作内容、完成情况、问题、计划）
   - 自评和上级评分
   - 日志导出（Excel 格式）

### 技术特性

- **认证授权**: JWT Token 认证 + RBAC 权限控制
- **异步任务**: Celery + Redis 实现日志导出
- **中间件**: 请求日志、Request ID、错误处理
- **可观测性**: 结构化日志、请求追踪
- **API 文档**: 自动生成的交互式 API 文档
- **容器化**: Docker 和 Docker Compose 部署
- **CI/CD**: GitHub Actions 自动化测试和部署

## 项目结构

```
stage5_crm_project/
├── README.md                      # 本文件
├── requirements.md                # 项目需求文档
├── architecture.md                # 架构设计文档
├── backend/                       # 后端项目
│   ├── fastapi_version/          # FastAPI 版本实现
│   └── flask_version/            # Flask 版本实现
├── frontend/                      # 前端项目
│   └── pure-admin-thin/          # Vue 3 前端
├── docs/                          # 项目文档
│   ├── api_documentation.md      # API 文档
│   ├── database_schema.md        # 数据库设计
│   ├── deployment_guide.md       # 部署指南
│   └── user_manual.md            # 用户手册
└── .github/                       # CI/CD 配置
    └── workflows/                 # GitHub Actions 工作流
```

## 快速开始

### 选择后端框架

本项目提供两个后端实现版本：

**FastAPI 版本**（推荐）
- 现代异步框架
- 自动生成 API 文档
- 类型提示和数据验证
- 高性能

**Flask 版本**
- 成熟稳定的框架
- 生态丰富
- 灵活可扩展
- 企业应用广泛

建议先学习一个版本，掌握后再对比学习另一个版本。

### 学习路径

1. **阅读文档**（1-2 天）
   - 阅读 `requirements.md` 了解项目需求
   - 阅读 `architecture.md` 理解系统架构
   - 阅读 `docs/database_schema.md` 了解数据模型

2. **搭建开发环境**（半天）
   - 安装 Python 3.9+
   - 安装 PostgreSQL 或 MySQL
   - 安装 Redis
   - 创建虚拟环境

3. **后端开发**（5-7 天）
   - 实现数据模型
   - 实现认证授权
   - 实现核心业务模块
   - 实现异步任务
   - 编写测试

4. **前端集成**（2-3 天）
   - 配置前端项目
   - 实现页面和组件
   - 对接后端 API

5. **部署上线**（1-2 天）
   - Docker 容器化
   - 配置 CI/CD
   - 部署到服务器

## 开发环境要求

### 必需软件

- Python 3.9 或更高版本
- PostgreSQL 13+ 或 MySQL 8+
- Redis 6+
- Node.js 16+ (前端开发)
- Docker 和 Docker Compose (可选，用于容器化部署)

### 推荐工具

- PyCharm Professional 或 VSCode
- Postman 或 Insomnia (API 测试)
- DBeaver 或 pgAdmin (数据库管理)
- Git (版本控制)

## 学习资源

### 官方文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Celery 文档](https://docs.celeryproject.org/)
- [Vue 3 文档](https://vuejs.org/)

### 参考项目

- [FastAPI 最佳实践](https://github.com/zhanymkanov/fastapi-best-practices)
- [Flask 大型应用结构](https://flask.palletsprojects.com/patterns/packages/)
- [PureAdmin 官方示例](https://github.com/pure-admin/vue-pure-admin)

### 视频教程

- FastAPI 完整教程（推荐 B 站搜索）
- Flask 企业级开发
- Vue 3 前端开发

## 常见问题

### Q: 应该选择 FastAPI 还是 Flask？

A: 如果你是新手或追求现代化开发体验，推荐 FastAPI。如果你需要更成熟的生态或公司使用 Flask，选择 Flask。两者都值得学习。

### Q: 前端必须使用 PureAdminThin 吗？

A: 不是必须的。你可以使用任何前端框架，甚至可以只开发后端 API。PureAdminThin 只是一个推荐的管理后台模板。

### Q: 数据库可以使用 SQLite 吗？

A: 开发阶段可以使用 SQLite，但生产环境建议使用 PostgreSQL 或 MySQL。

### Q: 需要部署到云服务器吗？

A: 不是必须的。你可以在本地运行和测试。如果想要真实的部署体验，可以使用免费的云服务（如 Heroku、Railway）。

## 项目亮点

本 CRM 项目的特色：

1. **真实的企业级架构**: 不是简单的 CRUD，而是完整的企业应用架构
2. **完整的权限系统**: RBAC 权限模型，可直接应用到实际项目
3. **异步任务处理**: 学习处理耗时操作的最佳实践
4. **可观测性**: 日志、追踪、监控等生产环境必备能力
5. **自动化测试**: 单元测试和集成测试保证代码质量
6. **容器化部署**: Docker 部署方案，一键启动
7. **CI/CD 流程**: 自动化构建、测试、部署
8. **双框架实现**: 对比学习 FastAPI 和 Flask

## 下一步

1. 阅读 [项目需求文档](requirements.md)
2. 阅读 [架构设计文档](architecture.md)
3. 查看 [数据库设计](docs/database_schema.md)
4. 选择后端框架开始开发

## 学习建议

- **循序渐进**: 不要急于求成，按照模块逐步实现
- **理解原理**: 不要只是复制代码，要理解每个设计决策
- **动手实践**: 边学边做，遇到问题及时查文档
- **代码规范**: 保持良好的代码风格和注释习惯
- **测试驱动**: 养成编写测试的习惯
- **版本控制**: 使用 Git 管理代码，记录开发过程

祝你学习愉快！如有问题，请查看故障排除指南或在社区提问。
