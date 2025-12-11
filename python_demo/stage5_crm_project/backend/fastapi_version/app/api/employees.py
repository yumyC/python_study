"""
员工管理 API 路由

演示如何在实际业务接口中使用认证授权系统
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Employee, EmployeeStatus
from app.auth import (
    get_current_active_user,
    require_permission,
    get_permission_checker,
    PermissionChecker
)

# 创建员工管理路由器
router = APIRouter(
    prefix="/employees",
    tags=["员工管理"],
    responses={
        401: {"description": "认证失败"},
        403: {"description": "权限不足"}
    }
)


class EmployeeResponse(BaseModel):
    """员工响应模式"""
    id: str
    username: str
    email: str
    full_name: str
    status: str
    position_name: Optional[str] = None
    role_name: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class EmployeeCreateRequest(BaseModel):
    """创建员工请求模式"""
    username: str
    email: str
    password: str
    full_name: str
    position_id: Optional[str] = None
    role_id: Optional[str] = None


class EmployeeUpdateRequest(BaseModel):
    """更新员工请求模式"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    position_id: Optional[str] = None
    role_id: Optional[str] = None
    status: Optional[str] = None


@router.get("/", response_model=List[EmployeeResponse], summary="获取员工列表")
async def get_employees(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/employees", "view"))
):
    """
    获取员工列表接口
    
    需要 /employees 路径的 view 权限
    支持分页和搜索功能
    """
    query = db.query(Employee)
    
    # 搜索功能
    if search:
        query = query.filter(
            (Employee.username.contains(search)) |
            (Employee.full_name.contains(search)) |
            (Employee.email.contains(search))
        )
    
    # 分页
    employees = query.offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for employee in employees:
        employee_data = EmployeeResponse(
            id=str(employee.id),
            username=employee.username,
            email=employee.email,
            full_name=employee.full_name,
            status=employee.status.value,
            position_name=employee.position.name if employee.position else None,
            role_name=employee.role.name if employee.role else None,
            created_at=employee.created_at.isoformat() if employee.created_at else None
        )
        result.append(employee_data)
    
    return result


@router.get("/{employee_id}", response_model=EmployeeResponse, summary="获取员工详情")
async def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/employees", "view"))
):
    """
    获取员工详情接口
    
    需要 /employees 路径的 view 权限
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    return EmployeeResponse(
        id=str(employee.id),
        username=employee.username,
        email=employee.email,
        full_name=employee.full_name,
        status=employee.status.value,
        position_name=employee.position.name if employee.position else None,
        role_name=employee.role.name if employee.role else None,
        created_at=employee.created_at.isoformat() if employee.created_at else None
    )


@router.post("/", response_model=EmployeeResponse, summary="创建员工")
async def create_employee(
    employee_data: EmployeeCreateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/employees", "create"))
):
    """
    创建员工接口
    
    需要 /employees 路径的 create 权限
    """
    from app.auth.jwt_handler import jwt_handler
    
    # 检查用户名和邮箱是否已存在
    existing_user = db.query(Employee).filter(
        (Employee.username == employee_data.username) |
        (Employee.email == employee_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )
    
    # 创建新员工
    new_employee = Employee(
        username=employee_data.username,
        email=employee_data.email,
        password_hash=jwt_handler.hash_password(employee_data.password),
        full_name=employee_data.full_name,
        position_id=employee_data.position_id,
        role_id=employee_data.role_id,
        status=EmployeeStatus.ACTIVE
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return EmployeeResponse(
        id=str(new_employee.id),
        username=new_employee.username,
        email=new_employee.email,
        full_name=new_employee.full_name,
        status=new_employee.status.value,
        position_name=new_employee.position.name if new_employee.position else None,
        role_name=new_employee.role.name if new_employee.role else None,
        created_at=new_employee.created_at.isoformat() if new_employee.created_at else None
    )


@router.put("/{employee_id}", response_model=EmployeeResponse, summary="更新员工")
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdateRequest,
    db: Session = Depends(get_db),
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    更新员工接口
    
    演示使用 PermissionChecker 进行灵活的权限控制
    """
    # 查找员工
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 权限检查：更新自己的信息只需要基础权限，更新他人信息需要管理权限
    if str(employee.id) == str(permission_checker.current_user.id):
        # 更新自己的信息，检查基础权限
        permission_checker.require_permission("/employees", "view")
    else:
        # 更新他人信息，需要更新权限
        permission_checker.require_permission("/employees", "update")
    
    # 更新字段
    if employee_data.email is not None:
        # 检查邮箱是否已被其他用户使用
        existing_user = db.query(Employee).filter(
            Employee.email == employee_data.email,
            Employee.id != employee_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用"
            )
        employee.email = employee_data.email
    
    if employee_data.full_name is not None:
        employee.full_name = employee_data.full_name
    
    if employee_data.position_id is not None:
        employee.position_id = employee_data.position_id
    
    if employee_data.role_id is not None:
        # 修改角色需要管理员权限
        permission_checker.require_role("ADMIN")
        employee.role_id = employee_data.role_id
    
    if employee_data.status is not None:
        # 修改状态需要管理员权限
        permission_checker.require_role("ADMIN")
        employee.status = EmployeeStatus(employee_data.status)
    
    db.commit()
    db.refresh(employee)
    
    return EmployeeResponse(
        id=str(employee.id),
        username=employee.username,
        email=employee.email,
        full_name=employee.full_name,
        status=employee.status.value,
        position_name=employee.position.name if employee.position else None,
        role_name=employee.role.name if employee.role else None,
        created_at=employee.created_at.isoformat() if employee.created_at else None
    )


@router.delete("/{employee_id}", summary="删除员工")
async def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/employees", "delete"))
):
    """
    删除员工接口
    
    需要 /employees 路径的 delete 权限
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 不能删除自己
    if str(employee.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    # 软删除：将状态设为 INACTIVE
    employee.status = EmployeeStatus.INACTIVE
    db.commit()
    
    return {"message": "员工已被禁用", "employee_id": employee_id}


@router.get("/me/profile", response_model=EmployeeResponse, summary="获取个人信息")
async def get_my_profile(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    获取当前用户的个人信息
    
    不需要额外权限，只需要认证即可
    """
    return EmployeeResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        status=current_user.status.value,
        position_name=current_user.position.name if current_user.position else None,
        role_name=current_user.role.name if current_user.role else None,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )