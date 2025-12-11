#!/usr/bin/env python
"""
Celery Worker 启动脚本

用于启动 Celery Worker 进程
"""

from app import create_app
from app.tasks.celery_app import make_celery

# 创建 Flask 应用
flask_app = create_app()

# 创建 Celery 实例
celery = make_celery(flask_app)

if __name__ == '__main__':
    # 启动 Celery Worker
    celery.start()