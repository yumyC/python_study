"""
角色管理 API 路由

提供角色的 CRUD 操作
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Role, Employee
from app.auth import require_permission, get_current_active_user

# 创建角色管理路由器
router = APIRouter(
    prefix="/roles",
    tags=["角色管理"],
    responses={
        401: {"description": "认证失败"},
        403: {"description": "权限不足"}
    }
)


class RoleResponse(BaseModel):
    """角色响应模式"""
    id: str
    name: str
    code: str
    description: Optional[str] = None
    employee_count: int
    permission_count: int
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    """创建角色请求模式"""
    name: str
    code: str
    description: Optional[str] = None


class RoleUpdateRequest(BaseModel):
    """更新角色请求模式"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class RoleDetailResponse(BaseModel):
    """角色详情响应模式"""
    id: str
    name: str
    code: str
    description: Optional[str] = None
    employee_count: int
    permission_count: int
    permissions: dict = {}
    employees: List[dict] = []
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[RoleResponse], summary="获取角色列表")
async def get_roles(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "view"))
):
    """
    获取角色列表接口
    
    需要 /roles 路径的 view 权限
    支持分页和搜索功能
    """
    query = db.query(Role)
    
    # 搜索功能
    if search:
        query = query.filter(
            (Role.name.contains(search)) |
            (Role.code.contains(search)) |
            (Role.description.contains(search))
        )
    
    # 按名称排序
    query = query.order_by(Role.name)
    
    # 分页
    roles = query.offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for role in roles:
        role_data = RoleResponse(
            id=str(role.id),
            name=role.name,
            code=role.code,
            description=role.description,
            employee_count=role.employees.count(),
            permission_count=role.menu_permissions.count(),
            created_at=role.created_at.isoformat() if role.created_at else None
        )
        result.append(role_data)
    
    return result


@router.get("/{role_id}", response_model=RoleDetailResponse, summary="获取角色详情")
async def get_role(
    role_id: str,
    include_employees: bool = Query(False, description="是否包含员工信息"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "view"))
):
    """
    获取角色详情接口
    
    需要 /roles 路径的 view 权限
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 获取角色权限
    permissions = role.get_permissions()
    
    # 获取员工信息（如果需要）
    employees = []
    if include_employees:
        for employee in role.employees:
            employee_data = {
                "id": str(employee.id),
                "username": employee.username,
                "full_name": employee.full_name,
                "email": employee.email,
                "status": employee.status.value,
                "position_name": employee.position.name if employee.position else None
            }
            employees.append(employee_data)
    
    return RoleDetailResponse(
        id=str(role.id),
        name=role.name,
        code=role.code,
        description=role.description,
        employee_count=role.employees.count(),
        permission_count=role.menu_permissions.count(),
        permissions=permissions,
        employees=employees,
        created_at=role.created_at.isoformat() if role.created_at else None
    )


@router.post("/", response_model=RoleResponse, summary="创建角色")
async def create_role(
    role_data: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "create"))
):
    """
    创建角色接口
    
    需要 /roles 路径的 create 权限
    """
    # 检查角色编码是否已存在
    existing_role = db.query(Role).filter(Role.code == role_data.code).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色编码已存在"
        )
    
    # 检查角色名称是否已存在
    existing_name = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称已存在"
        )
    
    # 创建新角色
    new_role = Role(
        name=role_data.name,
        code=role_data.code,
        description=role_data.description
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return RoleResponse(
        id=str(new_role.id),
        name=new_role.name,
        code=new_role.code,
        description=new_role.description,
        employee_count=0,
        permission_count=0,
        created_at=new_role.created_at.isoformat() if new_role.created_at else None
    )


@router.put("/{role_id}", response_model=RoleResponse, summary="更新角色")
async def update_role(
    role_id: str,
    role_data: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "update"))
):
    """
    更新角色接口
    
    需要 /roles 路径的 update 权限
    """
    # 查找角色
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 更新字段
    if role_data.name is not None:
        # 检查名称是否被其他角色使用
        existing_name = db.query(Role).filter(
            Role.name == role_data.name,
            Role.id != role_id
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已被其他角色使用"
            )
        role.name = role_data.name
    
    if role_data.code is not None:
        # 检查编码是否被其他角色使用
        existing_code = db.query(Role).filter(
            Role.code == role_data.code,
            Role.id != role_id
        ).first()
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色编码已被其他角色使用"
            )
        role.code = role_data.code
    
    if role_data.description is not None:
        role.description = role_data.description
    
    db.commit()
    db.refresh(role)
    
    return RoleResponse(
        id=str(role.id),
        name=role.name,
        code=role.code,
        description=role.description,
        employee_count=role.employees.count(),
        permission_count=role.menu_permissions.count(),
        created_at=role.created_at.isoformat() if role.created_at else None
    )


@router.delete("/{role_id}", summary="删除角色")
async def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "delete"))
):
    """
    删除角色接口
    
    需要 /roles 路径的 delete 权限
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查是否有员工使用此角色
    if role.employees.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该角色下还有员工，无法删除"
        )
    
    # 删除角色（会级联删除相关权限）
    db.delete(role)
    db.commit()
    
    return {"message": "角色已删除", "role_id": role_id}


