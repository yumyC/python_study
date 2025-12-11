# CRM 数据库设计文档

## 1. 数据库概述

### 1.1 数据库选择

**推荐数据库**: PostgreSQL 13+

**选择理由**:
- 开源免费，社区活跃
- 功能强大，支持 JSON、数组、全文搜索等高级特性
- 性能优秀，支持大规模数据
- 事务支持完善，ACID 特性
- 丰富的索引类型（B-tree、Hash、GiST、GIN 等）
- 企业级可靠性和稳定性

**备选方案**: MySQL 8.0+

### 1.2 设计原则

1. **规范化**: 遵循第三范式（3NF），减少数据冗余
2. **索引优化**: 为常用查询字段添加索引
3. **外键约束**: 使用外键保证数据完整性
4. **软删除**: 重要数据使用软删除（deleted_at 字段）
5. **审计字段**: 所有表包含 created_at 和 updated_at
6. **UUID 主键**: 使用 UUID 作为主键，便于分布式扩展
7. **命名规范**: 表名和字段名使用小写字母和下划线

### 1.3 数据库命名

- 数据库名: `crm_db`
- 字符集: UTF-8
- 排序规则: utf8mb4_unicode_ci (MySQL) 或 en_US.UTF-8 (PostgreSQL)

## 2. 数据表设计

### 2.1 员工表 (employees)

**表描述**: 存储员工基本信息和账号信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | UUID | PRIMARY KEY | 员工 ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名，用于登录 |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希值 |
| full_name | VARCHAR(100) | NOT NULL | 员工姓名 |
| position_id | UUID | FOREIGN KEY, NOT NULL | 岗位 ID |
| role_id | UUID | FOREIGN KEY, NOT NULL | 角色 ID |
| status | ENUM | NOT NULL, DEFAULT 'active' | 状态：active, inactive |
| last_login_at | TIMESTAMP | NULL | 最后登录时间 |
| login_failed_count | INTEGER | DEFAULT 0 | 登录失败次数 |
| locked_until | TIMESTAMP | NULL | 账号锁定截止时间 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMP | NULL | 删除时间（软删除） |

**索引**:
- PRIMARY KEY: id
- UNIQUE INDEX: username
- UNIQUE INDEX: email
- INDEX: position_id
- INDEX: role_id
- INDEX: status
- INDEX: deleted_at

**外键约束**:
- position_id REFERENCES positions(id) ON DELETE RESTRICT
- role_id REFERENCES roles(id) ON DELETE RESTRICT

**业务规则**:
- username 只能包含字母、数字和下划线
- email 必须符合邮箱格式
- password_hash 使用 bcrypt 加密
- 登录失败 5 次后锁定 30 分钟
- 软删除的员工不能登录


### 2.2 岗位表 (positions)

**表描述**: 存储组织架构和岗位信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | UUID | PRIMARY KEY | 岗位 ID |
| name | VARCHAR(100) | NOT NULL | 岗位名称 |
| code | VARCHAR(50) | UNIQUE, NOT NULL | 岗位编码 |
| description | TEXT | NULL | 岗位描述 |
| level | INTEGER | NOT NULL | 岗位层级（1 为最高） |
| parent_id | UUID | FOREIGN KEY, NULL | 上级岗位 ID |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMP | NULL | 删除时间（软删除） |

**索引**:
- PRIMARY KEY: id
- UNIQUE INDEX: code
- INDEX: parent_id
- INDEX: level
- INDEX: deleted_at

**外键约束**:
- parent_id REFERENCES positions(id) ON DELETE RESTRICT

**业务规则**:
- 岗位编码必须唯一
- 岗位层级从 1 开始，数字越小层级越高
- 上级岗位的层级必须小于当前岗位
- 有员工的岗位不能删除
- 有下级岗位的岗位不能删除
- 支持树形结构查询

**示例数据**:
```
CEO (level=1, parent_id=NULL)
├── CTO (level=2, parent_id=CEO.id)
│   ├── 技术总监 (level=3, parent_id=CTO.id)
│   │   ├── 后端开发工程师 (level=4)
│   │   └── 前端开发工程师 (level=4)
└── CFO (level=2, parent_id=CEO.id)
    └── 财务经理 (level=3, parent_id=CFO.id)
```

### 2.3 菜单表 (menus)

