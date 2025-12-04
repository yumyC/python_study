"""
Flask 数据库集成示例

演示如何在 Flask 中集成数据库，使用 Flask-SQLAlchemy 扩展。

学习要点:
1. 配置数据库连接
2. 创建数据库会话
3. 应用上下文管理
4. 基本的数据库操作

安装依赖:
    pip install flask-sqlalchemy

运行方式:
    python 04_database_integration.py
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# 创建 Flask 应用
app = Flask(__name__)

# ============ 数据库配置 ============

# 数据库 URI 配置
# SQLite 数据库（用于开发和学习）
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "app.db")}'

# 其他数据库示例:
# MySQL: 'mysql+pymysql://username:password@localhost/dbname'
# PostgreSQL: 'postgresql://username:password@localhost/dbname'

# 关闭 SQLAlchemy 的事件系统（节省资源）
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 显示 SQL 语句（调试用）
app.config['SQLALCHEMY_ECHO'] = True

# 创建 SQLAlchemy 实例
db = SQLAlchemy(app)


# ============ 定义简单模型 ============

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


# ============ 数据库初始化 ============

def init_db():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功！")
        
        # 检查是否已有数据
        if User.query.count() == 0:
            # 添加示例数据
            users = [
                User(username='张三', email='zhangsan@example.com'),
                User(username='李四', email='lisi@example.com'),
                User(username='王五', email='wangwu@example.com'),
            ]
            db.session.add_all(users)
            db.session.commit()
            print("示例数据添加成功！")


# ============ 路由和视图 ============

@app.route('/')
def index():
    """首页"""
    return '''
    <h1>Flask 数据库集成示例</h1>
    <h2>API 端点：</h2>
    <ul>
        <li><a href="/users">GET /users</a> - 获取所有用户</li>
        <li>POST /users - 创建用户（需要 JSON 数据）</li>
        <li>GET /users/&lt;id&gt; - 获取单个用户</li>
        <li>PUT /users/&lt;id&gt; - 更新用户（需要 JSON 数据）</li>
        <li>DELETE /users/&lt;id&gt; - 删除用户</li>
        <li><a href="/db-info">GET /db-info</a> - 数据库信息</li>
    </ul>
    
    <h2>测试命令：</h2>
    <pre>
# 获取所有用户
curl http://127.0.0.1:5000/users

# 创建用户
curl -X POST http://127.0.0.1:5000/users \\
  -H "Content-Type: application/json" \\
  -d '{"username":"赵六","email":"zhaoliu@example.com"}'

# 获取单个用户
curl http://127.0.0.1:5000/users/1

# 更新用户
curl -X PUT http://127.0.0.1:5000/users/1 \\
  -H "Content-Type: application/json" \\
  -d '{"email":"newemail@example.com"}'

# 删除用户
curl -X DELETE http://127.0.0.1:5000/users/1
    </pre>
    '''


@app.route('/users', methods=['GET'])
def get_users():
    """
    获取所有用户
    
    查询参数:
        page: 页码（默认1）
        per_page: 每页数量（默认10）
    """
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 查询所有用户（带分页）
    pagination = User.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    users = [user.to_dict() for user in pagination.items]
    
    return jsonify({
        'users': users,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@app.route('/users', methods=['POST'])
def create_user():
    """
    创建用户
    
    请求体:
        {
            "username": "用户名",
            "email": "邮箱"
        }
    """
    data = request.get_json()
    
    # 验证数据
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': '缺少必要字段'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 创建用户
    user = User(
        username=data['username'],
        email=data['email']
    )
    
    # 添加到数据库
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    更新用户
    
    请求体:
        {
            "username": "新用户名（可选）",
            "email": "新邮箱（可选）"
        }
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '没有提供数据'}), 400
    
    # 更新用户名
    if 'username' in data:
        # 检查新用户名是否已被其他用户使用
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': '用户名已存在'}), 400
        user.username = data['username']
    
    # 更新邮箱
    if 'email' in data:
        # 检查新邮箱是否已被其他用户使用
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': '邮箱已存在'}), 400
        user.email = data['email']
    
    # 提交更改
    db.session.commit()
    
    return jsonify(user.to_dict())


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户已删除'}), 200


@app.route('/db-info')
def db_info():
    """数据库信息"""
    with app.app_context():
        # 获取用户总数
        user_count = User.query.count()
        
        # 获取最新的用户
        latest_user = User.query.order_by(User.created_at.desc()).first()
        
        return jsonify({
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'],
            'user_count': user_count,
            'latest_user': latest_user.to_dict() if latest_user else None,
            'tables': db.metadata.tables.keys()
        })


# ============ 错误处理 ============

@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({'error': '资源未找到'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    db.session.rollback()  # 回滚数据库会话
    return jsonify({'error': '服务器内部错误'}), 500


# ============ 应用上下文管理 ============

@app.before_request
def before_request():
    """
    请求前钩子
    
    在每个请求处理之前执行
    可以用于：
    - 检查用户认证
    - 记录请求日志
    - 初始化数据库连接
    """
    pass


@app.after_request
def after_request(response):
    """
    请求后钩子
    
    在每个请求处理之后执行
    可以用于：
    - 添加响应头
    - 记录响应日志
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    应用上下文销毁时执行
    
    Flask-SQLAlchemy 会自动管理会话
    这里只是演示如何使用 teardown
    """
    if exception:
        db.session.rollback()


# ============ CLI 命令 ============

@app.cli.command()
def initdb():
    """初始化数据库（命令行工具）"""
    init_db()


@app.cli.command()
def dropdb():
    """删除数据库（命令行工具）"""
    with app.app_context():
        db.drop_all()
        print("数据库表已删除！")


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 运行应用
    app.run(debug=True, host='127.0.0.1', port=5000)


"""
知识点总结:

1. Flask-SQLAlchemy 配置
   - SQLALCHEMY_DATABASE_URI: 数据库连接字符串
   - SQLALCHEMY_TRACK_MODIFICATIONS: 是否追踪对象修改
   - SQLALCHEMY_ECHO: 是否显示 SQL 语句

2. 数据库操作
   - db.create_all(): 创建所有表
   - db.drop_all(): 删除所有表
   - db.session.add(): 添加对象
   - db.session.commit(): 提交事务
   - db.session.rollback(): 回滚事务
   - db.session.delete(): 删除对象

3. 查询操作
   - Model.query.all(): 查询所有
   - Model.query.get(id): 根据主键查询
   - Model.query.get_or_404(id): 查询或返回 404
   - Model.query.filter_by(field=value): 条件查询
   - Model.query.order_by(field): 排序
   - Model.query.paginate(): 分页查询
   - Model.query.count(): 计数

4. 应用上下文
   - with app.app_context(): 手动创建应用上下文
   - @app.before_request: 请求前钩子
   - @app.after_request: 请求后钩子
   - @app.teardown_appcontext: 上下文销毁钩子

5. 数据库 URI 格式
   - SQLite: sqlite:///path/to/database.db
   - MySQL: mysql+pymysql://user:pass@host/dbname
   - PostgreSQL: postgresql://user:pass@host/dbname

6. 最佳实践
   - 使用事务确保数据一致性
   - 错误时回滚会话
   - 使用 get_or_404() 简化错误处理
   - 在模型中定义 to_dict() 方法
   - 使用环境变量存储敏感配置

7. CLI 命令
   - @app.cli.command(): 定义命令行命令
   - flask initdb: 初始化数据库
   - flask dropdb: 删除数据库

下一步:
- 学习 ORM 模型和关系（05_orm_models.py）
- 了解数据库迁移（Flask-Migrate）
- 学习复杂查询和关系映射
"""

