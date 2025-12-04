"""
Flask ORM 模型示例

演示如何使用 SQLAlchemy ORM 定义复杂的数据模型和关系。

学习要点:
1. 定义数据模型
2. 字段类型和约束
3. 模型关系（一对多、多对多）
4. 复杂查询
5. 数据库迁移

安装依赖:
    pip install flask-sqlalchemy

运行方式:
    python 05_orm_models.py
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "blog.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


# ============ 定义模型 ============

# 多对多关系的关联表
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class User(db.Model):
    """
    用户模型
    
    演示:
    - 基本字段定义
    - 字段约束
    - 一对多关系
    """
    __tablename__ = 'users'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 字符串字段
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    
    # 文本字段
    bio = db.Column(db.Text)
    
    # 布尔字段
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # 日期时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系：一个用户可以有多篇文章
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    # 关系：一个用户可以有多条评论
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_posts=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'bio': self.bio,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'post_count': self.posts.count()
        }
        if include_posts:
            data['posts'] = [post.to_dict(include_author=False) for post in self.posts]
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """
    分类模型
    
    演示:
    - 简单模型定义
    - 一对多关系
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系：一个分类可以有多篇文章
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'post_count': self.posts.count()
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Post(db.Model):
    """
    文章模型
    
    演示:
    - 外键关系
    - 多对多关系
    - 一对多关系
    """
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    
    # 外键：关联用户
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 外键：关联分类
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # 状态字段
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    view_count = db.Column(db.Integer, default=0)
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # 关系：多对多关系（文章-标签）
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
    
    # 关系：一对多关系（文章-评论）
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_author=True, include_comments=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'status': self.status,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category': self.category.to_dict() if self.category else None,
            'tags': [tag.to_dict() for tag in self.tags],
            'comment_count': self.comments.count()
        }
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username
            }
        if include_comments:
            data['comments'] = [comment.to_dict(include_author=True) for comment in self.comments]
        return data
    
    def __repr__(self):
        return f'<Post {self.title}>'


class Tag(db.Model):
    """
    标签模型
    
    演示:
    - 多对多关系
    """
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'post_count': len(self.posts.all())
        }
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class Comment(db.Model):
    """
    评论模型
    
    演示:
    - 多个外键
    - 自引用关系（评论回复）
    """
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # 外键：关联用户
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 外键：关联文章
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    # 自引用：评论回复
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    # 时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, include_author=True, include_replies=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_author and self.author:
            data['author'] = {
                'id': self.author.id,
                'username': self.author.username
            }
        if include_replies:
            data['replies'] = [reply.to_dict(include_author=True) for reply in self.replies]
        return data
    
    def __repr__(self):
        return f'<Comment {self.id}>'


# ============ 初始化数据库 ============

def init_db():
    """初始化数据库并添加示例数据"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功！")
        
        # 检查是否已有数据
        if User.query.count() == 0:
            # 创建用户
            user1 = User(username='张三', email='zhangsan@example.com', bio='Python 开发者')
            user2 = User(username='李四', email='lisi@example.com', bio='Web 开发者')
            db.session.add_all([user1, user2])
            
            # 创建分类
            cat1 = Category(name='技术', description='技术相关文章')
            cat2 = Category(name='生活', description='生活随笔')
            db.session.add_all([cat1, cat2])
            
            # 创建标签
            tag1 = Tag(name='Python')
            tag2 = Tag(name='Flask')
            tag3 = Tag(name='数据库')
            db.session.add_all([tag1, tag2, tag3])
            
            db.session.commit()
            
            # 创建文章
            post1 = Post(
                title='Flask 入门教程',
                content='这是一篇关于 Flask 的入门教程...',
                summary='学习 Flask 基础知识',
                author=user1,
                category=cat1,
                status='published',
                published_at=datetime.utcnow()
            )
            post1.tags.extend([tag1, tag2])
            
            post2 = Post(
                title='SQLAlchemy ORM 详解',
                content='这是一篇关于 SQLAlchemy 的详细教程...',
                summary='深入理解 ORM',
                author=user1,
                category=cat1,
                status='published',
                published_at=datetime.utcnow()
            )
            post2.tags.extend([tag1, tag3])
            
            db.session.add_all([post1, post2])
            db.session.commit()
            
            # 创建评论
            comment1 = Comment(content='写得很好！', author=user2, post=post1)
            comment2 = Comment(content='感谢分享', author=user2, post=post1)
            comment3 = Comment(content='有帮助', author=user1, post=post2)
            
            db.session.add_all([comment1, comment2, comment3])
            db.session.commit()
            
            print("示例数据添加成功！")


# ============ API 路由 ============

@app.route('/')
def index():
    """首页"""
    return '''
    <h1>Flask ORM 模型示例</h1>
    <h2>API 端点：</h2>
    <ul>
        <li><a href="/users">GET /users</a> - 获取所有用户</li>
        <li><a href="/posts">GET /posts</a> - 获取所有文章</li>
        <li><a href="/posts/1">GET /posts/1</a> - 获取文章详情</li>
        <li><a href="/categories">GET /categories</a> - 获取所有分类</li>
        <li><a href="/tags">GET /tags</a> - 获取所有标签</li>
        <li><a href="/stats">GET /stats</a> - 数据统计</li>
    </ul>
    '''


@app.route('/users')
def get_users():
    """获取所有用户"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/posts')
