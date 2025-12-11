"""
认证装饰器

提供认证和权限控制的装饰器
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .jwt_handler import JWTHandler


def require_auth(f):
    """
    要求用户认证的装饰器
    
    Args:
        f: 被装饰的函数
        
    Returns:
        function: 装饰后的函数
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = JWTHandler.get_current_user()
        
        if not current_user:
            return jsonify({
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': '用户不存在或已被禁用',
                    'status_code': 401
                }
            }), 401
        
        # 将当前用户添加到函数参数中
        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    
    return decorated_function


def require_permission(menu_path, permission_type):
    """
    要求特定权限的装饰器
    
    Args:
        menu_path: 菜单路径
        permission_type: 权限类型 ('view', 'create', 'update', 'delete')
        
    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = JWTHandler.get_current_user()
            
            if not current_user:
                return jsonify({
                    'error': {
                        'code': 'USER_NOT_FOUND',
                        'message': '用户不存在或已被禁用',
                        'status_code': 401
                    }
                }), 401
            
            # 检查权限
            if not current_user.has_permission(menu_path, permission_type):
                return jsonify({
                    'error': {
                        'code': 'PERMISSION_DENIED',
                        'message': f'没有权限访问 {menu_path} 的 {permission_type} 操作',
                        'status_code': 403
                    }
                }), 403
            
            # 将当前用户添加到函数参数中
            kwargs['current_user'] = current_user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_role(role_code):
    """
    要求特定角色的装饰器
    
    Args:
        role_code: 角色编码
        
    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = JWTHandler.get_current_user()
            
            if not current_user:
                return jsonify({
                    'error': {
                        'code': 'USER_NOT_FOUND',
                        'message': '用户不存在或已被禁用',
                        'status_code': 401
                    }
                }), 401
            
            # 检查角色
            if not current_user.role or current_user.role.code != role_code:
                return jsonify({
                    'error': {
                        'code': 'ROLE_REQUIRED',
                        'message': f'需要 {role_code} 角色权限',
                        'status_code': 403
                    }
                }), 403
            
            # 将当前用户添加到函数参数中
            kwargs['current_user'] = current_user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_self_or_permission(menu_path, permission_type):
    """
    要求是本人操作或有特定权限的装饰器
    
    Args:
        menu_path: 菜单路径
        permission_type: 权限类型
        
    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = JWTHandler.get_current_user()
            
            if not current_user:
                return jsonify({
                    'error': {
                        'code': 'USER_NOT_FOUND',
                        'message': '用户不存在或已被禁用',
                        'status_code': 401
                    }
                }), 401
            
            # 获取目标用户ID（从路径参数或请求参数中）
            target_user_id = kwargs.get('user_id') or kwargs.get('employee_id')
            
            # 如果是本人操作，允许访问
            if target_user_id and str(current_user.id) == str(target_user_id):
                kwargs['current_user'] = current_user
                return f(*args, **kwargs)
            
            # 否则检查权限
            if not current_user.has_permission(menu_path, permission_type):
                return jsonify({
                    'error': {
                        'code': 'PERMISSION_DENIED',
                        'message': f'没有权限访问 {menu_path} 的 {permission_type} 操作',
                        'status_code': 403
                    }
                }), 403
            
            kwargs['current_user'] = current_user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator