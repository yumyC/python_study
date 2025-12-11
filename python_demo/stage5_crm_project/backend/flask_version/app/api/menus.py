"""
菜单管理 API

提供菜单的 CRUD 操作和树形结构管理功能
"""

from flask import Blueprint, request, jsonify
from app.auth import require_permission
from app.models import Menu
from app import db

menus_bp = Blueprint('menus', __name__)


@menus_bp.route('/menus', methods=['GET'])
@require_permission('/menus', 'view')
def get_menus(current_user):
    """获取菜单树形结构"""
    try:
        # 获取根菜单（没有父菜单的菜单）
        root_menus = Menu.query.filter(Menu.parent_id.is_(None)).order_by(Menu.sort_order).all()
        
        result = []
        for menu in root_menus:
            menu_tree = menu.to_tree_dict(include_children=True)
            result.append(menu_tree)
        
        return jsonify({
            'menus': result
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_MENUS_ERROR',
                'message': f'获取菜单列表失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@menus_bp.route('/menus', methods=['POST'])
@require_permission('/menus', 'create')
def create_menu(current_user):
    """创建菜单"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('path'):
            return jsonify({
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '菜单名称和路径不能为空',
                    'status_code': 400
                }
            }), 400
        
        menu = Menu(
            name=data['name'],
            path=data['path'],
            icon=data.get('icon'),
            component=data.get('component'),
            parent_id=data.get('parent_id'),
            sort_order=data.get('sort_order', 0),
            is_visible=data.get('is_visible', True)
        )
        
        db.session.add(menu)
        db.session.commit()
        
        return jsonify({
            'message': '菜单创建成功',
            'menu': menu.to_tree_dict(include_children=False)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'CREATE_MENU_ERROR',
                'message': f'创建菜单失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@menus_bp.route('/menus/<menu_id>', methods=['PUT'])
@require_permission('/menus', 'update')
def update_menu(menu_id, current_user):
    """更新菜单"""
    try:
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
        
        if 'name' in data:
            menu.name = data['name']
        if 'path' in data:
            menu.path = data['path']
        if 'icon' in data:
            menu.icon = data['icon']
        if 'component' in data:
            menu.component = data['component']
        if 'parent_id' in data:
            menu.parent_id = data['parent_id']
        if 'sort_order' in data:
            menu.sort_order = data['sort_order']
        if 'is_visible' in data:
            menu.is_visible = data['is_visible']
        
        db.session.commit()
        
        return jsonify({
            'message': '菜单更新成功',
            'menu': menu.to_tree_dict(include_children=False)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'UPDATE_MENU_ERROR',
                'message': f'更新菜单失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@menus_bp.route('/menus/<menu_id>', methods=['DELETE'])
@require_permission('/menus', 'delete')
def delete_menu(menu_id, current_user):
    """删除菜单"""
    try:
        menu = Menu.query.filter_by(id=menu_id).first()
        
        if not menu:
            return jsonify({
                'error': {
                    'code': 'MENU_NOT_FOUND',
                    'message': '菜单不存在',
                    'status_code': 404
                }
            }), 404
        
        # 检查是否有子菜单
        if menu.children.count() > 0:
            return jsonify({
                'error': {
                    'code': 'MENU_HAS_CHILDREN',
                    'message': '该菜单下还有子菜单，无法删除',
                    'status_code': 400
                }
            }), 400
        
        db.session.delete(menu)
        db.session.commit()
        
        return jsonify({
            'message': '菜单删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'DELETE_MENU_ERROR',
                'message': f'删除菜单失败: {str(e)}',
                'status_code': 500
            }
        }), 500