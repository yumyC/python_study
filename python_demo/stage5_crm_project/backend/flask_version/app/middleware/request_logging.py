"""
请求日志中间件

记录所有 HTTP 请求的详细信息
"""

import time
import logging
from flask import request, g

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """请求日志中间件"""
    
    def __init__(self, wsgi_app, log_request_body=False):
        """
        初始化中间件
        
        Args:
            wsgi_app: WSGI 应用
            log_request_body: 是否记录请求体
        """
        self.wsgi_app = wsgi_app
        self.log_request_body = log_request_body
    
    def __call__(self, environ, start_response):
        """WSGI 调用"""
        # 记录请求开始时间
        start_time = time.time()
        
        def new_start_response(status, response_headers, exc_info=None):
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录请求日志
            self._log_request(environ, status, process_time)
            
            return start_response(status, response_headers, exc_info)
        
        return self.wsgi_app(environ, new_start_response)
    
    def _log_request(self, environ, status, process_time):
        """记录请求日志"""
        try:
            # 获取请求信息
            method = environ.get('REQUEST_METHOD', 'GET')
            path = environ.get('PATH_INFO', '/')
            query_string = environ.get('QUERY_STRING', '')
            remote_addr = environ.get('REMOTE_ADDR', 'unknown')
            user_agent = environ.get('HTTP_USER_AGENT', 'unknown')
            
            # 构建完整URL
            url = path
            if query_string:
                url += f'?{query_string}'
            
            # 获取状态码
            status_code = status.split(' ')[0] if status else 'unknown'
            
            # 获取 Request ID（如果存在）
            request_id = environ.get('HTTP_X_REQUEST_ID', 'unknown')
            
            # 构建日志消息
            log_message = (
                f"[{request_id}] {method} {url} - "
                f"Status: {status_code} - "
                f"Time: {process_time:.3f}s - "
                f"IP: {remote_addr} - "
                f"User-Agent: {user_agent}"
            )
            
            # 记录请求体（如果启用）
            if self.log_request_body and method in ['POST', 'PUT', 'PATCH']:
                content_length = environ.get('CONTENT_LENGTH')
                if content_length and int(content_length) > 0:
                    try:
                        # 注意：这里只是示例，实际使用时需要小心处理请求体
                        # 因为 WSGI 环境中的请求体可能已经被读取
                        wsgi_input = environ.get('wsgi.input')
                        if wsgi_input:
                            # 在实际应用中，应该在 Flask 层面处理请求体日志
                            log_message += " - Body: [Request body logging enabled]"
                    except Exception:
                        log_message += " - Body: [Failed to read request body]"
            
            # 根据状态码选择日志级别
            if status_code.startswith('2'):
                logger.info(log_message)
            elif status_code.startswith('3'):
                logger.info(log_message)
            elif status_code.startswith('4'):
                logger.warning(log_message)
            elif status_code.startswith('5'):
                logger.error(log_message)
            else:
                logger.info(log_message)
                
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")


def setup_flask_request_logging(app):
    """
    为 Flask 应用设置请求日志
    
    这是一个更适合 Flask 的请求日志实现
    """
    
    @app.before_request
    def before_request():
        """请求开始前的处理"""
        g.start_time = time.time()
        
        # 获取或生成 Request ID
        request_id = request.headers.get('X-Request-ID', 'unknown')
        g.request_id = request_id
    
    @app.after_request
    def after_request(response):
        """请求结束后的处理"""
        try:
            # 计算处理时间
            process_time = time.time() - getattr(g, 'start_time', time.time())
            
            # 获取请求信息
            method = request.method
            url = request.url
            remote_addr = request.remote_addr or 'unknown'
            user_agent = request.headers.get('User-Agent', 'unknown')
            status_code = response.status_code
            request_id = getattr(g, 'request_id', 'unknown')
            
            # 构建日志消息
            log_message = (
                f"[{request_id}] {method} {url} - "
                f"Status: {status_code} - "
                f"Time: {process_time:.3f}s - "
                f"IP: {remote_addr} - "
                f"User-Agent: {user_agent}"
            )
            
            # 记录请求体（如果需要）
            if hasattr(app.config, 'LOG_REQUEST_BODY') and app.config.get('LOG_REQUEST_BODY'):
                if method in ['POST', 'PUT', 'PATCH'] and request.is_json:
                    try:
                        # 获取请求数据（注意：这可能会消耗请求体）
                        data = request.get_json(silent=True)
                        if data:
                            # 过滤敏感信息
                            filtered_data = {k: v for k, v in data.items() if k not in ['password', 'token']}
                            log_message += f" - Body: {filtered_data}"
                    except Exception:
                        log_message += " - Body: [Failed to parse JSON]"
            
            # 根据状态码选择日志级别
            if 200 <= status_code < 300:
                logger.info(log_message)
            elif 300 <= status_code < 400:
                logger.info(log_message)
            elif 400 <= status_code < 500:
                logger.warning(log_message)
            elif 500 <= status_code < 600:
                logger.error(log_message)
            else:
                logger.info(log_message)
                
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
        
        return response