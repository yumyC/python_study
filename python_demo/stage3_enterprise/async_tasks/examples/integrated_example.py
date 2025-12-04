"""
异步任务完整集成示例

本示例演示：
1. FastAPI 与 Celery 的集成
2. 工作日志导出功能（CRM 项目场景）
3. 任务状态追踪和进度更新
4. 文件生成和下载
5. 综合应用队列、重试、定时任务

运行说明：
1. 安装依赖：pip install fastapi celery redis uvicorn openpyxl
2. 启动 Redis：docker run -d -p 6379:6379 redis:latest
3. 启动 Celery Worker：celery -A examples.integrated_example worker --loglevel=info
4. 启动 FastAPI：uvicorn examples.integrated_example:app --reload
5. 访问 http://localhost:8000/docs 查看 API 文档
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from celery import Celery
from celery.result import AsyncResult
from datetime import datetime, timedelta
from typing import Optional, List
import os
import time
from pathlib import Path

# ============================================================================
# Celery 配置
# ============================================================================

celery_app = Celery(
    'integrated_example',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)

# 配置任务队列
from kombu import Queue

celery_app.conf.task_queues = (
    Queue('high_priority', routing_key='high'),
    Queue('default', routing_key='default'),
    Queue('export', routing_key='export'),
)

celery_app.conf.task_routes = {
    'integrated_example.export_work_logs': {'queue': 'export'},
    'integrated_example.send_notification': {'queue': 'high_priority'},
}

# ============================================================================
# FastAPI 应用
# ============================================================================

app = FastAPI(
    title="异步任务集成示例",
    description="演示 FastAPI 与 Celery 的集成应用",
    version="1.0.0"
)

# 确保导出目录存在
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

# ============================================================================
# Pydantic 模型
# ============================================================================

class WorkLog(BaseModel):
    """工作日志模型"""
    id: int
    employee_id: str
    employee_name: str
    log_date: str
    work_content: str
    completion_status: str
    problems_encountered: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    self_rating: int
    supervisor_rating: Optional[int] = None


class ExportRequest(BaseModel):
    """导出请求模型"""
    start_date: str
    end_date: str
    employee_ids: Optional[List[str]] = None
    export_format: str = "xlsx"


class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class NotificationRequest(BaseModel):
    """通知请求模型"""
    user_id: str
    message: str
    notification_type: str = "email"


# ============================================================================
# Celery 任务
# ============================================================================

@celery_app.task(name='integrated_example.export_work_logs', bind=True)
def export_work_logs(self, start_date: str, end_date: str, employee_ids: List[str] = None):
    """
    导出工作日志任务
    
    这是一个典型的异步任务场景：
    - 数据量可能很大
    - 需要较长时间处理
    - 需要生成文件
    - 需要追踪进度
    """
    try:
        print(f"[导出任务] 开始导出工作日志 - 任务 ID: {self.request.id}")
        print(f"日期范围: {start_date} 到 {end_date}")
        
        # 更新任务状态为处理中
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': '正在查询数据...'}
        )
        
        # 模拟查询数据库
        time.sleep(1)
        work_logs = _generate_sample_work_logs(start_date, end_date, employee_ids)
        total_logs = len(work_logs)
        
        print(f"[导出任务] 查询到 {total_logs} 条工作日志")
        
        # 更新进度
        self.update_state(
            state='PROGRESS',
            meta={'current': 20, 'total': 100, 'status': f'正在处理 {total_logs} 条数据...'}
        )
        
        # 生成 Excel 文件
        time.sleep(2)
        file_name = f"work_logs_{start_date}_{end_date}_{int(time.time())}.xlsx"
        file_path = EXPORT_DIR / file_name
        
        # 模拟写入 Excel（实际应用中使用 openpyxl 或 pandas）
        _create_excel_file(file_path, work_logs, self)
        
        # 任务完成
        result = {
            'file_name': file_name,
            'file_path': str(file_path),
            'records_count': total_logs,
            'start_date': start_date,
            'end_date': end_date,
            'created_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        print(f"[导出任务] 导出完成 - 文件: {file_name}")
        
        return result
        
    except Exception as e:
        print(f"[导出任务] 导出失败: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(name='integrated_example.send_notification', bind=True, max_retries=3)
def send_notification(self, user_id: str, message: str, notification_type: str = "email"):
    """
    发送通知任务（高优先级）
    
    支持重试机制
    """
    try:
        print(f"[通知任务] 发送通知 - 任务 ID: {self.request.id}")
        print(f"用户: {user_id}, 类型: {notification_type}")
        
        # 模拟发送通知
        time.sleep(1)
        
        # 模拟可能的失败
        import random
        if random.random() < 0.2:  # 20% 概率失败
            raise Exception("通知发送失败")
        
        result = {
            'user_id': user_id,
            'message': message,
            'notification_type': notification_type,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        print(f"[通知任务] 通知发送成功")
        return result
        
    except Exception as exc:
        print(f"[通知任务] 发送失败，准备重试...")
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(name='integrated_example.cleanup_old_exports')
def cleanup_old_exports(days_old: int = 7):
    """
    清理旧的导出文件（定时任务）
    
    删除超过指定天数的导出文件
    """
    print(f"[清理任务] 清理 {days_old} 天前的导出文件")
    
    cutoff_time = time.time() - (days_old * 24 * 60 * 60)
    deleted_count = 0
    
    for file_path in EXPORT_DIR.glob("*.xlsx"):
        if file_path.stat().st_mtime < cutoff_time:
            file_path.unlink()
            deleted_count += 1
            print(f"[清理任务] 删除文件: {file_path.name}")
    
    result = {
        'deleted_count': deleted_count,
        'days_old': days_old,
        'cleaned_at': datetime.now().isoformat()
    }
    
    print(f"[清理任务] 清理完成，删除 {deleted_count} 个文件")
    return result


# ============================================================================
# FastAPI 路由
# ============================================================================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "异步任务集成示例 API",
        "docs": "/docs",
        "endpoints": {
            "export": "POST /api/export/work-logs",
            "task_status": "GET /api/tasks/{task_id}",
            "download": "GET /api/download/{file_name}",
            "notification": "POST /api/notifications"
        }
    }


@app.post("/api/export/work-logs", response_model=dict)
async def create_export_task(request: ExportRequest):
    """
    创建工作日志导出任务
    
    返回任务 ID，客户端可以使用该 ID 查询任务状态
    """
    # 提交异步任务
    task = export_work_logs.delay(
        start_date=request.start_date,
        end_date=request.end_date,
        employee_ids=request.employee_ids
    )
    
    return {
        "task_id": task.id,
        "status": "processing",
        "message": "导出任务已提交，请使用 task_id 查询进度",
        "status_url": f"/api/tasks/{task.id}"
    }


@app.get("/api/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """
    查询任务状态
    
    返回任务的当前状态、进度和结果
    """
    task = AsyncResult(task_id, app=celery_app)
    
    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'status': 'pending',
            'progress': 0
        }
    elif task.state == 'PROGRESS':
        response = {
            'task_id': task_id,
            'status': 'processing',
            'progress': task.info.get('current', 0),
            'result': {
                'message': task.info.get('status', '处理中...')
            }
        }
    elif task.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'status': 'completed',
            'progress': 100,
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'task_id': task_id,
            'status': 'failed',
            'error': str(task.info)
        }
    else:
        response = {
            'task_id': task_id,
            'status': task.state.lower(),
        }
    
    return response


@app.get("/api/download/{file_name}")
async def download_file(file_name: str):
    """
    下载导出的文件
    
    验证文件存在后返回文件下载响应
    """
    file_path = EXPORT_DIR / file_name
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.post("/api/notifications", response_model=dict)
async def send_notification_endpoint(request: NotificationRequest):
    """
    发送通知（高优先级任务）
    
    立即返回响应，通知在后台发送
    """
    task = send_notification.delay(
        user_id=request.user_id,
        message=request.message,
        notification_type=request.notification_type
    )
    
    return {
        "task_id": task.id,
        "status": "processing",
        "message": "通知发送任务已提交"
    }


@app.post("/api/cleanup", response_model=dict)
async def trigger_cleanup(days_old: int = 7):
    """
    手动触发清理任务
    
    清理旧的导出文件
    """
    task = cleanup_old_exports.delay(days_old)
    
    return {
        "task_id": task.id,
        "status": "processing",
        "message": f"清理任务已提交，将删除 {days_old} 天前的文件"
    }


@app.get("/api/exports", response_model=dict)
async def list_exports():
    """
    列出所有导出文件
    
    返回可下载的文件列表
    """
    files = []
    for file_path in EXPORT_DIR.glob("*.xlsx"):
        stat = file_path.stat()
        files.append({
            'file_name': file_path.name,
            'size': stat.st_size,
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'download_url': f"/api/download/{file_path.name}"
        })
    
    return {
        'count': len(files),
        'files': sorted(files, key=lambda x: x['created_at'], reverse=True)
    }


# ============================================================================
# 辅助函数
# ============================================================================

def _generate_sample_work_logs(start_date: str, end_date: str, employee_ids: List[str] = None):
    """生成示例工作日志数据"""
    work_logs = []
    
    # 模拟数据
    employees = employee_ids or ['emp_001', 'emp_002', 'emp_003']
    
    for i in range(50):  # 生成 50 条示例数据
        work_logs.append({
            'id': i + 1,
            'employee_id': employees[i % len(employees)],
            'employee_name': f'员工{i % len(employees) + 1}',
            'log_date': start_date,
            'work_content': f'完成了任务 {i + 1}',
            'completion_status': 'completed',
            'problems_encountered': '无' if i % 3 == 0 else '遇到一些小问题',
            'tomorrow_plan': f'计划完成任务 {i + 2}',
            'self_rating': (i % 5) + 1,
            'supervisor_rating': (i % 5) + 1 if i % 2 == 0 else None
        })
    
    return work_logs


def _create_excel_file(file_path: Path, work_logs: List[dict], task):
    """创建 Excel 文件（模拟）"""
    # 实际应用中使用 openpyxl 或 pandas
    # 这里只是模拟文件创建过程
    
    total = len(work_logs)
    
    # 模拟写入过程
    for i in range(0, total, 10):
        time.sleep(0.3)
        progress = min((i + 10) / total * 80 + 20, 100)
        task.update_state(
            state='PROGRESS',
            meta={
                'current': int(progress),
                'total': 100,
                'status': f'正在写入 Excel 文件... ({i + 10}/{total})'
            }
        )
    
    # 创建一个简单的文本文件作为示例
    # 实际应用中应该使用 openpyxl 创建真正的 Excel 文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("工作日志导出文件\n")
        f.write(f"导出时间: {datetime.now().isoformat()}\n")
        f.write(f"记录数: {total}\n")


# ============================================================================
# 定时任务配置（可选）
# ============================================================================

celery_app.conf.beat_schedule = {
    # 每天凌晨 3 点清理旧文件
    'cleanup-old-exports-daily': {
        'task': 'integrated_example.cleanup_old_exports',
        'schedule': 3600.0,  # 为了演示，设置为每小时执行一次
        'args': (7,)  # 清理 7 天前的文件
    },
}


# ============================================================================
# 主程序
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              异步任务完整集成示例                            ║
    ║                                                              ║
    ║  启动步骤:                                                   ║
    ║  1. 启动 Redis:                                              ║
    ║     docker run -d -p 6379:6379 redis:latest                 ║
    ║                                                              ║
    ║  2. 启动 Celery Worker:                                      ║
    ║     celery -A examples.integrated_example worker \\          ║
    ║     --loglevel=info                                          ║
    ║                                                              ║
    ║  3. 启动 FastAPI:                                            ║
    ║     uvicorn examples.integrated_example:app --reload        ║
    ║                                                              ║
    ║  4. 访问 API 文档:                                           ║
    ║     http://localhost:8000/docs                               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
