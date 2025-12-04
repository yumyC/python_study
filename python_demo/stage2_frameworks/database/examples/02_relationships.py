"""
SQLAlchemy 关系查询示例

本示例演示如何定义和使用表之间的关系（一对多、多对一）。
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, DECIMAL, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timedelta

# 创建基类
Base = declarative_base()


# 定义岗位模型
class Position(Base):
    """岗位模型"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 一对多关系：一个岗位可以有多个员工
    employees = relationship("Employee", back_populates="position")
    
    def __repr__(self):
        return f"<Position(id={self.id}, name='{self.name}', code='{self.code}')>"


# 定义员工模型
class Employee(Base):
    """员工模型"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    salary = Column(DECIMAL(10, 2))
    hire_date = Column(DateTime, nullable=False)
    position_id = Column(Integer, ForeignKey('positions.id'))  # 外键
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 多对一关系：多个员工属于一个岗位
    position = relationship("Position", back_populates="employees")
    
    # 一对多关系：一个员工可以有多条工作日志
    work_logs = relationship("WorkLog", back_populates="employee", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, username='{self.username}', full_name='{self.full_name}')>"


# 定义工作日志模型
class WorkLog(Base):
    """工作日志模型"""
    __tablename__ = "work_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    log_date = Column(DateTime, nullable=False)
    work_content = Column(Text, nullable=False)
    completion_status = Column(String(50))
    self_rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 多对一关系：多条工作日志属于一个员工
    employee = relationship("Employee", back_populates="work_logs")
    
    def __repr__(self):
        return f"<WorkLog(id={self.id}, employee_id={self.employee_id}, date={self.log_date.date()})>"


# 数据库配置
DATABASE_URL = "sqlite:///./relationships.db"
engine = create_engine(DATABASE_URL, echo=False)  # echo=False 减少输出
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有表
Base.metadata.create_all(bind=engine)


def create_position(name: str, code: str, level: int, description: str = ""):
    """创建岗位"""
    db = SessionLocal()
    try:
        position = Position(
            name=name,
            code=code,
            level=level,
            description=description
        )
        db.add(position)
        db.commit()
        db.refresh(position)
        print(f"✓ 创建岗位: {position.name} (Level {position.level})")
        return position
    finally:
        db.close()


def create_employee(username: str, email: str, full_name: str, 
                   salary: float, position_id: int):
    """创建员工"""
    db = SessionLocal()
    try:
        employee = Employee(
            username=username,
            email=email,
            full_name=full_name,
            salary=salary,
            hire_date=datetime.utcnow(),
            position_id=position_id
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        print(f"✓ 创建员工: {employee.full_name} ({employee.username})")
        return employee
    finally:
        db.close()


def create_work_log(employee_id: int, work_content: str, 
                   completion_status: str, self_rating: int):
    """创建工作日志"""
    db = SessionLocal()
    try:
        work_log = WorkLog(
            employee_id=employee_id,
            log_date=datetime.utcnow(),
            work_content=work_content,
            completion_status=completion_status,
            self_rating=self_rating
        )
        db.add(work_log)
        db.commit()
        db.refresh(work_log)
        print(f"✓ 创建工作日志: Employee ID {employee_id}")
        return work_log
    finally:
        db.close()


def get_position_with_employees(position_id: int):
    """
    查询岗位及其所有员工（一对多关系）
    """
    db = SessionLocal()
    try:
        position = db.query(Position).filter(Position.id == position_id).first()
        if position:
            print(f"\n岗位信息: {position.name} (Level {position.level})")
            print(f"该岗位下的员工 ({len(position.employees)} 人):")
            for emp in position.employees:
                print(f"  - {emp.full_name} ({emp.username}) - 工资: ¥{emp.salary}")
            return position
        else:
            print(f"✗ 未找到 ID 为 {position_id} 的岗位")
            return None
    finally:
        db.close()


def get_employee_with_position(employee_id: int):
    """
    查询员工及其岗位信息（多对一关系）
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            print(f"\n员工信息: {employee.full_name} ({employee.username})")
            if employee.position:
                print(f"岗位: {employee.position.name} (Level {employee.position.level})")
            else:
                print("岗位: 未分配")
            return employee
        else:
            print(f"✗ 未找到 ID 为 {employee_id} 的员工")
            return None
    finally:
        db.close()


