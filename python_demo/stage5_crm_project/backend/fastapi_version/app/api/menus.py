"""
菜单管理 API 路由

提供菜单的 CRUD 操作和树形结构管理
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Menu, Employee
from app.auth import require_permission, get_current_active_user

# 创建菜单管理路由器
router = APIRouter(
    prefix="/menus",
    tags=["菜单管理"],
    responses={
        401: {"description": "认证失败"},
        403: {"description": "权限不足"}
    }
)


class MenuResponse(BaseModel):
    """菜单响应模式"""
    id: str
    name: str
    path: str
    icon: Optional[str] = None
    component: Optional[str] = None
    parent_id: Optional[str] = None
    parent_name: Optional[str] = None
    sort_order: int
    is_visible: bool
    level: int
    children_count: int
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class MenuCreateRequest(BaseModel):
    """创建菜单请求模式"""
    name: str
    path: str
    icon: Optional[str] = None
    component: Optional[str] = None
    parent_id: Optional[str] = None
    sort_order: int = 0
    is_visible: bool = True


class MenuUpdateRequest(BaseModel):
    """更新菜单请求模式"""
    name: Optional[str] = None
    path: Optional[str] = None
    icon: Optional[str] = None
    component: Optional[str] = None
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None
    is_visible: Optional[bool] = None


class MenuTreeResponse(BaseModel):
    """菜单树形响应模式"""
    id: str
    name: str
    path: str
    icon: Optional[str] = None
    component: Optional[str] = None
    sort_order: int
    is_visible: bool
    children: List['MenuTreeResponse'] = []
    
    class Config:
        from_attributes = True


# 解决前向引用问题
MenuTreeResponse.model_rebuild()


@router.get("/", response_model=List[MenuResponse], summary="获取菜单列表")
async def get_menus(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    parent_id: Optional[str] = Query(None, description="父菜单ID"),
    is_visible: Optional[bool] = Query(None, description="是否可见"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "view"))
):
    """
    获取菜单列表接口
    
    需要 /menus 路径的 view 权限
    支持分页、搜索和筛选
    """
    query = db.query(Menu)
    
    # 按父菜单筛选
    if parent_id:
        query = query.filter(Menu.parent_id == parent_id)
    elif parent_id == "":  # 空字符串表示获取根菜单
        query = query.filter(Menu.parent_id.is_(None))
    
    # 按可见性筛选
    if is_visible is not None:
        query = query.filter(Menu.is_visible == is_visible)
    
    # 搜索功能
    if search:
        query = query.filter(
            (Menu.name.contains(search)) |
            (Menu.path.contains(search)) |
            (Menu.component.contains(search))
        )
    
    # 按排序字段排序
    query = query.order_by(Menu.sort_order, Menu.name)
    
    # 分页
    menus = query.offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for menu in menus:
        menu_data = MenuResponse(
            id=str(menu.id),
            name=menu.name,
            path=menu.path,
            icon=menu.icon,
            component=menu.component,
            parent_id=str(menu.parent_id) if menu.parent_id else None,
            parent_name=menu.parent.name if menu.parent else None,
            sort_order=menu.sort_order,
            is_visible=menu.is_visible,
            level=menu.get_level(),
            children_count=menu.children.count(),
            created_at=menu.created_at.isoformat() if menu.created_at else None
        )
        result.append(menu_data)
    
    return result


@router.get("/tree", response_model=List[MenuTreeResponse], summary="获取菜单树形结构")
async def get_menu_tree(
    include_hidden: bool = Query(False, description="是否包含隐藏菜单"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "view"))
):
    """
    获取菜单的树形结构
    
    返回完整的菜单层级关系
    """
    def build_tree(menus, parent_id=None):
        """递归构建树形结构"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                # 根据是否包含隐藏菜单进行过滤
                if not include_hidden and not menu.is_visible:
                    continue
                
                children = build_tree(menus, menu.id)
                menu_node = MenuTreeResponse(
                    id=str(menu.id),
                    name=menu.name,
                    path=menu.path,
                    icon=menu.icon,
                    component=menu.component,
                    sort_order=menu.sort_order,
                    is_visible=menu.is_visible,
                    children=children
                )
                tree.append(menu_node)
        
        # 按排序字段排序
        tree.sort(key=lambda x: x.sort_order)
        return tree
    
    # 获取所有菜单
    menus = db.query(Menu).order_by(Menu.sort_order, Menu.name).all()
    
    # 构建树形结构
    tree = build_tree(menus)
    
    return tree