**表描述**: 存储系统菜单和路由信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | UUID | PRIMARY KEY | 菜单 ID |
| name | VARCHAR(100) | NOT NULL | 菜单名称 |
| path | VARCHAR(200) | NOT NULL | 菜单路径 |
| icon | VARCHAR(50) | NULL | 菜单图标 |
| component | VARCHAR(200) | NOT NULL | 组件路径 |
| parent_id | UUID | FOREIGN KEY, NULL | 上级菜单 ID |
| sort_order | INTEGER | DEFAULT 0 | 排序号（越小越靠前） |
| is_visible | BOOLEAN | DEFAULT TRUE | 是否可见 |
| menu_type | ENUM | NOT NULL | 菜单类型：menu, button |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMP | NULL | 删除时间（软删除） |

**索引**:
- PRIMARY KEY: id
- INDEX: parent_id
- INDEX: sort_order
- INDEX: is_visible
- INDEX: deleted_at

**外键约束**:
- parent_id REFERENCES menus(id) ON DELETE RESTRICT

**业务规则**:
- 菜单路径必须以 / 开头
- 支持多级菜单（树形结构）
- 按 sort_order 排序显示
- 不可见的菜单不在前端显示
- 有下级菜单的菜单不能删除
- menu_type 为 menu 表示菜单项，button 表示按钮权限

**示例数据**:
```
系统管理 (parent_id=NULL, sort_order=1)
├── 员工管理 (parent_id=系统管理.id, sort_order=1)
│   ├── 查看员工 (menu_type=button)
│   ├── 创建员工 (menu_type=button)
│   ├── 编辑员工 (menu_type=button)
│   └── 删除员工 (menu_type=button)
├── 岗位管理 (parent_id=系统管理.id, sort_order=2)
└── 角色管理 (parent_id=系统管理.id, sort_order=3)
```

### 2.4 角色表 (roles)

**表描述**: 存储角色信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | UUID | PRIMARY KEY | 角色 ID |
| name | VARCHAR(100) | NOT NULL | 角色名称 |
| code | VARCHAR(50) | UNIQUE, NOT NULL | 角色编码 |
| description | TEXT | NULL | 角色描述 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMP | NULL | 删除时间（软删除） |

**索引**:
- PRIMARY KEY: id
- UNIQUE INDEX: code
- INDEX: deleted_at

**业务规则**:
- 角色编码必须唯一
- 有员工使用的角色不能删除
- 删除角色会同时删除相关的权限绑定

**示例数据**:
```
- 系统管理员 (code=admin)
- HR 管理员 (code=hr_admin)
- 部门主管 (code=manager)
- 普通员工 (code=employee)
```

### 2.5 角色菜单权限表 (role_menu_permissions)

**表描述**: 存储角色与菜单的权限绑定关系

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | UUID | PRIMARY KEY | 权限 ID |
| role_id | UUID | FOREIGN KEY, NOT NULL | 角色 ID |
| menu_id | UUID | FOREIGN KEY, NOT NULL | 菜单 ID |
| permissions | JSON/TEXT | NOT NULL | 权限列表 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**索引**:
- PRIMARY KEY: id
- UNIQUE INDEX: (role_id, menu_id)
- INDEX: role_id
- INDEX: menu_id

**外键约束**:
- role_id REFERENCES roles(id) ON DELETE CASCADE
- menu_id REFERENCES menus(id) ON DELETE CASCADE

**业务规则**:
- 一个角色对一个菜单只能有一条权限记录
- permissions 字段存储权限数组，如 ["view", "create", "update", "delete"]
- 权限类型：
  - view: 查看权限
  - create: 创建权限
  - update: 更新权限
  - delete: 删除权限

**permissions 字段格式**:
```json
["view", "create", "update", "delete"]
```

**示例数据**:
```
角色：系统管理员
├── 员工管理菜单: ["view", "create", "update", "delete"]
├── 岗位管理菜单: ["view", "create", "update", "delete"]
└── 角色管理菜单: ["view", "create", "update", "delete"]

角色：普通员工
└── 工作日志菜单: ["view", "create", "update"]
```


### 2.6 工作日志表 (work_logs)

**表描述**: 存储员工的工作日志信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | UUID | PRIMARY KEY | 日志 ID |
| employee_id | UUID | FOREIGN KEY, NOT NULL | 员工 ID |
| log_date | DATE | NOT NULL | 日志日期 |
| work_content | TEXT | NOT NULL | 工作内容 |
| completion_status | ENUM | NOT NULL | 完成情况 |
| problems_encountered | TEXT | NULL | 遇到的问题 |
| tomorrow_plan | TEXT | NULL | 明日计划 |
| self_rating | INTEGER | NULL | 自评分数（1-5） |
| supervisor_rating | INTEGER | NULL | 上级评分（1-5） |
| supervisor_comment | TEXT | NULL | 上级评语 |
| supervisor_id | UUID | FOREIGN KEY, NULL | 评分上级 ID |
| rated_at | TIMESTAMP | NULL | 评分时间 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |
| deleted_at | TIMESTAMP | NULL | 删除时间（软删除） |

