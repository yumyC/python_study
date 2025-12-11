#!/usr/bin/env python3
"""
Celery Worker 启动脚本

用于启动 Celery 工作进程来处理异步任务
"""

import os
import sys
from app.tasks.celery_app import celery_app

if __name__ == "__main__":
    # 设置环境变量
    os.environ.setdefault("PYTHONPATH", ".")
    
    # 启动 Celery Worker
    # 可以通过命令行参数自定义配置
    argv = [
        "worker",
        "--app=app.tasks.celery_app:celery_app",
        "--loglevel=info",
        "--concurrency=4",  # 并发工作进程数
        "--queues=celery,export",  # 监听的队列
        "--hostname=worker@%h",
    ]
    
    # 添加命令行参数
    if len(sys.argv) > 1:
        argv.extend(sys.argv[1:])
    
    celery_app.worker_main(argv)