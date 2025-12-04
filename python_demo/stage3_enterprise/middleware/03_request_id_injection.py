"""
Request ID 注入中间件示例

本模块演示如何实现 Request ID 注入中间件，为每个请求生成唯一的标识符，
用于分布式系统的请求追踪和日志关联。

功能特点：
1. 为每个请求生成唯一的 Request ID
2. 支持从请求头中读取已有的 Request ID
3. 将 Request ID 注入到请求上下文
4. 在响应头中返回 Request ID
5. 在日志中自动关联 Request ID
"""

import uuid
import logging
from typing import Callable
from contextvars import ContextVar

# ============================================================================
# 全局上下文变量
# ============================================================================

# 使用 ContextVar 存储 Request ID，支持异步环境
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)


def get_request_id() -> str:
    """
    获取当前请求的 Request ID
    
    Returns:
        str: Request ID，如果不存在则返回 None
    """
    return request_id_var.get()


def set_request_id(request_id: str):
    """
    设置当前请求的 Request ID
    
    Args:
        request_id: Request ID
    """
    request_id_var.set(request_id)


# ============================================================================
# 自定义日志过滤器
# ============================================================================

class RequestIdFilter(logging.Filter):
    """
    日志过滤器，自动在日志中添加 Request ID
    """
    
    def filter(self, record):
        """
        为日志记录添加 Request ID
        
        Args:
            record: 日志记录对象
            
        Returns:
            bool: 是否记录该日志
        """
        record.request_id = get_request_id() or "N/A"
        return True


# 配置日志，包含 Request ID
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s'
)

# 添加过滤器到根日志记录器
logger = logging.getLogger(__name__)
logger.addFilter(RequestIdFilter())


