# 第二阶段：Web 框架与数据库

## 阶段简介

欢迎来到第二阶段！在这个阶段，你将学习 Python 的主流 Web 框架（FastAPI 和 Flask）以及数据库操作。通过本阶段的学习，你将能够开发完整的 Web 应用程序，包括 API 接口、数据库集成和 CRUD 操作。

## 学习目标

完成本阶段学习后，你将能够：

1. 理解 Web 框架的工作原理
2. 使用 FastAPI 开发高性能的异步 API
3. 使用 Flask 开发传统的 Web 应用
4. 掌握 SQL 基础知识和数据库操作
5. 使用 SQLAlchemy ORM 进行数据库操作
6. 实现完整的 CRUD 功能
7. 理解前后端分离架构
8. 掌握 RESTful API 设计原则

## 前置知识

在开始本阶段学习前，你应该已经掌握：

- Python 基础语法（变量、数据类型、控制流）
- 函数和类的使用
- 模块和包的概念
- 文件操作
- 虚拟环境的创建和使用

如果还没有掌握这些知识，请先完成 [第一阶段：Python 基础](../stage1_basics/README.md)。

## 学习内容

### 1. FastAPI 框架

FastAPI 是一个现代、快速（高性能）的 Web 框架，用于构建 API。

**学习路径:**

1. **基础教程** (`fastapi/tutorials/`)
   - Hello World 和基本路由
   - 路径参数和查询参数
   - 请求体和响应模型
   - 数据库集成
   - ORM 模型使用

2. **CRUD 项目** (`fastapi/crud_project/`)
   - 完整的项目结构
   - 数据模型定义
   - API 路由实现
   - 数据库操作
   - 请求验证

**特点:**
- 基于 Python 类型提示
- 自动生成 API 文档（Swagger UI）
- 高性能（基于 Starlette 和 Pydantic）
- 原生支持异步操作
- 现代化的开发体验

**适用场景:**
- RESTful API 开发
- 微服务架构
- 高性能要求的应用
- 需要自动文档生成的项目

### 2. Flask 框架

Flask 是一个轻量级的 Web 框架，简单易学，生态丰富。

**学习路径:**

1. **基础教程** (`flask/tutorials/`)
   - Hello World 和路由
   - 模板渲染
   - 数据库集成
   - ORM 模型使用

2. **CRUD 项目** (`flask/crud_project/`)
   - 完整的项目结构
   - 蓝图（Blueprint）使用
   - 数据库操作
   - 表单处理

**特点:**
- 简单易学
- 灵活可扩展
- 丰富的扩展生态
- 成熟稳定

**适用场景:**
- 中小型 Web 应用
- 快速原型开发
- 传统的服务端渲染应用
- 需要高度定制的项目

### 3. 数据库

数据库是 Web 应用的核心组件，用于持久化存储数据。

**学习路径:**

1. **SQL 基础** (`database/sql_basics.md`)
   - 数据库基础概念
   - DDL（数据定义语言）
   - DML（数据操作语言）
   - DQL（数据查询语言）
   - 索引和事务
   - 常用函数

2. **ORM 使用指南** (`database/orm_guide.md`)
   - ORM 概念和优势
   - SQLAlchemy 基础
   - 模型定义
   - CRUD 操作
   - 关系查询
   - 高级查询技巧

3. **示例代码** (`database/examples/`)
   - 基础 CRUD 操作
   - 关系查询
   - 高级查询技巧

**支持的数据库:**
- SQLite（开发环境）
- MySQL（生产环境）
- PostgreSQL（生产环境）

## 目录结构

```
stage2_frameworks/
├── README.md                          # 本文件
├── checklist.md                       # 知识点检查清单
│
├── fastapi/                           # FastAPI 学习模块
│   ├── README.md                      # FastAPI 模块说明
│   ├── resources.md                   # 学习资源链接
│   ├── tutorials/                     # 基础教程
│   │   ├── 01_hello_world.py
│   │   ├── 02_routing.py
│   │   ├── 03_request_response.py
│   │   ├── 04_database_integration.py
│   │   └── 05_orm_models.py
│   └── crud_project/                  # CRUD 示例项目
│       ├── app/
│       ├── requirements.txt
│       ├── README.md
│       └── run.py
│
├── flask/                             # Flask 学习模块
│   ├── README.md                      # Flask 模块说明
│   ├── resources.md                   # 学习资源链接
│   ├── tutorials/                     # 基础教程
│   │   ├── 01_hello_world.py
│   │   ├── 02_routing.py
│   │   ├── 03_templates.py
│   │   ├── 04_database_integration.py
│   │   └── 05_orm_models.py
│   └── crud_project/                  # CRUD 示例项目
│       ├── app/
│       ├── requirements.txt
│       ├── README.md
│       └── run.py
│
└── database/                          # 数据库学习模块
    ├── sql_basics.md                  # SQL 基础教程
    ├── orm_guide.md                   # ORM 使用指南
    └── examples/                      # 示例代码
        ├── README.md
        ├── 01_basic_crud.py
        ├── 02_relationships.py
        └── 03_advanced_queries.py
```

## 学习建议

