# SQL 基础教程

## 简介

SQL (Structured Query Language) 是用于管理关系型数据库的标准语言。本教程将介绍 SQL 的基础知识，帮助你理解如何创建、查询、更新和删除数据。

## 数据库基础概念

### 什么是数据库？

数据库是有组织地存储和管理数据的系统。关系型数据库使用表格来存储数据，表格由行和列组成。

### 核心概念

- **数据库 (Database)**: 相关数据的集合
- **表 (Table)**: 存储数据的结构，由行和列组成
- **行 (Row/Record)**: 表中的一条记录
- **列 (Column/Field)**: 表中的一个字段
- **主键 (Primary Key)**: 唯一标识每行数据的列
- **外键 (Foreign Key)**: 引用另一个表主键的列
- **索引 (Index)**: 提高查询速度的数据结构

## SQL 语句分类

### 1. DDL (Data Definition Language) - 数据定义语言

用于定义和管理数据库结构。

#### 创建数据库

```sql
-- 创建数据库
CREATE DATABASE company_db;

-- 使用数据库
USE company_db;
```

#### 创建表

```sql
-- 创建员工表
CREATE TABLE employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    position_id INT,
    salary DECIMAL(10, 2),
    hire_date DATE NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建岗位表
CREATE TABLE positions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    level INT DEFAULT 1,
    parent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES positions(id) ON DELETE SET NULL
);
```

#### 修改表结构

```sql
-- 添加列
ALTER TABLE employees ADD COLUMN phone VARCHAR(20);

-- 修改列
ALTER TABLE employees MODIFY COLUMN phone VARCHAR(30);

-- 删除列
ALTER TABLE employees DROP COLUMN phone;

-- 添加外键约束
ALTER TABLE employees 
ADD CONSTRAINT fk_position 
FOREIGN KEY (position_id) REFERENCES positions(id);
```

#### 删除表和数据库

```sql
-- 删除表
DROP TABLE IF EXISTS employees;

-- 删除数据库
DROP DATABASE IF EXISTS company_db;
```

### 2. DML (Data Manipulation Language) - 数据操作语言

用于操作表中的数据。

#### INSERT - 插入数据

```sql
-- 插入单条记录
INSERT INTO positions (name, code, description, level)
VALUES ('软件工程师', 'SE001', '负责软件开发', 3);

-- 插入多条记录
INSERT INTO positions (name, code, description, level) VALUES
    ('高级工程师', 'SE002', '负责技术架构', 4),
    ('技术经理', 'TM001', '负责团队管理', 5),
    ('产品经理', 'PM001', '负责产品规划', 4);

-- 插入员工数据
INSERT INTO employees (username, email, full_name, position_id, salary, hire_date)
VALUES ('zhangsan', 'zhangsan@example.com', '张三', 1, 15000.00, '2023-01-15');
```

#### SELECT - 查询数据

```sql
-- 查询所有列
SELECT * FROM employees;

-- 查询指定列
SELECT username, full_name, email FROM employees;

-- 条件查询
SELECT * FROM employees WHERE status = 'active';

-- 多条件查询
SELECT * FROM employees 
WHERE status = 'active' AND salary > 10000;

-- 模糊查询
SELECT * FROM employees WHERE full_name LIKE '张%';

-- 范围查询
SELECT * FROM employees WHERE salary BETWEEN 10000 AND 20000;

-- IN 查询
SELECT * FROM employees WHERE position_id IN (1, 2, 3);

-- 排序
SELECT * FROM employees ORDER BY salary DESC;

-- 限制结果数量
SELECT * FROM employees LIMIT 10;

-- 分页查询
SELECT * FROM employees LIMIT 10 OFFSET 20;  -- 跳过前20条，取10条
```

#### UPDATE - 更新数据

```sql
-- 更新单条记录
UPDATE employees 
SET salary = 16000.00 
WHERE username = 'zhangsan';

-- 更新多个字段
UPDATE employees 
SET salary = salary * 1.1, status = 'active'
WHERE hire_date < '2023-01-01';

-- 条件更新
UPDATE employees 
SET position_id = 2 
WHERE salary > 15000 AND position_id = 1;
```

#### DELETE - 删除数据

```sql
-- 删除指定记录
DELETE FROM employees WHERE username = 'zhangsan';

-- 条件删除
DELETE FROM employees WHERE status = 'inactive' AND hire_date < '2020-01-01';

-- 删除所有记录（保留表结构）
DELETE FROM employees;

-- 清空表（更快，重置自增ID）
TRUNCATE TABLE employees;
```

### 3. DQL (Data Query Language) - 数据查询语言

高级查询技巧。

#### 聚合函数

```sql
-- 计数
SELECT COUNT(*) FROM employees;
SELECT COUNT(DISTINCT position_id) FROM employees;

-- 求和
SELECT SUM(salary) FROM employees;

-- 平均值
SELECT AVG(salary) FROM employees;

-- 最大值和最小值
SELECT MAX(salary), MIN(salary) FROM employees;

-- 分组统计
SELECT position_id, COUNT(*) as employee_count, AVG(salary) as avg_salary
FROM employees
GROUP BY position_id;

-- 分组过滤
SELECT position_id, AVG(salary) as avg_salary
FROM employees
GROUP BY position_id
HAVING AVG(salary) > 12000;
```

#### 连接查询 (JOIN)

```sql
-- 内连接 (INNER JOIN) - 返回两表匹配的记录
SELECT e.username, e.full_name, p.name as position_name
FROM employees e
INNER JOIN positions p ON e.position_id = p.id;

-- 左连接 (LEFT JOIN) - 返回左表所有记录，右表匹配的记录
SELECT e.username, e.full_name, p.name as position_name
FROM employees e
LEFT JOIN positions p ON e.position_id = p.id;

-- 右连接 (RIGHT JOIN) - 返回右表所有记录，左表匹配的记录
SELECT e.username, e.full_name, p.name as position_name
FROM employees e
RIGHT JOIN positions p ON e.position_id = p.id;

-- 多表连接
SELECT e.username, e.full_name, p.name as position_name, p.level
FROM employees e
INNER JOIN positions p ON e.position_id = p.id
WHERE p.level >= 3
ORDER BY p.level DESC, e.salary DESC;
```

#### 子查询

```sql
-- WHERE 子查询
SELECT * FROM employees
WHERE position_id IN (
    SELECT id FROM positions WHERE level >= 4
);

-- FROM 子查询
SELECT avg_salary_by_position.position_id, avg_salary_by_position.avg_salary
FROM (
    SELECT position_id, AVG(salary) as avg_salary
    FROM employees
    GROUP BY position_id
) as avg_salary_by_position
WHERE avg_salary_by_position.avg_salary > 15000;

-- EXISTS 子查询
SELECT * FROM positions p
WHERE EXISTS (
    SELECT 1 FROM employees e WHERE e.position_id = p.id
);
```

### 4. DCL (Data Control Language) - 数据控制语言

用于管理权限和访问控制。

```sql
-- 创建用户
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'password123';

-- 授予权限
GRANT SELECT, INSERT, UPDATE, DELETE ON company_db.* TO 'app_user'@'localhost';

-- 授予所有权限
GRANT ALL PRIVILEGES ON company_db.* TO 'app_user'@'localhost';

-- 撤销权限
REVOKE DELETE ON company_db.* FROM 'app_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 删除用户
DROP USER 'app_user'@'localhost';
```

## 索引

索引可以显著提高查询性能，但会增加写入开销。

```sql
-- 创建索引
CREATE INDEX idx_username ON employees(username);

-- 创建唯一索引
CREATE UNIQUE INDEX idx_email ON employees(email);

-- 创建复合索引
CREATE INDEX idx_position_status ON employees(position_id, status);

-- 查看索引
SHOW INDEX FROM employees;

-- 删除索引
DROP INDEX idx_username ON employees;
```

## 事务

事务确保一组操作要么全部成功，要么全部失败。

```sql
-- 开始事务
START TRANSACTION;

-- 执行操作
UPDATE employees SET salary = salary - 1000 WHERE id = 1;
UPDATE employees SET salary = salary + 1000 WHERE id = 2;

-- 提交事务
COMMIT;

-- 或者回滚事务
ROLLBACK;
```

### 事务的 ACID 特性