**索引**:
- PRIMARY KEY: id
- UNIQUE INDEX: (employee_id, log_date)
- INDEX: employee_id
- INDEX: log_date
- INDEX: completion_status
- INDEX: supervisor_id
- INDEX: deleted_at

**外键约束**:
- employee_id REFERENCES employees(id) ON DELETE CASCADE
- supervisor_id REFERENCES employees(id) ON DELETE SET NULL

**业务规则**:
- 每个员工每天只能创建一条日志
- completion_status 枚举值：
  - completed: 已完成
  - in_progress: 进行中
  - pending: 待处理
- self_rating 和 supervisor_rating 范围：1-5 分
- 只能创建和修改当天的日志
- 已被上级评分的日志不能修改工作内容
- 只有上级可以评分
- 员工只能查看自己的日志
- 主管可以查看下属的日志
- 管理员可以查看所有日志

**示例数据**:
```
{
  "employee_id": "uuid-1",
  "log_date": "2024-01-15",
  "work_content": "完成用户管理模块的 API 开发，包括 CRUD 操作和权限验证",
  "completion_status": "completed",
  "problems_encountered": "遇到了权限验证的性能问题，通过添加缓存解决",
  "tomorrow_plan": "开始开发工作日志模块",
  "self_rating": 4,
  "supervisor_rating": 5,
  "supervisor_comment": "完成质量很高，解决问题的思路很好"
}
```

### 2.7 导出任务表 (export_tasks)

**表描述**: 存储异步导出任务的状态信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| id | UUID | PRIMARY KEY | 任务 ID |
| task_id | VARCHAR(100) | UNIQUE, NOT NULL | Celery 任务 ID |
| employee_id | UUID | FOREIGN KEY, NOT NULL | 发起导出的员工 ID |
| task_type | VARCHAR(50) | NOT NULL | 任务类型 |
| params | JSON | NOT NULL | 导出参数 |
| status | ENUM | NOT NULL | 任务状态 |
| progress | INTEGER | DEFAULT 0 | 进度百分比（0-100） |
| file_path | VARCHAR(500) | NULL | 文件路径 |
| file_url | VARCHAR(500) | NULL | 下载链接 |
| error_message | TEXT | NULL | 错误信息 |
| started_at | TIMESTAMP | NULL | 开始时间 |
| completed_at | TIMESTAMP | NULL | 完成时间 |
| expires_at | TIMESTAMP | NULL | 过期时间 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**索引**:
- PRIMARY KEY: id
- UNIQUE INDEX: task_id
- INDEX: employee_id
- INDEX: status
- INDEX: created_at
- INDEX: expires_at

**外键约束**:
- employee_id REFERENCES employees(id) ON DELETE CASCADE

**业务规则**:
- task_type 值：worklog_export（工作日志导出）
- status 枚举值：
  - pending: 等待中
  - processing: 处理中
  - completed: 已完成
  - failed: 失败
- 文件下载链接 24 小时有效
- 过期的文件自动清理
- 记录导出参数用于重试

**params 字段格式**:
```json
{
  "employee_id": "uuid",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "format": "xlsx"
}
```

## 3. 数据库关系图

```
┌─────────────┐         ┌─────────────┐
│  positions  │◄────┐   │    roles    │
└─────────────┘     │   └─────────────┘
       ▲            │          ▲
       │            │          │
       │            │          │
       │      ┌─────────────┐  │
       │      │  employees  │  │
       │      └─────────────┘  │
       │            │          │
       │            │          │
       │            ▼          │
       │      ┌─────────────┐  │
       │      │ work_logs   │  │
       │      └─────────────┘  │
       │            │          │
       │            │          │
       │            ▼          │
       │      ┌─────────────┐  │
       │      │export_tasks │  │
       │      └─────────────┘  │
       │                       │
       │                       │
┌─────────────┐         ┌──────────────────────┐
│    menus    │◄────────┤role_menu_permissions │
└─────────────┘         └──────────────────────┘
       ▲                         ▲
       │                         │
       └─────────────────────────┘
```

