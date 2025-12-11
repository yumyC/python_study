"""
JWT 处理器

处理 JWT 令牌的创建、验证和解析
"""

from flask_jwt_extended import get_jwt_identity, get_jwt
from app.models import Employee


class JWTHandler:
    """JWT 处理器类"""
    
    @staticmethod
    def get_current_user():
        """
        从 JWT 令牌中获取当前用户
        
        Returns:
            Employee or None: 当前用户对象，如果未找到返回 None
        """
        try:
            identity = get_jwt_identity()
            if not identity or not isinstance(identity, dict):
                return None
            
            user_id = identity.get('user_id')
            if not user_id:
                return None
            
            user = Employee.query.filter_by(id=user_id).first()
            
            # 检查用户是否仍然活跃
            if user and user.is_active():
                return user
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_current_user_id():
        """
        从 JWT 令牌中获取当前用户ID
        
        Returns:
            str or None: 用户ID，如果未找到返回 None
        """
        try:
            identity = get_jwt_identity()
            if not identity or not isinstance(identity, dict):
                return None
            
            return identity.get('user_id')
        except Exception:
            return None
    
    @staticmethod
    def get_current_username():
        """
        从 JWT 令牌中获取当前用户名
        
        Returns:
            str or None: 用户名，如果未找到返回 None
        """
        try:
            identity = get_jwt_identity()
            if not identity or not isinstance(identity, dict):
                return None
            
            return identity.get('username')
        except Exception:
            return None
    
    @staticmethod
    def get_current_role_id():
        """
        从 JWT 令牌中获取当前用户的角色ID
        
        Returns:
            str or None: 角色ID，如果未找到返回 None
        """
        try:
            identity = get_jwt_identity()
            if not identity or not isinstance(identity, dict):
                return None
            
            return identity.get('role_id')
        except Exception:
            return None
    
    @staticmethod
    def get_jwt_claims():
        """
        获取 JWT 令牌中的自定义声明
        
        Returns:
            dict: JWT 声明字典
        """
        try:
            return get_jwt()
        except Exception:
            return {}
    
    @staticmethod
    def validate_token_user(required_user_id=None):
        """
        验证令牌中的用户是否有效
        
        Args:
            required_user_id: 要求的用户ID（可选）
            
        Returns:
            bool: 验证成功返回 True
        """
        current_user = JWTHandler.get_current_user()
        
        if not current_user:
            return False
        
        if required_user_id and str(current_user.id) != str(required_user_id):
            return False
        
        return True