@router.get("/{menu_id}", response_model=MenuResponse, summary="获取菜单详情")
async def get_menu(
    menu_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "view"))
):
    """
    获取菜单详情接口
    
    需要 /menus 路径的 view 权限
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    return MenuResponse(
        id=str(menu.id),
        name=menu.name,
        path=menu.path,
        icon=menu.icon,
        component=menu.component,
        parent_id=str(menu.parent_id) if menu.parent_id else None,
        parent_name=menu.parent.name if menu.parent else None,
        sort_order=menu.sort_order,
        is_visible=menu.is_visible,
        level=menu.get_level(),
        children_count=menu.children.count(),
        created_at=menu.created_at.isoformat() if menu.created_at else None
    )


@router.post("/", response_model=MenuResponse, summary="创建菜单")
async def create_menu(
    menu_data: MenuCreateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "create"))
):
    """
    创建菜单接口
    
    需要 /menus 路径的 create 权限
    """
    # 检查路径是否已存在
    existing_menu = db.query(Menu).filter(Menu.path == menu_data.path).first()
    if existing_menu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="菜单路径已存在"
        )
    
    # 如果指定了父菜单，验证父菜单是否存在
    if menu_data.parent_id:
        parent_menu = db.query(Menu).filter(Menu.id == menu_data.parent_id).first()
        if not parent_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父菜单不存在"
            )
    
    # 创建新菜单
    new_menu = Menu(
        name=menu_data.name,
        path=menu_data.path,
        icon=menu_data.icon,
        component=menu_data.component,
        parent_id=menu_data.parent_id,
        sort_order=menu_data.sort_order,
        is_visible=menu_data.is_visible
    )
    
    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    
    return MenuResponse(
        id=str(new_menu.id),
        name=new_menu.name,
        path=new_menu.path,
        icon=new_menu.icon,
        component=new_menu.component,
        parent_id=str(new_menu.parent_id) if new_menu.parent_id else None,
        parent_name=new_menu.parent.name if new_menu.parent else None,
        sort_order=new_menu.sort_order,
        is_visible=new_menu.is_visible,
        level=new_menu.get_level(),
        children_count=0,
        created_at=new_menu.created_at.isoformat() if new_menu.created_at else None
    )


@router.put("/{menu_id}", response_model=MenuResponse, summary="更新菜单")
async def update_menu(
    menu_id: str,
    menu_data: MenuUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "update"))
):
    """
    更新菜单接口
    
    需要 /menus 路径的 update 权限
    """
    # 查找菜单
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 更新字段
    if menu_data.name is not None:
        menu.name = menu_data.name
    
    if menu_data.path is not None:
        # 检查路径是否被其他菜单使用
        existing_menu = db.query(Menu).filter(
            Menu.path == menu_data.path,
            Menu.id != menu_id
        ).first()
        if existing_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="菜单路径已被其他菜单使用"
            )
        menu.path = menu_data.path
    
    if menu_data.icon is not None:
        menu.icon = menu_data.icon
    
    if menu_data.component is not None:
        menu.component = menu_data.component
    
    if menu_data.parent_id is not None:
        # 验证不能设置自己为父菜单
        if menu_data.parent_id == menu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能设置自己为父菜单"
            )
        
        # 验证不能设置子菜单为父菜单（避免循环引用）
        if menu_data.parent_id:
            potential_parent = db.query(Menu).filter(Menu.id == menu_data.parent_id).first()
            if not potential_parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父菜单不存在"
                )
            
            # 检查是否会形成循环引用
            all_children = menu.get_all_children()
            child_ids = [str(child.id) for child in all_children]
            if menu_data.parent_id in child_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能设置子菜单为父菜单"
                )
        
        menu.parent_id = menu_data.parent_id
    
    if menu_data.sort_order is not None:
        menu.sort_order = menu_data.sort_order
    
    if menu_data.is_visible is not None:
        menu.is_visible = menu_data.is_visible
    
    db.commit()
    db.refresh(menu)
    
    return MenuResponse(
        id=str(menu.id),
        name=menu.name,
        path=menu.path,
        icon=menu.icon,
        component=menu.component,
        parent_id=str(menu.parent_id) if menu.parent_id else None,
        parent_name=menu.parent.name if menu.parent else None,
        sort_order=menu.sort_order,
        is_visible=menu.is_visible,
        level=menu.get_level(),
        children_count=menu.children.count(),
        created_at=menu.created_at.isoformat() if menu.created_at else None
    )


@router.delete("/{menu_id}", summary="删除菜单")
async def delete_menu(
    menu_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "delete"))
):
    """
    删除菜单接口
    
    需要 /menus 路径的 delete 权限
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 检查是否有子菜单
    if menu.children.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该菜单下还有子菜单，无法删除"
        )
    
    # 检查是否有角色权限关联
    if menu.role_permissions.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该菜单已分配给角色，无法删除"
        )
    
    db.delete(menu)
    db.commit()
    
    return {"message": "菜单已删除", "menu_id": menu_id}


