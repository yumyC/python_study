"""
Request ID 中间件

为每个请求生成唯一的 Request ID，用于分布式追踪
"""

import uuid


class RequestIDMiddleware:
    """Request ID 中间件"""
    
    def __init__(self, wsgi_app):
        """
        初始化中间件
        
        Args:
            wsgi_app: WSGI 应用
        """
        self.wsgi_app = wsgi_app
    
    def __call__(self, environ, start_response):
        """WSGI 调用"""
        # 获取或生成 Request ID
        request_id = environ.get('HTTP_X_REQUEST_ID')
        
        if not request_id:
            request_id = str(uuid.uuid4())
            environ['HTTP_X_REQUEST_ID'] = request_id
        
        def new_start_response(status, response_headers, exc_info=None):
            # 在响应头中添加 Request ID
            response_headers.append(('X-Request-ID', request_id))
            return start_response(status, response_headers, exc_info)
        
        return self.wsgi_app(environ, new_start_response)


def setup_flask_request_id(app):
    """
    为 Flask 应用设置 Request ID
    
    这是一个更适合 Flask 的 Request ID 实现
    """
    
    @app.before_request
    def before_request():
        """请求开始前生成 Request ID"""
        from flask import request, g
        
        # 获取或生成 Request ID
        request_id = request.headers.get('X-Request-ID')
        
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # 存储到 g 对象中，供其他地方使用
        g.request_id = request_id
    
    @app.after_request
    def after_request(response):
        """请求结束后在响应头中添加 Request ID"""
        from flask import g
        
        request_id = getattr(g, 'request_id', str(uuid.uuid4()))
        response.headers['X-Request-ID'] = request_id
        
        return response