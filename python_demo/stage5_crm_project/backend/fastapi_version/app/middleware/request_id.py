"""
Request ID 中间件

为每个请求生成唯一的 Request ID，用于分布式追踪和日志关联
"""

import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import contextvars

# 创建上下文变量来存储当前请求的 Request ID
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('request_id', default='')


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Request ID 中间件
    
    功能：
    1. 为每个请求生成或提取唯一的 Request ID
    2. 将 Request ID 添加到响应头
    3. 将 Request ID 存储到上下文变量中，供其他组件使用
    4. 支持从请求头中提取已有的 Request ID（用于分布式追踪）
    """
    
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Request-ID",
        response_header_name: str = "X-Request-ID",
        generate_if_missing: bool = True
    ):
        """
        初始化 Request ID 中间件
        
        Args:
            app: ASGI 应用
            header_name: 请求头中 Request ID 的字段名
            response_header_name: 响应头中 Request ID 的字段名
            generate_if_missing: 如果请求头中没有 Request ID，是否自动生成
        """
        super().__init__(app)
        self.header_name = header_name
        self.response_header_name = response_header_name
        self.generate_if_missing = generate_if_missing
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并注入 Request ID
        
        Args:
            request: HTTP 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            HTTP 响应对象
        """
        # 从请求头获取 Request ID，如果没有则生成新的
        request_id = request.headers.get(self.header_name.lower())
        
        if not request_id and self.generate_if_missing:
            request_id = self._generate_request_id()
        
        if not request_id:
            request_id = "unknown"
        
        # 将 Request ID 存储到上下文变量
        request_id_var.set(request_id)
        
        # 将 Request ID 添加到请求对象（方便在路由中访问）
        request.state.request_id = request_id
        
        # 处理请求
        response = await call_next(request)
        
        # 将 Request ID 添加到响应头
        response.headers[self.response_header_name] = request_id
        
        return response
    
    def _generate_request_id(self) -> str:
        """
        生成新的 Request ID
        
        Returns:
            唯一的 Request ID 字符串
        """
        return str(uuid.uuid4())


def get_request_id() -> str:
    """
    获取当前请求的 Request ID
    
    Returns:
        当前请求的 Request ID，如果没有则返回空字符串
    """
    return request_id_var.get('')


def set_request_id(request_id: str):
    """
    设置当前请求的 Request ID
    
    Args:
        request_id: Request ID 字符串
    """
    request_id_var.set(request_id)


class RequestIDLoggerAdapter:
    """
    Request ID 日志适配器
    
    自动在日志消息中包含 Request ID
    """
    
    def __init__(self, logger):
        """
        初始化日志适配器
        
        Args:
            logger: 原始日志记录器
        """
        self.logger = logger
    
    def _log_with_request_id(self, level, msg, *args, **kwargs):
        """
        在日志消息中添加 Request ID
        
        Args:
            level: 日志级别
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        request_id = get_request_id()
        if request_id:
            msg = f"[{request_id}] {msg}"
        
        getattr(self.logger, level)(msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        """记录 DEBUG 级别日志"""
        self._log_with_request_id('debug', msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """记录 INFO 级别日志"""
        self._log_with_request_id('info', msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """记录 WARNING 级别日志"""
        self._log_with_request_id('warning', msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """记录 ERROR 级别日志"""
        self._log_with_request_id('error', msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        """记录 CRITICAL 级别日志"""
        self._log_with_request_id('critical', msg, *args, **kwargs)


def get_logger_with_request_id(logger):
    """
    获取带 Request ID 的日志记录器
    
    Args:
        logger: 原始日志记录器
        
    Returns:
        带 Request ID 的日志适配器
    """
    return RequestIDLoggerAdapter(logger)


def setup_request_id_middleware(app, **kwargs):
    """
    设置 Request ID 中间件的便捷函数
    
    Args:
        app: FastAPI 应用实例
        **kwargs: 中间件配置参数
    """
    app.add_middleware(RequestIDMiddleware, **kwargs)