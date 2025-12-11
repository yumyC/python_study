"""
岗位管理 API 路由

提供岗位的 CRUD 操作和层级关系管理
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Position, Employee
from app.auth import require_permission, get_current_active_user

# 创建岗位管理路由器
router = APIRouter(
    prefix="/positions",
    tags=["岗位管理"],
    responses={
        401: {"description": "认证失败"},
        403: {"description": "权限不足"}
    }
)


class PositionResponse(BaseModel):
    """岗位响应模式"""
    id: str
    name: str
    code: str
    description: Optional[str] = None
    level: int
    parent_id: Optional[str] = None
    parent_name: Optional[str] = None
    full_path: str
    employee_count: int
    children_count: int
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class PositionCreateRequest(BaseModel):
    """创建岗位请求模式"""
    name: str
    code: str
    description: Optional[str] = None
    level: int = 1
    parent_id: Optional[str] = None


class PositionUpdateRequest(BaseModel):
    """更新岗位请求模式"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    parent_id: Optional[str] = None


class PositionTreeResponse(BaseModel):
    """岗位树形响应模式"""
    id: str
    name: str
    code: str
    level: int
    employee_count: int
    children: List['PositionTreeResponse'] = []
    
    class Config:
        from_attributes = True


# 解决前向引用问题
PositionTreeResponse.model_rebuild()


@router.get("/", response_model=List[PositionResponse], summary="获取岗位列表")
async def get_positions(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    parent_id: Optional[str] = Query(None, description="父岗位ID"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "view"))
):
    """
    获取岗位列表接口
    
    需要 /positions 路径的 view 权限
    支持分页、搜索和按父岗位筛选
    """
    query = db.query(Position)
    
    # 按父岗位筛选
    if parent_id:
        query = query.filter(Position.parent_id == parent_id)
    elif parent_id == "":  # 空字符串表示获取根岗位
        query = query.filter(Position.parent_id.is_(None))
    
    # 搜索功能
    if search:
        query = query.filter(
            (Position.name.contains(search)) |
            (Position.code.contains(search)) |
            (Position.description.contains(search))
        )
    
    # 按级别和名称排序
    query = query.order_by(Position.level, Position.name)
    
    # 分页
    positions = query.offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for position in positions:
        position_data = PositionResponse(
            id=str(position.id),
            name=position.name,
            code=position.code,
            description=position.description,
            level=position.level,
            parent_id=str(position.parent_id) if position.parent_id else None,
            parent_name=position.parent.name if position.parent else None,
            full_path=position.get_full_path(),
            employee_count=position.employees.count(),
            children_count=position.children.count(),
            created_at=position.created_at.isoformat() if position.created_at else None
        )
        result.append(position_data)
    
    return result


@router.get("/tree", response_model=List[PositionTreeResponse], summary="获取岗位树形结构")
async def get_position_tree(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "view"))
):
    """
    获取岗位的树形结构
    
    返回完整的岗位层级关系
    """
    def build_tree(positions, parent_id=None):
        """递归构建树形结构"""
        tree = []
        for position in positions:
            if position.parent_id == parent_id:
                children = build_tree(positions, position.id)
                position_node = PositionTreeResponse(
                    id=str(position.id),
                    name=position.name,
                    code=position.code,
                    level=position.level,
                    employee_count=position.employees.count(),
                    children=children
                )
                tree.append(position_node)
        return tree
    
    # 获取所有岗位
    positions = db.query(Position).order_by(Position.level, Position.name).all()
    
    # 构建树形结构
    tree = build_tree(positions)
    
    return tree


