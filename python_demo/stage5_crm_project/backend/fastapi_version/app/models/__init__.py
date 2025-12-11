# 数据模型包初始化文件

"""
CRM 系统数据模型

这个包包含了 CRM 系统的所有数据模型：
- Employee: 员工模型
- Position: 岗位模型
- Menu: 菜单模型
- Role: 角色模型
- RoleMenuPermission: 角色菜单权限模型
- WorkLog: 工作日志模型
"""

from .base import BaseModel
from .employee import Employee, EmployeeStatus
from .position import Position
from .menu import Menu
from .role import Role
from .role_menu_permission import RoleMenuPermission
from .work_log import WorkLog, CompletionStatus

# 导出所有模型类
__all__ = [
    "BaseModel",
    "Employee",
    "EmployeeStatus", 
    "Position",
    "Menu",
    "Role",
    "RoleMenuPermission",
    "WorkLog",
    "CompletionStatus"
]