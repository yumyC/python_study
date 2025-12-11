"""
认证 API

提供用户登录、注册、令牌刷新等认证相关的接口
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app.auth import AuthService, require_auth
from app.models import Employee
from app import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体:
        {
            "username": "用户名",
            "password": "密码"
        }
    
    响应:
        {
            "access_token": "访问令牌",
            "refresh_token": "刷新令牌",
            "token_type": "Bearer",
            "user": {用户信息}
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求体不能为空',
                    'status_code': 400
                }
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'error': {
                    'code': 'MISSING_CREDENTIALS',
                    'message': '用户名和密码不能为空',
                    'status_code': 400
                }
            }), 400
        
        # 验证用户凭据
        user = AuthService.authenticate_user(username, password)
        
        if not user:
            return jsonify({
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': '用户名或密码错误',
                    'status_code': 401
                }
            }), 401
        
        # 创建令牌
        tokens = AuthService.create_tokens(user)
        
        # 获取用户信息
        user_info = AuthService.get_user_info(user)
        
        return jsonify({
            **tokens,
            'user': user_info
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'LOGIN_ERROR',
                'message': f'登录失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新访问令牌
    
    需要在请求头中包含有效的刷新令牌
    
    响应:
        {
            "access_token": "新的访问令牌",
            "token_type": "Bearer"
        }
    """
    try:
        identity = get_jwt_identity()
        
        if not identity or not isinstance(identity, dict):
            return jsonify({
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': '无效的刷新令牌',
                    'status_code': 401
                }
            }), 401
        
        # 验证用户是否仍然存在且活跃
        user_id = identity.get('user_id')
        user = Employee.query.filter_by(id=user_id).first()
        
        if not user or not user.is_active():
            return jsonify({
                'error': {
                    'code': 'USER_INACTIVE',
                    'message': '用户不存在或已被禁用',
                    'status_code': 401
                }
            }), 401
        
        # 创建新的访问令牌
        access_token = create_access_token(identity=identity)
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer'
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'REFRESH_ERROR',
                'message': f'令牌刷新失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@auth_bp.route('/auth/me', methods=['GET'])
@require_auth
def get_current_user(current_user):
    """
    获取当前用户信息
    
    需要在请求头中包含有效的访问令牌
    
    响应:
        {
            "user": {用户信息}
        }
    """
    try:
        user_info = AuthService.get_user_info(current_user)
        
        return jsonify({
            'user': user_info
        })
        
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'GET_USER_ERROR',
                'message': f'获取用户信息失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@auth_bp.route('/auth/change-password', methods=['POST'])
@require_auth
def change_password(current_user):
    """
    修改密码
    
    请求体:
        {
            "old_password": "旧密码",
            "new_password": "新密码"
        }
    
    响应:
        {
            "message": "密码修改成功"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求体不能为空',
                    'status_code': 400
                }
            }), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'error': {
                    'code': 'MISSING_PASSWORDS',
                    'message': '旧密码和新密码不能为空',
                    'status_code': 400
                }
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'error': {
                    'code': 'WEAK_PASSWORD',
                    'message': '新密码长度不能少于6位',
                    'status_code': 400
                }
            }), 400
        
        # 修改密码
        AuthService.change_password(current_user, old_password, new_password)
        
        return jsonify({
            'message': '密码修改成功'
        })
        
    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'INVALID_OLD_PASSWORD',
                'message': str(e),
                'status_code': 400
            }
        }), 400
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'CHANGE_PASSWORD_ERROR',
                'message': f'密码修改失败: {str(e)}',
                'status_code': 500
            }
        }), 500


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    用户注册（仅用于演示，生产环境应该由管理员创建用户）
    
    请求体:
        {
            "username": "用户名",
            "email": "邮箱",
            "password": "密码",
            "full_name": "姓名"
        }
    
    响应:
        {
            "message": "注册成功",
            "user": {用户信息}
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求体不能为空',
                    'status_code': 400
                }
            }), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        # 验证必填字段
        if not all([username, email, password, full_name]):
            return jsonify({
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '用户名、邮箱、密码和姓名不能为空',
                    'status_code': 400
                }
            }), 400
        
        # 验证密码强度
        if len(password) < 6:
            return jsonify({
                'error': {
                    'code': 'WEAK_PASSWORD',
                    'message': '密码长度不能少于6位',
                    'status_code': 400
                }
            }), 400
        
        # 创建用户
        user = AuthService.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        # 获取用户信息
        user_info = AuthService.get_user_info(user)
        
        return jsonify({
            'message': '注册成功',
            'user': user_info
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': {
                'code': 'REGISTRATION_ERROR',
                'message': str(e),
                'status_code': 400
            }
        }), 400
    except Exception as e:
        return jsonify({
            'error': {
                'code': 'REGISTRATION_ERROR',
                'message': f'注册失败: {str(e)}',
                'status_code': 500
            }
        }), 500