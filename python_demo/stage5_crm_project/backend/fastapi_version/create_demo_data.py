#!/usr/bin/env python3
"""
CRM 系统演示数据创建脚本

这个脚本用于创建演示数据，包括：
1. 更多的员工数据
2. 丰富的工作日志数据  
3. 完整的组织架构
4. 真实的业务场景数据

使用方法:
    python create_demo_data.py

注意: 运行前请确保数据库已经初始化 (python app/init_db.py)
"""

import random
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    Employee, EmployeeStatus,
    Position, 
    Role,
    WorkLog, CompletionStatus
)
from app.auth.jwt_handler import jwt_handler


# 演示数据配置
DEMO_EMPLOYEES = [
    {
        "username": "wang_dev",
        "email": "wang.dev@crm.com",
        "full_name": "王小明",
        "position_code": "SENIOR_DEV",
        "role_code": "EMPLOYEE"
    },
    {
        "username": "li_dev", 
        "email": "li.dev@crm.com",
        "full_name": "李小红",
        "position_code": "JUNIOR_DEV",
        "role_code": "EMPLOYEE"
    },
    {
        "username": "zhang_hr",
        "email": "zhang.hr@crm.com", 
        "full_name": "张小华",
        "position_code": "HR_SPEC",
        "role_code": "EMPLOYEE"
    },
    {
        "username": "chen_dev",
        "email": "chen.dev@crm.com",
        "full_name": "陈小强",
        "position_code": "SENIOR_DEV", 
        "role_code": "EMPLOYEE"
    },
    {
        "username": "liu_dev",
        "email": "liu.dev@crm.com",
        "full_name": "刘小美",
        "position_code": "JUNIOR_DEV",
        "role_code": "EMPLOYEE"
    }
]

# 工作内容模板
WORK_CONTENT_TEMPLATES = [
    "完成了用户管理模块的开发，包括用户注册、登录、信息修改等功能",
    "修复了系统中的若干 Bug，提升了系统稳定性",
    "参与了项目需求评审会议，明确了下一阶段的开发任务",
    "完成了数据库设计优化，提升了查询性能",
    "编写了单元测试用例，保证代码质量",
    "参与了代码审查，学习了团队的最佳实践",
    "完成了 API 文档的编写和更新",
    "进行了技术调研，为项目选型提供了参考",
    "优化了前端页面的用户体验",
    "参与了系统部署和运维工作",
    "完成了新员工的技术培训",
    "参与了客户需求沟通，收集了用户反馈",
    "完成了系统监控和日志分析",
    "进行了安全漏洞扫描和修复",
    "参与了技术分享会，提升了团队技术水平"
]

PROBLEMS_TEMPLATES = [
    "遇到了数据库连接超时的问题，通过调整连接池配置解决",
    "在处理并发请求时出现了死锁，通过优化事务逻辑解决",
    "前端页面在某些浏览器上显示异常，通过兼容性处理解决",
    "第三方 API 调用失败，通过添加重试机制解决",
    "服务器内存使用率过高，通过代码优化和配置调整解决",
    "测试环境部署失败，通过检查配置文件解决",
    "代码合并时出现冲突，通过仔细对比和沟通解决",
    None,  # 有些日志没有问题
    None,
    "新技术学习遇到困难，通过查阅文档和请教同事解决"
]

TOMORROW_PLANS = [
    "继续完成当前模块的开发，争取按时交付",
    "开始下一个功能模块的设计和开发",
    "进行代码重构，提升代码质量和可维护性",
    "编写更多的测试用例，提高测试覆盖率",
    "学习新的技术框架，提升个人技能",
    "参与产品需求讨论，明确开发方向",
    "优化系统性能，提升用户体验",
    "完善项目文档，方便团队协作",
    "进行技术分享，帮助团队成长",
    "参与系统维护和监控工作"
]


def create_demo_employees(db: Session):
    """
    创建演示员工数据
    """
    print("创建演示员工数据...")
    
    created_count = 0
    
    for emp_data in DEMO_EMPLOYEES:
        # 检查员工是否已存在
        existing_emp = db.query(Employee).filter_by(username=emp_data["username"]).first()
        if existing_emp:
            print(f"员工 {emp_data['username']} 已存在，跳过创建")
            continue
        
        # 获取岗位和角色
        position = db.query(Position).filter_by(code=emp_data["position_code"]).first()
        role = db.query(Role).filter_by(code=emp_data["role_code"]).first()
        
        if not position or not role:
            print(f"岗位 {emp_data['position_code']} 或角色 {emp_data['role_code']} 不存在，跳过员工 {emp_data['username']}")
            continue
        
        # 创建员工
        employee = Employee(
            username=emp_data["username"],
            email=emp_data["email"],
            password_hash=jwt_handler.hash_password("123456"),  # 默认密码
            full_name=emp_data["full_name"],
            position_id=position.id,
            role_id=role.id,
            status=EmployeeStatus.ACTIVE
        )
        
        db.add(employee)
        created_count += 1
    
    db.commit()
    print(f"✓ 创建了 {created_count} 个演示员工")


