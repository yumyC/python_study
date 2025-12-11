"""
角色管理 API

提供角色的 CRUD 操作功能
"""

from flask import Blueprint, request, jsonify
from app.auth import require_permission
from app.models import Role
from app import db

roles_bp = Blueprint('roles', __name__)


@roles_bp.route('/roles', methods=['GET'])
@require_permission('/roles', 'view')
def get_roles(current_user):
    """获取角色列表"""
    try:
        roles = Role.query.order_by(Role.name).all()
        
        result = []
        for role in roles:
            result.append(role.to_dict())
        
        return jsonify({
            'roles': result
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_ROLES_ERROR',
                'message': f'获取角色列表失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@roles_bp.route('/roles', methods=['POST'])
@require_permission('/roles', 'create')
def create_role(current_user):
    """创建角色"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('code'):
            return jsonify({
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '角色名称和编码不能为空',
                    'status_code': 400
                }
            }), 400
        
        # 检查编码是否已存在
        if Role.query.filter_by(code=data['code']).first():
            return jsonify({
                'error': {
                    'code': 'CODE_EXISTS',
                    'message': '角色编码已存在',
                    'status_code': 400
                }
            }), 400
        
        role = Role(
            name=data['name'],
            code=data['code'],
            description=data.get('description')
        )
        
        db.session.add(role)
        db.session.commit()
        
        return jsonify({
            'message': '角色创建成功',
            'role': role.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'CREATE_ROLE_ERROR',
                'message': f'创建角色失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@roles_bp.route('/roles/<role_id>', methods=['PUT'])
@require_permission('/roles', 'update')
def update_role(role_id, current_user):
    """更新角色"""
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
        
        data = request.get_json()
        
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': '角色更新成功',
            'role': role.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_ROLE_ERROR',
                'message': f'更新角色失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@roles_bp.route('/roles/<role_id>', methods=['DELETE'])
@require_permission('/roles', 'delete')
def delete_role(role_id, current_user):
    """删除角色"""
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
        
        # 检查是否有员工使用此角色
        if role.employees.count() > 0:
            return jsonify({
                'error': {
                    'code': 'ROLE_IN_USE',
                    'message': '该角色下还有员工，无法删除',
                    'status_code': 400
                }
            }), 400
        
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({
            'message': '角色删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'DELETE_ROLE_ERROR',
                'message': f'删除角色失败: {str(e)}',
                'status_code': 500
            }
        }), 500