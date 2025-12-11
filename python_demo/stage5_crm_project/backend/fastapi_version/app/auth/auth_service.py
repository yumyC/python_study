"""
认证服务

提供用户认证、权限验证等业务逻辑
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import Employee, Role, Menu, RoleMenuPermission
from .jwt_handler import jwt_handler
from .schemas import LoginResponse, TokenData, UserInfo, RoleInfo, PositionInfo


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> Optional[Employee]:
        """
        验证用户凭据
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            验证成功返回 Employee 对象，失败返回 None
        """
        # 支持用户名或邮箱登录
        employee = self.db.query(Employee).filter(
            (Employee.username == username) | (Employee.email == username)
        ).first()
        
        if not employee:
            return None
        
        # 检查员工状态
        if not employee.is_active():
            return None
        
        # 验证密码
        if not jwt_handler.verify_password(password, employee.password_hash):
            return None
        
        return employee
    
    def login(self, username: str, password: str) -> LoginResponse:
        """
        用户登录
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            登录响应，包含用户信息和 tokens
            
        Raises:
            HTTPException: 登录失败时抛出异常
        """
        # 验证用户凭据
        employee = self.authenticate_user(username, password)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成 tokens
        token_data = {
            "sub": str(employee.id),  # subject: 用户 ID
            "username": employee.username,
            "email": employee.email,
            "role_id": str(employee.role_id) if employee.role_id else None,
        }
        
        access_token = jwt_handler.create_access_token(token_data)
        refresh_token = jwt_handler.create_refresh_token({"sub": str(employee.id)})
        
        # 构建响应
        user_info = self._build_user_info(employee)
        tokens = TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=jwt_handler.get_token_expire_time("access")
        )
        
        return LoginResponse(user=user_info, tokens=tokens)
    
    def refresh_token(self, refresh_token: str) -> TokenData:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的 token 数据
            
        Raises:
            HTTPException: 刷新失败时抛出异常
        """
        # 验证刷新令牌
        payload = jwt_handler.verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 获取用户信息
        user_id = payload.get("sub")
        employee = self.db.query(Employee).filter(Employee.id == user_id).first()
        if not employee or not employee.is_active():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成新的 tokens
        token_data = {
            "sub": str(employee.id),
            "username": employee.username,
            "email": employee.email,
            "role_id": str(employee.role_id) if employee.role_id else None,
        }
        
        new_access_token = jwt_handler.create_access_token(token_data)
        new_refresh_token = jwt_handler.create_refresh_token({"sub": str(employee.id)})
        
        return TokenData(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=jwt_handler.get_token_expire_time("access")
        )
    
    def get_current_user(self, token: str) -> Employee:
        """
        根据 token 获取当前用户
        
        Args:
            token: 访问令牌
            
        Returns:
            当前用户的 Employee 对象
            
        Raises:
            HTTPException: token 无效或用户不存在时抛出异常
        """
        # 验证 token
        payload = jwt_handler.verify_token(token, "access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 获取用户 ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌中缺少用户信息",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 查询用户
        employee = self.db.query(Employee).filter(Employee.id == user_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if not employee.is_active():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return employee
    
    def get_user_permissions(self, employee: Employee) -> List[str]:
        """
        获取用户权限列表
        
        Args:
            employee: 员工对象
            
        Returns:
            权限字符串列表，格式为 "menu_path:permission"
        """
        if not employee.role:
            return []
        
        permissions = []
        
        # 查询角色的菜单权限
        role_permissions = self.db.query(RoleMenuPermission).filter(
            RoleMenuPermission.role_id == employee.role_id
        ).all()
        
        for rmp in role_permissions:
            if rmp.menu and rmp.permissions:
                menu_path = rmp.menu.path
                for perm in rmp.permissions:
                    permissions.append(f"{menu_path}:{perm}")
        
        return permissions
    
    def check_permission(self, employee: Employee, menu_path: str, required_permission: str) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            employee: 员工对象
            menu_path: 菜单路径
            required_permission: 所需权限 ('view', 'create', 'update', 'delete')
            
        Returns:
            是否有权限
        """
        if not employee.role:
            return False
        
        # 查询角色对该菜单的权限
        role_permission = self.db.query(RoleMenuPermission).join(Menu).filter(
            RoleMenuPermission.role_id == employee.role_id,
            Menu.path == menu_path
        ).first()
        
        if not role_permission or not role_permission.permissions:
            return False
        
        return required_permission in role_permission.permissions
    
    def get_user_menu_permissions(self, employee: Employee) -> List[Dict[str, Any]]:
        """
        获取用户的菜单权限列表
        
        Args:
            employee: 员工对象
            
        Returns:
            菜单权限列表
        """
        if not employee.role:
            return []
        
        # 查询角色的所有菜单权限
        role_permissions = self.db.query(RoleMenuPermission).join(Menu).filter(
            RoleMenuPermission.role_id == employee.role_id,
            Menu.is_visible == True
        ).order_by(Menu.sort_order).all()
        
        menu_permissions = []
        for rmp in role_permissions:
            if rmp.menu:
                menu_permissions.append({
                    "menu_id": str(rmp.menu.id),
                    "menu_name": rmp.menu.name,
                    "menu_path": rmp.menu.path,
                    "menu_icon": rmp.menu.icon,
                    "parent_id": str(rmp.menu.parent_id) if rmp.menu.parent_id else None,
                    "permissions": rmp.permissions or []
                })
        
        return menu_permissions
    
    def _build_user_info(self, employee: Employee) -> UserInfo:
        """
        构建用户信息对象
        
        Args:
            employee: 员工对象
            
        Returns:
            用户信息对象
        """
        # 构建角色信息
        role_info = None
        if employee.role:
            role_info = RoleInfo(
                id=str(employee.role.id),
                name=employee.role.name,
                code=employee.role.code,
                description=employee.role.description
            )
        
        # 构建岗位信息
        position_info = None
        if employee.position:
            position_info = PositionInfo(
                id=str(employee.position.id),
                name=employee.position.name,
                code=employee.position.code,
                description=employee.position.description,
                level=employee.position.level
            )
        
        # 获取用户权限
        permissions = self.get_user_permissions(employee)
        
        return UserInfo(
            id=str(employee.id),
            username=employee.username,
            email=employee.email,
            full_name=employee.full_name,
            role=role_info,
            position=position_info,
            permissions=permissions,
            status=employee.status.value,
            created_at=employee.created_at
        )