def get_employee_with_work_logs(employee_id: int):
    """
    查询员工及其所有工作日志（一对多关系）
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            print(f"\n员工信息: {employee.full_name} ({employee.username})")
            print(f"工作日志 ({len(employee.work_logs)} 条):")
            for log in employee.work_logs:
                print(f"  - {log.log_date.date()}: {log.work_content[:50]}... (评分: {log.self_rating}/5)")
            return employee
        else:
            print(f"✗ 未找到 ID 为 {employee_id} 的员工")
            return None
    finally:
        db.close()


def get_all_employees_with_positions():
    """
    查询所有员工及其岗位信息（使用 JOIN）
    """
    db = SessionLocal()
    try:
        # 使用 join 查询
        employees = db.query(Employee).join(Position).all()
        print(f"\n所有员工及其岗位信息 ({len(employees)} 人):")
        for emp in employees:
            print(f"  - {emp.full_name}: {emp.position.name} (Level {emp.position.level}) - ¥{emp.salary}")
        return employees
    finally:
        db.close()


def get_positions_with_employee_count():
    """
    统计每个岗位的员工数量
    """
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # 使用聚合函数统计
        results = db.query(
            Position.name,
            Position.level,
            func.count(Employee.id).label('employee_count'),
            func.avg(Employee.salary).label('avg_salary')
        ).outerjoin(Employee).group_by(Position.id).all()
        
        print("\n岗位统计信息:")
        for name, level, count, avg_salary in results:
            avg_salary_str = f"¥{float(avg_salary):.2f}" if avg_salary else "N/A"
            print(f"  - {name} (Level {level}): {count} 人, 平均工资: {avg_salary_str}")
        return results
    finally:
        db.close()


def get_high_level_employees():
    """
    查询高级别岗位的员工（Level >= 4）
    """
    db = SessionLocal()
    try:
        employees = db.query(Employee).join(Position).filter(
            Position.level >= 4
        ).all()
        
        print(f"\n高级别岗位员工 (Level >= 4, 共 {len(employees)} 人):")
        for emp in employees:
            print(f"  - {emp.full_name}: {emp.position.name} (Level {emp.position.level})")
        return employees
    finally:
        db.close()


def update_employee_position(employee_id: int, new_position_id: int):
    """
    更新员工的岗位
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        new_position = db.query(Position).filter(Position.id == new_position_id).first()
        
        if employee and new_position:
            old_position = employee.position.name if employee.position else "未分配"
            employee.position_id = new_position_id
            db.commit()
            db.refresh(employee)
            print(f"✓ 更新员工岗位: {employee.full_name} 从 '{old_position}' 调整为 '{new_position.name}'")
            return employee
        else:
            print("✗ 员工或岗位不存在")
            return None
    finally:
        db.close()


def main():
    """主函数：演示关系查询"""
    print("=" * 60)
    print("SQLAlchemy 关系查询示例")
    print("=" * 60)
    
    # 1. 创建岗位
    print("\n1. 创建岗位")
    print("-" * 60)
    pos1 = create_position("初级工程师", "JE001", 2, "负责基础开发工作")
    pos2 = create_position("中级工程师", "ME001", 3, "负责模块开发")
    pos3 = create_position("高级工程师", "SE001", 4, "负责核心功能开发")
    pos4 = create_position("技术经理", "TM001", 5, "负责技术管理")
    
    # 2. 创建员工
    print("\n2. 创建员工")
    print("-" * 60)
    emp1 = create_employee("zhangsan", "zhangsan@example.com", "张三", 12000.00, pos1.id)
    emp2 = create_employee("lisi", "lisi@example.com", "李四", 15000.00, pos2.id)
    emp3 = create_employee("wangwu", "wangwu@example.com", "王五", 18000.00, pos3.id)
    emp4 = create_employee("zhaoliu", "zhaoliu@example.com", "赵六", 25000.00, pos4.id)
    emp5 = create_employee("sunqi", "sunqi@example.com", "孙七", 14000.00, pos2.id)
    
    # 3. 创建工作日志
    print("\n3. 创建工作日志")
    print("-" * 60)
    create_work_log(emp1.id, "完成用户登录功能开发", "已完成", 4)
    create_work_log(emp1.id, "修复若干 Bug", "已完成", 3)
    create_work_log(emp2.id, "完成订单模块设计和开发", "进行中", 4)
    create_work_log(emp3.id, "完成系统架构优化", "已完成", 5)
    
    # 4. 查询岗位及其员工（一对多）
    print("\n4. 查询岗位及其员工")
    print("-" * 60)
    get_position_with_employees(pos2.id)
    
    # 5. 查询员工及其岗位（多对一）
    print("\n5. 查询员工及其岗位")
    print("-" * 60)
    get_employee_with_position(emp3.id)
    
    # 6. 查询员工及其工作日志（一对多）
    print("\n6. 查询员工及其工作日志")
    print("-" * 60)
    get_employee_with_work_logs(emp1.id)
    
    # 7. 查询所有员工及其岗位（JOIN）
    print("\n7. 查询所有员工及其岗位")
    print("-" * 60)
    get_all_employees_with_positions()
    
    # 8. 统计岗位信息
    print("\n8. 统计岗位信息")
    print("-" * 60)
    get_positions_with_employee_count()
    
    # 9. 查询高级别岗位员工
    print("\n9. 查询高级别岗位员工")
    print("-" * 60)
    get_high_level_employees()
    
    # 10. 更新员工岗位
    print("\n10. 更新员工岗位")
    print("-" * 60)
    update_employee_position(emp1.id, pos2.id)
    
    # 11. 验证更新结果
    print("\n11. 验证更新结果")
    print("-" * 60)
    get_position_with_employees(pos2.id)
    
    print("\n" + "=" * 60)
    print("示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
