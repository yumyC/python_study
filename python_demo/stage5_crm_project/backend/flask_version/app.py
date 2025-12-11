"""
Flask CRM 应用主入口

这个文件演示了如何使用定义的数据模型和认证授权系统
"""

from flask import Flask, jsonify
from app import create_app, db
from app.models import Employee, Position, Menu, Role, WorkLog
from app.middleware.request_logging import setup_flask_request_logging
from app.middleware.request_id import setup_flask_request_id
from app.middleware.error_handler import setup_flask_error_handler

# 创建应用实例
app = create_app()

# 设置中间件（Flask 风格）
setup_flask_request_id(app)
setup_flask_request_logging(app)
setup_flask_error_handler(app)


@app.route('/')
def root():
    """
    根路径，返回 API 信息
    """
    return jsonify({
        "message": "欢迎使用 Flask CRM 系统 API",
        "version": "1.0.0",
        "framework": "Flask",
        "docs": "/docs"  # 注意：Flask 没有自动生成的文档，需要手动实现
    })


@app.route('/health')
def health_check():
    """
    健康检查接口
    
    检查数据库连接和基本功能
    """
    try:
        # 测试数据库连接
        employee_count = Employee.query.count()
        position_count = Position.query.count()
        menu_count = Menu.query.count()
        role_count = Role.query.count()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "framework": "Flask",
            "counts": {
                "employees": employee_count,
                "positions": position_count,
                "menus": menu_count,
                "roles": role_count
            }
        })
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'HEALTH_CHECK_FAILED',
                'message': f'健康检查失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@app.route('/demo/employees')
