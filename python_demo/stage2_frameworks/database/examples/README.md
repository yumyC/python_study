# 数据库示例代码

本目录包含 SQLAlchemy ORM 的实践示例代码，帮助你理解和掌握数据库操作。

## 示例列表

### 01_basic_crud.py - 基础 CRUD 操作

演示最基本的数据库操作：

- 创建数据库连接
- 定义数据模型
- 创建记录 (Create)
- 查询记录 (Read)
- 更新记录 (Update)
- 删除记录 (Delete)

**运行方式:**
```bash
python 01_basic_crud.py
```

**学习要点:**
- SQLAlchemy 基本配置
- 模型定义和表创建
- 会话管理
- 基本的增删改查操作

### 02_relationships.py - 关系查询

演示表之间的关系定义和查询：

- 一对多关系（岗位-员工）
- 多对一关系（员工-岗位）
- 关系查询和预加载
- JOIN 查询
- 聚合统计

**运行方式:**
```bash
python 02_relationships.py
```

**学习要点:**
- 外键定义
- relationship 配置
- 关系查询技巧
- 避免 N+1 查询问题
- 聚合函数使用

### 03_advanced_queries.py - 高级查询

演示复杂的查询技巧：

- 聚合查询（COUNT, SUM, AVG, MAX, MIN）
- 子查询
- 复杂过滤条件（AND, OR, IN, LIKE, BETWEEN）
- 排序和分页
- CASE 表达式
- 分组和 HAVING 子句

**运行方式:**
```bash
python 03_advanced_queries.py
```

**学习要点:**
- 聚合函数和分组
- 子查询的使用场景
- 复杂条件组合
- 分页实现
- 条件表达式

## 运行环境

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install sqlalchemy
```

### 数据库选择

示例代码默认使用 SQLite 数据库（无需额外安装），会在当前目录生成 `.db` 文件。

如果要使用其他数据库，需要安装相应的驱动：

```bash
# MySQL
pip install pymysql

# PostgreSQL
pip install psycopg2-binary
```

然后修改代码中的 `DATABASE_URL`：

```python
# MySQL
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/database_name"

# PostgreSQL
DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/database_name"
```

## 学习建议

### 学习顺序

1. 先学习 `sql_basics.md`，理解 SQL 基础概念
2. 阅读 `orm_guide.md`，了解 ORM 的原理和优势
3. 按顺序运行示例代码：
   - 01_basic_crud.py
   - 02_relationships.py
   - 03_advanced_queries.py
4. 修改示例代码，尝试不同的查询和操作
5. 在 FastAPI/Flask 项目中应用所学知识

### 实践建议

1. **阅读代码**: 仔细阅读每个示例的代码和注释
2. **运行示例**: 运行代码，观察输出结果
3. **修改实验**: 修改代码参数，观察变化
4. **独立实现**: 尝试不看代码，独立实现类似功能
5. **查看 SQL**: 设置 `echo=True` 查看生成的 SQL 语句

### 常见问题

#### 1. 数据库文件在哪里？

SQLite 数据库文件会在运行目录生成，文件名如 `employees.db`、`relationships.db` 等。

#### 2. 如何清空数据重新运行？

删除 `.db` 文件，重新运行示例即可。

```bash
rm *.db
python 01_basic_crud.py
```

#### 3. 如何查看数据库内容？

可以使用 SQLite 客户端工具：

```bash
# 安装 sqlite3（通常系统自带）
sqlite3 employees.db

# 查看表
.tables

# 查看表结构
.schema employees

# 查询数据
SELECT * FROM employees;

# 退出
.quit
```

或使用图形化工具：
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [DBeaver](https://dbeaver.io/)

#### 4. 为什么要使用 ORM？

ORM 的优势：
- 使用 Python 代码操作数据库，更直观
- 自动处理 SQL 注入问题
- 数据库无关性，方便切换数据库
- 类型安全和 IDE 支持

但也要注意：
- 复杂查询可能需要原生 SQL
- 需要理解 ORM 生成的 SQL
- 注意性能优化（N+1 查询等）

## 扩展练习

### 练习 1: 添加新模型

创建一个 `Project` 模型，包含：
- 项目名称
- 项目描述
- 开始日期
- 结束日期
- 负责人（外键关联到 Employee）

实现项目的 CRUD 操作。

### 练习 2: 多对多关系

实现员工和项目的多对多关系：
- 一个员工可以参与多个项目
- 一个项目可以有多个员工
- 使用中间表记录参与时间和角色

### 练习 3: 复杂查询

实现以下查询：
1. 查询参与项目最多的员工
2. 查询每个部门的项目数量
3. 查询工资排名前 10% 的员工
4. 查询入职超过 1 年且工资低于部门平均工资的员工

### 练习 4: 事务处理

实现一个转账功能：
- 从一个员工的工资转移到另一个员工
- 使用事务确保原子性
- 处理余额不足等异常情况

## 参考资源

- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [SQLAlchemy 教程](https://docs.sqlalchemy.org/en/20/tutorial/)
- [FastAPI 数据库集成](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)

## 下一步

完成这些示例后，建议：

1. 学习数据库迁移工具 Alembic
2. 在实际项目中应用 SQLAlchemy
3. 学习数据库性能优化
4. 了解数据库设计最佳实践