def create_demo_work_logs(db: Session):
    """
    创建演示工作日志数据
    """
    print("创建演示工作日志数据...")
    
    # 获取所有员工
    employees = db.query(Employee).all()
    
    created_count = 0
    
    # 为每个员工创建最近 30 天的工作日志
    for employee in employees:
        for i in range(30):
            log_date = date.today() - timedelta(days=i)
            
            # 检查是否已存在该日期的日志
            existing_log = db.query(WorkLog).filter_by(
                employee_id=employee.id,
                log_date=log_date
            ).first()
            
            if existing_log:
                continue  # 跳过已存在的日志
            
            # 随机选择工作内容和其他字段
            work_content = random.choice(WORK_CONTENT_TEMPLATES)
            problems = random.choice(PROBLEMS_TEMPLATES)
            tomorrow_plan = random.choice(TOMORROW_PLANS)
            
            # 随机生成完成状态和评分
            completion_status = random.choices(
                [CompletionStatus.COMPLETED, CompletionStatus.IN_PROGRESS, CompletionStatus.PENDING],
                weights=[70, 25, 5]  # 70% 完成，25% 进行中，5% 待处理
            )[0]
            
            self_rating = random.randint(3, 5)  # 自评 3-5 分
            
            # 30% 的概率有上级评分
            supervisor_rating = None
            supervisor_comment = None
            if random.random() < 0.3:
                supervisor_rating = random.randint(3, 5)
                supervisor_comment = f"工作完成情况{'良好' if supervisor_rating >= 4 else '一般'}，{'继续保持' if supervisor_rating >= 4 else '需要改进'}。"
            
            work_log = WorkLog(
                employee_id=employee.id,
                log_date=log_date,
                work_content=work_content,
                completion_status=completion_status,
                problems_encountered=problems,
                tomorrow_plan=tomorrow_plan,
                self_rating=self_rating,
                supervisor_rating=supervisor_rating,
                supervisor_comment=supervisor_comment
            )
            
            db.add(work_log)
            created_count += 1
    
    db.commit()
    print(f"✓ 创建了 {created_count} 条演示工作日志")


def create_additional_positions(db: Session):
    """
    创建更多的岗位数据，丰富组织架构
    """
    print("创建额外的岗位数据...")
    
    # 获取现有的部门岗位
    tech_director = db.query(Position).filter_by(code="TECH_DIR").first()
    hr_director = db.query(Position).filter_by(code="HR_DIR").first()
    
    if not tech_director or not hr_director:
        print("基础岗位不存在，请先运行 init_db.py")
        return
    
    additional_positions = [
        {
            "name": "产品经理",
            "code": "PRODUCT_MANAGER",
            "description": "负责产品规划和需求管理",
            "level": 3,
            "parent_id": tech_director.id
        },
        {
            "name": "UI/UX 设计师",
            "code": "UI_DESIGNER", 
            "description": "负责用户界面和体验设计",
            "level": 3,
            "parent_id": tech_director.id
        },
        {
            "name": "测试工程师",
            "code": "QA_ENGINEER",
            "description": "负责软件测试和质量保证",
            "level": 3,
            "parent_id": tech_director.id
        },
        {
            "name": "运维工程师",
            "code": "DEVOPS_ENGINEER",
            "description": "负责系统运维和部署",
            "level": 3,
            "parent_id": tech_director.id
        },
        {
            "name": "招聘专员",
            "code": "RECRUITER",
            "description": "负责人才招聘和面试",
            "level": 3,
            "parent_id": hr_director.id
        },
        {
            "name": "培训专员",
            "code": "TRAINER",
            "description": "负责员工培训和发展",
            "level": 3,
            "parent_id": hr_director.id
        }
    ]
    
    created_count = 0
    
    for pos_data in additional_positions:
        # 检查岗位是否已存在
        existing_pos = db.query(Position).filter_by(code=pos_data["code"]).first()
        if existing_pos:
            continue
        
        position = Position(
            name=pos_data["name"],
            code=pos_data["code"],
            description=pos_data["description"],
            level=pos_data["level"],
            parent_id=pos_data["parent_id"]
        )
        
        db.add(position)
        created_count += 1
    
    db.commit()
    print(f"✓ 创建了 {created_count} 个额外岗位")


def main():
    """
    主函数：创建所有演示数据
    """
    print("开始创建 CRM 系统演示数据...")
    print("=" * 50)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查数据库是否已初始化
        admin_user = db.query(Employee).filter_by(username="admin").first()
        if not admin_user:
            print("❌ 数据库尚未初始化，请先运行: python app/init_db.py")
            return
        
        # 创建演示数据
        create_additional_positions(db)
        create_demo_employees(db)
        create_demo_work_logs(db)
        
        print("=" * 50)
        print("✅ 演示数据创建完成！")
        
        # 统计信息
        total_employees = db.query(Employee).count()
        total_positions = db.query(Position).count()
        total_work_logs = db.query(WorkLog).count()
        
        print(f"\n📊 数据统计:")
        print(f"员工总数: {total_employees}")
        print(f"岗位总数: {total_positions}")
        print(f"工作日志总数: {total_work_logs}")
        
        print(f"\n🔑 演示账户信息:")
        print("管理员: admin / admin123")
        print("经理: manager / manager123")
        print("员工: employee / employee123")
        print("演示员工: wang_dev, li_dev, zhang_hr, chen_dev, liu_dev / 123456")
        
        print(f"\n🌐 访问地址:")
        print("前端: http://localhost:3000")
        print("后端 API: http://localhost:8000")
        print("API 文档: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ 创建演示数据失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()