@router.get("/{position_id}", response_model=PositionResponse, summary="获取岗位详情")
async def get_position(
    position_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "view"))
):
    """
    获取岗位详情接口
    
    需要 /positions 路径的 view 权限
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在"
        )
    
    return PositionResponse(
        id=str(position.id),
        name=position.name,
        code=position.code,
        description=position.description,
        level=position.level,
        parent_id=str(position.parent_id) if position.parent_id else None,
        parent_name=position.parent.name if position.parent else None,
        full_path=position.get_full_path(),
        employee_count=position.employees.count(),
        children_count=position.children.count(),
        created_at=position.created_at.isoformat() if position.created_at else None
    )


@router.post("/", response_model=PositionResponse, summary="创建岗位")
async def create_position(
    position_data: PositionCreateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "create"))
):
    """
    创建岗位接口
    
    需要 /positions 路径的 create 权限
    """
    # 检查岗位编码是否已存在
    existing_position = db.query(Position).filter(Position.code == position_data.code).first()
    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="岗位编码已存在"
        )
    
    # 如果指定了父岗位，验证父岗位是否存在
    if position_data.parent_id:
        parent_position = db.query(Position).filter(Position.id == position_data.parent_id).first()
        if not parent_position:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父岗位不存在"
            )
        
        # 自动设置级别为父岗位级别+1
        if position_data.level <= parent_position.level:
            position_data.level = parent_position.level + 1
    
    # 创建新岗位
    new_position = Position(
        name=position_data.name,
        code=position_data.code,
        description=position_data.description,
        level=position_data.level,
        parent_id=position_data.parent_id
    )
    
    db.add(new_position)
    db.commit()
    db.refresh(new_position)
    
    return PositionResponse(
        id=str(new_position.id),
        name=new_position.name,
        code=new_position.code,
        description=new_position.description,
        level=new_position.level,
        parent_id=str(new_position.parent_id) if new_position.parent_id else None,
        parent_name=new_position.parent.name if new_position.parent else None,
        full_path=new_position.get_full_path(),
        employee_count=0,
        children_count=0,
        created_at=new_position.created_at.isoformat() if new_position.created_at else None
    )


@router.put("/{position_id}", response_model=PositionResponse, summary="更新岗位")
async def update_position(
    position_id: str,
    position_data: PositionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "update"))
):
    """
    更新岗位接口
    
    需要 /positions 路径的 update 权限
    """
    # 查找岗位
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在"
        )
    
    # 更新字段
    if position_data.name is not None:
        position.name = position_data.name
    
    if position_data.code is not None:
        # 检查编码是否被其他岗位使用
        existing_position = db.query(Position).filter(
            Position.code == position_data.code,
            Position.id != position_id
        ).first()
        if existing_position:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="岗位编码已被其他岗位使用"
            )
        position.code = position_data.code
    
    if position_data.description is not None:
        position.description = position_data.description
    
    if position_data.level is not None:
        position.level = position_data.level
    
    if position_data.parent_id is not None:
        # 验证不能设置自己为父岗位
        if position_data.parent_id == position_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能设置自己为父岗位"
            )
        
        # 验证不能设置子岗位为父岗位（避免循环引用）
        if position_data.parent_id:
            potential_parent = db.query(Position).filter(Position.id == position_data.parent_id).first()
            if not potential_parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父岗位不存在"
                )
            
            if position.is_ancestor_of(potential_parent):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能设置子岗位为父岗位"
                )
        
        position.parent_id = position_data.parent_id
    
    db.commit()
    db.refresh(position)
    
    return PositionResponse(
        id=str(position.id),
        name=position.name,
        code=position.code,
        description=position.description,
        level=position.level,
        parent_id=str(position.parent_id) if position.parent_id else None,
        parent_name=position.parent.name if position.parent else None,
        full_path=position.get_full_path(),
        employee_count=position.employees.count(),
        children_count=position.children.count(),
        created_at=position.created_at.isoformat() if position.created_at else None
    )


@router.delete("/{position_id}", summary="删除岗位")
async def delete_position(
    position_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "delete"))
):
    """
    删除岗位接口
    
    需要 /positions 路径的 delete 权限
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在"
        )
    
    # 检查是否有员工在此岗位
    if position.employees.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该岗位下还有员工，无法删除"
        )
    
    # 检查是否有子岗位
    if position.children.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该岗位下还有子岗位，无法删除"
        )
    
    db.delete(position)
    db.commit()
    
    return {"message": "岗位已删除", "position_id": position_id}


@router.get("/{position_id}/children", response_model=List[PositionResponse], summary="获取子岗位")
async def get_position_children(
    position_id: str,
    recursive: bool = Query(False, description="是否递归获取所有子岗位"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "view"))
):
    """
    获取岗位的子岗位
    
    支持递归获取所有层级的子岗位
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在"
        )
    
    if recursive:
        # 递归获取所有子岗位
        children = position.get_all_children()
    else:
        # 只获取直接子岗位
        children = list(position.children.order_by(Position.level, Position.name))
    
    # 构建响应数据
    result = []
    for child in children:
        child_data = PositionResponse(
            id=str(child.id),
            name=child.name,
            code=child.code,
            description=child.description,
            level=child.level,
            parent_id=str(child.parent_id) if child.parent_id else None,
            parent_name=child.parent.name if child.parent else None,
            full_path=child.get_full_path(),
            employee_count=child.employees.count(),
            children_count=child.children.count(),
            created_at=child.created_at.isoformat() if child.created_at else None
        )
        result.append(child_data)
    
    return result


@router.get("/{position_id}/employees", response_model=List[dict], summary="获取岗位员工")
async def get_position_employees(
    position_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/positions", "view"))
):
    """
    获取岗位下的所有员工
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在"
        )
    
    employees = list(position.employees)
    
    result = []
    for employee in employees:
        employee_data = {
            "id": str(employee.id),
            "username": employee.username,
            "full_name": employee.full_name,
            "email": employee.email,
            "status": employee.status.value,
            "role_name": employee.role.name if employee.role else None
        }
        result.append(employee_data)
    
    return result