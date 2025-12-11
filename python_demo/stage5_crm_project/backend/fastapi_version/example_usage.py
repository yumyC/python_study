#!/usr/bin/env python3
"""
FastAPI 认证授权系统使用示例

这个文件演示了如何在实际项目中使用认证授权系统
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

# 导入认证相关模块
from app.auth import (
    # 基础认证
    get_current_user,
    get_current_active_user,
    
    # 权限控制
    require_permission,
    require_role,
    
    # 灵活权限检查
    get_permission_checker,
    PermissionChecker,
    
    # 可选认证
    optional_auth,
    
    # 数据模型
    UserInfo
)
from app.database import get_db
from app.models import Employee

# 创建示例应用
example_app = FastAPI(title="认证授权使用示例")


# ============================================================================
# 1. 基础认证示例
# ============================================================================

@example_app.get("/basic-auth-example")
async def basic_auth_example(
    current_user: Employee = Depends(get_current_user)
):
    """
    基础认证示例
    
    只需要用户登录即可访问，不检查具体权限
    """
    return {
        "message": "这是一个需要登录的接口",
        "user": current_user.username,
        "user_id": str(current_user.id)
    }


@example_app.get("/active-user-example")
async def active_user_example(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    活跃用户认证示例
    
    需要用户登录且账户状态为活跃
    """
    return {
        "message": "这是一个需要活跃用户的接口",
        "user": current_user.username,
        "status": current_user.status.value
    }


# ============================================================================
# 2. 权限控制示例
# ============================================================================

@example_app.get("/employees-view-example")
async def employees_view_example(
    current_user: Employee = Depends(require_permission("/employees", "view"))
):
    """
    权限控制示例 - 查看员工
    
    需要 /employees 路径的 view 权限
    """
    return {
        "message": "你有查看员工的权限",
        "user": current_user.username,
        "permission": "/employees:view"
    }


@example_app.post("/employees-create-example")
async def employees_create_example(
    current_user: Employee = Depends(require_permission("/employees", "create"))
):
    """
    权限控制示例 - 创建员工
    
    需要 /employees 路径的 create 权限
    """
    return {
        "message": "你有创建员工的权限",
        "user": current_user.username,
        "permission": "/employees:create"
    }


@example_app.delete("/employees-delete-example")
async def employees_delete_example(
    current_user: Employee = Depends(require_permission("/employees", "delete"))
):
    """
    权限控制示例 - 删除员工
    
    需要 /employees 路径的 delete 权限
    """
    return {
        "message": "你有删除员工的权限",
        "user": current_user.username,
        "permission": "/employees:delete"
    }


# ============================================================================
# 3. 角色控制示例
# ============================================================================

@example_app.get("/admin-only-example")
async def admin_only_example(
    current_user: Employee = Depends(require_role("ADMIN"))
):
    """
    角色控制示例 - 仅管理员
    
    只有 ADMIN 角色的用户才能访问
    """
    return {
        "message": "这是管理员专用接口",
        "user": current_user.username,
        "role": current_user.role.code if current_user.role else None
    }


@example_app.get("/manager-only-example")
async def manager_only_example(
    current_user: Employee = Depends(require_role("MANAGER"))
):
    """
    角色控制示例 - 仅经理
    
    只有 MANAGER 角色的用户才能访问
    """
    return {
        "message": "这是经理专用接口",
        "user": current_user.username,
        "role": current_user.role.code if current_user.role else None
    }


# ============================================================================
# 4. 灵活权限检查示例
# ============================================================================

@example_app.put("/flexible-permission-example/{resource_id}")
async def flexible_permission_example(
    resource_id: str,
    action: str,
    checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    灵活权限检查示例
    
    根据不同条件进行不同的权限检查
    """
    # 示例：根据资源 ID 和当前用户关系决定权限要求
    if resource_id == str(checker.current_user.id):
        # 操作自己的资源，只需要基础权限
        checker.require_permission("/profile", "view")
        message = "你正在操作自己的资源"
    else:
        # 操作他人资源，需要管理权限
        checker.require_permission("/employees", "update")
        message = "你正在操作他人的资源"
    
    # 根据操作类型检查不同权限
    if action == "sensitive_operation":
        # 敏感操作需要管理员角色
        checker.require_role("ADMIN")
        message += "，这是敏感操作"
    
    return {
        "message": message,
        "resource_id": resource_id,
        "action": action,
        "user": checker.current_user.username
    }


@example_app.get("/conditional-permission-example")
async def conditional_permission_example(
    include_sensitive: bool = False,
    checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    条件权限检查示例
    
    根据请求参数决定是否需要额外权限
    """
    # 基础数据，所有登录用户都可以访问
    data = {
        "basic_info": "这是基础信息",
        "user": checker.current_user.username
    }
    
    # 如果请求敏感数据，需要额外权限
    if include_sensitive:
        if checker.has_permission("/sensitive-data", "view"):
            data["sensitive_info"] = "这是敏感信息"
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="访问敏感数据需要额外权限"
            )
    
    return data


