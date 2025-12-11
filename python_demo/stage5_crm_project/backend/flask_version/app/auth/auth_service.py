"""
认证服务

提供用户认证相关的业务逻辑
"""

from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import Employee
from app import db


class AuthService:
    """认证服务类"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Employee or None: 验证成功返回用户对象，失败返回 None
        """
        user = Employee.query.filter_by(username=username).first()
        
        if user and user.is_active() and user.check_password(password):
            return user
        
        return None
    
    @staticmethod
    def create_tokens(user):
        """
        为用户创建访问令牌和刷新令牌
        
        Args:
            user: 用户对象
            
        Returns:
            dict: 包含访问令牌和刷新令牌的字典
        """
        # 创建令牌的身份信息
        identity = {
            'user_id': str(user.id),
            'username': user.username,
            'role_id': str(user.role_id) if user.role_id else None
        }
        
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }
    
    @staticmethod
    def get_user_info(user):
        """
        获取用户信息
        
        Args:
            user: 用户对象
            
        Returns:
            dict: 用户信息字典
        """
        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'status': user.status.value,
            'position': {
                'id': str(user.position.id),
                'name': user.position.name,
                'code': user.position.code
            } if user.position else None,
            'role': {
                'id': str(user.role.id),
                'name': user.role.name,
                'code': user.role.code
            } if user.role else None,
            'permissions': user.get_permissions(),
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
    
    @staticmethod
    def create_user(username, email, password, full_name, position_id=None, role_id=None):
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            full_name: 姓名
            position_id: 岗位ID
            role_id: 角色ID
            
        Returns:
            Employee: 创建的用户对象
            
        Raises:
            ValueError: 如果用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        if Employee.query.filter_by(username=username).first():
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        if Employee.query.filter_by(email=email).first():
            raise ValueError("邮箱已存在")
        
        # 创建新用户
        user = Employee(
            username=username,
            email=email,
            full_name=full_name,
            position_id=position_id,
            role_id=role_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        修改用户密码
        
        Args:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            bool: 修改成功返回 True
            
        Raises:
            ValueError: 如果旧密码不正确
        """
        if not user.check_password(old_password):
            raise ValueError("旧密码不正确")
        
        user.set_password(new_password)
        db.session.commit()
        
        return True
    
    @staticmethod
    def reset_password(user, new_password):
        """
        重置用户密码（管理员操作）
        
        Args:
            user: 用户对象
            new_password: 新密码
            
        Returns:
            bool: 重置成功返回 True
        """
        user.set_password(new_password)
        db.session.commit()
        
        return True