# ============================================================================
# FastAPI 实现
# ============================================================================

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Request ID 中间件
    
    为每个请求生成或提取 Request ID，并注入到上下文中
    """
    
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = "X-Request-ID",
        generate_if_missing: bool = True
    ):
        """
        初始化中间件
        
        Args:
            app: ASGI 应用实例
            header_name: Request ID 的请求头名称
            generate_if_missing: 如果请求头中没有 Request ID，是否自动生成
        """
        super().__init__(app)
        self.header_name = header_name
        self.generate_if_missing = generate_if_missing
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并注入 Request ID
        
        Args:
            request: 请求对象
            call_next: 调用下一个中间件或路由处理函数
            
        Returns:
            Response: 响应对象
        """
        # 从请求头中获取 Request ID，如果不存在则生成新的
        request_id = request.headers.get(self.header_name)
        
        if not request_id and self.generate_if_missing:
            request_id = self._generate_request_id()
        
        # 设置到上下文变量
        set_request_id(request_id)
        
        # 记录请求开始
        logger.info(f"请求开始: {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 在响应头中添加 Request ID
        if request_id:
            response.headers[self.header_name] = request_id
        
        # 记录请求完成
        logger.info(f"请求完成: {request.method} {request.url.path}")
        
        return response
    
    def _generate_request_id(self) -> str:
        """
        生成唯一的 Request ID
        
        Returns:
            str: UUID 格式的 Request ID
        """
        return str(uuid.uuid4())


# 使用装饰器方式实现（更简洁）
def create_request_id_middleware(
    app: FastAPI,
    header_name: str = "X-Request-ID"
):
    """
    使用装饰器方式创建 Request ID 中间件
    
    Args:
        app: FastAPI 应用实例
        header_name: Request ID 的请求头名称
    """
    
    @app.middleware("http")
    async def add_request_id(request: Request, call_next: Callable):
        """注入 Request ID"""
        # 获取或生成 Request ID
        request_id = request.headers.get(header_name) or str(uuid.uuid4())
        
        # 设置到上下文
        set_request_id(request_id)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加到响应头
        response.headers[header_name] = request_id
        
        return response


# ============================================================================
# Flask 实现
# ============================================================================

from flask import Flask, request as flask_request, g


def setup_request_id_middleware(
    app: Flask,
    header_name: str = "X-Request-ID",
    generate_if_missing: bool = True
):
    """
    为 Flask 应用设置 Request ID 中间件
    
    Args:
        app: Flask 应用实例
        header_name: Request ID 的请求头名称
        generate_if_missing: 如果请求头中没有 Request ID，是否自动生成
    """
    
    @app.before_request
    def inject_request_id():
        """在请求处理前注入 Request ID"""
        # 从请求头中获取 Request ID
        request_id = flask_request.headers.get(header_name)
        
        # 如果不存在且需要生成，则生成新的
        if not request_id and generate_if_missing:
            request_id = str(uuid.uuid4())
        
        # 保存到 g 对象和上下文变量
        g.request_id = request_id
        set_request_id(request_id)
        
        # 记录请求开始
        logger.info(f"请求开始: {flask_request.method} {flask_request.path}")
    
    @app.after_request
    def add_request_id_header(response):
        """在响应中添加 Request ID 头"""
        request_id = getattr(g, 'request_id', None)
        if request_id:
            response.headers[header_name] = request_id
        
        # 记录请求完成
        logger.info(f"请求完成: {flask_request.method} {flask_request.path}")
        
        return response


# ============================================================================
# 高级功能：Request ID 传播
# ============================================================================

import httpx
from typing import Optional


class RequestIdPropagation:
    """
    Request ID 传播工具
    
    在调用其他服务时自动传递 Request ID，实现分布式追踪
    """
    
    def __init__(self, header_name: str = "X-Request-ID"):
        """
        初始化
        
        Args:
            header_name: Request ID 的请求头名称
        """
        self.header_name = header_name
    
    def get_headers(self, additional_headers: Optional[dict] = None) -> dict:
        """
        获取包含 Request ID 的请求头
        
        Args:
            additional_headers: 额外的请求头
            
        Returns:
            dict: 包含 Request ID 的请求头字典
        """
        headers = additional_headers or {}
        request_id = get_request_id()
        
        if request_id:
            headers[self.header_name] = request_id
        
        return headers
    
    async def get_async(self, url: str, **kwargs) -> httpx.Response:
        """
        发送 GET 请求并传递 Request ID
        
        Args:
            url: 请求 URL
            **kwargs: httpx.get 的其他参数
            
        Returns:
            httpx.Response: 响应对象
        """
        headers = self.get_headers(kwargs.pop('headers', None))
        async with httpx.AsyncClient() as client:
            return await client.get(url, headers=headers, **kwargs)
    
    async def post_async(self, url: str, **kwargs) -> httpx.Response:
        """
        发送 POST 请求并传递 Request ID
        
        Args:
            url: 请求 URL
            **kwargs: httpx.post 的其他参数
            
        Returns:
            httpx.Response: 响应对象
        """
        headers = self.get_headers(kwargs.pop('headers', None))
        async with httpx.AsyncClient() as client:
            return await client.post(url, headers=headers, **kwargs)


# 创建全局实例
request_id_propagation = RequestIdPropagation()


# ============================================================================
# 示例应用
# ============================================================================

# FastAPI 示例
fastapi_app = FastAPI(title="Request ID 中间件示例")

# 方式 1: 使用类中间件
fastapi_app.add_middleware(
    RequestIdMiddleware,
    header_name="X-Request-ID",
    generate_if_missing=True
)

# 方式 2: 使用装饰器中间件（注释掉，避免重复）
# create_request_id_middleware(fastapi_app, header_name="X-Request-ID")


@fastapi_app.get("/")
async def root():
    """根路径"""
    request_id = get_request_id()
    logger.info("处理根路径请求")
    return {
        "message": "Hello World",
        "request_id": request_id
    }


@fastapi_app.get("/users/{user_id}")
async def get_user(user_id: str):
    """获取用户信息"""
    request_id = get_request_id()
    logger.info(f"获取用户信息: {user_id}")
    return {
        "user_id": user_id,
        "name": "John Doe",
        "request_id": request_id
    }


@fastapi_app.get("/call-external")
async def call_external_service():
    """
    调用外部服务示例
    
    演示如何在调用其他服务时传递 Request ID
    """
    request_id = get_request_id()
    logger.info("准备调用外部服务")
    
    # 模拟调用外部服务（实际应用中替换为真实的服务 URL）
    # response = await request_id_propagation.get_async("http://external-service/api/data")
    
    return {
        "message": "External service called",
        "request_id": request_id,
        "note": "Request ID will be propagated to external service"
    }


@fastapi_app.get("/chain")
async def chain_request():
    """
    链式请求示例
    
    演示在同一个 Request ID 下进行多个操作
    """
    request_id = get_request_id()
    
    logger.info("开始链式操作 - 步骤 1")
    # 模拟第一步操作
    
    logger.info("开始链式操作 - 步骤 2")
    # 模拟第二步操作
    
    logger.info("开始链式操作 - 步骤 3")
    # 模拟第三步操作
    
    logger.info("链式操作完成")
    
    return {
        "message": "Chain request completed",
        "request_id": request_id,
        "steps": 3
    }


# Flask 示例
flask_app = Flask(__name__)

# 设置 Request ID 中间件
setup_request_id_middleware(
    flask_app,
    header_name="X-Request-ID",
    generate_if_missing=True
)


@flask_app.route("/")
def flask_root():
    """根路径"""
    request_id = get_request_id()
    logger.info("处理根路径请求")
    return {
        "message": "Hello World",
        "request_id": request_id
    }


@flask_app.route("/users/<user_id>")
def flask_get_user(user_id):
    """获取用户信息"""
    request_id = get_request_id()
    logger.info(f"获取用户信息: {user_id}")
    return {
        "user_id": user_id,
        "name": "John Doe",
        "request_id": request_id
    }


@flask_app.route("/chain")
def flask_chain():
    """链式请求示例"""
    request_id = get_request_id()
    
    logger.info("开始链式操作 - 步骤 1")
    logger.info("开始链式操作 - 步骤 2")
    logger.info("开始链式操作 - 步骤 3")
    logger.info("链式操作完成")
    
    return {
        "message": "Chain request completed",
        "request_id": request_id,
        "steps": 3
    }


# ============================================================================
# 运行说明
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Request ID 注入中间件示例")
    print("=" * 70)
    print("\n选择要运行的框架:")
    print("1. FastAPI (推荐使用 uvicorn 运行)")
    print("2. Flask")
    print("\nFastAPI 运行命令:")
    print("  uvicorn 03_request_id_injection:fastapi_app --reload")
    print("\nFlask 运行命令:")
    print("  python 03_request_id_injection.py")
    print("\n测试端点:")
    print("  GET http://localhost:8000/")
    print("  GET http://localhost:8000/users/123")
    print("  GET http://localhost:8000/call-external")
    print("  GET http://localhost:8000/chain")
    print("\n测试方法:")
    print("1. 不带 X-Request-ID 头发送请求，观察自动生成的 ID")
    print("2. 带 X-Request-ID 头发送请求，观察 ID 的传递")
    print("3. 查看日志输出，所有日志都包含相同的 Request ID")
    print("\ncurl 示例:")
    print('  curl -H "X-Request-ID: my-custom-id" http://localhost:8000/')
    print("=" * 70)
    
    # 运行 Flask 应用
    flask_app.run(debug=True, port=5000)
