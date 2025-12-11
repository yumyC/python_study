"""
数据库初始化脚本

这个脚本用于：
1. 创建所有数据表
2. 插入初始数据
3. 创建默认管理员账户
"""

from datetime import date
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, create_tables
from app.models import (
    Employee, EmployeeStatus,
    Position, 
    Menu,
    Role,
    RoleMenuPermission,
    WorkLog, CompletionStatus
)
from app.auth.jwt_handler import jwt_handler


def create_initial_positions(db: Session):
    """
    创建初始岗位数据
    """
    print("创建初始岗位数据...")
    
    # 创建根岗位
    ceo_position = Position(
        name="首席执行官",
        code="CEO",
        description="公司最高管理者",
        level=1
    )
    db.add(ceo_position)
    db.flush()  # 获取ID但不提交
    
    # 创建部门岗位
    tech_director = Position(
        name="技术总监",
        code="TECH_DIR",
        description="技术部门负责人",
        level=2,
        parent_id=ceo_position.id
    )
    
    hr_director = Position(
        name="人事总监", 
        code="HR_DIR",
        description="人事部门负责人",
        level=2,
        parent_id=ceo_position.id
    )
    
    db.add_all([tech_director, hr_director])
    db.flush()
    
    # 创建具体岗位
    positions = [
        Position(
            name="高级开发工程师",
            code="SENIOR_DEV",
            description="负责核心功能开发",
            level=3,
            parent_id=tech_director.id
        ),
        Position(
            name="初级开发工程师",
            code="JUNIOR_DEV", 
            description="负责基础功能开发",
            level=4,
            parent_id=tech_director.id
        ),
        Position(
            name="人事专员",
            code="HR_SPEC",
            description="负责招聘和员工管理",
            level=3,
            parent_id=hr_director.id
        )
    ]
    
    db.add_all(positions)
    print("✓ 岗位数据创建完成")


def create_initial_menus(db: Session):
    """
    创建初始菜单数据
    """
    print("创建初始菜单数据...")
    
    # 主菜单
    dashboard = Menu(
        name="仪表盘",
        path="/dashboard",
        icon="dashboard",
        component="Dashboard",
        sort_order=1
    )
    
    system_menu = Menu(
        name="系统管理",
        path="/system",
        icon="system",
        component="",
        sort_order=2
    )
    
    work_menu = Menu(
        name="工作管理",
        path="/work",
        icon="work",
        component="",
        sort_order=3
    )
    
    db.add_all([dashboard, system_menu, work_menu])
    db.flush()
    
    # 系统管理子菜单
    system_submenus = [
        Menu(
            name="员工管理",
            path="/system/employees",
            icon="user",
            component="EmployeeManagement",
            parent_id=system_menu.id,
            sort_order=1
        ),
        Menu(
            name="岗位管理",
            path="/system/positions",
            icon="position",
            component="PositionManagement",
            parent_id=system_menu.id,
            sort_order=2
        ),
        Menu(
            name="角色管理",
            path="/system/roles",
            icon="role",
            component="RoleManagement",
            parent_id=system_menu.id,
            sort_order=3
        ),
        Menu(
            name="菜单管理",
            path="/system/menus",
            icon="menu",
            component="MenuManagement",
            parent_id=system_menu.id,
            sort_order=4
        )
    ]
    
    # 工作管理子菜单
    work_submenus = [
        Menu(
            name="工作日志",
            path="/work/logs",
            icon="log",
            component="WorkLogManagement",
            parent_id=work_menu.id,
            sort_order=1
        ),
        Menu(
            name="日志统计",
            path="/work/statistics",
            icon="chart",
            component="WorkStatistics",
            parent_id=work_menu.id,
            sort_order=2
        )
    ]
    
    db.add_all(system_submenus + work_submenus)
    print("✓ 菜单数据创建完成")


