"""
Flask 会话管理示例

本示例演示 Flask 会话管理的高级用法，包括：
- Flask Session 配置
- Redis 会话存储
- 会话安全设置
- 会话生命周期管理

依赖安装：
    pip install flask flask-session redis passlib[bcrypt]

注意：需要运行 Redis 服务器
    docker run -d -p 6379:6379 redis

运行方式：
    python 04_session_management.py

访问地址：
    http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, session
from flask_session import Session
from passlib.context import CryptContext
from datetime import timedelta
import os
import redis

app = Flask(__name__)

# 会话配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# 使用 Redis 存储会话（生产环境推荐）
# 如果 Redis 不可用，会自动降级到文件系统存储
try:
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis.from_url(
        os.getenv('REDIS_URL', 'redis://localhost:6379')
    )
    print("✓ 使用 Redis 存储会话")
except Exception as e:
    print(f"⚠ Redis 连接失败，使用文件系统存储: {e}")
    app.config['SESSION_TYPE'] = 'filesystem'

# 会话安全配置
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止 JavaScript 访问 Cookie
app.config['SESSION_COOKIE_SECURE'] = False   # 生产环境应设为 True（需要 HTTPS）
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 防止 CSRF 攻击
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 会话过期时间

# 初始化 Session
Session(app)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟数据库
fake_users_db = {}


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


def login_required(f):
    """登录检查装饰器"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'error': '未授权',
                'message': '请先登录'
            }), 401
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== API 端点 ====================

@app.route('/')
def index():
    """首页"""
    if 'user_id' in session:
        user = get_user(session['user_id'])
        return jsonify({
            'message': f'欢迎回来，{user["username"]}！',
            'session_info': {
                'user_id': session['user_id'],
                'login_time': session.get('login_time'),
                'permanent': session.permanent
            }
        })
    
    return jsonify({
        'message': 'Flask 会话管理示例',
        'endpoints': {
            'register': 'POST /register',
            'login': 'POST /login',
            'logout': 'POST /logout',
            'me': 'GET /users/me (需要登录)',
            'session_info': 'GET /session/info'
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
            "password": "string",
            "remember": boolean (可选，默认 false)
        }
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '缺少必填字段'}), 400
    
    user = authenticate_user(data['username'], data['password'])
    
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 设置会话
    session.clear()  # 清除旧会话
    session['user_id'] = user['username']
    session['login_time'] = str(timedelta(seconds=0))
    
    # 设置会话是否持久化（Remember Me）
    remember = data.get('remember', False)
    session.permanent = remember
    
    return jsonify({
        'message': '登录成功',
        'user': {
            'username': user['username'],
            'email': user['email'],
            'full_name': user.get('full_name')
        },
        'session': {
            'permanent': session.permanent,
            'expires_in': str(app.config['PERMANENT_SESSION_LIFETIME']) if remember else '浏览器关闭时'
        }
    })


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    用户登出
    
    清除会话
    """
    username = session.get('user_id')
    session.clear()
    
    return jsonify({
        'message': f'用户 {username} 已登出'
    })


@app.route('/users/me')
@login_required
def get_current_user():
    """
    获取当前用户信息
    
    需要登录
    """
    user_id = session['user_id']
    user = get_user(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'user': {
            'username': user['username'],
            'email': user['email'],
            'full_name': user.get('full_name')
        },
        'session': {
            'user_id': session['user_id'],
            'login_time': session.get('login_time'),
            'permanent': session.permanent
        }
    })


@app.route('/session/info')
def session_info():
    """
    获取会话信息
    
    用于调试和了解会话状态
    """
    if 'user_id' not in session:
        return jsonify({
            'authenticated': False,
            'message': '未登录'
        })
    
    return jsonify({
        'authenticated': True,
        'session_data': {
            'user_id': session.get('user_id'),
            'login_time': session.get('login_time'),
            'permanent': session.permanent
        },
        'session_config': {
            'cookie_name': app.config['SESSION_COOKIE_NAME'],
            'httponly': app.config['SESSION_COOKIE_HTTPONLY'],
            'secure': app.config['SESSION_COOKIE_SECURE'],
            'samesite': app.config['SESSION_COOKIE_SAMESITE'],
            'lifetime': str(app.config['PERMANENT_SESSION_LIFETIME'])
        }
    })


@app.route('/session/update', methods=['POST'])
@login_required
def update_session():
    """
    更新会话数据
    
    演示如何在会话中存储自定义数据
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '缺少数据'}), 400
    
    # 在会话中存储自定义数据
    for key, value in data.items():
        if key not in ['user_id', 'login_time']:  # 保护关键字段
            session[key] = value
    
    return jsonify({
        'message': '会话数据已更新',
        'session_data': dict(session)
    })


@app.route('/protected')
@login_required
def protected():
    """
    受保护的端点
    
    需要登录
    """
    user_id = session['user_id']
    
    return jsonify({
        'message': f'你好，{user_id}！',
        'data': '这是受保护的数据'
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
    
    print("Flask 会话管理示例")
    print("\n测试用户：")
    print("  用户名: testuser")
    print("  密码: testpass123")
    print("\n会话配置：")
    print(f"  存储类型: {app.config['SESSION_TYPE']}")
    print(f"  Cookie 名称: {app.config['SESSION_COOKIE_NAME']}")
    print(f"  HttpOnly: {app.config['SESSION_COOKIE_HTTPONLY']}")
    print(f"  SameSite: {app.config['SESSION_COOKIE_SAMESITE']}")
    print(f"  过期时间: {app.config['PERMANENT_SESSION_LIFETIME']}")
    print("\n使用说明：")
    print("  1. POST /login 登录（可选 remember=true 启用持久会话）")
    print("  2. 访问受保护的端点（会话自动管理）")
    print("  3. GET /session/info 查看会话信息")
    print("  4. POST /logout 登出清除会话")
    print("\n运行地址: http://127.0.0.1:5000")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