- **原子性 (Atomicity)**: 事务中的所有操作要么全部完成，要么全部不完成
- **一致性 (Consistency)**: 事务必须使数据库从一个一致性状态变换到另一个一致性状态
- **隔离性 (Isolation)**: 多个事务并发执行时，一个事务的执行不应影响其他事务
- **持久性 (Durability)**: 事务一旦提交，其结果就是永久性的

## 视图

视图是虚拟表，基于 SQL 查询的结果。

```sql
-- 创建视图
CREATE VIEW employee_details AS
SELECT e.id, e.username, e.full_name, e.email, 
       p.name as position_name, p.level, e.salary
FROM employees e
LEFT JOIN positions p ON e.position_id = p.id;

-- 使用视图
SELECT * FROM employee_details WHERE level >= 3;

-- 删除视图
DROP VIEW employee_details;
```

## 常用函数

### 字符串函数

```sql
-- 连接字符串
SELECT CONCAT(full_name, ' (', username, ')') FROM employees;

-- 转换大小写
SELECT UPPER(username), LOWER(email) FROM employees;

-- 截取字符串
SELECT SUBSTRING(full_name, 1, 2) FROM employees;

-- 字符串长度
SELECT LENGTH(full_name) FROM employees;

-- 去除空格
SELECT TRIM(full_name) FROM employees;
```

### 日期函数

```sql
-- 当前日期和时间
SELECT NOW(), CURDATE(), CURTIME();

-- 日期格式化
SELECT DATE_FORMAT(hire_date, '%Y年%m月%d日') FROM employees;

-- 日期计算
SELECT DATE_ADD(hire_date, INTERVAL 1 YEAR) FROM employees;
SELECT DATEDIFF(NOW(), hire_date) as days_employed FROM employees;

-- 提取日期部分
SELECT YEAR(hire_date), MONTH(hire_date), DAY(hire_date) FROM employees;
```

### 数学函数

```sql
-- 四舍五入
SELECT ROUND(salary, 0) FROM employees;

-- 向上取整
SELECT CEIL(salary / 1000) FROM employees;

-- 向下取整
SELECT FLOOR(salary / 1000) FROM employees;

-- 绝对值
SELECT ABS(-100);

-- 随机数
SELECT RAND();
```

## 最佳实践

### 1. 命名规范

- 使用小写字母和下划线
- 表名使用复数形式（如 employees）
- 列名要有意义且简洁
- 避免使用 SQL 关键字作为名称

### 2. 性能优化

- 为经常查询的列创建索引
- 避免 SELECT *，只查询需要的列
- 使用 LIMIT 限制结果集大小
- 合理使用 JOIN，避免笛卡尔积
- 使用 EXPLAIN 分析查询性能

### 3. 安全性

- 使用参数化查询防止 SQL 注入
- 最小权限原则，只授予必要的权限
- 定期备份数据库
- 不在代码中硬编码数据库密码

### 4. 数据完整性

- 使用主键确保记录唯一性
- 使用外键维护表间关系
- 使用 NOT NULL 约束必填字段
- 使用 CHECK 约束验证数据
- 使用 UNIQUE 约束防止重复

## 练习题

### 基础练习

1. 创建一个 `departments` 表，包含 id、name、description 字段
2. 向 `departments` 表插入 3 条记录
3. 查询所有部门信息
4. 更新某个部门的描述
5. 删除一个部门

### 进阶练习

1. 查询工资最高的前 5 名员工
2. 统计每个岗位的员工数量和平均工资
3. 查询工资高于所在岗位平均工资的员工
4. 查询没有员工的岗位
5. 查询入职时间超过 1 年的员工，并按工资降序排列

### 综合练习

1. 创建一个视图，显示员工的详细信息（包括岗位名称）
2. 编写一个事务，将一个员工的工资转移给另一个员工
3. 为 employees 表创建合适的索引以优化查询性能
4. 使用子查询找出工资排名前 10% 的员工

## 参考资源

- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [SQL Tutorial - W3Schools](https://www.w3schools.com/sql/)
- [SQLBolt - 交互式 SQL 教程](https://sqlbolt.com/)

## 下一步

学习完 SQL 基础后，建议：

1. 学习 ORM 使用指南（orm_guide.md）
2. 实践数据库示例代码
3. 在 FastAPI 和 Flask 项目中应用数据库知识
4. 学习数据库设计和规范化理论