**关系说明**:
- employees.position_id → positions.id (多对一)
- employees.role_id → roles.id (多对一)
- positions.parent_id → positions.id (自引用，树形结构)
- menus.parent_id → menus.id (自引用，树形结构)
- role_menu_permissions.role_id → roles.id (多对一)
- role_menu_permissions.menu_id → menus.id (多对一)
- work_logs.employee_id → employees.id (多对一)
- work_logs.supervisor_id → employees.id (多对一)
- export_tasks.employee_id → employees.id (多对一)

## 4. 数据库初始化

### 4.1 创建数据库

**PostgreSQL**:
```sql
CREATE DATABASE crm_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
```

**MySQL**:
```sql
CREATE DATABASE crm_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

### 4.2 初始数据

**创建默认角色**:
```sql
INSERT INTO roles (id, name, code, description) VALUES
('uuid-1', '系统管理员', 'admin', '拥有所有权限'),
('uuid-2', 'HR 管理员', 'hr_admin', '管理员工和岗位'),
('uuid-3', '部门主管', 'manager', '管理部门员工和工作日志'),
('uuid-4', '普通员工', 'employee', '基本权限');
```

**创建默认岗位**:
```sql
INSERT INTO positions (id, name, code, level, parent_id) VALUES
('uuid-1', 'CEO', 'CEO', 1, NULL),
('uuid-2', 'CTO', 'CTO', 2, 'uuid-1'),
('uuid-3', '技术总监', 'TECH_DIR', 3, 'uuid-2'),
('uuid-4', '后端开发工程师', 'BACKEND_DEV', 4, 'uuid-3'),
('uuid-5', '前端开发工程师', 'FRONTEND_DEV', 4, 'uuid-3');
```

**创建默认管理员账号**:
```sql
INSERT INTO employees (id, username, email, password_hash, full_name, position_id, role_id, status)
VALUES (
    'uuid-admin',
    'admin',
    'admin@example.com',
    '$2b$12$...', -- bcrypt hash of 'Admin123456'
    '系统管理员',
    'uuid-1',
    'uuid-1',
    'active'
);
```


## 5. 数据库优化

### 5.1 索引策略

**单列索引**:
- 主键自动创建索引
- 外键字段创建索引
- 常用查询字段（如 status, deleted_at）

**复合索引**:
```sql
-- 员工表：按岗位和状态查询
CREATE INDEX idx_employees_position_status ON employees(position_id, status);

-- 工作日志表：按员工和日期查询
CREATE INDEX idx_worklogs_employee_date ON work_logs(employee_id, log_date DESC);

-- 工作日志表：按日期范围查询
CREATE INDEX idx_worklogs_date_range ON work_logs(log_date);
```

**唯一索引**:
```sql
-- 确保每个员工每天只有一条日志
CREATE UNIQUE INDEX idx_worklogs_employee_date_unique 
ON work_logs(employee_id, log_date) 
WHERE deleted_at IS NULL;
```

### 5.2 查询优化

**避免 N+1 查询**:
```python
# 不好的做法
employees = session.query(Employee).all()
for emp in employees:
    print(emp.position.name)  # 每次都查询数据库

# 好的做法
employees = session.query(Employee).options(
    joinedload(Employee.position),
    joinedload(Employee.role)
).all()
for emp in employees:
    print(emp.position.name)  # 不再查询数据库
```

**使用分页**:
```python
# 分页查询
page = 1
page_size = 20
offset = (page - 1) * page_size

employees = session.query(Employee)\
    .limit(page_size)\
    .offset(offset)\
    .all()
```

**使用索引提示**:
```sql
-- PostgreSQL
SELECT * FROM employees 
WHERE status = 'active' 
ORDER BY created_at DESC;

-- 确保使用了索引
EXPLAIN ANALYZE SELECT * FROM employees WHERE status = 'active';
```

### 5.3 数据归档

**归档策略**:
- 工作日志超过 1 年的数据归档到历史表
- 导出任务超过 30 天的数据清理
- 软删除的数据定期清理

**归档表**:
```sql
CREATE TABLE work_logs_archive (
    LIKE work_logs INCLUDING ALL
);

-- 归档数据
INSERT INTO work_logs_archive
SELECT * FROM work_logs
WHERE log_date < CURRENT_DATE - INTERVAL '1 year';

-- 删除已归档数据
DELETE FROM work_logs
WHERE log_date < CURRENT_DATE - INTERVAL '1 year';
```

### 5.4 数据库连接池

**配置示例**:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,          # 连接池大小
    max_overflow=20,       # 最大溢出连接数
    pool_timeout=30,       # 获取连接超时时间
    pool_recycle=3600,     # 连接回收时间
    pool_pre_ping=True     # 连接前检查
)
```

## 6. 数据库备份与恢复

### 6.1 备份策略

**全量备份**:
```bash
# PostgreSQL
pg_dump -U postgres -d crm_db -F c -f crm_db_backup_$(date +%Y%m%d).dump

# MySQL
mysqldump -u root -p crm_db > crm_db_backup_$(date +%Y%m%d).sql
```

**增量备份**:
- 使用 WAL 归档（PostgreSQL）
- 使用 binlog（MySQL）

**备份频率**:
- 全量备份：每天凌晨 2 点
- 增量备份：每小时
- 保留最近 30 天的备份

### 6.2 恢复策略

**全量恢复**:
```bash
# PostgreSQL
pg_restore -U postgres -d crm_db -c crm_db_backup_20240115.dump

# MySQL
mysql -u root -p crm_db < crm_db_backup_20240115.sql
```

**时间点恢复**:
```bash
# PostgreSQL PITR
pg_restore -U postgres -d crm_db -t "2024-01-15 14:30:00"
```

## 7. 数据库监控

### 7.1 监控指标

**性能指标**:
- 查询响应时间
- 慢查询数量
- 连接数
- 缓存命中率
- 锁等待时间

**资源指标**:
- CPU 使用率
- 内存使用率
- 磁盘 I/O
- 磁盘空间

### 7.2 慢查询日志

**PostgreSQL**:
```sql
-- 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1秒
SELECT pg_reload_conf();

-- 查看慢查询
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

**MySQL**:
```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

-- 查看慢查询
SELECT * FROM mysql.slow_log
ORDER BY query_time DESC
LIMIT 10;
```

### 7.3 表统计信息

**PostgreSQL**:
```sql
-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## 8. 数据库安全

### 8.1 访问控制

**创建应用用户**:
```sql
-- PostgreSQL
CREATE USER crm_app WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE crm_db TO crm_app;
GRANT USAGE ON SCHEMA public TO crm_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO crm_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO crm_app;

-- MySQL
CREATE USER 'crm_app'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON crm_db.* TO 'crm_app'@'localhost';
FLUSH PRIVILEGES;
```

**最小权限原则**:
- 应用用户只有必要的权限
- 不使用 root 或 postgres 用户
- 定期审查权限

### 8.2 数据加密

**传输加密**:
- 使用 SSL/TLS 连接数据库
- 配置证书验证

**存储加密**:
- 敏感字段加密（如身份证号）
- 使用数据库透明加密（TDE）

### 8.3 审计日志

**启用审计**:
```sql
-- PostgreSQL
CREATE EXTENSION IF NOT EXISTS pgaudit;
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
SELECT pg_reload_conf();

-- 查看审计日志
SELECT * FROM pg_audit_log
WHERE timestamp > NOW() - INTERVAL '1 day'
ORDER BY timestamp DESC;
```

## 9. 数据库迁移

### 9.1 使用 Alembic (FastAPI)

**初始化**:
```bash
alembic init alembic
```

**配置**:
```python
# alembic/env.py
from app.models import Base
target_metadata = Base.metadata
```

**创建迁移**:
```bash
alembic revision --autogenerate -m "create initial tables"
```

**执行迁移**:
```bash
alembic upgrade head
```

**回滚迁移**:
```bash
alembic downgrade -1
```

### 9.2 使用 Flask-Migrate (Flask)

**初始化**:
```bash
flask db init
```

**创建迁移**:
```bash
flask db migrate -m "create initial tables"
```

**执行迁移**:
```bash
flask db upgrade
```

**回滚迁移**:
```bash
flask db downgrade
```

## 10. 常见问题

### Q1: 如何处理大量数据的查询？

A: 使用分页、索引优化、缓存和数据归档。

### Q2: 如何保证数据一致性？

A: 使用事务、外键约束和乐观锁。

### Q3: 如何处理并发更新？

A: 使用乐观锁（version 字段）或悲观锁（SELECT FOR UPDATE）。

### Q4: 如何优化树形结构查询？

A: 使用递归查询（CTE）或物化路径。

### Q5: 如何处理软删除？

A: 添加 deleted_at 字段，查询时过滤 deleted_at IS NULL。

## 11. 参考资料

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [数据库设计最佳实践](https://www.sqlstyle.guide/)
- [数据库索引优化](https://use-the-index-luke.com/)

## 12. 附录

### 12.1 完整建表 SQL (PostgreSQL)

详见项目代码中的 `migrations` 目录或使用 ORM 自动生成。

### 12.2 ER 图

详见项目文档中的 `database_er_diagram.png`。

### 12.3 数据字典

所有表和字段的详细说明见本文档第 2 节。
