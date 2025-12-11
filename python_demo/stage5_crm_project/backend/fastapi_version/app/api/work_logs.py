"""
工作日志管理 API 路由

提供工作日志的 CRUD 操作和评分功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime, timedelta

from app.database import get_db
from app.models import WorkLog, Employee, CompletionStatus
from app.auth import require_permission, get_current_active_user, get_permission_checker, PermissionChecker

# 创建工作日志管理路由器
router = APIRouter(
    prefix="/work-logs",
    tags=["工作日志管理"],
    responses={
        401: {"description": "认证失败"},
        403: {"description": "权限不足"}
    }
)


class WorkLogResponse(BaseModel):
    """工作日志响应模式"""
    id: str
    employee_id: str
    employee_name: str
    log_date: str
    work_content: str
    completion_status: str
    status_display: str
    problems_encountered: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    self_rating: Optional[int] = None
    supervisor_rating: Optional[int] = None
    supervisor_comment: Optional[str] = None
    is_rated: bool
    rating_difference: Optional[int] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class WorkLogCreateRequest(BaseModel):
    """创建工作日志请求模式"""
    employee_id: Optional[str] = None  # 如果不提供，使用当前用户
    log_date: str  # YYYY-MM-DD 格式
    work_content: str
    completion_status: str = "in_progress"
    problems_encountered: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    self_rating: Optional[int] = None


class WorkLogUpdateRequest(BaseModel):
    """更新工作日志请求模式"""
    work_content: Optional[str] = None
    completion_status: Optional[str] = None
    problems_encountered: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    self_rating: Optional[int] = None


class SupervisorRatingRequest(BaseModel):
    """上级评分请求模式"""
    supervisor_rating: int
    supervisor_comment: Optional[str] = None


class WorkLogStatistics(BaseModel):
    """工作日志统计响应模式"""
    total_logs: int
    avg_self_rating: float
    avg_supervisor_rating: float
    completion_rate: float
    rated_logs: int
    rating_coverage: float
    period: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[WorkLogResponse], summary="获取工作日志列表")
async def get_work_logs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    employee_id: Optional[str] = Query(None, description="员工ID筛选"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    completion_status: Optional[str] = Query(None, description="完成状态筛选"),
    db: Session = Depends(get_db),
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    获取工作日志列表接口
    
    支持分页、筛选和搜索功能
    """
    # 权限检查：查看自己的日志只需要基础权限，查看他人日志需要管理权限
    if employee_id and employee_id != str(permission_checker.current_user.id):
        permission_checker.require_permission("/work-logs", "view")
    else:
        # 查看自己的日志，只需要认证即可
        pass
    
    query = db.query(WorkLog)
    
    # 员工筛选
    if employee_id:
        query = query.filter(WorkLog.employee_id == employee_id)
    elif not permission_checker.has_permission("/work-logs", "view"):
        # 如果没有管理权限，只能查看自己的日志
        query = query.filter(WorkLog.employee_id == permission_checker.current_user.id)
    
    # 日期范围筛选
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(WorkLog.log_date >= start_date_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式错误，请使用 YYYY-MM-DD 格式"
            )
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(WorkLog.log_date <= end_date_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式错误，请使用 YYYY-MM-DD 格式"
            )
    
    # 完成状态筛选
    if completion_status:
        try:
            status_enum = CompletionStatus(completion_status)
            query = query.filter(WorkLog.completion_status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的完成状态"
            )
    
    # 按日期倒序排列
    query = query.order_by(WorkLog.log_date.desc(), WorkLog.created_at.desc())
    
    # 分页
    work_logs = query.offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for log in work_logs:
        log_data = WorkLogResponse(
            id=str(log.id),
            employee_id=str(log.employee_id),
            employee_name=log.employee.full_name if log.employee else "未知员工",
            log_date=log.log_date.isoformat() if log.log_date else "",
            work_content=log.work_content,
            completion_status=log.completion_status.value,
            status_display=log.get_status_display(),
            problems_encountered=log.problems_encountered,
            tomorrow_plan=log.tomorrow_plan,
            self_rating=log.self_rating,
            supervisor_rating=log.supervisor_rating,
            supervisor_comment=log.supervisor_comment,
            is_rated=log.is_rated_by_supervisor(),
            rating_difference=log.get_rating_difference(),
            created_at=log.created_at.isoformat() if log.created_at else None
        )
        result.append(log_data)
    
    return result