@router.get("/{role_id}/employees", response_model=List[dict], summary="获取角色员工")
async def get_role_employees(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "view"))
):
    """
    获取角色下的所有员工
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    employees = list(role.employees)
    
    result = []
    for employee in employees:
        employee_data = {
            "id": str(employee.id),
            "username": employee.username,
            "full_name": employee.full_name,
            "email": employee.email,
            "status": employee.status.value,
            "position_name": employee.position.name if employee.position else None,
            "created_at": employee.created_at.isoformat() if employee.created_at else None
        }
        result.append(employee_data)
    
    return result


@router.get("/{role_id}/permissions", response_model=dict, summary="获取角色权限")
async def get_role_permissions(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "view"))
):
    """
    获取角色的所有权限
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    permissions = role.get_permissions()
    
    # 获取详细的权限信息，包含菜单名称
    detailed_permissions = {}
    for permission in role.menu_permissions:
        menu_info = {
            "menu_name": permission.menu.name,
            "menu_path": permission.menu.path,
            "permissions": permission.permissions
        }
        detailed_permissions[str(permission.menu_id)] = menu_info
    
    return {
        "role_id": role_id,
        "role_name": role.name,
        "permissions": detailed_permissions
    }


@router.get("/{role_id}/accessible-menus", response_model=List[dict], summary="获取角色可访问菜单")
async def get_role_accessible_menus(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "view"))
):
    """
    获取角色可访问的所有菜单
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    accessible_menus = role.get_accessible_menus()
    
    result = []
    for menu in accessible_menus:
        menu_data = {
            "id": str(menu.id),
            "name": menu.name,
            "path": menu.path,
            "icon": menu.icon,
            "component": menu.component,
            "parent_id": str(menu.parent_id) if menu.parent_id else None,
            "sort_order": menu.sort_order,
            "is_visible": menu.is_visible
        }
        result.append(menu_data)
    
    return result


@router.post("/{role_id}/copy", response_model=RoleResponse, summary="复制角色")
async def copy_role(
    role_id: str,
    new_name: str = Query(..., description="新角色名称"),
    new_code: str = Query(..., description="新角色编码"),
    copy_permissions: bool = Query(True, description="是否复制权限"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/roles", "create"))
):
    """
    复制角色接口
    
    创建一个基于现有角色的新角色，可选择是否复制权限
    """
    # 查找源角色
    source_role = db.query(Role).filter(Role.id == role_id).first()
    if not source_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="源角色不存在"
        )
    
    # 检查新角色编码和名称是否已存在
    existing_code = db.query(Role).filter(Role.code == new_code).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色编码已存在"
        )
    
    existing_name = db.query(Role).filter(Role.name == new_name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称已存在"
        )
    
    # 创建新角色
    new_role = Role(
        name=new_name,
        code=new_code,
        description=f"复制自 {source_role.name}"
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    # 复制权限（如果需要）
    if copy_permissions:
        from app.models import RoleMenuPermission
        
        for permission in source_role.menu_permissions:
            new_permission = RoleMenuPermission(
                role_id=new_role.id,
                menu_id=permission.menu_id,
                permissions=permission.permissions.copy()
            )
            db.add(new_permission)
        
        db.commit()
    
    return RoleResponse(
        id=str(new_role.id),
        name=new_role.name,
        code=new_role.code,
        description=new_role.description,
        employee_count=0,
        permission_count=new_role.menu_permissions.count(),
        created_at=new_role.created_at.isoformat() if new_role.created_at else None
    )