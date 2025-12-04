"""
SQLAlchemy 基础 CRUD 操作示例

本示例演示如何使用 SQLAlchemy 进行基本的增删改查操作。
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, DECIMAL, Enum
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import enum

# 创建基类
Base = declarative_base()

# 定义员工状态枚举
class EmployeeStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

# 定义员工模型
class Employee(Base):
    """员工模型"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    salary = Column(DECIMAL(10, 2))
    hire_date = Column(DateTime, nullable=False)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Employee(id={self.id}, username='{self.username}', full_name='{self.full_name}')>"


# 数据库配置
DATABASE_URL = "sqlite:///./employees.db"

# 创建引擎
engine = create_engine(DATABASE_URL, echo=True)  # echo=True 会打印 SQL 语句

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有表
Base.metadata.create_all(bind=engine)


def create_employee(username: str, email: str, full_name: str, salary: float):
    """
    创建员工
    
    Args:
        username: 用户名
        email: 邮箱
        full_name: 全名
        salary: 工资
    
    Returns:
        Employee: 创建的员工对象
    """
    db = SessionLocal()
    try:
        employee = Employee(
            username=username,
            email=email,
            full_name=full_name,
            salary=salary,
            hire_date=datetime.utcnow(),
            status=EmployeeStatus.active
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)  # 刷新对象以获取数据库生成的字段
        print(f"✓ 创建员工成功: {employee}")
        return employee
    except Exception as e:
        db.rollback()
        print(f"✗ 创建员工失败: {e}")
        raise
    finally:
        db.close()


def get_employee_by_id(employee_id: int):
    """
    根据 ID 查询员工
    
    Args:
        employee_id: 员工 ID
    
    Returns:
        Employee: 员工对象，如果不存在返回 None
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            print(f"✓ 查询到员工: {employee}")
        else:
            print(f"✗ 未找到 ID 为 {employee_id} 的员工")
        return employee
    finally:
        db.close()


def get_all_employees(skip: int = 0, limit: int = 100):
    """
    查询所有员工（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
    
    Returns:
        list: 员工列表
    """
    db = SessionLocal()
    try:
        employees = db.query(Employee).offset(skip).limit(limit).all()
        print(f"✓ 查询到 {len(employees)} 名员工")
        for emp in employees:
            print(f"  - {emp}")
        return employees
    finally:
        db.close()


def get_employees_by_status(status: EmployeeStatus):
    """
    根据状态查询员工
    
    Args:
        status: 员工状态
    
    Returns:
        list: 员工列表
    """
    db = SessionLocal()
    try:
        employees = db.query(Employee).filter(Employee.status == status).all()
        print(f"✓ 查询到 {len(employees)} 名 {status.value} 状态的员工")
        return employees
    finally:
        db.close()


def search_employees(keyword: str):
    """
    搜索员工（模糊查询）
    
    Args:
        keyword: 搜索关键词
    
    Returns:
        list: 员工列表
    """
    db = SessionLocal()
    try:
        employees = db.query(Employee).filter(
            (Employee.full_name.like(f"%{keyword}%")) |
            (Employee.username.like(f"%{keyword}%"))
        ).all()
        print(f"✓ 搜索 '{keyword}' 找到 {len(employees)} 名员工")
        return employees
    finally:
        db.close()


def update_employee_salary(employee_id: int, new_salary: float):
    """
    更新员工工资
    
    Args:
        employee_id: 员工 ID
        new_salary: 新工资
    
    Returns:
        Employee: 更新后的员工对象
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            old_salary = employee.salary
            employee.salary = new_salary
            db.commit()
            db.refresh(employee)
            print(f"✓ 更新员工工资成功: {employee.full_name} 从 {old_salary} 更新为 {new_salary}")
            return employee
        else:
            print(f"✗ 未找到 ID 为 {employee_id} 的员工")
            return None
    except Exception as e:
        db.rollback()
        print(f"✗ 更新员工工资失败: {e}")
        raise
    finally:
        db.close()


def update_employee_status(employee_id: int, status: EmployeeStatus):
    """
    更新员工状态
    
    Args:
        employee_id: 员工 ID
        status: 新状态
    
    Returns:
        Employee: 更新后的员工对象
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            employee.status = status
            db.commit()
            db.refresh(employee)
            print(f"✓ 更新员工状态成功: {employee.full_name} 状态更新为 {status.value}")
            return employee
        else:
            print(f"✗ 未找到 ID 为 {employee_id} 的员工")
            return None
    except Exception as e:
        db.rollback()
        print(f"✗ 更新员工状态失败: {e}")
        raise
    finally:
        db.close()


def delete_employee(employee_id: int):
    """
    删除员工
    
    Args:
        employee_id: 员工 ID
    
    Returns:
        bool: 是否删除成功
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            db.delete(employee)
            db.commit()
            print(f"✓ 删除员工成功: {employee.full_name}")
            return True
        else:
            print(f"✗ 未找到 ID 为 {employee_id} 的员工")
            return False
    except Exception as e:
        db.rollback()
        print(f"✗ 删除员工失败: {e}")
        raise
    finally:
        db.close()


def main():
    """主函数：演示所有 CRUD 操作"""
    print("=" * 60)
    print("SQLAlchemy 基础 CRUD 操作示例")
    print("=" * 60)
    
    # 1. 创建员工
    print("\n1. 创建员工")
    print("-" * 60)
    emp1 = create_employee("zhangsan", "zhangsan@example.com", "张三", 15000.00)
    emp2 = create_employee("lisi", "lisi@example.com", "李四", 18000.00)
    emp3 = create_employee("wangwu", "wangwu@example.com", "王五", 12000.00)
    
    # 2. 查询员工
    print("\n2. 查询员工")
    print("-" * 60)
    print("\n2.1 根据 ID 查询")
    get_employee_by_id(emp1.id)
    
    print("\n2.2 查询所有员工")
    get_all_employees()
    
    print("\n2.3 根据状态查询")
    get_employees_by_status(EmployeeStatus.active)
    
    print("\n2.4 搜索员工")
    search_employees("张")
    
    # 3. 更新员工
    print("\n3. 更新员工")
    print("-" * 60)
    print("\n3.1 更新工资")
    update_employee_salary(emp1.id, 16000.00)
    
    print("\n3.2 更新状态")
    update_employee_status(emp3.id, EmployeeStatus.inactive)
    
    # 4. 再次查询验证更新
    print("\n4. 验证更新结果")
    print("-" * 60)
    get_all_employees()
    
    # 5. 删除员工
    print("\n5. 删除员工")
    print("-" * 60)
    delete_employee(emp3.id)
    
    # 6. 最终查询
    print("\n6. 最终员工列表")
    print("-" * 60)
    get_all_employees()
    
    print("\n" + "=" * 60)
    print("示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