def get_posts():
    """获取所有文章"""
    # 支持过滤和排序
    category_id = request.args.get('category_id', type=int)
    tag_name = request.args.get('tag')
    status = request.args.get('status', 'published')
    
    # 构建查询
    query = Post.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if tag_name:
        query = query.join(Post.tags).filter(Tag.name == tag_name)
    
    if status:
        query = query.filter_by(status=status)
    
    # 排序
    query = query.order_by(Post.created_at.desc())
    
    posts = query.all()
    return jsonify([post.to_dict() for post in posts])


@app.route('/posts/<int:post_id>')
def get_post(post_id):
    """获取文章详情"""
    post = Post.query.get_or_404(post_id)
    
    # 增加浏览次数
    post.view_count += 1
    db.session.commit()
    
    return jsonify(post.to_dict(include_comments=True))


@app.route('/categories')
def get_categories():
    """获取所有分类"""
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories])


@app.route('/tags')
def get_tags():
    """获取所有标签"""
    tags = Tag.query.all()
    return jsonify([tag.to_dict() for tag in tags])


@app.route('/stats')
def get_stats():
    """数据统计"""
    stats = {
        'user_count': User.query.count(),
        'post_count': Post.query.count(),
        'published_post_count': Post.query.filter_by(status='published').count(),
        'comment_count': Comment.query.count(),
        'category_count': Category.query.count(),
        'tag_count': Tag.query.count(),
        'total_views': db.session.query(db.func.sum(Post.view_count)).scalar() or 0,
        'most_viewed_post': Post.query.order_by(Post.view_count.desc()).first().to_dict() if Post.query.count() > 0 else None,
        'most_active_author': db.session.query(
            User.username,
            db.func.count(Post.id).label('post_count')
        ).join(Post).group_by(User.id).order_by(db.text('post_count DESC')).first()
    }
    return jsonify(stats)


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    # 运行应用
    app.run(debug=True, host='127.0.0.1', port=5000)


"""
知识点总结:

1. 字段类型
   - Integer: 整数
   - String(length): 字符串
   - Text: 长文本
   - Boolean: 布尔值
   - DateTime: 日期时间
   - Float: 浮点数
   - Numeric: 精确数值

2. 字段约束
   - primary_key: 主键
   - unique: 唯一约束
   - nullable: 是否可为空
   - default: 默认值
   - index: 创建索引
   - onupdate: 更新时自动设置

3. 关系类型
   - 一对多: db.relationship() + db.ForeignKey()
   - 多对多: db.relationship() + secondary table
   - 自引用: remote_side 参数

4. 关系参数
   - backref: 反向引用
   - lazy: 加载策略（'select', 'dynamic', 'joined', 'subquery'）
   - cascade: 级联操作
   - order_by: 排序

5. 查询方法
   - filter(): 条件过滤
   - filter_by(): 简单条件过滤
   - order_by(): 排序
   - join(): 连接查询
   - group_by(): 分组
   - count(): 计数
   - first(): 第一条
   - all(): 所有记录

6. 聚合函数
   - db.func.count(): 计数
   - db.func.sum(): 求和
   - db.func.avg(): 平均值
   - db.func.max(): 最大值
   - db.func.min(): 最小值

7. 级联操作
   - all: 所有操作
   - delete: 删除时级联
   - delete-orphan: 删除孤儿记录
   - save-update: 保存更新时级联

8. 最佳实践
   - 使用 __tablename__ 明确指定表名
   - 定义 __repr__() 方法便于调试
   - 定义 to_dict() 方法便于序列化
   - 使用索引提高查询性能
   - 合理使用关系的 lazy 参数
   - 注意 N+1 查询问题

下一步:
- 学习数据库迁移（Flask-Migrate）
- 了解查询优化技巧
- 学习事务管理
- 实践 CRUD 项目
"""

