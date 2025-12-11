"""
FastAPI CRM 应用主入口

这个文件演示了如何使用定义的数据模型和认证授权系统
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, create_tables
from app.models import Employee, Position, Menu, Role, WorkLog
from app.init_db import init_database
from app.api import (
    auth_router, 
    employees_router, 
    positions_router, 
    menus_router, 
    roles_router, 
    permissions_router, 
    work_logs_router
)
from app.api.tasks import router as tasks_router
from app.auth import get_current_active_user, require_permission
from app.middleware import RequestLoggingMiddleware, RequestIDMiddleware, ErrorHandlerMiddleware

# 创建 FastAPI 应用实例
app = FastAPI(
    title="CRM 系统 API",
    description="基于 FastAPI 的客户关系管理系统，包含完整的认证授权功能和异步任务处理",
    version="1.0.0"
)

# 添加中间件（注意顺序：后添加的先执行）
app.add_middleware(ErrorHandlerMiddleware, debug=True)
app.add_middleware(RequestLoggingMiddleware, log_request_body=False)
app.add_middleware(RequestIDMiddleware)

# 注册 API 路由
app.include_router(auth_router, prefix="/api")
app.include_router(employees_router, prefix="/api")
app.include_router(positions_router, prefix="/api")
app.include_router(menus_router, prefix="/api")
app.include_router(roles_router, prefix="/api")
app.include_router(permissions_router, prefix="/api")
app.include_router(work_logs_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """
    应用启动时的初始化操作
    """
    # 创建数据表
    create_tables()
    
    # 初始化数据库（如果需要）
    try:
        init_database()
    except Exception as e:
        print(f"数据库初始化警告: {e}")


@app.get("/")
async def root():
    """
    根路径，返回 API 信息
    """
    return {
        "message": "欢迎使用 CRM 系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/employees", response_model=List[dict])
async def get_employees(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/employees", "view"))
):
    """
    获取所有员工列表
    
    演示 Employee 模型的查询操作和权限控制
    需要 /employees 路径的 view 权限
    """
    employees = db.query(Employee).all()
    
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
    
    return result


@app.get("/positions", response_model=List[dict])
async def get_positions(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "view"))
):
    """
    获取所有岗位列表
    
    演示 Position 模型的查询和层级关系，需要权限验证
    """
    positions = db.query(Position).all()
    
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
    
    return result


@app.get("/menus", response_model=List[dict])
async def get_menus(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "view"))
):
    """
    获取菜单树形结构
    
    演示 Menu 模型的树形结构查询，需要权限验证
    """
    # 获取根菜单（没有父菜单的菜单）
    root_menus = db.query(Menu).filter(Menu.parent_id.is_(None)).order_by(Menu.sort_order).all()
    
    result = []
    for menu in root_menus:
        menu_tree = menu.to_tree_dict(include_children=True)
        result.append(menu_tree)
    
    return result


@app.get("/roles", response_model=List[dict])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "view"))
):
    """
    获取所有角色及其权限
    
    演示 Role 和 RoleMenuPermission 模型的关联查询，需要权限验证
    """
    roles = db.query(Role).all()
    
    result = []
    for role in roles:
        role_data = {
            "id": str(role.id),
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "employee_count": role.employees.count(),
            "permissions": role.get_permissions(),
            "menu_count": role.menu_permissions.count()
        }
        result.append(role_data)
    
    return result


@app.get("/work-logs", response_model=List[dict])
async def get_work_logs(
    employee_id: str = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/work-logs", "view"))
):
    """
    获取工作日志列表
    
    演示 WorkLog 模型的查询和关联数据，需要权限验证
    """
    query = db.query(WorkLog)
    
    if employee_id:
        query = query.filter(WorkLog.employee_id == employee_id)
    
    work_logs = query.order_by(WorkLog.log_date.desc()).limit(limit).all()
    
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
    
    return result


@app.get("/statistics/work-logs")
async def get_work_log_statistics(
    employee_id: str = None,
    db: Session = Depends(get_db)
):
    """
    获取工作日志统计信息
    
    演示 WorkLog 模型的统计方法
    """
    from datetime import date, timedelta
    
    # 获取最近30天的统计
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    stats = WorkLog.get_rating_statistics(
        session=db,
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "period": f"{start_date} 到 {end_date}",
        "statistics": stats
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    健康检查接口
    
    检查数据库连接和基本功能
    """
    try:
        # 测试数据库连接
        employee_count = db.query(Employee).count()
        position_count = db.query(Position).count()
        menu_count = db.query(Menu).count()
        role_count = db.query(Role).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "counts": {
                "employees": employee_count,
                "positions": position_count,
                "menus": menu_count,
                "roles": role_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # 运行开发服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )