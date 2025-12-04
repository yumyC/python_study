# ORM 使用指南

## 简介

ORM (Object-Relational Mapping，对象关系映射) 是一种编程技术，用于在面向对象编程语言和关系型数据库之间建立映射关系。通过 ORM，你可以使用 Python 类和对象来操作数据库，而不需要编写 SQL 语句。

## 为什么使用 ORM？

### 优点

1. **提高开发效率**: 使用 Python 代码操作数据库，无需编写 SQL
2. **代码可维护性**: 数据库操作逻辑集中在模型类中
3. **数据库无关性**: 更换数据库时只需修改配置，代码基本不变
4. **防止 SQL 注入**: ORM 自动处理参数化查询
5. **类型安全**: 利用 Python 的类型系统进行数据验证

### 缺点

1. **性能开销**: ORM 会有一定的性能损失
2. **学习曲线**: 需要学习 ORM 框架的 API
3. **复杂查询**: 某些复杂 SQL 查询用 ORM 实现较困难
4. **调试难度**: 生成的 SQL 可能不够直观

## SQLAlchemy 简介

SQLAlchemy 是 Python 最流行的 ORM 框架，支持多种数据库（MySQL、PostgreSQL、SQLite 等）。

### 安装

```bash
# 安装 SQLAlchemy
pip install sqlalchemy

# 安装数据库驱动
pip install pymysql          # MySQL
pip install psycopg2-binary  # PostgreSQL
pip install asyncpg          # PostgreSQL (异步)
```

### SQLAlchemy 架构

SQLAlchemy 分为两个主要部分：

1. **Core**: 底层 SQL 表达式语言
2. **ORM**: 高层对象关系映射

## SQLAlchemy 2.0 基础

### 1. 数据库连接

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 创建数据库引擎
# SQLite
engine = create_engine('sqlite:///./test.db', echo=True)

# MySQL
engine = create_engine(
    'mysql+pymysql://username:password@localhost:3306/database_name',
    echo=True  # 打印 SQL 语句
)

