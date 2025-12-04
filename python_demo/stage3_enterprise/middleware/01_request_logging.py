"""
请求日志中间件示例

本模块演示如何实现请求日志记录中间件，用于记录每个 HTTP 请求的详细信息，
包括请求方法、路径、处理时间、响应状态码等。

功能特点：
1. 记录请求的基本信息（方法、路径、查询参数）
2. 计算请求处理时间
3. 记录响应状态码
4. 支持结构化日志输出
5. 可配置日志级别和格式
"""

import time
import logging
from typing import Callable
from datetime import datetime

# ============================================================================
# FastAPI 实现
# ============================================================================

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI 请求日志中间件
    
    记录每个请求的详细信息和处理时间
    """
    
    def __init__(self, app: ASGIApp, log_request_body: bool = False):
        """
        初始化中间件
        
        Args:
            app: ASGI 应用实例
            log_request_body: 是否记录请求体（默认 False，避免记录敏感信息）
        """
        super().__init__(app)
        self.log_request_body = log_request_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求和响应
        
        Args:
            request: 请求对象
            call_next: 调用下一个中间件或路由处理函数
            
        Returns:
            Response: 响应对象
        """
        # 记录请求开始时间
        start_time = time.time()
        
        # 提取请求信息
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # 可选：记录请求体（注意：读取后需要重新设置）
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_info["body_size"] = len(body)
                # 注意：这里不记录实际内容，避免记录敏感信息
            except Exception as e:
                logger.warning(f"无法读取请求体: {e}")
        
        # 记录请求开始
        logger.info(f"请求开始: {request_info['method']} {request_info['path']}")
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            response_info = {
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            }
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            # 记录请求完成
            logger.info(
                f"请求完成: {request_info['method']} {request_info['path']} "
                f"- 状态码: {response_info['status_code']} "
                f"- 耗时: {response_info['process_time']}"
            )
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"请求异常: {request_info['method']} {request_info['path']} "
                f"- 错误: {str(e)} "
                f"- 耗时: {process_time:.3f}s",
                exc_info=True
            )
            raise


# 使用装饰器方式实现（更简洁）
def create_logging_middleware_decorator(app: FastAPI):
    """
    使用装饰器方式创建日志中间件
    
    Args:
        app: FastAPI 应用实例
    """
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):
        """记录请求日志"""
        start_time = time.time()
        
        # 记录请求
        logger.info(f"收到请求: {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录响应
        logger.info(
            f"响应: {request.method} {request.url.path} "
            f"- {response.status_code} - {process_time:.3f}s"
        )
        
        return response


# ============================================================================
# Flask 实现
# ============================================================================

from flask import Flask, request as flask_request, g
import json


def setup_request_logging(app: Flask, log_request_body: bool = False):
    """
    为 Flask 应用设置请求日志中间件
    
    Args:
        app: Flask 应用实例
        log_request_body: 是否记录请求体
    """
    
    @app.before_request
    def log_request_start():
        """请求开始前记录信息"""
        # 记录开始时间
        g.start_time = time.time()
        
        # 提取请求信息
        request_info = {
            "method": flask_request.method,
            "url": flask_request.url,
            "path": flask_request.path,
            "query_params": dict(flask_request.args),
            "client_ip": flask_request.remote_addr,
            "user_agent": flask_request.headers.get("User-Agent"),
        }
        
        # 可选：记录请求体大小
        if log_request_body and flask_request.method in ["POST", "PUT", "PATCH"]:
            try:
                if flask_request.is_json:
                    request_info["body_size"] = len(flask_request.get_data())
            except Exception as e:
                logger.warning(f"无法读取请求体: {e}")
        
        # 记录请求开始
        logger.info(f"请求开始: {request_info['method']} {request_info['path']}")
        
        # 保存请求信息到 g 对象，供后续使用
        g.request_info = request_info
    
    @app.after_request
    def log_request_end(response):
        """请求结束后记录信息"""
        # 计算处理时间
        if hasattr(g, 'start_time'):
            process_time = time.time() - g.start_time
            
            # 添加处理时间到响应头
            response.headers['X-Process-Time'] = str(process_time)
            
            # 记录响应信息
            request_info = getattr(g, 'request_info', {})
            logger.info(
                f"请求完成: {request_info.get('method')} {request_info.get('path')} "
                f"- 状态码: {response.status_code} "
                f"- 耗时: {process_time:.3f}s"
            )
        
        return response
    
    @app.teardown_request
    def log_request_exception(exception=None):
        """请求异常时记录信息"""
        if exception:
            process_time = time.time() - g.start_time if hasattr(g, 'start_time') else 0
            request_info = getattr(g, 'request_info', {})
            logger.error(
                f"请求异常: {request_info.get('method')} {request_info.get('path')} "
                f"- 错误: {str(exception)} "
                f"- 耗时: {process_time:.3f}s",
                exc_info=True
            )


# ============================================================================
# 结构化日志实现（使用 structlog）
# ============================================================================

try:
    import structlog
    
    # 配置 structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    struct_logger = structlog.get_logger()
    
    class StructuredLoggingMiddleware(BaseHTTPMiddleware):
        """
        使用结构化日志的中间件
        
        输出 JSON 格式的日志，便于日志聚合和分析
        """
        
        async def dispatch(self, request: Request, call_next: Callable) -> Response:
            """处理请求并记录结构化日志"""
            start_time = time.time()
            
            # 记录请求开始
            struct_logger.info(
                "request_started",
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params),
                client_host=request.client.host if request.client else None,
            )
            
            try:
                response = await call_next(request)
                process_time = time.time() - start_time
                
                # 记录请求完成
                struct_logger.info(
                    "request_completed",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    process_time=process_time,
                )
                
                response.headers["X-Process-Time"] = str(process_time)
                return response
                
            except Exception as e:
                process_time = time.time() - start_time
                
                # 记录请求异常
                struct_logger.error(
                    "request_failed",
                    method=request.method,
                    path=request.url.path,
                    error=str(e),
                    process_time=process_time,
                    exc_info=True,
                )
                raise
    
