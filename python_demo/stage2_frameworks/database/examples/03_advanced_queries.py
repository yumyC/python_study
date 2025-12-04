"""
SQLAlchemy 高级查询示例

本示例演示聚合查询、子查询、复杂过滤等高级查询技巧。
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, DECIMAL, ForeignKey, func, and_, or_, case
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timedelta
import random

Base = declarative_base()


class Department(Base):
    """部门模型"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    
    employees = relationship("Employee", back_populates="department")
    
    def __repr__(self):
        return f"<Department(name='{self.name}')>"


class Employee(Base):
    """员工模型"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    salary = Column(DECIMAL(10, 2))
    hire_date = Column(DateTime, nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    
    department = relationship("Department", back_populates="employees")
    
    def __repr__(self):
        return f"<Employee(name='{self.full_name}', salary={self.salary})>"


# 数据库配置
DATABASE_URL = "sqlite:///./advanced_queries.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def init_sample_data():
    """初始化示例数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(Department).count() > 0:
            print("数据已存在，跳过初始化")
            return
        
        # 创建部门
        departments = [
            Department(name="技术部", code="TECH"),
            Department(name="产品部", code="PROD"),
            Department(name="运营部", code="OPS"),
            Department(name="市场部", code="MKT"),
        ]
        db.add_all(departments)
        db.commit()
        
        # 创建员工
        names = ["张三", "李四", "王五", "赵六", "孙七", "周八", "吴九", "郑十",
                "钱一", "陈二", "刘三", "杨四", "黄五", "朱六", "林七", "何八"]
        
        for i, name in enumerate(names):
            employee = Employee(
                username=f"user{i+1:02d}",
                full_name=name,
                salary=random.randint(8000, 30000),
                hire_date=datetime.utcnow() - timedelta(days=random.randint(30, 1000)),
                department_id=random.choice([d.id for d in departments])
            )
            db.add(employee)
        
        db.commit()
        print("✓ 示例数据初始化完成")
    finally:
        db.close()


def aggregate_queries():
    """聚合查询示例"""
    db = SessionLocal()
    try:
        print("\n【聚合查询】")
        print("-" * 60)
        
        # 1. 基本统计
        total_employees = db.query(func.count(Employee.id)).scalar()
        total_salary = db.query(func.sum(Employee.salary)).scalar()
        avg_salary = db.query(func.avg(Employee.salary)).scalar()
        max_salary = db.query(func.max(Employee.salary)).scalar()
        min_salary = db.query(func.min(Employee.salary)).scalar()
        
        print(f"员工总数: {total_employees}")
        print(f"工资总额: ¥{float(total_salary):,.2f}")
        print(f"平均工资: ¥{float(avg_salary):,.2f}")
        print(f"最高工资: ¥{float(max_salary):,.2f}")
        print(f"最低工资: ¥{float(min_salary):,.2f}")
        
        # 2. 按部门分组统计
        print("\n按部门统计:")
        dept_stats = db.query(
            Department.name,
            func.count(Employee.id).label('employee_count'),
            func.avg(Employee.salary).label('avg_salary'),
            func.sum(Employee.salary).label('total_salary')
        ).join(Employee).group_by(Department.id).all()
        
        for dept_name, count, avg_sal, total_sal in dept_stats:
            print(f"  {dept_name}: {count}人, 平均¥{float(avg_sal):,.2f}, 总计¥{float(total_sal):,.2f}")
        
        # 3. HAVING 子句过滤
        print("\n平均工资超过 15000 的部门:")
        high_salary_depts = db.query(
            Department.name,
            func.avg(Employee.salary).label('avg_salary')
        ).join(Employee).group_by(Department.id).having(
            func.avg(Employee.salary) > 15000
        ).all()
        
        for dept_name, avg_sal in high_salary_depts:
            print(f"  {dept_name}: 平均¥{float(avg_sal):,.2f}")
        
    finally:
        db.close()


def subquery_examples():
    """子查询示例"""
    db = SessionLocal()
    try:
        print("\n【子查询】")
        print("-" * 60)
        
        # 1. 查询工资高于平均工资的员工
        avg_salary = db.query(func.avg(Employee.salary)).scalar()
        above_avg_employees = db.query(Employee).filter(
            Employee.salary > avg_salary
        ).all()
        
        print(f"工资高于平均工资 (¥{float(avg_salary):,.2f}) 的员工:")
        for emp in above_avg_employees:
            print(f"  {emp.full_name}: ¥{float(emp.salary):,.2f}")
        
        # 2. 查询每个部门工资最高的员工
        print("\n每个部门工资最高的员工:")
        
        # 子查询：每个部门的最高工资
        subq = db.query(
            Employee.department_id,
            func.max(Employee.salary).label('max_salary')
        ).group_by(Employee.department_id).subquery()
        
        # 主查询：找到对应的员工
        top_earners = db.query(Employee).join(
            subq,
            and_(
                Employee.department_id == subq.c.department_id,
                Employee.salary == subq.c.max_salary
            )
        ).all()
        
        for emp in top_earners:
            print(f"  {emp.department.name}: {emp.full_name} - ¥{float(emp.salary):,.2f}")
        
        # 3. 查询有员工的部门（EXISTS）
        print("\n有员工的部门:")
        from sqlalchemy import exists
        
        departments_with_employees = db.query(Department).filter(
            exists().where(Employee.department_id == Department.id)
        ).all()
        
        for dept in departments_with_employees:
            print(f"  {dept.name}")
        
    finally:
        db.close()