### 学习顺序

1. **数据库基础** (1-2 周)
   - 先学习 SQL 基础知识
   - 理解数据库的基本概念
   - 练习基本的 SQL 语句

2. **ORM 学习** (1 周)
   - 学习 SQLAlchemy ORM
   - 运行数据库示例代码
   - 理解 ORM 的优势和使用场景

3. **FastAPI 学习** (2-3 周)
   - 按顺序学习 FastAPI 教程
   - 运行和修改示例代码
   - 完成 CRUD 项目
   - 理解异步编程概念

4. **Flask 学习** (2-3 周)
   - 按顺序学习 Flask 教程
   - 对比 FastAPI 和 Flask 的差异
   - 完成 CRUD 项目
   - 理解模板渲染

5. **综合实践** (1-2 周)
   - 选择一个框架深入学习
   - 开发自己的小项目
   - 完成知识点检查清单

### 学习方法

1. **理论学习**
   - 阅读文档和教程
   - 理解框架的设计理念
   - 学习最佳实践

2. **动手实践**
   - 运行所有示例代码
   - 修改代码观察变化
   - 尝试实现新功能

3. **项目驱动**
   - 从简单项目开始
   - 逐步增加复杂度
   - 完成完整的 CRUD 应用

4. **对比学习**
   - 对比 FastAPI 和 Flask
   - 理解各自的优势和适用场景
   - 选择适合自己的框架

### 实践项目建议

1. **博客系统**
   - 文章的增删改查
   - 分类和标签
   - 评论功能

2. **任务管理系统**
   - 任务的创建和管理
   - 任务状态跟踪
   - 用户分配

3. **图书管理系统**
   - 图书信息管理
   - 借阅记录
   - 用户管理

4. **API 服务**
   - 天气查询 API
   - 数据统计 API
   - 文件上传 API

## 开发环境

### 必需工具

- Python 3.9+
- 代码编辑器（PyCharm 或 VSCode）
- 数据库客户端（可选）

### 推荐安装

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装 FastAPI 相关
pip install fastapi uvicorn sqlalchemy pydantic

# 安装 Flask 相关
pip install flask flask-sqlalchemy

# 安装数据库驱动
pip install pymysql psycopg2-binary

# 开发工具
pip install black flake8 pytest
```

## 学习资源

### 官方文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [Pydantic 官方文档](https://docs.pydantic.dev/)

### 视频教程

- [FastAPI 入门教程](https://www.youtube.com/results?search_query=fastapi+tutorial)
- [Flask 入门教程](https://www.youtube.com/results?search_query=flask+tutorial)
- [SQL 基础教程](https://www.youtube.com/results?search_query=sql+tutorial)

### 推荐书籍

- 《Flask Web 开发实战》
- 《Python Web 开发实战》
- 《SQL 必知必会》

### 在线资源

- [FastAPI 中文文档](https://fastapi.tiangolo.com/zh/)
- [Flask 中文文档](https://dormousehole.readthedocs.io/)
- [SQLAlchemy 中文教程](https://www.osgeo.cn/sqlalchemy/)

## 常见问题

### 1. FastAPI 和 Flask 应该学哪个？

**建议**: 两个都学，但可以有侧重。

- 如果你想开发现代化的 API 服务，优先学习 FastAPI
- 如果你想快速上手或需要服务端渲染，优先学习 Flask
- 两个框架的核心概念相似，学会一个后学另一个会很快

### 2. 需要深入学习 SQL 吗？

**建议**: 需要掌握基础，但不必深入。

- 理解基本的 CRUD 操作
- 了解 JOIN、聚合函数等常用功能
- 复杂查询可以使用 ORM 或在需要时学习

### 3. ORM 和原生 SQL 哪个更好？

**建议**: 根据场景选择。

- 日常开发优先使用 ORM（提高效率、防止 SQL 注入）
- 复杂查询或性能关键的地方可以使用原生 SQL
- 理解 ORM 生成的 SQL 语句

### 4. 如何选择数据库？

**建议**:
- 开发环境：SQLite（无需安装，方便快捷）
- 生产环境：MySQL 或 PostgreSQL
- 学习阶段：SQLite 足够

### 5. 异步编程难吗？

**建议**:
- FastAPI 的异步是可选的，初学者可以先用同步方式
- 理解基本概念后再深入学习异步
- 对于 I/O 密集型应用，异步能显著提升性能

## 下一步

完成本阶段学习后，你可以：

1. 进入 [第三阶段：企业特性](../stage3_enterprise/README.md)
   - 学习安全认证和授权
   - 掌握中间件开发
   - 了解可观测性和异步任务

2. 深入学习当前阶段
   - 开发更复杂的项目
   - 学习框架的高级特性
   - 优化数据库性能

3. 参与开源项目
   - 阅读优秀项目的源码
   - 贡献代码或文档
   - 学习最佳实践

## 获取帮助

遇到问题时：

1. 查看本阶段的文档和示例代码
2. 阅读官方文档
3. 搜索 Stack Overflow
4. 查看 GitHub Issues
5. 参考 [故障排除指南](../../common/troubleshooting.md)

祝学习愉快！🚀
