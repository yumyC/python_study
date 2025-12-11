"""
Pydantic 模式定义

包含所有 API 的请求和响应模式
"""

from .common import PaginationParams, PaginatedResponse
from .employee import EmployeeResponse, EmployeeCreateRequest, EmployeeUpdateRequest
from .position import PositionResponse, PositionCreateRequest, PositionUpdateRequest, PositionTreeResponse
from .menu import MenuResponse, MenuCreateRequest, MenuUpdateRequest, MenuTreeResponse
from .role import RoleResponse, RoleCreateRequest, RoleUpdateRequest, RoleDetailResponse
from .permission import PermissionResponse, PermissionCreateRequest, PermissionUpdateRequest, BatchPermissionRequest
from .work_log import WorkLogResponse, WorkLogCreateRequest, WorkLogUpdateRequest, SupervisorRatingRequest, WorkLogStatistics

__all__ = [
    # Common
    "PaginationParams",
    "PaginatedResponse",
    
    # Employee
    "EmployeeResponse",
    "EmployeeCreateRequest", 
    "EmployeeUpdateRequest",
    
    # Position
    "PositionResponse",
    "PositionCreateRequest",
    "PositionUpdateRequest",
    "PositionTreeResponse",
    
    # Menu
    "MenuResponse",
    "MenuCreateRequest",
    "MenuUpdateRequest", 
    "MenuTreeResponse",
    
    # Role
    "RoleResponse",
    "RoleCreateRequest",
    "RoleUpdateRequest",
    "RoleDetailResponse",
    
    # Permission
    "PermissionResponse",
    "PermissionCreateRequest",
    "PermissionUpdateRequest",
    "BatchPermissionRequest",
    
    # Work Log
    "WorkLogResponse",
    "WorkLogCreateRequest",
    "WorkLogUpdateRequest",
    "SupervisorRatingRequest",
    "WorkLogStatistics"
]