"""
Flask CRM 应用工厂

这个模块负责创建和配置 Flask 应用实例
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称 ('development', 'production', 'testing')
    
    Returns:
        Flask: 配置好的 Flask 应用实例
    """
    app = Flask(__name__)
    
    # 配置应用
    configure_app(app, config_name)
    
    # 初始化扩展
    initialize_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册中间件
    register_middleware(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app


def configure_app(app, config_name):
    """配置应用"""
    # 基础配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///crm_flask.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT 配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1小时
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400 * 30  # 30天
    
    # Celery 配置
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # 根据环境设置特定配置
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    elif config_name == 'production':
        app.config['DEBUG'] = False
    else:
        app.config['DEBUG'] = True


def initialize_extensions(app):
    """初始化扩展"""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 启用 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })


def register_blueprints(app):
    """注册蓝图"""
    from app.api.auth import auth_bp
    from app.api.employees import employees_bp
    from app.api.positions import positions_bp
    from app.api.menus import menus_bp
    from app.api.roles import roles_bp
    from app.api.permissions import permissions_bp
    from app.api.work_logs import work_logs_bp
    from app.api.tasks import tasks_bp
    
    # 注册 API 蓝图
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(employees_bp, url_prefix='/api')
    app.register_blueprint(positions_bp, url_prefix='/api')
    app.register_blueprint(menus_bp, url_prefix='/api')
    app.register_blueprint(roles_bp, url_prefix='/api')
    app.register_blueprint(permissions_bp, url_prefix='/api')
    app.register_blueprint(work_logs_bp, url_prefix='/api')
    app.register_blueprint(tasks_bp, url_prefix='/api')


def register_middleware(app):
    """注册中间件"""
    from app.middleware.request_logging import RequestLoggingMiddleware
    from app.middleware.request_id import RequestIDMiddleware
    from app.middleware.error_handler import ErrorHandlerMiddleware
    
    # 注册中间件（注意顺序）
    app.wsgi_app = ErrorHandlerMiddleware(app.wsgi_app)
    app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)
    app.wsgi_app = RequestIDMiddleware(app.wsgi_app)


def register_error_handlers(app):
    """注册错误处理器"""
    from flask import jsonify
    from werkzeug.exceptions import HTTPException
    from flask_jwt_extended.exceptions import JWTExtendedException
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理 HTTP 异常"""
        return jsonify({
            'error': {
                'code': e.name.upper().replace(' ', '_'),
                'message': e.description,
                'status_code': e.code
            }
        }), e.code
    
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exception(e):
        """处理 JWT 异常"""
        return jsonify({
            'error': {
                'code': 'JWT_ERROR',
                'message': str(e),
                'status_code': 401
            }
        }), 401
    
    @app.errorhandler(Exception)
    def handle_general_exception(e):
        """处理一般异常"""
        if app.debug:
            # 开发环境下返回详细错误信息
            import traceback
            return jsonify({
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': str(e),
                    'traceback': traceback.format_exc(),
                    'status_code': 500
                }
            }), 500
        else:
            # 生产环境下返回通用错误信息
            return jsonify({
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'An internal server error occurred',
                    'status_code': 500
                }
            }), 500