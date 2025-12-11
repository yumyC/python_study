"""
异步任务模块

这个模块包含了 CRM 系统的异步任务实现，使用 Celery 作为任务队列
"""

from .celery_app import celery_app
from .work_log_tasks import export_work_logs_task

__all__ = ["celery_app", "export_work_logs_task"]