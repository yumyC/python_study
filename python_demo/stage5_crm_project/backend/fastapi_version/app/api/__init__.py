"""
API 路由模块

包含所有 API 端点的路由定义
"""

from .auth import router as auth_router
from .employees import router as employees_router
from .positions import router as positions_router
from .menus import router as menus_router
from .roles import router as roles_router
from .permissions import router as permissions_router
from .work_logs import router as work_logs_router
from .tasks import router as tasks_router

__all__ = [
    "auth_router", 
    "employees_router", 
    "positions_router", 
    "menus_router", 
    "roles_router", 
    "permissions_router", 
    "work_logs_router",
    "tasks_router"
]