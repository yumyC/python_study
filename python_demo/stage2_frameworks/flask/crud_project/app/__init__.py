"""
Flask CRUD 项目 - 应用初始化

这个包包含了 Flask 应用的核心组件。
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# 创建 SQLAlchemy 实例
db = SQLAlchemy()


def create_app():
    """
    应用工厂函数
    
    使用工厂模式创建 Flask 应用实例，便于测试和配置管理。
    """
    app = Flask(__name__)
    
    # 配置数据库
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "crud_app.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # 显示 SQL 语句（开发环境）
    
    # JSON 配置
    app.config['JSON_AS_ASCII'] = False  # 支持中文
    app.config['JSON_SORT_KEYS'] = False  # 不排序键
    
    # 初始化扩展
    db.init_app(app)
    
    # 注册蓝图
    from app.views import bp as main_bp
    app.register_blueprint(main_bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