# ============================================================================
# 5. 可选认证示例
# ============================================================================

@example_app.get("/optional-auth-example")
async def optional_auth_example(
    current_user: Optional[Employee] = Depends(optional_auth)
):
    """
    可选认证示例
    
    登录和未登录用户都可以访问，但返回不同内容
    """
    if current_user:
        return {
            "message": "欢迎回来！",
            "user": current_user.username,
            "personalized_content": "这是为你定制的内容"
        }
    else:
        return {
            "message": "欢迎访问！",
            "public_content": "这是公开内容",
            "suggestion": "登录后可以获得更多功能"
        }


# ============================================================================
# 6. 复合权限检查示例
# ============================================================================

@example_app.post("/complex-permission-example")
async def complex_permission_example(
    operation_type: str,
    target_user_id: Optional[str] = None,
    checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    复合权限检查示例
    
    演示复杂的权限检查逻辑
    """
    result = {
        "operation": operation_type,
        "user": checker.current_user.username,
        "permissions_checked": []
    }
    
    # 根据操作类型检查不同权限
    if operation_type == "view_reports":
        # 查看报表需要报表权限
        checker.require_permission("/reports", "view")
        result["permissions_checked"].append("/reports:view")
        
    elif operation_type == "export_data":
        # 导出数据需要导出权限
        checker.require_permission("/data", "export")
        result["permissions_checked"].append("/data:export")
        
    elif operation_type == "system_config":
        # 系统配置需要管理员角色
        checker.require_role("ADMIN")
        result["permissions_checked"].append("role:ADMIN")
        
    elif operation_type == "user_management":
        # 用户管理需要多个权限
        if target_user_id and target_user_id == str(checker.current_user.id):
            # 管理自己，基础权限即可
            checker.require_permission("/profile", "update")
            result["permissions_checked"].append("/profile:update")
        else:
            # 管理他人，需要用户管理权限
            checker.require_permission("/employees", "update")
            result["permissions_checked"].append("/employees:update")
    
    # 检查是否有任意一个管理权限
    management_permissions = ["/employees", "/roles", "/positions"]
    has_any_management = any(
        checker.has_permission(path, "view") 
        for path in management_permissions
    )
    
    if has_any_management:
        result["management_access"] = True
        result["message"] = "你有管理权限"
    else:
        result["management_access"] = False
        result["message"] = "你没有管理权限"
    
    return result


# ============================================================================
# 7. 权限信息查询示例
# ============================================================================

@example_app.get("/my-permissions-example")
async def my_permissions_example(
    checker: PermissionChecker = Depends(get_permission_checker),
    db: Session = Depends(get_db)
):
    """
    权限信息查询示例
    
    展示当前用户的详细权限信息
    """
    from app.auth import AuthService
    
    auth_service = AuthService(db)
    
    # 获取用户的所有权限
    permissions = auth_service.get_user_permissions(checker.current_user)
    
    # 获取菜单权限
    menu_permissions = auth_service.get_user_menu_permissions(checker.current_user)
    
    # 检查常用权限
    common_checks = {
        "can_view_employees": checker.has_permission("/employees", "view"),
        "can_create_employees": checker.has_permission("/employees", "create"),
        "can_update_employees": checker.has_permission("/employees", "update"),
        "can_delete_employees": checker.has_permission("/employees", "delete"),
        "is_admin": checker.has_role("ADMIN"),
        "is_manager": checker.has_role("MANAGER"),
    }
    
    return {
        "user": {
            "id": str(checker.current_user.id),
            "username": checker.current_user.username,
            "role": checker.current_user.role.code if checker.current_user.role else None
        },
        "all_permissions": permissions,
        "menu_permissions": menu_permissions,
        "common_checks": common_checks,
        "permission_summary": {
            "total_permissions": len(permissions),
            "total_menus": len(menu_permissions),
            "has_management_access": any(
                checker.has_permission(path, "view") 
                for path in ["/employees", "/roles", "/positions"]
            )
        }
    }


# ============================================================================
# 使用说明
# ============================================================================

if __name__ == "__main__":
    print("""
FastAPI 认证授权系统使用示例

这个文件展示了如何在实际项目中使用认证授权系统的各种功能：

1. 基础认证 - 只需要用户登录
2. 权限控制 - 检查特定菜单的特定权限
3. 角色控制 - 检查用户角色
4. 灵活权限检查 - 根据业务逻辑进行复杂权限检查
5. 可选认证 - 支持登录和未登录用户
6. 复合权限检查 - 多种权限检查的组合
7. 权限信息查询 - 获取用户的详细权限信息

要运行这些示例：

1. 启动 FastAPI 应用：
   python -m uvicorn example_usage:example_app --reload --port 8001

2. 访问 API 文档：
   http://localhost:8001/docs

3. 使用测试脚本：
   python test_auth_system.py

4. 或者手动测试：
   - 先调用 /api/auth/login 获取 token
   - 在请求头中添加 Authorization: Bearer <token>
   - 访问各种示例接口

注意：这些示例需要配合完整的 CRM 系统使用，确保数据库已初始化。
""")