@router.get("/{log_id}", response_model=WorkLogResponse, summary="获取工作日志详情")
async def get_work_log(
    log_id: str,
    db: Session = Depends(get_db),
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    获取工作日志详情接口
    """
    work_log = db.query(WorkLog).filter(WorkLog.id == log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    
    # 权限检查：查看自己的日志或有管理权限
    if (str(work_log.employee_id) != str(permission_checker.current_user.id) and 
        not permission_checker.has_permission("/work-logs", "view")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return WorkLogResponse(
        id=str(work_log.id),
        employee_id=str(work_log.employee_id),
        employee_name=work_log.employee.full_name if work_log.employee else "未知员工",
        log_date=work_log.log_date.isoformat() if work_log.log_date else "",
        work_content=work_log.work_content,
        completion_status=work_log.completion_status.value,
        status_display=work_log.get_status_display(),
        problems_encountered=work_log.problems_encountered,
        tomorrow_plan=work_log.tomorrow_plan,
        self_rating=work_log.self_rating,
        supervisor_rating=work_log.supervisor_rating,
        supervisor_comment=work_log.supervisor_comment,
        is_rated=work_log.is_rated_by_supervisor(),
        rating_difference=work_log.get_rating_difference(),
        created_at=work_log.created_at.isoformat() if work_log.created_at else None
    )


@router.post("/", response_model=WorkLogResponse, summary="创建工作日志")
async def create_work_log(
    log_data: WorkLogCreateRequest,
    db: Session = Depends(get_db),
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    创建工作日志接口
    """
    # 确定员工ID
    employee_id = log_data.employee_id or str(permission_checker.current_user.id)
    
    # 权限检查：创建自己的日志或有管理权限
    if (employee_id != str(permission_checker.current_user.id) and 
        not permission_checker.has_permission("/work-logs", "create")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 验证员工是否存在
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="员工不存在"
        )
    
    # 解析日期
    try:
        log_date_obj = datetime.strptime(log_data.log_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式错误，请使用 YYYY-MM-DD 格式"
        )
    
    # 检查是否已存在相同日期的日志
    existing_log = db.query(WorkLog).filter(
        WorkLog.employee_id == employee_id,
        WorkLog.log_date == log_date_obj
    ).first()
    
    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该日期已存在工作日志"
        )
    
    # 验证完成状态
    try:
        completion_status_enum = CompletionStatus(log_data.completion_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的完成状态"
        )
    
    # 验证自评分数
    if log_data.self_rating is not None and not (1 <= log_data.self_rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="自评分数必须在1-5之间"
        )
    
    # 创建新工作日志
    new_log = WorkLog(
        employee_id=employee_id,
        log_date=log_date_obj,
        work_content=log_data.work_content,
        completion_status=completion_status_enum,
        problems_encountered=log_data.problems_encountered,
        tomorrow_plan=log_data.tomorrow_plan,
        self_rating=log_data.self_rating
    )
    
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
    return WorkLogResponse(
        id=str(new_log.id),
        employee_id=str(new_log.employee_id),
        employee_name=new_log.employee.full_name if new_log.employee else "未知员工",
        log_date=new_log.log_date.isoformat() if new_log.log_date else "",
        work_content=new_log.work_content,
        completion_status=new_log.completion_status.value,
        status_display=new_log.get_status_display(),
        problems_encountered=new_log.problems_encountered,
        tomorrow_plan=new_log.tomorrow_plan,
        self_rating=new_log.self_rating,
        supervisor_rating=new_log.supervisor_rating,
        supervisor_comment=new_log.supervisor_comment,
        is_rated=new_log.is_rated_by_supervisor(),
        rating_difference=new_log.get_rating_difference(),
        created_at=new_log.created_at.isoformat() if new_log.created_at else None
    )