@router.get("/{menu_id}/breadcrumb", response_model=List[dict], summary="获取菜单面包屑")
async def get_menu_breadcrumb(
    menu_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "view"))
):
    """
    获取菜单的面包屑路径
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    breadcrumb = menu.get_breadcrumb()
    return breadcrumb


@router.get("/{menu_id}/children", response_model=List[MenuResponse], summary="获取子菜单")
async def get_menu_children(
    menu_id: str,
    recursive: bool = Query(False, description="是否递归获取所有子菜单"),
    include_hidden: bool = Query(False, description="是否包含隐藏菜单"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "view"))
):
    """
    获取菜单的子菜单
    
    支持递归获取所有层级的子菜单
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    if recursive:
        # 递归获取所有子菜单
        children = menu.get_all_children()
    else:
        # 只获取直接子菜单
        children = list(menu.children.order_by(Menu.sort_order))
    
    # 过滤隐藏菜单
    if not include_hidden:
        children = [child for child in children if child.is_visible]
    
    # 构建响应数据
    result = []
    for child in children:
        child_data = MenuResponse(
            id=str(child.id),
            name=child.name,
            path=child.path,
            icon=child.icon,
            component=child.component,
            parent_id=str(child.parent_id) if child.parent_id else None,
            parent_name=child.parent.name if child.parent else None,
            sort_order=child.sort_order,
            is_visible=child.is_visible,
            level=child.get_level(),
            children_count=child.children.count(),
            created_at=child.created_at.isoformat() if child.created_at else None
        )
        result.append(child_data)
    
    return result


@router.post("/{menu_id}/toggle-visibility", response_model=MenuResponse, summary="切换菜单可见性")
async def toggle_menu_visibility(
    menu_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/menus", "update"))
):
    """
    切换菜单的可见性状态
    """
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 切换可见性
    menu.is_visible = not menu.is_visible
    db.commit()
    db.refresh(menu)
    
    return MenuResponse(
        id=str(menu.id),
        name=menu.name,
        path=menu.path,
        icon=menu.icon,
        component=menu.component,
        parent_id=str(menu.parent_id) if menu.parent_id else None,
        parent_name=menu.parent.name if menu.parent else None,
        sort_order=menu.sort_order,
        is_visible=menu.is_visible,
        level=menu.get_level(),
        children_count=menu.children.count(),
        created_at=menu.created_at.isoformat() if menu.created_at else None
    )