# PostgreSQL
engine = create_engine(
    'postgresql+psycopg2://username:password@localhost:5432/database_name',
    echo=True
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 获取会话
db = SessionLocal()
```

### 2. 定义模型

使用声明式基类定义模型：

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, DECIMAL
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

# 创建基类
Base = declarative_base()

# 定义枚举类型
class EmployeeStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

# 定义岗位模型
class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(500))
    level = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey('positions.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    employees = relationship("Employee", back_populates="position")
    children = relationship("Position", backref="parent", remote_side=[id])

# 定义员工模型
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    position_id = Column(Integer, ForeignKey('positions.id'))
    salary = Column(DECIMAL(10, 2))
    hire_date = Column(DateTime, nullable=False)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    position = relationship("Position", back_populates="employees")
    work_logs = relationship("WorkLog", back_populates="employee")

# 定义工作日志模型
class WorkLog(Base):
    __tablename__ = "work_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    log_date = Column(DateTime, nullable=False)
    work_content = Column(String(2000), nullable=False)
    completion_status = Column(String(50))
    problems_encountered = Column(String(2000))
    tomorrow_plan = Column(String(2000))
    self_rating = Column(Integer)
    supervisor_rating = Column(Integer, nullable=True)
    supervisor_comment = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    employee = relationship("Employee", back_populates="work_logs")
```

### 3. 创建表

```python
# 创建所有表
Base.metadata.create_all(bind=engine)

# 删除所有表
Base.metadata.drop_all(bind=engine)
```

## CRUD 操作

### Create - 创建记录

```python
from sqlalchemy.orm import Session

def create_position(db: Session, name: str, code: str, level: int):
    """创建岗位"""
    position = Position(
        name=name,
        code=code,
        level=level,
        description=f"{name}岗位"
    )
    db.add(position)
    db.commit()
    db.refresh(position)  # 刷新以获取数据库生成的字段（如 id）
    return position

def create_employee(db: Session, username: str, email: str, full_name: str, 
                   position_id: int, salary: float):
    """创建员工"""
    employee = Employee(
        username=username,
        email=email,
        full_name=full_name,
        password_hash="hashed_password",  # 实际应用中应该加密
        position_id=position_id,
        salary=salary,
        hire_date=datetime.utcnow(),
        status=EmployeeStatus.active
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

# 批量创建
def create_multiple_positions(db: Session, positions_data: list):
    """批量创建岗位"""
    positions = [Position(**data) for data in positions_data]
    db.add_all(positions)
    db.commit()
    return positions

# 使用示例
db = SessionLocal()
try:
    position = create_position(db, "软件工程师", "SE001", 3)
    employee = create_employee(db, "zhangsan", "zhangsan@example.com", 
                              "张三", position.id, 15000.00)
finally:
    db.close()
```

### Read - 查询记录

```python
from sqlalchemy import select, and_, or_, func

def get_employee_by_id(db: Session, employee_id: int):
    """根据 ID 查询员工"""
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_username(db: Session, username: str):
    """根据用户名查询员工"""
    return db.query(Employee).filter(Employee.username == username).first()

def get_all_employees(db: Session, skip: int = 0, limit: int = 100):
    """查询所有员工（分页）"""
    return db.query(Employee).offset(skip).limit(limit).all()

def get_active_employees(db: Session):
    """查询所有在职员工"""
    return db.query(Employee).filter(
        Employee.status == EmployeeStatus.active
    ).all()

def get_employees_by_position(db: Session, position_id: int):
    """查询指定岗位的员工"""
    return db.query(Employee).filter(
        Employee.position_id == position_id
    ).all()

def search_employees(db: Session, keyword: str):
    """搜索员工（模糊查询）"""
    return db.query(Employee).filter(
        or_(
            Employee.full_name.like(f"%{keyword}%"),
            Employee.username.like(f"%{keyword}%"),
            Employee.email.like(f"%{keyword}%")
        )
    ).all()

def get_high_salary_employees(db: Session, min_salary: float):
    """查询高薪员工"""
    return db.query(Employee).filter(
        Employee.salary >= min_salary
    ).order_by(Employee.salary.desc()).all()

def get_employees_with_position(db: Session):
    """查询员工及其岗位信息（JOIN）"""
    return db.query(Employee).join(Position).all()

def get_employee_count_by_position(db: Session):
    """统计每个岗位的员工数量"""
    return db.query(
        Position.name,
        func.count(Employee.id).label('employee_count')
    ).join(Employee).group_by(Position.id).all()

# SQLAlchemy 2.0 风格查询
def get_employees_new_style(db: Session):
    """使用 SQLAlchemy 2.0 风格查询"""
    stmt = select(Employee).where(Employee.status == EmployeeStatus.active)
    result = db.execute(stmt)
    return result.scalars().all()
```

### Update - 更新记录

```python
def update_employee_salary(db: Session, employee_id: int, new_salary: float):
    """更新员工工资"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        employee.salary = new_salary
        db.commit()
        db.refresh(employee)
    return employee

def update_employee_status(db: Session, employee_id: int, status: EmployeeStatus):
    """更新员工状态"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        employee.status = status
        db.commit()
        db.refresh(employee)
    return employee

def bulk_update_salary(db: Session, position_id: int, increase_percent: float):
    """批量更新某岗位员工的工资"""
    db.query(Employee).filter(
        Employee.position_id == position_id
    ).update({
        Employee.salary: Employee.salary * (1 + increase_percent / 100)
    }, synchronize_session=False)
    db.commit()
```

### Delete - 删除记录

```python
def delete_employee(db: Session, employee_id: int):
    """删除员工"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        db.delete(employee)
        db.commit()
        return True
    return False

def delete_inactive_employees(db: Session):
    """删除所有离职员工"""
    deleted_count = db.query(Employee).filter(
        Employee.status == EmployeeStatus.inactive
    ).delete()
    db.commit()
    return deleted_count
```

## 关系查询

### 一对多关系

```python
def get_position_with_employees(db: Session, position_id: int):
    """查询岗位及其所有员工"""
    position = db.query(Position).filter(Position.id == position_id).first()
    if position:
        # 通过关系访问员工
        employees = position.employees
        return position, employees
    return None, []

def get_employee_with_work_logs(db: Session, employee_id: int):
    """查询员工及其工作日志"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        work_logs = employee.work_logs
        return employee, work_logs
    return None, []
```

### 预加载（Eager Loading）

```python
from sqlalchemy.orm import joinedload, selectinload

def get_employees_with_positions_eager(db: Session):
    """预加载员工和岗位信息（避免 N+1 查询问题）"""
    # 使用 joinedload（LEFT OUTER JOIN）
    employees = db.query(Employee).options(
        joinedload(Employee.position)
    ).all()
    return employees

def get_positions_with_employees_eager(db: Session):
    """预加载岗位和员工信息"""
    # 使用 selectinload（单独查询）
    positions = db.query(Position).options(
        selectinload(Position.employees)
    ).all()
    return positions
```

## 高级查询

### 聚合查询

```python
def get_salary_statistics(db: Session):
    """获取工资统计信息"""
    result = db.query(
        func.count(Employee.id).label('total_employees'),
        func.sum(Employee.salary).label('total_salary'),
        func.avg(Employee.salary).label('avg_salary'),
        func.max(Employee.salary).label('max_salary'),
        func.min(Employee.salary).label('min_salary')
    ).first()
    return result

def get_position_salary_stats(db: Session):
    """按岗位统计工资"""
    return db.query(
        Position.name,
        func.count(Employee.id).label('employee_count'),
        func.avg(Employee.salary).label('avg_salary'),
        func.sum(Employee.salary).label('total_salary')
    ).join(Employee).group_by(Position.id).all()
```

### 子查询

```python
from sqlalchemy import exists

def get_positions_with_employees_subquery(db: Session):
    """查询有员工的岗位（使用子查询）"""
    subquery = db.query(Employee.position_id).distinct().subquery()
    positions = db.query(Position).filter(
        Position.id.in_(subquery)
    ).all()
    return positions

def get_employees_above_avg_salary(db: Session):
    """查询工资高于平均工资的员工"""
    avg_salary = db.query(func.avg(Employee.salary)).scalar()
    return db.query(Employee).filter(
        Employee.salary > avg_salary
    ).all()

def check_position_has_employees(db: Session, position_id: int):
    """检查岗位是否有员工"""
    has_employees = db.query(
        exists().where(Employee.position_id == position_id)
    ).scalar()
    return has_employees
```

## 事务管理

```python
from contextlib import contextmanager

@contextmanager
def get_db():
    """数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# 使用示例
def transfer_salary(from_employee_id: int, to_employee_id: int, amount: float):
    """转移工资（事务示例）"""
    with get_db() as db:
        from_employee = db.query(Employee).filter(
            Employee.id == from_employee_id
        ).first()
        to_employee = db.query(Employee).filter(
            Employee.id == to_employee_id
        ).first()
        
        if not from_employee or not to_employee:
            raise ValueError("员工不存在")
        
        if from_employee.salary < amount:
            raise ValueError("工资不足")
        
        from_employee.salary -= amount
        to_employee.salary += amount
        # 如果没有异常，事务会自动提交
```

## 异步 ORM

SQLAlchemy 2.0 支持异步操作：

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

# 创建异步引擎
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    echo=True
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 异步 CRUD 操作
async def create_employee_async(username: str, email: str, full_name: str):
    """异步创建员工"""
    async with AsyncSessionLocal() as session:
        employee = Employee(
            username=username,
            email=email,
            full_name=full_name,
            password_hash="hashed_password",
            hire_date=datetime.utcnow()
        )
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        return employee

async def get_employees_async():
    """异步查询员工"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.status == EmployeeStatus.active)
        )
        return result.scalars().all()
```

## 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
# 安装 Alembic
pip install alembic

# 初始化 Alembic
alembic init alembic

# 创建迁移脚本
alembic revision --autogenerate -m "Create employees table"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 最佳实践

### 1. 会话管理

```python
# 推荐：使用上下文管理器
with get_db() as db:
    employee = create_employee(db, ...)

# 或使用依赖注入（FastAPI）
from fastapi import Depends

def get_db_dependency():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/employees")
def read_employees(db: Session = Depends(get_db_dependency)):
    return db.query(Employee).all()
```

### 2. 避免 N+1 查询问题

```python
# 不推荐：会产生 N+1 查询
employees = db.query(Employee).all()
for employee in employees:
    print(employee.position.name)  # 每次都会查询数据库

# 推荐：使用预加载
employees = db.query(Employee).options(
    joinedload(Employee.position)
).all()
for employee in employees:
    print(employee.position.name)  # 不会额外查询
```

### 3. 使用索引

```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # 添加索引
    email = Column(String(100), unique=True, index=True)
    
    # 复合索引
    __table_args__ = (
        Index('idx_position_status', 'position_id', 'status'),
    )
```

### 4. 数据验证

```python
from sqlalchemy.orm import validates

class Employee(Base):
    __tablename__ = "employees"
    
    # ... 其他字段 ...
    
    @validates('email')
    def validate_email(self, key, email):
        """验证邮箱格式"""
        if '@' not in email:
            raise ValueError("Invalid email address")
        return email
    
    @validates('salary')
    def validate_salary(self, key, salary):
        """验证工资范围"""
        if salary < 0:
            raise ValueError("Salary must be positive")
        return salary
```

### 5. 软删除

```python
class Employee(Base):
    __tablename__ = "employees"
    
    # ... 其他字段 ...
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

def soft_delete_employee(db: Session, employee_id: int):
    """软删除员工"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        employee.is_deleted = True
        employee.deleted_at = datetime.utcnow()
        db.commit()
```

## 常见问题

### 1. DetachedInstanceError

**问题**: 会话关闭后访问对象属性

**解决方案**:
```python
# 方法1：在会话中访问所有需要的属性
employee = db.query(Employee).first()
position_name = employee.position.name  # 在会话中访问

# 方法2：使用 expunge 和 merge
db.expunge(employee)  # 从会话中分离
db.merge(employee)    # 重新附加到会话
```

### 2. 循环导入

**问题**: 模型之间相互引用导致循环导入

**解决方案**:
```python
# 使用字符串引用
class Employee(Base):
    position = relationship("Position", back_populates="employees")

# 或延迟导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .position import Position
```

### 3. 性能优化

```python
# 使用 bulk 操作
db.bulk_insert_mappings(Employee, [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"},
])

# 使用原生 SQL（复杂查询）
from sqlalchemy import text
result = db.execute(text("SELECT * FROM employees WHERE salary > :salary"), 
                   {"salary": 10000})
```

## 参考资源

- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [SQLAlchemy 2.0 迁移指南](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [FastAPI 数据库集成](https://fastapi.tiangolo.com/tutorial/sql-databases/)

## 下一步

学习完 ORM 后，建议：

1. 实践数据库示例代码
2. 在 FastAPI/Flask 项目中集成 SQLAlchemy
3. 学习数据库迁移工具 Alembic
4. 了解数据库性能优化技巧
