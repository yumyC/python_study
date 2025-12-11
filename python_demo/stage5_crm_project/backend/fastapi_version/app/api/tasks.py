"""
异步任务管理 API

提供任务创建、状态查询、文件下载等功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import os
import tempfile

from ..database import get_db
from ..auth import get_current_active_user, require_permission
from ..models import Employee, WorkLog
from ..tasks import celery_app, export_work_logs_task
from ..tasks.celery_app import get_task_status, revoke_task, get_active_tasks, get_worker_stats
from ..middleware.error_handler import BusinessLogicError, ResourceNotFoundError

router = APIRouter(tags=["异步任务"])


@router.post("/tasks/export-work-logs")
async def create_export_task(
    employee_id: Optional[str] = Query(None, description="员工ID，为空则导出所有员工"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    export_format: str = Query("xlsx", description="导出格式"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_permission("/work-logs", "export"))
):
    """
    创建工作日志导出任务
    
    需要工作日志的导出权限
    """
    # 验证日期格式
    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise BusinessLogicError("开始日期格式错误，请使用 YYYY-MM-DD 格式")
    
    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise BusinessLogicError("结束日期格式错误，请使用 YYYY-MM-DD 格式")
    
    # 验证日期范围
    if start_date and end_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_dt > end_dt:
            raise BusinessLogicError("开始日期不能晚于结束日期")
    
    # 验证员工是否存在
    if employee_id:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise ResourceNotFoundError("员工", employee_id)
    
    # 创建异步任务
    task = export_work_logs_task.delay(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        export_format=export_format,
        requested_by=str(current_user.id)
    )
    
    return {
        "task_id": task.id,
        "status": "PENDING",
        "message": "导出任务已创建，正在处理中...",
        "created_at": datetime.now().isoformat(),
        "filters": {
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date,
            "export_format": export_format
        }
    }


@router.get("/tasks/{task_id}/status")
async def get_task_status_endpoint(
    task_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    获取任务状态
    
    返回任务的当前状态、进度和结果信息
    """
    try:
        status_info = get_task_status(task_id)
        
        # 格式化返回信息
        response = {
            "task_id": task_id,
            "status": status_info["status"],
            "created_at": None,  # Celery 不直接提供创建时间
            "updated_at": datetime.now().isoformat()
        }
        
        # 根据状态添加不同的信息
        if status_info["status"] == "PENDING":
            response["message"] = "任务等待处理中..."
            
        elif status_info["status"] == "PROGRESS":
            if isinstance(status_info["info"], dict):
                response["progress"] = status_info["info"]
                response["message"] = status_info["info"].get("status", "任务处理中...")
            else:
                response["message"] = "任务处理中..."
                
        elif status_info["status"] == "SUCCESS":
            response["message"] = "任务完成"
            response["result"] = status_info["result"]
            
            # 如果是导出任务，添加下载链接
            if status_info["result"] and status_info["result"].get("success"):
                response["download_url"] = f"/api/tasks/{task_id}/download"
                
        elif status_info["status"] == "FAILURE":
            response["message"] = "任务失败"
            response["error"] = status_info["result"] if status_info["result"] else "未知错误"
            
            if status_info["traceback"]:
                response["traceback"] = status_info["traceback"]
                
        elif status_info["status"] == "REVOKED":
            response["message"] = "任务已被撤销"
            
        else:
            response["message"] = f"未知状态: {status_info['status']}"
        
        return response
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(exc)}")


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    terminate: bool = Query(False, description="是否强制终止正在运行的任务"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    取消任务
    
    撤销等待中的任务或终止正在运行的任务
    """
    try:
        # 先检查任务状态
        status_info = get_task_status(task_id)
        
        if status_info["status"] in ["SUCCESS", "FAILURE"]:
            raise BusinessLogicError(f"任务已完成，无法取消（状态：{status_info['status']}）")
        
        # 撤销任务
        result = revoke_task(task_id, terminate=terminate)
        
        return {
            "task_id": task_id,
            "cancelled": True,
            "terminated": result["terminated"],
            "message": "任务已取消" if not terminate else "任务已强制终止",
            "cancelled_at": datetime.now().isoformat()
        }
        
    except BusinessLogicError:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(exc)}")


@router.get("/tasks/{task_id}/download")
async def download_task_result(
    task_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    下载任务结果文件
    
    仅支持已完成的导出任务
    """
    try:
        # 检查任务状态
        status_info = get_task_status(task_id)
        
        if status_info["status"] != "SUCCESS":
            raise BusinessLogicError(f"任务未完成，无法下载（状态：{status_info['status']}）")
        
        result = status_info["result"]
        if not result or not result.get("success"):
            raise BusinessLogicError("任务执行失败，没有可下载的文件")
        
        file_path = result.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise ResourceNotFoundError("文件")
        
        file_name = result.get("file_name", os.path.basename(file_path))
        
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except (BusinessLogicError, ResourceNotFoundError):
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(exc)}")


@router.get("/tasks/active")
async def get_active_tasks_endpoint(
    current_user: Employee = Depends(require_permission("/tasks", "view"))
):
    """
    获取活跃任务列表
    
    需要任务管理权限
    """
    try:
        active_tasks = get_active_tasks()
        
        # 格式化任务信息
        formatted_tasks = []
        for task in active_tasks:
            formatted_task = {
                "task_id": task.get("id"),
                "name": task.get("name"),
                "worker": task.get("worker"),
                "args": task.get("args", []),
                "kwargs": task.get("kwargs", {}),
                "time_start": task.get("time_start"),
                "acknowledged": task.get("acknowledged", False)
            }
            formatted_tasks.append(formatted_task)
        
        return {
            "active_tasks": formatted_tasks,
            "count": len(formatted_tasks),
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"获取活跃任务失败: {str(exc)}")


@router.get("/tasks/stats")
async def get_task_stats(
    current_user: Employee = Depends(require_permission("/tasks", "view"))
):
    """
    获取任务系统统计信息
    
    需要任务管理权限
    """
    try:
        stats = get_worker_stats()
        
        return {
            "worker_stats": stats,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"获取任务统计失败: {str(exc)}")


@router.post("/tasks/cleanup-files")
async def cleanup_export_files(
    max_age_hours: int = Query(24, description="文件最大保留时间（小时）"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: Employee = Depends(require_permission("/tasks", "manage"))
):
    """
    清理过期的导出文件
    
    需要任务管理权限
    """
    from ..tasks.work_log_tasks import cleanup_export_files_task
    
    # 创建后台清理任务
    task = cleanup_export_files_task.delay(max_age_hours=max_age_hours)
    
    return {
        "task_id": task.id,
        "message": f"文件清理任务已创建，将清理 {max_age_hours} 小时前的文件",
        "max_age_hours": max_age_hours,
        "created_at": datetime.now().isoformat()
    }


@router.get("/tasks/export-history")
async def get_export_history(
    limit: int = Query(20, description="返回记录数量"),
    offset: int = Query(0, description="跳过记录数量"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    获取导出历史记录
    
    注意：这是一个简化的实现，实际项目中应该将任务信息存储到数据库
    """
    # 这里只是一个示例，实际应该从数据库查询任务历史
    # 可以创建一个 TaskHistory 模型来存储任务信息
    
    return {
        "message": "导出历史功能需要配合数据库存储实现",
        "suggestion": "建议创建 TaskHistory 模型来记录任务执行历史",
        "current_user": current_user.username,
        "limit": limit,
        "offset": offset
    }