def complex_filters():
    """复杂过滤条件示例"""
    db = SessionLocal()
    try:
        print("\n【复杂过滤】")
        print("-" * 60)
        
        # 1. AND 条件
        print("工资在 15000-20000 之间的员工:")
        employees = db.query(Employee).filter(
            and_(
                Employee.salary >= 15000,
                Employee.salary <= 20000
            )
        ).all()
        
        for emp in employees:
            print(f"  {emp.full_name}: ¥{float(emp.salary):,.2f}")
        
        # 2. OR 条件
        print("\n工资低于 10000 或高于 25000 的员工:")
        employees = db.query(Employee).filter(
            or_(
                Employee.salary < 10000,
                Employee.salary > 25000
            )
        ).all()
        
        for emp in employees:
            print(f"  {emp.full_name}: ¥{float(emp.salary):,.2f}")
        
        # 3. IN 查询
        print("\n技术部和产品部的员工:")
        dept_ids = db.query(Department.id).filter(
            Department.name.in_(['技术部', '产品部'])
        ).all()
        dept_ids = [d[0] for d in dept_ids]
        
        employees = db.query(Employee).filter(
            Employee.department_id.in_(dept_ids)
        ).all()
        
        for emp in employees:
            print(f"  {emp.full_name} ({emp.department.name})")
        
        # 4. LIKE 模糊查询
        print("\n姓名包含'张'的员工:")
        employees = db.query(Employee).filter(
            Employee.full_name.like('%张%')
        ).all()
        
        for emp in employees:
            print(f"  {emp.full_name}")
        
        # 5. BETWEEN 范围查询
        print("\n入职时间在最近 180 天内的员工:")
        cutoff_date = datetime.utcnow() - timedelta(days=180)
        employees = db.query(Employee).filter(
            Employee.hire_date.between(cutoff_date, datetime.utcnow())
        ).all()
        
        for emp in employees:
            days_ago = (datetime.utcnow() - emp.hire_date).days
            print(f"  {emp.full_name}: {days_ago} 天前入职")
        
    finally:
        db.close()


def sorting_and_pagination():
    """排序和分页示例"""
    db = SessionLocal()
    try:
        print("\n【排序和分页】")
        print("-" * 60)
        
        # 1. 单字段排序
        print("按工资降序排列:")
        employees = db.query(Employee).order_by(Employee.salary.desc()).limit(5).all()
        
        for i, emp in enumerate(employees, 1):
            print(f"  {i}. {emp.full_name}: ¥{float(emp.salary):,.2f}")
        
        # 2. 多字段排序
        print("\n按部门和工资排序:")
        employees = db.query(Employee).join(Department).order_by(
            Department.name.asc(),
            Employee.salary.desc()
        ).all()
        
        current_dept = None
        for emp in employees:
            if emp.department.name != current_dept:
                current_dept = emp.department.name
                print(f"\n  {current_dept}:")
            print(f"    {emp.full_name}: ¥{float(emp.salary):,.2f}")
        
        # 3. 分页
        print("\n分页查询 (每页 5 条):")
        page_size = 5
        total = db.query(Employee).count()
        total_pages = (total + page_size - 1) // page_size
        
        for page in range(1, min(3, total_pages + 1)):  # 只显示前两页
            offset = (page - 1) * page_size
            employees = db.query(Employee).offset(offset).limit(page_size).all()
            print(f"\n  第 {page} 页:")
            for emp in employees:
                print(f"    {emp.full_name}")
        
    finally:
        db.close()


def case_expressions():
    """CASE 表达式示例"""
    db = SessionLocal()
    try:
        print("\n【CASE 表达式】")
        print("-" * 60)
        
        # 根据工资划分等级
        salary_level = case(
            (Employee.salary < 10000, '初级'),
            (Employee.salary < 20000, '中级'),
            else_='高级'
        ).label('salary_level')
        
        results = db.query(
            Employee.full_name,
            Employee.salary,
            salary_level
        ).all()
        
        print("员工工资等级:")
        for name, salary, level in results:
            print(f"  {name}: ¥{float(salary):,.2f} ({level})")
        
        # 统计各等级人数
        print("\n各等级人数统计:")
        level_stats = db.query(
            salary_level,
            func.count(Employee.id).label('count')
        ).group_by(salary_level).all()
        
        for level, count in level_stats:
            print(f"  {level}: {count}人")
        
    finally:
        db.close()


def window_functions():
    """窗口函数示例（需要支持窗口函数的数据库）"""
    db = SessionLocal()
    try:
        print("\n【排名查询】")
        print("-" * 60)
        
        # 按工资排名
        from sqlalchemy import select
        
        # 简单的排名实现（不使用窗口函数）
        employees = db.query(Employee).order_by(Employee.salary.desc()).all()
        
        print("工资排名:")
        for rank, emp in enumerate(employees, 1):
            print(f"  {rank}. {emp.full_name}: ¥{float(emp.salary):,.2f}")
        
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 60)
    print("SQLAlchemy 高级查询示例")
    print("=" * 60)
    
    # 初始化数据
    init_sample_data()
    
    # 1. 聚合查询
    aggregate_queries()
    
    # 2. 子查询
    subquery_examples()
    
    # 3. 复杂过滤
    complex_filters()
    
    # 4. 排序和分页
    sorting_and_pagination()
    
    # 5. CASE 表达式
    case_expressions()
    
    # 6. 排名查询
    window_functions()
    
    print("\n" + "=" * 60)
    print("示例执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