@router.put("/{log_id}", response_model=WorkLogResponse, summary="更新工作日志")
async def update_work_log(
    log_id: str,
    log_data: WorkLogUpdateRequest,
    db: Session = Depends(get_db),
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    更新工作日志接口
    """
    # 查找工作日志
    work_log = db.query(WorkLog).filter(WorkLog.id == log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    
    # 权限检查：更新自己的日志或有管理权限
    if (str(work_log.employee_id) != str(permission_checker.current_user.id) and 
        not permission_checker.has_permission("/work-logs", "update")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 更新字段
    if log_data.work_content is not None:
        work_log.work_content = log_data.work_content
    
    if log_data.completion_status is not None:
        try:
            completion_status_enum = CompletionStatus(log_data.completion_status)
            work_log.completion_status = completion_status_enum
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的完成状态"
            )
    
    if log_data.problems_encountered is not None:
        work_log.problems_encountered = log_data.problems_encountered
    
    if log_data.tomorrow_plan is not None:
        work_log.tomorrow_plan = log_data.tomorrow_plan
    
    if log_data.self_rating is not None:
        if not (1 <= log_data.self_rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="自评分数必须在1-5之间"
            )
        work_log.self_rating = log_data.self_rating
    
    db.commit()
    db.refresh(work_log)
    
    return WorkLogResponse(
        id=str(work_log.id),
        employee_id=str(work_log.employee_id),
        employee_name=work_log.employee.full_name if work_log.employee else "未知员工",
        log_date=work_log.log_date.isoformat() if work_log.log_date else "",
        work_content=work_log.work_content,
        completion_status=work_log.completion_status.value,
        status_display=work_log.get_status_display(),
        problems_encountered=work_log.problems_encountered,
        tomorrow_plan=work_log.tomorrow_plan,
        self_rating=work_log.self_rating,
        supervisor_rating=work_log.supervisor_rating,
        supervisor_comment=work_log.supervisor_comment,
        is_rated=work_log.is_rated_by_supervisor(),
        rating_difference=work_log.get_rating_difference(),
        created_at=work_log.created_at.isoformat() if work_log.created_at else None
    )


@router.delete("/{log_id}", summary="删除工作日志")
async def delete_work_log(
    log_id: str,
    db: Session = Depends(get_db),
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    删除工作日志接口
    """
    work_log = db.query(WorkLog).filter(WorkLog.id == log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    
    # 权限检查：删除自己的日志或有管理权限
    if (str(work_log.employee_id) != str(permission_checker.current_user.id) and 
        not permission_checker.has_permission("/work-logs", "delete")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    db.delete(work_log)
    db.commit()
    
    return {"message": "工作日志已删除", "log_id": log_id}


@router.post("/{log_id}/supervisor-rating", response_model=WorkLogResponse, summary="上级评分")
async def set_supervisor_rating(
    log_id: str,
    rating_data: SupervisorRatingRequest,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/work-logs", "update"))
):
    """
    上级评分接口
    
    需要 /work-logs 路径的 update 权限
    """
    work_log = db.query(WorkLog).filter(WorkLog.id == log_id).first()
    if not work_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作日志不存在"
        )
    
    # 验证评分范围
    if not (1 <= rating_data.supervisor_rating <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上级评分必须在1-5之间"
        )
    
    # 设置上级评分
    work_log.supervisor_rating = rating_data.supervisor_rating
    work_log.supervisor_comment = rating_data.supervisor_comment
    
    db.commit()
    db.refresh(work_log)
    
    return WorkLogResponse(
        id=str(work_log.id),
        employee_id=str(work_log.employee_id),
        employee_name=work_log.employee.full_name if work_log.employee else "未知员工",
        log_date=work_log.log_date.isoformat() if work_log.log_date else "",
        work_content=work_log.work_content,
        completion_status=work_log.completion_status.value,
        status_display=work_log.get_status_display(),
        problems_encountered=work_log.problems_encountered,
        tomorrow_plan=work_log.tomorrow_plan,
        self_rating=work_log.self_rating,
        supervisor_rating=work_log.supervisor_rating,
        supervisor_comment=work_log.supervisor_comment,
        is_rated=work_log.is_rated_by_supervisor(),
        rating_difference=work_log.get_rating_difference(),
        created_at=work_log.created_at.isoformat() if work_log.created_at else None
    )


@router.get("/statistics/summary", response_model=WorkLogStatistics, summary="获取工作日志统计")
async def get_work_log_statistics(
    employee_id: Optional[str] = Query(None, description="员工ID筛选"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    获取工作日志统计信息
    """
    # 权限检查：查看自己的统计或有管理权限
    if employee_id and employee_id != str(permission_checker.current_user.id):
        permission_checker.require_permission("/work-logs", "view")
    elif not employee_id and not permission_checker.has_permission("/work-logs", "view"):
        # 如果没有管理权限，只能查看自己的统计
        employee_id = str(permission_checker.current_user.id)
    
    # 解析日期范围
    start_date_obj = None
    end_date_obj = None
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期格式错误"
            )
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="结束日期格式错误"
            )
    
    # 如果没有指定日期范围，默认最近30天
    if not start_date_obj and not end_date_obj:
        end_date_obj = date.today()
        start_date_obj = end_date_obj - timedelta(days=30)
    
    # 获取统计数据
    stats = WorkLog.get_rating_statistics(
        session=db,
        employee_id=employee_id,
        start_date=start_date_obj,
        end_date=end_date_obj
    )
    
    # 构建期间描述
    period = f"{start_date_obj} 到 {end_date_obj}" if start_date_obj and end_date_obj else "全部"
    
    return WorkLogStatistics(
        total_logs=stats["total_logs"],
        avg_self_rating=round(stats["avg_self_rating"], 2),
        avg_supervisor_rating=round(stats["avg_supervisor_rating"], 2),
        completion_rate=round(stats["completion_rate"], 2),
        rated_logs=stats["rated_logs"],
        rating_coverage=round(stats["rating_coverage"], 2),
        period=period
    )


@router.get("/my/recent", response_model=List[WorkLogResponse], summary="获取我的最近日志")
async def get_my_recent_logs(
    days: int = Query(7, ge=1, le=30, description="最近天数"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    获取当前用户最近的工作日志
    
    不需要额外权限，只需要认证即可
    """
    # 计算日期范围
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # 查询用户的最近日志
    work_logs = db.query(WorkLog).filter(
        WorkLog.employee_id == current_user.id,
        WorkLog.log_date >= start_date,
        WorkLog.log_date <= end_date
    ).order_by(WorkLog.log_date.desc()).all()
    
    # 构建响应数据
    result = []
    for log in work_logs:
        log_data = WorkLogResponse(
            id=str(log.id),
            employee_id=str(log.employee_id),
            employee_name=log.employee.full_name if log.employee else "未知员工",
            log_date=log.log_date.isoformat() if log.log_date else "",
            work_content=log.work_content,
            completion_status=log.completion_status.value,
            status_display=log.get_status_display(),
            problems_encountered=log.problems_encountered,
            tomorrow_plan=log.tomorrow_plan,
            self_rating=log.self_rating,
            supervisor_rating=log.supervisor_rating,
            supervisor_comment=log.supervisor_comment,
            is_rated=log.is_rated_by_supervisor(),
            rating_difference=log.get_rating_difference(),
            created_at=log.created_at.isoformat() if log.created_at else None
        )
        result.append(log_data)
    
    return result