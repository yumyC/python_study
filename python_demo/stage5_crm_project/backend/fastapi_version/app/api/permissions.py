"""
权限管理 API 路由

提供角色-菜单权限绑定的管理功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import RoleMenuPermission, Role, Menu, Employee
from app.auth import require_permission, get_current_active_user

# 创建权限管理路由器
router = APIRouter(
    prefix="/permissions",
    tags=["权限管理"],
    responses={
        401: {"description": "认证失败"},
        403: {"description": "权限不足"}
    }
)


class PermissionResponse(BaseModel):
    """权限响应模式"""
    id: str
    role_id: str
    role_name: str
    role_code: str
    menu_id: str
    menu_name: str
    menu_path: str
    permissions: List[str]
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class PermissionCreateRequest(BaseModel):
    """创建权限请求模式"""
    role_id: str
    menu_id: str
    permissions: List[str]


class PermissionUpdateRequest(BaseModel):
    """更新权限请求模式"""
    permissions: List[str]


class BatchPermissionRequest(BaseModel):
    """批量权限操作请求模式"""
    role_id: str
    menu_permissions: List[dict]  # [{"menu_id": "xxx", "permissions": ["view", "create"]}]


class RolePermissionSummary(BaseModel):
    """角色权限汇总响应模式"""
    role_id: str
    role_name: str
    role_code: str
    total_menus: int
    accessible_menus: int
    permissions_detail: List[dict]
    
    class Config:
        from_attributes = True


# 定义可用的权限类型
AVAILABLE_PERMISSIONS = ["view", "create", "update", "delete"]


@router.get("/", response_model=List[PermissionResponse], summary="获取权限列表")
async def get_permissions(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回的记录数"),
    role_id: Optional[str] = Query(None, description="角色ID筛选"),
    menu_id: Optional[str] = Query(None, description="菜单ID筛选"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "view"))
):
    """
    获取权限列表接口
    
    需要 /permissions 路径的 view 权限
    支持分页和按角色、菜单筛选
    """
    query = db.query(RoleMenuPermission)
    
    # 按角色筛选
    if role_id:
        query = query.filter(RoleMenuPermission.role_id == role_id)
    
    # 按菜单筛选
    if menu_id:
        query = query.filter(RoleMenuPermission.menu_id == menu_id)
    
    # 关联查询角色和菜单信息
    query = query.join(Role).join(Menu)
    
    # 排序
    query = query.order_by(Role.name, Menu.name)
    
    # 分页
    permissions = query.offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for permission in permissions:
        permission_data = PermissionResponse(
            id=str(permission.id),
            role_id=str(permission.role_id),
            role_name=permission.role.name,
            role_code=permission.role.code,
            menu_id=str(permission.menu_id),
            menu_name=permission.menu.name,
            menu_path=permission.menu.path,
            permissions=permission.permissions,
            created_at=permission.created_at.isoformat() if permission.created_at else None
        )
        result.append(permission_data)
    
    return result


@router.get("/{permission_id}", response_model=PermissionResponse, summary="获取权限详情")
async def get_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "view"))
):
    """
    获取权限详情接口
    
    需要 /permissions 路径的 view 权限
    """
    permission = db.query(RoleMenuPermission).filter(RoleMenuPermission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限记录不存在"
        )
    
    return PermissionResponse(
        id=str(permission.id),
        role_id=str(permission.role_id),
        role_name=permission.role.name,
        role_code=permission.role.code,
        menu_id=str(permission.menu_id),
        menu_name=permission.menu.name,
        menu_path=permission.menu.path,
        permissions=permission.permissions,
        created_at=permission.created_at.isoformat() if permission.created_at else None
    )


@router.post("/", response_model=PermissionResponse, summary="创建权限")
async def create_permission(
    permission_data: PermissionCreateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "create"))
):
    """
    创建权限接口
    
    需要 /permissions 路径的 create 权限
    """
    # 验证角色是否存在
    role = db.query(Role).filter(Role.id == permission_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色不存在"
        )
    
    # 验证菜单是否存在
    menu = db.query(Menu).filter(Menu.id == permission_data.menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="菜单不存在"
        )
    
    # 验证权限类型
    invalid_permissions = [p for p in permission_data.permissions if p not in AVAILABLE_PERMISSIONS]
    if invalid_permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的权限类型: {invalid_permissions}"
        )
    
    # 检查是否已存在相同的角色-菜单权限
    existing_permission = db.query(RoleMenuPermission).filter(
        RoleMenuPermission.role_id == permission_data.role_id,
        RoleMenuPermission.menu_id == permission_data.menu_id
    ).first()
    
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该角色已有此菜单的权限配置"
        )
    
    # 创建新权限
    new_permission = RoleMenuPermission(
        role_id=permission_data.role_id,
        menu_id=permission_data.menu_id,
        permissions=permission_data.permissions
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return PermissionResponse(
        id=str(new_permission.id),
        role_id=str(new_permission.role_id),
        role_name=new_permission.role.name,
        role_code=new_permission.role.code,
        menu_id=str(new_permission.menu_id),
        menu_name=new_permission.menu.name,
        menu_path=new_permission.menu.path,
        permissions=new_permission.permissions,
        created_at=new_permission.created_at.isoformat() if new_permission.created_at else None
    )


@router.put("/{permission_id}", response_model=PermissionResponse, summary="更新权限")
async def update_permission(
    permission_id: str,
    permission_data: PermissionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "update"))
):
    """
    更新权限接口
    
    需要 /permissions 路径的 update 权限
    """
    # 查找权限记录
    permission = db.query(RoleMenuPermission).filter(RoleMenuPermission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限记录不存在"
        )
    
    # 验证权限类型
    invalid_permissions = [p for p in permission_data.permissions if p not in AVAILABLE_PERMISSIONS]
    if invalid_permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的权限类型: {invalid_permissions}"
        )
    
    # 更新权限
    permission.permissions = permission_data.permissions
    
    db.commit()
    db.refresh(permission)
    
    return PermissionResponse(
        id=str(permission.id),
        role_id=str(permission.role_id),
        role_name=permission.role.name,
        role_code=permission.role.code,
        menu_id=str(permission.menu_id),
        menu_name=permission.menu.name,
        menu_path=permission.menu.path,
        permissions=permission.permissions,
        created_at=permission.created_at.isoformat() if permission.created_at else None
    )


@router.delete("/{permission_id}", summary="删除权限")
async def delete_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "delete"))
):
    """
    删除权限接口
    
    需要 /permissions 路径的 delete 权限
    """
    permission = db.query(RoleMenuPermission).filter(RoleMenuPermission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限记录不存在"
        )
    
    db.delete(permission)
    db.commit()
    
    return {"message": "权限已删除", "permission_id": permission_id}


@router.post("/batch", response_model=List[PermissionResponse], summary="批量设置权限")
async def batch_set_permissions(
    batch_data: BatchPermissionRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "create"))
):
    """
    批量设置角色权限接口
    
    需要 /permissions 路径的 create 权限
    """
    # 验证角色是否存在
    role = db.query(Role).filter(Role.id == batch_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色不存在"
        )
    
    # 删除角色的所有现有权限
    db.query(RoleMenuPermission).filter(RoleMenuPermission.role_id == batch_data.role_id).delete()
    
    # 创建新权限
    created_permissions = []
    for menu_perm in batch_data.menu_permissions:
        menu_id = menu_perm.get("menu_id")
        permissions = menu_perm.get("permissions", [])
        
        # 验证菜单是否存在
        menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if not menu:
            continue  # 跳过不存在的菜单
        
        # 验证权限类型
        valid_permissions = [p for p in permissions if p in AVAILABLE_PERMISSIONS]
        if not valid_permissions:
            continue  # 跳过无效权限
        
        # 创建权限记录
        new_permission = RoleMenuPermission(
            role_id=batch_data.role_id,
            menu_id=menu_id,
            permissions=valid_permissions
        )
        
        db.add(new_permission)
        created_permissions.append(new_permission)
    
    db.commit()
    
    # 刷新并返回创建的权限
    result = []
    for permission in created_permissions:
        db.refresh(permission)
        permission_data = PermissionResponse(
            id=str(permission.id),
            role_id=str(permission.role_id),
            role_name=permission.role.name,
            role_code=permission.role.code,
            menu_id=str(permission.menu_id),
            menu_name=permission.menu.name,
            menu_path=permission.menu.path,
            permissions=permission.permissions,
            created_at=permission.created_at.isoformat() if permission.created_at else None
        )
        result.append(permission_data)
    
    return result


@router.get("/roles/{role_id}/summary", response_model=RolePermissionSummary, summary="获取角色权限汇总")
async def get_role_permission_summary(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "view"))
):
    """
    获取角色权限汇总信息
    
    包含角色的所有权限详情和统计信息
    """
    # 验证角色是否存在
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 获取所有菜单数量
    total_menus = db.query(Menu).count()
    
    # 获取角色权限
    role_permissions = db.query(RoleMenuPermission).filter(
        RoleMenuPermission.role_id == role_id
    ).all()
    
    # 构建权限详情
    permissions_detail = []
    for permission in role_permissions:
        detail = {
            "menu_id": str(permission.menu_id),
            "menu_name": permission.menu.name,
            "menu_path": permission.menu.path,
            "permissions": permission.permissions,
            "permission_count": len(permission.permissions)
        }
        permissions_detail.append(detail)
    
    return RolePermissionSummary(
        role_id=role_id,
        role_name=role.name,
        role_code=role.code,
        total_menus=total_menus,
        accessible_menus=len(role_permissions),
        permissions_detail=permissions_detail
    )


@router.post("/roles/{role_id}/copy-from/{source_role_id}", response_model=List[PermissionResponse], summary="复制角色权限")
async def copy_role_permissions(
    role_id: str,
    source_role_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "create"))
):
    """
    从源角色复制权限到目标角色
    
    需要 /permissions 路径的 create 权限
    """
    # 验证目标角色是否存在
    target_role = db.query(Role).filter(Role.id == role_id).first()
    if not target_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标角色不存在"
        )
    
    # 验证源角色是否存在
    source_role = db.query(Role).filter(Role.id == source_role_id).first()
    if not source_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="源角色不存在"
        )
    
    # 删除目标角色的所有现有权限
    db.query(RoleMenuPermission).filter(RoleMenuPermission.role_id == role_id).delete()
    
    # 复制源角色的权限
    source_permissions = db.query(RoleMenuPermission).filter(
        RoleMenuPermission.role_id == source_role_id
    ).all()
    
    created_permissions = []
    for source_perm in source_permissions:
        new_permission = RoleMenuPermission(
            role_id=role_id,
            menu_id=source_perm.menu_id,
            permissions=source_perm.permissions.copy()
        )
        
        db.add(new_permission)
        created_permissions.append(new_permission)
    
    db.commit()
    
    # 刷新并返回创建的权限
    result = []
    for permission in created_permissions:
        db.refresh(permission)
        permission_data = PermissionResponse(
            id=str(permission.id),
            role_id=str(permission.role_id),
            role_name=permission.role.name,
            role_code=permission.role.code,
            menu_id=str(permission.menu_id),
            menu_name=permission.menu.name,
            menu_path=permission.menu.path,
            permissions=permission.permissions,
            created_at=permission.created_at.isoformat() if permission.created_at else None
        )
        result.append(permission_data)
    
    return result


@router.get("/available-permissions", response_model=List[str], summary="获取可用权限类型")
async def get_available_permissions(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    获取系统中可用的权限类型
    """
    return AVAILABLE_PERMISSIONS


@router.post("/check", response_model=dict, summary="检查权限")
async def check_permission(
    role_id: str = Query(..., description="角色ID"),
    menu_path: str = Query(..., description="菜单路径"),
    permission_type: str = Query(..., description="权限类型"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/permissions", "view"))
):
    """
    检查角色是否有特定菜单的特定权限
    """
    # 验证角色是否存在
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 查找菜单
    menu = db.query(Menu).filter(Menu.path == menu_path).first()
    if not menu:
        return {
            "has_permission": False,
            "reason": "菜单不存在"
        }
    
    # 检查权限
    has_permission = role.has_permission(menu.id, permission_type)
    
    return {
        "role_id": role_id,
        "role_name": role.name,
        "menu_path": menu_path,
        "menu_name": menu.name,
        "permission_type": permission_type,
        "has_permission": has_permission
    }