except ImportError:
    # structlog 未安装时的占位符
    StructuredLoggingMiddleware = None
    struct_logger = None


# ============================================================================
# 示例应用
# ============================================================================

# FastAPI 示例
fastapi_app = FastAPI(title="请求日志中间件示例")

# 方式 1: 使用类中间件
fastapi_app.add_middleware(RequestLoggingMiddleware, log_request_body=False)

# 方式 2: 使用装饰器中间件（注释掉，避免重复）
# create_logging_middleware_decorator(fastapi_app)

# 方式 3: 使用结构化日志中间件（如果可用）
# if StructuredLoggingMiddleware:
#     fastapi_app.add_middleware(StructuredLoggingMiddleware)


@fastapi_app.get("/")
async def root():
    """根路径"""
    return {"message": "Hello World"}


@fastapi_app.get("/slow")
async def slow_endpoint():
    """模拟慢速端点"""
    import asyncio
    await asyncio.sleep(2)
    return {"message": "This took 2 seconds"}


@fastapi_app.post("/data")
async def create_data(data: dict):
    """创建数据端点"""
    return {"received": data, "status": "created"}


# Flask 示例
flask_app = Flask(__name__)

# 设置请求日志
setup_request_logging(flask_app, log_request_body=False)


@flask_app.route("/")
def flask_root():
    """根路径"""
    return {"message": "Hello World"}


@flask_app.route("/slow")
def flask_slow():
    """模拟慢速端点"""
    time.sleep(2)
    return {"message": "This took 2 seconds"}


@flask_app.route("/data", methods=["POST"])
def flask_create_data():
    """创建数据端点"""
    data = flask_request.get_json()
    return {"received": data, "status": "created"}


# ============================================================================
# 运行说明
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("请求日志中间件示例")
    print("=" * 70)
    print("\n选择要运行的框架:")
    print("1. FastAPI (推荐使用 uvicorn 运行)")
    print("2. Flask")
    print("\nFastAPI 运行命令:")
    print("  uvicorn 01_request_logging:fastapi_app --reload")
    print("\nFlask 运行命令:")
    print("  python 01_request_logging.py")
    print("\n测试端点:")
    print("  GET  http://localhost:8000/")
    print("  GET  http://localhost:8000/slow")
    print("  POST http://localhost:8000/data")
    print("\n观察日志输出，查看请求信息和处理时间")
    print("=" * 70)
    
    # 运行 Flask 应用
    flask_app.run(debug=True, port=5000)
