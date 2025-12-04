"""
Flask 授权控制示例

本示例演示如何使用 Flask-Principal 实现权限管理，包括：
- 基于角色的访问控制 (RBAC)
- 权限装饰器
- 动态权限检查
- 资源级别权限

依赖安装：
    pip install flask flask-login flask-principal passlib[bcrypt]

运行方式：
    python 02_authorization.py

访问地址：
    http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_principal import (
    Principal,
    Permission,
    RoleNeed,
    UserNeed,
    Identity,
    AnonymousIdentity,
    identity_changed,
    identity_loaded
)
from passlib.context import CryptContext
from functools import wraps
from enum import Enum
import os

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# 初始化扩展
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

principals = Principal(app)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟数据库
fake_users_db = {}
fake_articles_db = {}


# ==================== 角色和权限定义 ====================

class Role(str, Enum):
    """角色枚举"""
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"
    GUEST = "guest"


# 定义权限
admin_permission = Permission(RoleNeed(Role.ADMIN))
editor_permission = Permission(RoleNeed(Role.EDITOR))
user_permission = Permission(RoleNeed(Role.USER))


# ==================== 用户模型 ====================

class User(UserMixin):
    """用户模型"""
    
    def __init__(self, username, email, password_hash, role=Role.USER, full_name=None):
        self.id = username
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name
        }


# ==================== Flask-Login 回调 ====================

@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    if user_id in fake_users_db:
        user_data = fake_users_db[user_id]
        return User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            role=user_data['role'],
            full_name=user_data.get('full_name')
        )
    return None


# ==================== Flask-Principal 回调 ====================

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    """
    当身份加载时，添加用户的角色和权限
    
    Args:
        sender: 发送者
        identity: 身份对象
    """
    # 设置用户身份
    identity.user = current_user
    
    # 添加 UserNeed
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    
    # 添加 RoleNeed
    if hasattr(current_user, 'role'):
        identity.provides.add(RoleNeed(current_user.role))


# ==================== 辅助函数 ====================

def verify_password(plain_password: str, password_hash: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def get_user(username: str):
    """获取用户"""
    if username in fake_users_db:
        user_data = fake_users_db[username]
        return User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            role=user_data['role'],
            full_name=user_data.get('full_name')
        )
    return None


def authenticate_user(username: str, password: str):
    """认证用户"""
    user = get_user(username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


# ==================== 权限装饰器 ====================

def require_permission(permission):
    """
    权限检查装饰器
    
    Args:
        permission: 要求的权限
    
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not permission.can():
                return jsonify({
                    'error': '权限不足',
                    'required_permission': str(permission)
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role: Role):
    """
    角色检查装饰器
    
    Args:
        role: 要求的角色
    
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != role and current_user.role != Role.ADMIN:
                return jsonify({
                    'error': '权限不足',
                    'required_role': role
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== API 端点 ====================

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'Flask 授权控制示例',
        'roles': [role.value for role in Role],
        'test_users': {
            'admin': 'admin123 (管理员)',
            'editor': 'editor123 (编辑)',
            'user': 'user123 (普通用户)',
            'guest': 'guest123 (访客)'
        }
    })


@app.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    user = authenticate_user(data['username'], data['password'])
    
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 登录用户
    login_user(user)
    
    # 通知 Flask-Principal 身份变更
    identity_changed.send(app, identity=Identity(user.id))
    
    return jsonify({
        'message': '登录成功',
        'user': user.to_dict()
    })


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    
    # 通知 Flask-Principal 身份变更为匿名
    identity_changed.send(app, identity=AnonymousIdentity())
    
    return jsonify({'message': '登出成功'})


@app.route('/users/me')
@login_required
def get_current_user_info():
    """获取当前用户信息"""
    return jsonify({
        'user': current_user.to_dict()
    })


@app.route('/articles')
@login_required
def list_articles():
    """
    获取文章列表
    
    所有登录用户都可以访问
    """
    return jsonify({
        'articles': list(fake_articles_db.values()),
        'total': len(fake_articles_db)
    })


@app.route('/articles', methods=['POST'])
@require_role(Role.EDITOR)
def create_article():
    """
    创建文章
    
    需要 EDITOR 或 ADMIN 角色
    """
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': '缺少必填字段'}), 400
    
    article_id = len(fake_articles_db) + 1
    article = {
        'id': article_id,
        'title': data['title'],
        'content': data['content'],
        'author': current_user.username
    }
    
    fake_articles_db[article_id] = article
    
    return jsonify({
        'message': '文章创建成功',
        'article': article
    }), 201


@app.route('/articles/<int:article_id>', methods=['PUT'])
@require_role(Role.EDITOR)
def update_article(article_id):
    """
    更新文章
    
    需要 EDITOR 或 ADMIN 角色
    编辑只能更新自己的文章，管理员可以更新所有文章
    """
    if article_id not in fake_articles_db:
        return jsonify({'error': '文章不存在'}), 404
    
    article = fake_articles_db[article_id]
    
    # 资源级别权限检查
    if article['author'] != current_user.username and current_user.role != Role.ADMIN:
        return jsonify({'error': '您只能更新自己的文章'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        article['title'] = data['title']
    if 'content' in data:
        article['content'] = data['content']
    
    return jsonify({
        'message': '文章更新成功',
        'article': article
    })


@app.route('/articles/<int:article_id>', methods=['DELETE'])
@require_permission(admin_permission)
def delete_article(article_id):
    """
    删除文章
    
    仅管理员可以删除
    """
    if article_id not in fake_articles_db:
        return jsonify({'error': '文章不存在'}), 404
    
    deleted_article = fake_articles_db.pop(article_id)
    
    return jsonify({
        'message': '文章删除成功',
        'article': deleted_article
    })


@app.route('/admin/users')
@require_permission(admin_permission)
def list_users():
    """
    获取用户列表
    
    仅管理员可以访问
    """
    users = [
        {
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'full_name': user.get('full_name')
        }
        for user in fake_users_db.values()
    ]
    
    return jsonify({
        'users': users,
        'total': len(users)
    })


# ==================== 初始化测试数据 ====================

def init_test_data():
    """初始化测试数据"""
    # 创建测试用户
    test_users = [
        {'username': 'admin', 'password': 'admin123', 'role': Role.ADMIN, 'email': 'admin@example.com', 'full_name': '管理员'},
        {'username': 'editor', 'password': 'editor123', 'role': Role.EDITOR, 'email': 'editor@example.com', 'full_name': '编辑'},
        {'username': 'user', 'password': 'user123', 'role': Role.USER, 'email': 'user@example.com', 'full_name': '普通用户'},
        {'username': 'guest', 'password': 'guest123', 'role': Role.GUEST, 'email': 'guest@example.com', 'full_name': '访客'},
    ]
    
    for user_data in test_users:
        password = user_data.pop('password')
        fake_users_db[user_data['username']] = {
            **user_data,
            'password_hash': get_password_hash(password)
        }
    
    # 创建测试文章
    fake_articles_db[1] = {
        'id': 1,
        'title': 'Flask 入门',
        'content': 'Flask 是一个轻量级的 Python Web 框架',
        'author': 'editor'
    }


# ==================== 启动应用 ====================

if __name__ == '__main__':
    init_test_data()
    
    print("Flask 授权控制示例")
    print("\n测试用户：")
    print("  admin / admin123 (管理员 - 所有权限)")
    print("  editor / editor123 (编辑 - 可创建和编辑文章)")
    print("  user / user123 (普通用户 - 只读)")
    print("  guest / guest123 (访客 - 只读)")
    print("\n运行地址: http://127.0.0.1:5000")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
