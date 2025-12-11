"""
权限管理 API

提供角色菜单权限的管理功能
"""

from flask import Blueprint, request, jsonify
from app.auth import require_permission
from app.models import Role, Menu, RoleMenuPermission
from app import db

permissions_bp = Blueprint('permissions', __name__)


@permissions_bp.route('/permissions/roles/<role_id>', methods=['GET'])
@require_permission('/permissions', 'view')
def get_role_permissions(role_id, current_user):
    """获取角色的所有权限"""
    try:
        role = Role.query.filter_by(id=role_id).first()
        
        if not role:
            return jsonify({
                'error': {
                    'code': 'ROLE_NOT_FOUND',
                    'message': '角色不存在',
                    'status_code': 404
                }
            }), 404
        
        permissions = []
        for permission in role.menu_permissions:
            permission_data = {
                'id': str(permission.id),
                'menu_id': str(permission.menu_id),
                'menu_name': permission.menu.name if permission.menu else None,
                'menu_path': permission.menu.path if permission.menu else None,
                'permissions': permission.permissions or []
            }
            permissions.append(permission_data)
        
        return jsonify({
            'role': role.to_dict(),
            'permissions': permissions
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_PERMISSIONS_ERROR',
                'message': f'获取权限失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@permissions_bp.route('/permissions/roles/<role_id>/menus/<menu_id>', methods=['POST'])
@require_permission('/permissions', 'create')
def assign_menu_permission(role_id, menu_id, current_user):
    """为角色分配菜单权限"""
    try:
        role = Role.query.filter_by(id=role_id).first()
        if not role:
            return jsonify({
                'error': {
                    'code': 'ROLE_NOT_FOUND',
                    'message': '角色不存在',
                    'status_code': 404
                }
            }), 404
        
        menu = Menu.query.filter_by(id=menu_id).first()
        if not menu:
            return jsonify({
                'error': {
                    'code': 'MENU_NOT_FOUND',
                    'message': '菜单不存在',
                    'status_code': 404
                }
            }), 404
        
        data = request.get_json()
        permissions = data.get('permissions', [])
        
        # 验证权限类型
        valid_permissions = {'view', 'create', 'update', 'delete'}
        invalid_permissions = set(permissions) - valid_permissions
        if invalid_permissions:
            return jsonify({
                'error': {
                    'code': 'INVALID_PERMISSIONS',
                    'message': f'无效的权限类型: {list(invalid_permissions)}',
                    'status_code': 400
                }
            }), 400
        
        # 检查是否已存在权限记录
        existing = RoleMenuPermission.query.filter_by(
            role_id=role_id,
            menu_id=menu_id
        ).first()
        
        if existing:
            existing.permissions = permissions
        else:
            permission = RoleMenuPermission(
                role_id=role_id,
                menu_id=menu_id,
                permissions=permissions
            )
            db.session.add(permission)
        
        db.session.commit()
        
        return jsonify({
            'message': '权限分配成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'ASSIGN_PERMISSION_ERROR',
                'message': f'分配权限失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@permissions_bp.route('/permissions/roles/<role_id>/menus/<menu_id>', methods=['DELETE'])
@require_permission('/permissions', 'delete')
def remove_menu_permission(role_id, menu_id, current_user):
    """移除角色的菜单权限"""
    try:
        permission = RoleMenuPermission.query.filter_by(
            role_id=role_id,
            menu_id=menu_id
        ).first()
        
        if not permission:
            return jsonify({
                'error': {
                    'code': 'PERMISSION_NOT_FOUND',
                    'message': '权限记录不存在',
                    'status_code': 404
                }
            }), 404
        
        db.session.delete(permission)
        db.session.commit()
        
        return jsonify({
            'message': '权限移除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'REMOVE_PERMISSION_ERROR',
                'message': f'移除权限失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@permissions_bp.route('/permissions/available', methods=['GET'])
@require_permission('/permissions', 'view')
def get_available_permissions(current_user):
    """获取所有可用的权限类型"""
    try:
        return jsonify({
            'permission_types': RoleMenuPermission.get_all_permission_types(),
            'permission_descriptions': RoleMenuPermission.get_permission_descriptions()
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_AVAILABLE_PERMISSIONS_ERROR',
                'message': f'获取可用权限失败: {str(e)}',
                'status_code': 500
            }
        }), 500