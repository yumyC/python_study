"""
Celery 应用配置

配置 Celery 任务队列，使用 Redis 作为消息代理
"""

from celery import Celery
import os
from typing import Optional

# 从环境变量获取 Redis 配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 创建 Celery 应用实例
celery_app = Celery(
    "crm_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.work_log_tasks"]
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化格式
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务结果过期时间（秒）
    result_expires=3600,
    
    # 任务路由配置
    task_routes={
        "app.tasks.work_log_tasks.export_work_logs_task": {"queue": "export"},
    },
    
    # 工作进程配置
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    
    # 任务重试配置
    task_default_retry_delay=60,  # 重试延迟60秒
    task_max_retries=3,
)


def get_task_status(task_id: str) -> dict:
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态信息
    """
    result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "info": result.info,
        "traceback": result.traceback if result.failed() else None
    }


def revoke_task(task_id: str, terminate: bool = False) -> dict:
    """
    撤销任务
    
    Args:
        task_id: 任务ID
        terminate: 是否强制终止正在运行的任务
        
    Returns:
        撤销结果
    """
    celery_app.control.revoke(task_id, terminate=terminate)
    
    return {
        "task_id": task_id,
        "revoked": True,
        "terminated": terminate
    }


def get_active_tasks() -> list:
    """
    获取活跃任务列表
    
    Returns:
        活跃任务列表
    """
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active()
    
    if not active_tasks:
        return []
    
    # 合并所有工作节点的任务
    all_tasks = []
    for worker, tasks in active_tasks.items():
        for task in tasks:
            task["worker"] = worker
            all_tasks.append(task)
    
    return all_tasks


def get_worker_stats() -> dict:
    """
    获取工作节点统计信息
    
    Returns:
        工作节点统计
    """
    inspect = celery_app.control.inspect()
    
    return {
        "stats": inspect.stats(),
        "registered": inspect.registered(),
        "active": inspect.active(),
        "scheduled": inspect.scheduled(),
        "reserved": inspect.reserved()
    }


# 任务状态常量
class TaskStatus:
    PENDING = "PENDING"      # 等待中
    STARTED = "STARTED"      # 已开始
    SUCCESS = "SUCCESS"      # 成功
    FAILURE = "FAILURE"      # 失败
    RETRY = "RETRY"          # 重试中
    REVOKED = "REVOKED"      # 已撤销