def demo_employees():
    """
    演示员工查询功能（无需认证）
    
    演示 Employee 模型的查询操作
    """
    try:
        employees = Employee.query.limit(10).all()
        
        result = []
        for employee in employees:
            employee_data = {
                "id": str(employee.id),
                "username": employee.username,
                "email": employee.email,
                "full_name": employee.full_name,
                "status": employee.status.value,
                "position": employee.position.name if employee.position else None,
                "role": employee.role.name if employee.role else None,
                "created_at": employee.created_at.isoformat() if employee.created_at else None
            }
            result.append(employee_data)
        
        return jsonify({
            'employees': result,
            'total': len(result),
            'message': '这是演示数据，实际使用需要认证'
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'DEMO_ERROR',
                'message': f'演示查询失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@app.route('/demo/positions')
def demo_positions():
    """
    演示岗位查询功能（无需认证）
    
    演示 Position 模型的查询和层级关系
    """
    try:
        positions = Position.query.limit(10).all()
        
        result = []
        for position in positions:
            position_data = {
                "id": str(position.id),
                "name": position.name,
                "code": position.code,
                "description": position.description,
                "level": position.level,
                "parent_name": position.parent.name if position.parent else None,
                "full_path": position.get_full_path(),
                "employee_count": position.employees.count()
            }
            result.append(position_data)
        
        return jsonify({
            'positions': result,
            'total': len(result),
            'message': '这是演示数据，实际使用需要认证'
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'DEMO_ERROR',
                'message': f'演示查询失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@app.route('/demo/menus')
def demo_menus():
    """
    演示菜单查询功能（无需认证）
    
    演示 Menu 模型的树形结构查询
    """
    try:
        # 获取根菜单（没有父菜单的菜单）
        root_menus = Menu.query.filter(Menu.parent_id.is_(None)).order_by(Menu.sort_order).limit(5).all()
        
        result = []
        for menu in root_menus:
            menu_tree = menu.to_tree_dict(include_children=True)
            result.append(menu_tree)
        
        return jsonify({
            'menus': result,
            'total': len(result),
            'message': '这是演示数据，实际使用需要认证'
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'DEMO_ERROR',
                'message': f'演示查询失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@app.route('/demo/work-logs')
def demo_work_logs():
    """
    演示工作日志查询功能（无需认证）
    
    演示 WorkLog 模型的查询和关联数据
    """
    try:
        work_logs = WorkLog.query.order_by(WorkLog.log_date.desc()).limit(10).all()
        
        result = []
        for log in work_logs:
            log_data = {
                "id": str(log.id),
                "employee_name": log.employee.full_name if log.employee else None,
                "log_date": log.log_date.isoformat() if log.log_date else None,
                "work_content": log.work_content,
                "completion_status": log.completion_status.value,
                "status_display": log.get_status_display(),
                "self_rating": log.self_rating,
                "supervisor_rating": log.supervisor_rating,
                "is_rated": log.is_rated_by_supervisor(),
                "rating_difference": log.get_rating_difference()
            }
            result.append(log_data)
        
        return jsonify({
            'work_logs': result,
            'total': len(result),
            'message': '这是演示数据，实际使用需要认证'
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'DEMO_ERROR',
                'message': f'演示查询失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@app.route('/demo/statistics')
def demo_statistics():
    """
    演示统计功能（无需认证）
    
    演示 WorkLog 模型的统计方法
    """
    try:
        from datetime import date, timedelta
        
        # 获取最近30天的统计
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        stats = WorkLog.get_rating_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            "period": f"{start_date} 到 {end_date}",
            "statistics": stats,
            'message': '这是演示数据，实际使用需要认证'
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'DEMO_ERROR',
                'message': f'演示查询失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print("数据库表创建完成")


@app.cli.command()
def create_sample_data():
    """创建示例数据"""
    from app.auth import AuthService
    
    try:
        # 创建示例岗位
        if not Position.query.first():
            positions = [
                Position(name="CEO", code="CEO", description="首席执行官", level=1),
                Position(name="CTO", code="CTO", description="首席技术官", level=2),
                Position(name="开发经理", code="DEV_MGR", description="开发团队经理", level=3),
                Position(name="高级开发工程师", code="SR_DEV", description="高级开发工程师", level=4),
                Position(name="开发工程师", code="DEV", description="开发工程师", level=5),
            ]
            
            for position in positions:
                db.session.add(position)
            
            db.session.commit()
            print("示例岗位创建完成")
        
        # 创建示例角色
        if not Role.query.first():
            roles = [
                Role(name="超级管理员", code="SUPER_ADMIN", description="系统超级管理员"),
                Role(name="管理员", code="ADMIN", description="系统管理员"),
                Role(name="经理", code="MANAGER", description="部门经理"),
                Role(name="员工", code="EMPLOYEE", description="普通员工"),
            ]
            
            for role in roles:
                db.session.add(role)
            
            db.session.commit()
            print("示例角色创建完成")
        
        # 创建示例菜单
        if not Menu.query.first():
            menus = [
                Menu(name="系统管理", path="/system", icon="system", sort_order=1),
                Menu(name="员工管理", path="/employees", icon="user", sort_order=2),
                Menu(name="岗位管理", path="/positions", icon="position", sort_order=3),
                Menu(name="工作日志", path="/work-logs", icon="log", sort_order=4),
            ]
            
            for menu in menus:
                db.session.add(menu)
            
            db.session.commit()
            print("示例菜单创建完成")
        
        # 创建示例用户
        if not Employee.query.first():
            admin_role = Role.query.filter_by(code="SUPER_ADMIN").first()
            ceo_position = Position.query.filter_by(code="CEO").first()
            
            admin_user = AuthService.create_user(
                username="admin",
                email="admin@example.com",
                password="admin123",
                full_name="系统管理员",
                position_id=ceo_position.id if ceo_position else None,
                role_id=admin_role.id if admin_role else None
            )
            
            print("示例用户创建完成")
            print("管理员账号: admin / admin123")
        
        print("所有示例数据创建完成")
        
    except Exception as e:
        db.session.rollback()
        print(f"创建示例数据失败: {str(e)}")


if __name__ == "__main__":
    # 运行开发服务器
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )