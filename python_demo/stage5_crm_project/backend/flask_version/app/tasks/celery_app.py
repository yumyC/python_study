"""
Celery 应用配置

配置和初始化 Celery 应用
"""

from celery import Celery
import os


def make_celery(app=None):
    """
    创建 Celery 应用实例
    
    Args:
        app: Flask 应用实例（可选）
        
    Returns:
        Celery: 配置好的 Celery 实例
    """
    # 获取配置
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # 创建 Celery 实例
    celery = Celery(
        'crm_flask',
        broker=broker_url,
        backend=result_backend,
        include=['app.tasks.work_log_tasks']  # 包含任务模块
    )
    
    # 配置 Celery
    celery.conf.update(
        # 任务序列化
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        
        # 时区设置
        timezone='Asia/Shanghai',
        enable_utc=True,
        
        # 任务路由
        task_routes={
            'app.tasks.work_log_tasks.*': {'queue': 'work_logs'},
        },
        
        # 任务结果过期时间（秒）
        result_expires=3600,
        
        # 任务重试配置
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        
        # 任务限制
        task_time_limit=300,  # 5分钟
        task_soft_time_limit=240,  # 4分钟
    )
    
    # 如果提供了 Flask 应用，配置任务上下文
    if app:
        class ContextTask(celery.Task):
            """在 Flask 应用上下文中执行的任务"""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery


# 创建默认的 Celery 实例
celery = make_celery()