def create_initial_roles(db: Session):
    """
    创建初始角色数据
    """
    print("创建初始角色数据...")
    
    # 创建角色
    admin_role = Role(
        name="系统管理员",
        code="ADMIN",
        description="拥有系统所有权限"
    )
    
    manager_role = Role(
        name="部门经理",
        code="MANAGER", 
        description="部门管理权限"
    )
    
    employee_role = Role(
        name="普通员工",
        code="EMPLOYEE",
        description="基础员工权限"
    )
    
    db.add_all([admin_role, manager_role, employee_role])
    db.flush()
    
    # 获取所有菜单
    menus = db.query(Menu).all()
    
    # 为管理员角色分配所有权限
    for menu in menus:
        admin_permission = RoleMenuPermission(
            role_id=admin_role.id,
            menu_id=menu.id,
            permissions=['view', 'create', 'update', 'delete']
        )
        db.add(admin_permission)
    
    # 为经理角色分配部分权限
    manager_menus = [menu for menu in menus if menu.path in [
        '/dashboard', '/work/logs', '/work/statistics', '/system/employees'
    ]]
    
    for menu in manager_menus:
        manager_permission = RoleMenuPermission(
            role_id=manager_role.id,
            menu_id=menu.id,
            permissions=['view', 'create', 'update']
        )
        db.add(manager_permission)
    
    # 为员工角色分配基础权限
    employee_menus = [menu for menu in menus if menu.path in [
        '/dashboard', '/work/logs'
    ]]
    
    for menu in employee_menus:
        employee_permission = RoleMenuPermission(
            role_id=employee_role.id,
            menu_id=menu.id,
            permissions=['view', 'create']
        )
        db.add(employee_permission)
    
    print("✓ 角色和权限数据创建完成")
    return admin_role, manager_role, employee_role


def create_initial_employees(db: Session, admin_role: Role, manager_role: Role, employee_role: Role):
    """
    创建初始员工数据
    """
    print("创建初始员工数据...")
    
    # 获取岗位
    ceo_position = db.query(Position).filter_by(code="CEO").first()
    tech_director_position = db.query(Position).filter_by(code="TECH_DIR").first()
    senior_dev_position = db.query(Position).filter_by(code="SENIOR_DEV").first()
    
    # 创建管理员账户
    admin_user = Employee(
        username="admin",
        email="admin@crm.com",
        password_hash=jwt_handler.hash_password("admin123"),
        full_name="系统管理员",
        position_id=ceo_position.id if ceo_position else None,
        role_id=admin_role.id,
        status=EmployeeStatus.ACTIVE
    )
    
    # 创建测试用户
    manager_user = Employee(
        username="manager",
        email="manager@crm.com", 
        password_hash=jwt_handler.hash_password("manager123"),
        full_name="张经理",
        position_id=tech_director_position.id if tech_director_position else None,
        role_id=manager_role.id,
        status=EmployeeStatus.ACTIVE
    )
    
    employee_user = Employee(
        username="employee",
        email="employee@crm.com",
        password_hash=jwt_handler.hash_password("employee123"),
        full_name="李开发",
        position_id=senior_dev_position.id if senior_dev_position else None,
        role_id=employee_role.id,
        status=EmployeeStatus.ACTIVE
    )
    
    db.add_all([admin_user, manager_user, employee_user])
    db.flush()
    
    print("✓ 员工数据创建完成")
    return admin_user, manager_user, employee_user


def create_sample_work_logs(db: Session, employees):
    """
    创建示例工作日志数据
    """
    print("创建示例工作日志数据...")
    
    from datetime import datetime, timedelta
    
    # 为每个员工创建最近几天的工作日志
    for employee in employees:
        for i in range(5):  # 创建5天的日志
            log_date = date.today() - timedelta(days=i)
            
            work_log = WorkLog(
                employee_id=employee.id,
                log_date=log_date,
                work_content=f"完成了{employee.full_name}的第{i+1}天工作任务，包括代码开发、文档编写等。",
                completion_status=CompletionStatus.COMPLETED if i < 3 else CompletionStatus.IN_PROGRESS,
                problems_encountered="遇到了一些技术难题，已通过查阅资料解决。" if i % 2 == 0 else None,
                tomorrow_plan=f"明天计划继续推进项目进度，完成剩余功能开发。",
                self_rating=4 if i < 3 else 3,
                supervisor_rating=4 if i < 2 else None,
                supervisor_comment="工作完成质量较好，继续保持。" if i < 2 else None
            )
            
            db.add(work_log)
    
    print("✓ 工作日志数据创建完成")


def init_database():
    """
    初始化数据库
    """
    print("开始初始化数据库...")
    
    # 创建所有表
    create_tables()
    print("✓ 数据表创建完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已经初始化过
        existing_admin = db.query(Employee).filter_by(username="admin").first()
        if existing_admin:
            print("数据库已经初始化过，跳过初始化步骤")
            return
        
        # 创建初始数据
        create_initial_positions(db)
        create_initial_menus(db)
        admin_role, manager_role, employee_role = create_initial_roles(db)
        admin_user, manager_user, employee_user = create_initial_employees(
            db, admin_role, manager_role, employee_role
        )
        create_sample_work_logs(db, [admin_user, manager_user, employee_user])
        
        # 提交所有更改
        db.commit()
        print("✓ 数据库初始化完成！")
        
        # 输出默认账户信息
        print("\n默认账户信息：")
        print("管理员账户: admin / admin123")
        print("经理账户: manager / manager123") 
        print("员工账户: employee / employee123")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()