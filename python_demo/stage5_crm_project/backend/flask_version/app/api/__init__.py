"""
API 模块

包含所有 API 蓝图
"""

from .auth import auth_bp
from .employees import employees_bp
from .positions import positions_bp
from .menus import menus_bp
from .roles import roles_bp
from .permissions import permissions_bp
from .work_logs import work_logs_bp
from .tasks import tasks_bp

__all__ = [
    'auth_bp',
    'employees_bp',
    'positions_bp',
    'menus_bp',
    'roles_bp',
    'permissions_bp',
    'work_logs_bp',
    'tasks_bp'
]