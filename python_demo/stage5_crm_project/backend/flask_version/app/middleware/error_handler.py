"""
错误处理中间件

统一处理应用中的异常和错误
"""

import logging
import traceback
from flask import jsonify, g

# 配置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """错误处理中间件"""
    
    def __init__(self, wsgi_app, debug=False):
        """
        初始化中间件
        
        Args:
            wsgi_app: WSGI 应用
            debug: 是否为调试模式
        """
        self.wsgi_app = wsgi_app
        self.debug = debug
    
    def __call__(self, environ, start_response):
        """WSGI 调用"""
        try:
            return self.wsgi_app(environ, start_response)
        except Exception as e:
            # 记录错误日志
            self._log_error(environ, e)
            
            # 返回错误响应
            error_response = self._create_error_response(e)
            
            # 设置响应状态和头部
            status = '500 Internal Server Error'
            headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_response)))
            ]
            
            # 添加 Request ID（如果存在）
            request_id = environ.get('HTTP_X_REQUEST_ID')
            if request_id:
                headers.append(('X-Request-ID', request_id))
            
            start_response(status, headers)
            return [error_response.encode('utf-8')]
    
    def _log_error(self, environ, exception):
        """记录错误日志"""
        try:
            # 获取请求信息
            method = environ.get('REQUEST_METHOD', 'GET')
            path = environ.get('PATH_INFO', '/')
            query_string = environ.get('QUERY_STRING', '')
            remote_addr = environ.get('REMOTE_ADDR', 'unknown')
            request_id = environ.get('HTTP_X_REQUEST_ID', 'unknown')
            
            # 构建完整URL
            url = path
            if query_string:
                url += f'?{query_string}'
            
            # 记录错误日志
            error_message = (
                f"[{request_id}] Unhandled exception in {method} {url} "
                f"from {remote_addr}: {str(exception)}"
            )
            
            logger.error(error_message)
            
            # 记录堆栈跟踪
            if self.debug:
                logger.error(f"[{request_id}] Traceback:\n{traceback.format_exc()}")
                
        except Exception as log_error:
            logger.error(f"Failed to log error: {str(log_error)}")
    
    def _create_error_response(self, exception):
        """创建错误响应"""
        import json
        
        error_data = {
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal server error occurred',
                'status_code': 500
            }
        }
        
        # 在调试模式下包含详细错误信息
        if self.debug:
            error_data['error']['message'] = str(exception)
            error_data['error']['traceback'] = traceback.format_exc()
        
        return json.dumps(error_data, ensure_ascii=False, indent=2)


def setup_flask_error_handler(app):
    """
    为 Flask 应用设置错误处理
    
    这是一个更适合 Flask 的错误处理实现
    """
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """处理所有未捕获的异常"""
        try:
            # 获取 Request ID
            request_id = getattr(g, 'request_id', 'unknown')
            
            # 记录错误日志
            from flask import request
            
            error_message = (
                f"[{request_id}] Unhandled exception in {request.method} {request.url} "
                f"from {request.remote_addr}: {str(e)}"
            )
            
            logger.error(error_message)
            
            # 在调试模式下记录堆栈跟踪
            if app.debug:
                logger.error(f"[{request_id}] Traceback:\n{traceback.format_exc()}")
            
            # 构建错误响应
            error_data = {
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'An internal server error occurred',
                    'status_code': 500,
                    'request_id': request_id
                }
            }
            
            # 在调试模式下包含详细错误信息
            if app.debug:
                error_data['error']['message'] = str(e)
                error_data['error']['traceback'] = traceback.format_exc()
            
            return jsonify(error_data), 500
            
        except Exception as handler_error:
            # 如果错误处理器本身出错，返回最基本的错误响应
            logger.error(f"Error in error handler: {str(handler_error)}")
            
            return jsonify({
                'error': {
                    'code': 'CRITICAL_ERROR',
                    'message': 'A critical error occurred',
                    'status_code': 500
                }
            }), 500
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """处理 404 错误"""
        request_id = getattr(g, 'request_id', 'unknown')
        
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found',
                'status_code': 404,
                'request_id': request_id
            }
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """处理 405 错误"""
        request_id = getattr(g, 'request_id', 'unknown')
        
        return jsonify({
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'The method is not allowed for the requested URL',
                'status_code': 405,
                'request_id': request_id
            }
        }), 405