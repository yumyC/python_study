"""
JWT Token 处理器

负责 JWT Token 的生成、验证和解析
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
import os
from uuid import UUID


class JWTHandler:
    """JWT Token 处理器"""
    
    def __init__(self):
        # JWT 配置
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # 密码加密上下文
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码到 token 中的数据
            
        Returns:
            JWT access token 字符串
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        
        # 确保 UUID 对象被转换为字符串
        for key, value in to_encode.items():
            if isinstance(value, UUID):
                to_encode[key] = str(value)
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        创建刷新令牌
        
        Args:
            data: 要编码到 token 中的数据
            
        Returns:
            JWT refresh token 字符串
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        
        # 确保 UUID 对象被转换为字符串
        for key, value in to_encode.items():
            if isinstance(value, UUID):
                to_encode[key] = str(value)
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        验证并解析 JWT token
        
        Args:
            token: JWT token 字符串
            token_type: token 类型 ('access' 或 'refresh')
            
        Returns:
            解析后的 payload 数据，验证失败返回 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查 token 类型
            if payload.get("type") != token_type:
                return None
            
            # 检查是否过期
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            # Token 已过期
            return None
        except jwt.JWTError:
            # Token 无效
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        从 token 中提取用户 ID
        
        Args:
            token: JWT token 字符串
            
        Returns:
            用户 ID 字符串，提取失败返回 None
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")  # subject 通常存储用户 ID
        return None
    
    def hash_password(self, password: str) -> str:
        """
        对密码进行哈希加密
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希后的密码
            
        Returns:
            密码是否匹配
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_token_expire_time(self, token_type: str = "access") -> int:
        """
        获取 token 过期时间（秒）
        
        Args:
            token_type: token 类型
            
        Returns:
            过期时间（秒）
        """
        if token_type == "access":
            return self.access_token_expire_minutes * 60
        elif token_type == "refresh":
            return self.refresh_token_expire_days * 24 * 60 * 60
        else:
            return 0


# 全局 JWT 处理器实例
jwt_handler = JWTHandler()