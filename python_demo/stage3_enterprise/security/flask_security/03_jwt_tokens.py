"""
Flask JWT 令牌认证示例

本示例演示如何使用 Flask-JWT-Extended 实现 JWT 认证，包括：
- JWT 令牌生成和验证
- Access Token 和 Refresh Token
- 令牌刷新机制
- 令牌撤销（黑名单）

依赖安装：
    pip install flask flask-jwt-extended passlib[bcrypt]

运行方式：
    python 03_jwt_tokens.py

访问地址：
    http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from passlib.context import CryptContext
from datetime import timedelta
import os

app = Flask(__name__)

# JWT 配置
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

# 初始化 JWT
jwt = JWTManager(app)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟数据库
fake_users_db = {}

# 令牌黑名单（生产环境应使用 Redis）
token_blacklist = set()


# ==================== JWT 回调 ====================

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """
    检查令牌是否在黑名单中
    
    Args:
        jwt_header: JWT 头部
        jwt_payload: JWT 载荷
    
    Returns:
        bool: 令牌是否被撤销
    """
    jti = jwt_payload['jti']  # JWT ID
    return jti in token_blacklist


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """令牌过期回调"""
    return jsonify({
        'error': '令牌已过期',
        'message': '请使用 Refresh Token 刷新'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    """无效令牌回调"""
    return jsonify({
        'error': '无效的令牌',
        'message': str(error)
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    """缺少令牌回调"""
    return jsonify({
        'error': '缺少令牌',
        'message': '请提供有效的 JWT 令牌'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """令牌已撤销回调"""
    return jsonify({
        'error': '令牌已被撤销',
        'message': '请重新登录'
    }), 401


# ==================== 辅助函数 ====================

def verify_password(plain_password: str, password_hash: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def get_user(username: str):
    """获取用户"""
    return fake_users_db.get(username)


def authenticate_user(username: str, password: str):
    """认证用户"""
    user = get_user(username)
    if not user or not verify_password(password, user['password_hash']):
        return None
    return user


# ==================== API 端点 ====================

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'Flask JWT 认证示例',
        'endpoints': {
            'register': 'POST /register',
            'login': 'POST /login',
            'refresh': 'POST /token/refresh',
            'logout': 'POST /logout',
            'me': 'GET /users/me (需要 JWT)',
            'protected': 'GET /protected (需要 JWT)'
        },
        'test_user': {
            'username': 'testuser',
            'password': 'testpass123'
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
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    username = data['username']
    
    if username in fake_users_db:
        return jsonify({'error': '用户名已存在'}), 400
    
    # 创建新用户
    user = {
        'username': username,
        'email': data['email'],
        'password_hash': get_password_hash(data['password']),
        'full_name': data.get('full_name')
    }
    
    fake_users_db[username] = user
    
    return jsonify({
        'message': '注册成功',
        'user': {
            'username': user['username'],
            'email': user['email'],
            'full_name': user.get('full_name')
        }
    }), 201


@app.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体：
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        JSON: Access Token 和 Refresh Token
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    user = authenticate_user(data['username'], data['password'])
    
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 创建令牌
    access_token = create_access_token(identity=user['username'])
    refresh_token = create_refresh_token(identity=user['username'])
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    })


@app.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新 Access Token
    
    需要 Refresh Token
    
    Returns:
        JSON: 新的 Access Token
    """
    # 获取当前用户身份
    current_user = get_jwt_identity()
    
    # 创建新的 Access Token
    new_access_token = create_access_token(identity=current_user)
    
    return jsonify({
        'access_token': new_access_token,
        'token_type': 'bearer'
    })


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    用户登出
    
    将当前令牌加入黑名单
    
    需要 Access Token
    """
    jti = get_jwt()['jti']  # JWT ID
    token_blacklist.add(jti)
    
    return jsonify({
        'message': '登出成功'
    })


@app.route('/users/me')
@jwt_required()
def get_current_user():
    """
    获取当前用户信息
    
    需要 Access Token
    """
    current_user = get_jwt_identity()
    user = get_user(current_user)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': {
            'username': user['username'],
            'email': user['email'],
            'full_name': user.get('full_name')
        }
    })


@app.route('/protected')
@jwt_required()
def protected():
    """
    受保护的端点
    
    需要 Access Token
    """
    current_user = get_jwt_identity()
    jwt_data = get_jwt()
    
    return jsonify({
        'message': f'你好，{current_user}！',
        'jwt_info': {
            'user': current_user,
            'jti': jwt_data.get('jti'),
            'type': jwt_data.get('type'),
            'exp': jwt_data.get('exp')
        }
    })


@app.route('/items')
@jwt_required()
def get_items():
    """
    获取项目列表
    
    需要 Access Token
    """
    current_user = get_jwt_identity()
    
    items = [
        {'id': 1, 'name': 'Item 1', 'description': '第一个项目'},
        {'id': 2, 'name': 'Item 2', 'description': '第二个项目'},
    ]
    
    return jsonify({
        'items': items,
        'user': current_user
    })


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
    init_test_data()
    
    print("Flask JWT 认证示例")
    print("\n测试用户：")
    print("  用户名: testuser")
    print("  密码: testpass123")
    print("\n使用流程：")
    print("  1. POST /login 登录获取令牌")
    print("  2. 在请求头中添加: Authorization: Bearer <access_token>")
    print("  3. 访问受保护的端点")
    print("  4. Access Token 过期后使用 Refresh Token 刷新")
    print("  5. POST /logout 登出撤销令牌")
    print("\n运行地址: http://127.0.0.1:5000")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
