"""
请求日志中间件

记录所有 HTTP 请求的详细信息，包括请求时间、响应时间、状态码等
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json


# 配置日志记录器
logger = logging.getLogger("request_logger")
logger.setLevel(logging.INFO)

# 创建控制台处理器
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志记录中间件
    
    功能：
    1. 记录每个请求的基本信息（方法、路径、IP等）
    2. 记录请求处理时间
    3. 记录响应状态码和大小
    4. 过滤敏感信息（如密码）
    """
    
    def __init__(
        self,
        app: ASGIApp,
        skip_paths: list = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_size: int = 1024
    ):
        """
        初始化请求日志中间件
        
        Args:
            app: ASGI 应用
            skip_paths: 跳过记录的路径列表
            log_request_body: 是否记录请求体
            log_response_body: 是否记录响应体
            max_body_size: 最大记录的请求/响应体大小
        """
        super().__init__(app)
        self.skip_paths = skip_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        
        # 敏感字段列表
        self.sensitive_fields = {
            "password", "token", "secret", "key", "authorization",
            "passwd", "pwd", "pass", "credential", "auth"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录日志
        
        Args:
            request: HTTP 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            HTTP 响应对象
        """
        # 检查是否跳过此路径
        if self._should_skip_logging(request):
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        request_info = await self._extract_request_info(request)
        
        # 记录请求开始
        logger.info(f"Request started: {request_info['method']} {request_info['path']}")
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 获取响应信息
            response_info = self._extract_response_info(response, process_time)
            
            # 记录完整的请求-响应日志
            self._log_request_response(request_info, response_info)
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as exc:
            # 记录异常
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed: {request_info['method']} {request_info['path']} "
                f"- Error: {str(exc)} - Time: {process_time:.4f}s"
            )
            
            raise exc
    
    def _should_skip_logging(self, request: Request) -> bool:
        """
        判断是否应该跳过日志记录
        
        Args:
            request: HTTP 请求对象
            
        Returns:
            是否跳过
        """
        path = request.url.path
        return any(skip_path in path for skip_path in self.skip_paths)
    
    async def _extract_request_info(self, request: Request) -> dict:
        """
        提取请求信息
        
        Args:
            request: HTTP 请求对象
            
        Returns:
            请求信息字典
        """
        # 基本信息
        info = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "request_id": request.headers.get("x-request-id", "")
        }
        
        # 过滤敏感信息
        info["headers"] = self._filter_sensitive_data(info["headers"])
        info["query_params"] = self._filter_sensitive_data(info["query_params"])
        
        # 记录请求体（如果启用）
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    # 尝试解析 JSON
                    try:
                        body_json = json.loads(body.decode())
                        info["body"] = self._filter_sensitive_data(body_json)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        info["body"] = f"<binary data, {len(body)} bytes>"
                else:
                    info["body"] = f"<large body, {len(body)} bytes>"
            except Exception:
                info["body"] = "<failed to read body>"
        
        return info
    
    def _extract_response_info(self, response: Response, process_time: float) -> dict:
        """
        提取响应信息
        
        Args:
            response: HTTP 响应对象
            process_time: 处理时间
            
        Returns:
            响应信息字典
        """
        info = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "process_time": process_time
        }
        
        # 获取响应大小
        content_length = response.headers.get("content-length")
        if content_length:
            info["content_length"] = int(content_length)
        
        return info
    
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实 IP 地址
        
        Args:
            request: HTTP 请求对象
            
        Returns:
            客户端 IP 地址
        """
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 返回直接连接的 IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _filter_sensitive_data(self, data: dict) -> dict:
        """
        过滤敏感数据
        
        Args:
            data: 原始数据字典
            
        Returns:
            过滤后的数据字典
        """
        if not isinstance(data, dict):
            return data
        
        filtered = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # 检查是否为敏感字段
            if any(sensitive in key_lower for sensitive in self.sensitive_fields):
                filtered[key] = "***FILTERED***"
            elif isinstance(value, dict):
                filtered[key] = self._filter_sensitive_data(value)
            else:
                filtered[key] = value
        
        return filtered
    
    def _log_request_response(self, request_info: dict, response_info: dict):
        """
        记录完整的请求-响应日志
        
        Args:
            request_info: 请求信息
            response_info: 响应信息
        """
        # 构建日志消息
        log_data = {
            "request": {
                "method": request_info["method"],
                "path": request_info["path"],
                "client_ip": request_info["client_ip"],
                "user_agent": request_info["user_agent"],
                "request_id": request_info["request_id"]
            },
            "response": {
                "status_code": response_info["status_code"],
                "process_time": f"{response_info['process_time']:.4f}s"
            }
        }
        
        # 添加查询参数（如果有）
        if request_info["query_params"]:
            log_data["request"]["query_params"] = request_info["query_params"]
        
        # 添加请求体（如果记录）
        if "body" in request_info:
            log_data["request"]["body"] = request_info["body"]
        
        # 添加响应大小（如果有）
        if "content_length" in response_info:
            log_data["response"]["content_length"] = response_info["content_length"]
        
        # 根据状态码选择日志级别
        if response_info["status_code"] >= 500:
            logger.error(f"Request completed: {json.dumps(log_data, ensure_ascii=False)}")
        elif response_info["status_code"] >= 400:
            logger.warning(f"Request completed: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            logger.info(f"Request completed: {json.dumps(log_data, ensure_ascii=False)}")


def setup_request_logging(app, **kwargs):
    """
    设置请求日志中间件的便捷函数
    
    Args:
        app: FastAPI 应用实例
        **kwargs: 中间件配置参数
    """
    app.add_middleware(RequestLoggingMiddleware, **kwargs)