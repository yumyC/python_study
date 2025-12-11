"""
岗位管理 API

提供岗位的 CRUD 操作和层级管理功能
"""

from flask import Blueprint, request, jsonify
from app.auth import require_permission
from app.models import Position
from app import db

positions_bp = Blueprint('positions', __name__)


@positions_bp.route('/positions', methods=['GET'])
@require_permission('/positions', 'view')
def get_positions(current_user):
    """获取岗位列表"""
    try:
        positions = Position.query.order_by(Position.level, Position.name).all()
        
        result = []
        for position in positions:
            result.append(position.to_dict())
        
        return jsonify({
            'positions': result
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_POSITIONS_ERROR',
                'message': f'获取岗位列表失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@positions_bp.route('/positions', methods=['POST'])
@require_permission('/positions', 'create')
def create_position(current_user):
    """创建岗位"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('code'):
            return jsonify({
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '岗位名称和编码不能为空',
                    'status_code': 400
                }
            }), 400
        
        # 检查编码是否已存在
        if Position.query.filter_by(code=data['code']).first():
            return jsonify({
                'error': {
                    'code': 'CODE_EXISTS',
                    'message': '岗位编码已存在',
                    'status_code': 400
                }
            }), 400
        
        position = Position(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            level=data.get('level', 1),
            parent_id=data.get('parent_id')
        )
        
        db.session.add(position)
        db.session.commit()
        
        return jsonify({
            'message': '岗位创建成功',
            'position': position.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'CREATE_POSITION_ERROR',
                'message': f'创建岗位失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@positions_bp.route('/positions/<position_id>', methods=['PUT'])
@require_permission('/positions', 'update')
def update_position(position_id, current_user):
    """更新岗位"""
    try:
        position = Position.query.filter_by(id=position_id).first()
        
        if not position:
            return jsonify({
                'error': {
                    'code': 'POSITION_NOT_FOUND',
                    'message': '岗位不存在',
                    'status_code': 404
                }
            }), 404
        
        data = request.get_json()
        
        if 'name' in data:
            position.name = data['name']
        if 'description' in data:
            position.description = data['description']
        if 'level' in data:
            position.level = data['level']
        if 'parent_id' in data:
            position.parent_id = data['parent_id']
        
        db.session.commit()
        
        return jsonify({
            'message': '岗位更新成功',
            'position': position.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_POSITION_ERROR',
                'message': f'更新岗位失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@positions_bp.route('/positions/<position_id>', methods=['DELETE'])
@require_permission('/positions', 'delete')
def delete_position(position_id, current_user):
    """删除岗位"""
    try:
        position = Position.query.filter_by(id=position_id).first()
        
        if not position:
            return jsonify({
                'error': {
                    'code': 'POSITION_NOT_FOUND',
                    'message': '岗位不存在',
                    'status_code': 404
                }
            }), 404
        
        # 检查是否有员工使用此岗位
        if position.employees.count() > 0:
            return jsonify({
                'error': {
                    'code': 'POSITION_IN_USE',
                    'message': '该岗位下还有员工，无法删除',
                    'status_code': 400
                }
            }), 400
        
        db.session.delete(position)
        db.session.commit()
        
        return jsonify({
            'message': '岗位删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'DELETE_POSITION_ERROR',
                'message': f'删除岗位失败: {str(e)}',
                'status_code': 500
            }
        }), 500