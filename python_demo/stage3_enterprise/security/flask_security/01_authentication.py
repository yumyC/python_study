"""
Flask 基础认证示例

本示例演示如何使用 Flask-Login 实现用户认证系统，包括：
- 用户注册和登录
- 会话管理
- Remember Me 功能
- 登录保护装饰器

依赖安装：
    pip install flask flask-login passlib[bcrypt]

运行方式：
    python 01_authentication.py

访问地址：
    http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, session
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from passlib.context import CryptContext
from typing import Optional
import os

app = Flask(__name__)

# 配置（生产环境应从环境变量读取）
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-keep-it-secret')
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止 XSS 攻击
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 防止 CSRF 攻击
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 会话过期时间（秒）

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 未登录时重定向的端点
login_manager.login_message = '请先登录'

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟数据库
fake_users_db = {}


# ==================== 用户模型 ====================

class User(UserMixin):
    """
    用户模型
    
    继承 UserMixin 提供默认实现：
    - is_authenticated: 是否已认证
    - is_active: 是否活跃
    - is_anonymous: 是否匿名
    - get_id(): 获取用户 ID
    """
    
    def __init__(self, username, email, password_hash, full_name=None):
        self.id = username  # 使用 username 作为 ID
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self._is_active = True
    
    @property
    def is_active(self):
        """用户是否活跃"""
        return self._is_active
    
    def to_dict(self):
        """转换为字典"""
        return {
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active
        }


# ==================== Flask-Login 回调 ====================

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login 用户加载回调
    
    根据用户 ID 从数据库加载用户对象
    
    Args:
        user_id: 用户 ID（username）
    
    Returns:
        User: 用户对象，不存在则返回 None
    """
    if user_id in fake_users_db:
        user_data = fake_users_db[user_id]
        return User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            full_name=user_data.get('full_name')
        )
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """未授权访问处理"""
    return jsonify({
        'error': '未授权',
        'message': '请先登录'
    }), 401


# ==================== 辅助函数 ====================

def verify_password(plain_password: str, password_hash: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[User]:
    """获取用户"""
    if username in fake_users_db:
        user_data = fake_users_db[username]
        return User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            full_name=user_data.get('full_name')
        )
    return None


def authenticate_user(username: str, password: str) -> Optional[User]:
    """认证用户"""
    user = get_user(username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


# ==================== API 端点 ====================

@app.route('/')
def index():
    """首页"""
    if current_user.is_authenticated:
        return jsonify({
            'message': f'欢迎回来，{current_user.username}！',
            'user': current_user.to_dict()
        })
    return jsonify({
        'message': '欢迎使用 Flask 认证系统',
        'endpoints': {
            'register': 'POST /register',
            'login': 'POST /login',
            'logout': 'POST /logout',
            'me': 'GET /users/me (需要登录)',
            'profile': 'GET /profile (需要登录)'
        }
    })


@app.route('/register', methods=['POST'])
def register():
    """
    用户注册
    
    请求体：
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "full_name": "string" (可选)
        }
    
    Returns:
        JSON: 注册结果
    """
    data = request.get_json()
    
    # 验证必填字段
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({
            'error': '缺少必填字段',
            'required': ['username', 'email', 'password']
        }), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    full_name = data.get('full_name')
    
    # 验证用户名长度
    if len(username) < 3:
        return jsonify({'error': '用户名至少 3 个字符'}), 400
    
    # 验证密码长度
    if len(password) < 6:
        return jsonify({'error': '密码至少 6 个字符'}), 400
    
    # 检查用户名是否已存在
    if username in fake_users_db:
        return jsonify({'error': '用户名已存在'}), 400
    
    # 创建新用户
    password_hash = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name
    )
    
    # 保存到"数据库"
    fake_users_db[username] = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'full_name': full_name
    }
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201


@app.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体：
        {
            "username": "string",
            "password": "string",
            "remember": boolean (可选，默认 false)
        }
    
    Returns:
        JSON: 登录结果
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({
            'error': '缺少必填字段',
            'required': ['username', 'password']
        }), 400
    
    username = data['username']
    password = data['password']
    remember = data.get('remember', False)
    
    # 认证用户
    user = authenticate_user(username, password)
    
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 登录用户
    login_user(user, remember=remember)
    
    return jsonify({
        'message': '登录成功',
        'user': user.to_dict()
    })


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    用户登出
    
    需要登录
    
    Returns:
        JSON: 登出结果
    """
    username = current_user.username
    logout_user()
    
    return jsonify({
        'message': f'用户 {username} 已登出'
    })


@app.route('/users/me')
@login_required
def get_current_user_info():
    """
    获取当前用户信息
    
    需要登录
    
    Returns:
        JSON: 当前用户信息
    """
    return jsonify({
        'user': current_user.to_dict(),
        'session_info': {
            'is_authenticated': current_user.is_authenticated,
            'is_active': current_user.is_active,
            'is_anonymous': current_user.is_anonymous
        }
    })


@app.route('/profile')
@login_required
def profile():
    """
    用户个人资料页面
    
    需要登录
    
    Returns:
        JSON: 用户资料
    """
    return jsonify({
        'profile': current_user.to_dict(),
        'message': '这是受保护的个人资料页面'
    })


@app.route('/users/<username>')
@login_required
def get_user_info(username):
    """
    获取指定用户信息
    
    需要登录
    
    Args:
        username: 用户名
    
    Returns:
        JSON: 用户信息
    """
    user = get_user(username)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': user.to_dict()
    })


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({'error': '资源不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500


# ==================== 初始化测试数据 ====================

def init_test_data():
    """初始化测试数据"""
    test_user = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password_hash': get_password_hash('testpass123'),
        'full_name': '测试用户'
    }
    fake_users_db['testuser'] = test_user


# ==================== 启动应用 ====================

if __name__ == '__main__':
    # 初始化测试数据
    init_test_data()
    
    print("Flask 认证示例")
    print("\n测试用户：")
    print("  用户名: testuser")
    print("  密码: testpass123")
    print("\n使用说明：")
    print("  1. POST /register 注册新用户")
    print("  2. POST /login 登录（可选 remember=true 启用 Remember Me）")
    print("  3. GET /users/me 获取当前用户信息（需要登录）")
    print("  4. POST /logout 登出")
    print("\n运行地址: http://127.0.0.1:5000")
    
    # 启动应用
    app.run(debug=True, host='127.0.0.1', port=5000)
