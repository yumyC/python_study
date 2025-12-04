"""
CORS 跨域资源共享中间件示例

本模块演示如何实现 CORS（Cross-Origin Resource Sharing）中间件，
用于处理跨域请求，支持前后端分离架构和多域名部署。

功能特点：
1. 处理跨域资源共享（CORS）请求
2. 配置允许的源（Origin）
3. 配置允许的 HTTP 方法
4. 配置允许的请求头
5. 处理预检请求（OPTIONS）
6. 支持凭证传递（Credentials）
"""

import logging
from typing import List, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FastAPI 实现
# ============================================================================

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable


class CustomCORSMiddleware(BaseHTTPMiddleware):
    """
    自定义 CORS 中间件
    
    提供更灵活的 CORS 配置和日志记录
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        expose_headers: List[str] = None,
        max_age: int = 600,
        log_requests: bool = True
    ):
        """
        初始化 CORS 中间件
        
        Args:
            app: ASGI 应用实例
            allow_origins: 允许的源列表，["*"] 表示允许所有源
            allow_methods: 允许的 HTTP 方法列表
            allow_headers: 允许的请求头列表
            allow_credentials: 是否允许发送凭证（cookies）
            expose_headers: 暴露给客户端的响应头列表
            max_age: 预检请求的缓存时间（秒）
            log_requests: 是否记录 CORS 请求日志
        """
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        self.log_requests = log_requests
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理 CORS 请求
        
        Args:
            request: 请求对象
            call_next: 调用下一个中间件或路由处理函数
            
        Returns:
            Response: 响应对象
        """
        origin = request.headers.get("origin")
        
        # 记录跨域请求
        if self.log_requests and origin:
            logger.info(f"CORS 请求: {request.method} {request.url.path} from {origin}")
        
        # 处理预检请求（OPTIONS）
        if request.method == "OPTIONS":
            return self._handle_preflight_request(request, origin)
        
        # 处理实际请求
        response = await call_next(request)
        
        # 添加 CORS 响应头
        if origin and self._is_origin_allowed(origin):
            self._add_cors_headers(response, origin)
        
        return response
    
    def _handle_preflight_request(self, request: Request, origin: str) -> Response:
        """
        处理预检请求
        
        Args:
            request: 请求对象
            origin: 请求源
            
        Returns:
            Response: 预检响应
        """
        if self.log_requests:
            logger.info(f"处理预检请求: {origin}")
        
        # 创建预检响应
        response = Response(status_code=200)
        
        # 添加 CORS 响应头
        if self._is_origin_allowed(origin):
            self._add_cors_headers(response, origin, is_preflight=True)
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """
        检查源是否被允许
        
        Args:
            origin: 请求源
            
        Returns:
            bool: 是否允许
        """
        if "*" in self.allow_origins:
            return True
        return origin in self.allow_origins
    
    def _add_cors_headers(self, response: Response, origin: str, is_preflight: bool = False):
        """
        添加 CORS 响应头
        
        Args:
            response: 响应对象
            origin: 请求源
            is_preflight: 是否为预检请求
        """
        # 允许的源
        if "*" in self.allow_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        else:
            response.headers["Access-Control-Allow-Origin"] = origin
        
        # 允许凭证
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # 预检请求的额外响应头
        if is_preflight:
            # 允许的方法
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            
            # 允许的请求头
            if "*" in self.allow_headers:
                # 如果允许所有头，则返回请求中的 Access-Control-Request-Headers
                requested_headers = response.headers.get("Access-Control-Request-Headers")
                if requested_headers:
                    response.headers["Access-Control-Allow-Headers"] = requested_headers
            else:
                response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            
            # 预检请求缓存时间
            response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        # 暴露的响应头
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)


# ============================================================================
# Flask 实现
# ============================================================================

from flask import Flask, request as flask_request, make_response
from functools import wraps


def setup_cors_middleware(
    app: Flask,
    allow_origins: List[str] = None,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None,
    allow_credentials: bool = False,
    expose_headers: List[str] = None,
    max_age: int = 600,
    log_requests: bool = True
):
    """
    为 Flask 应用设置 CORS 中间件
    
    Args:
        app: Flask 应用实例
        allow_origins: 允许的源列表
        allow_methods: 允许的 HTTP 方法列表
        allow_headers: 允许的请求头列表
        allow_credentials: 是否允许发送凭证
        expose_headers: 暴露给客户端的响应头列表
        max_age: 预检请求的缓存时间（秒）
        log_requests: 是否记录 CORS 请求日志
    """
    allow_origins = allow_origins or ["*"]
    allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    allow_headers = allow_headers or ["*"]
    expose_headers = expose_headers or []
    
    def is_origin_allowed(origin: str) -> bool:
        """检查源是否被允许"""
        if "*" in allow_origins:
            return True
        return origin in allow_origins
    
    @app.after_request
    def add_cors_headers(response):
        """在响应中添加 CORS 头"""
        origin = flask_request.headers.get("Origin")
        
        if origin and is_origin_allowed(origin):
            # 记录跨域请求
            if log_requests:
                logger.info(
                    f"CORS 请求: {flask_request.method} {flask_request.path} from {origin}"
                )
            
            # 允许的源
            if "*" in allow_origins:
                response.headers["Access-Control-Allow-Origin"] = "*"
            else:
                response.headers["Access-Control-Allow-Origin"] = origin
            
            # 允许凭证
            if allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            
            # 允许的方法
            response.headers["Access-Control-Allow-Methods"] = ", ".join(allow_methods)
            
            # 允许的请求头
            if "*" in allow_headers:
                requested_headers = flask_request.headers.get("Access-Control-Request-Headers")
                if requested_headers:
                    response.headers["Access-Control-Allow-Headers"] = requested_headers
            else:
                response.headers["Access-Control-Allow-Headers"] = ", ".join(allow_headers)
            
            # 暴露的响应头
            if expose_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(expose_headers)
            
            # 预检请求缓存时间
            response.headers["Access-Control-Max-Age"] = str(max_age)
        
        return response
    
    # 处理 OPTIONS 预检请求
    @app.before_request
    def handle_preflight():
        """处理预检请求"""
        if flask_request.method == "OPTIONS":
            origin = flask_request.headers.get("Origin")
            if origin and is_origin_allowed(origin):
                if log_requests:
                    logger.info(f"处理预检请求: {origin}")
                response = make_response()
                response.status_code = 200
                return response


# ============================================================================
# CORS 配置示例
# ============================================================================

# 开发环境配置（允许所有源）
DEV_CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    "allow_headers": ["*"],
    "allow_credentials": False,
    "max_age": 600,
}

# 生产环境配置（限制特定源）
PROD_CORS_CONFIG = {
    "allow_origins": [
        "https://example.com",
        "https://www.example.com",
        "https://app.example.com",
    ],
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
    "allow_headers": [
        "Content-Type",
        "Authorization",
        "X-Request-ID",
        "X-API-Key",
    ],
    "allow_credentials": True,
    "expose_headers": ["X-Request-ID", "X-Total-Count"],
    "max_age": 3600,
}

# 前后端分离配置
FRONTEND_CORS_CONFIG = {
    "allow_origins": [
        "http://localhost:3000",  # React 开发服务器
        "http://localhost:8080",  # Vue 开发服务器
        "http://localhost:4200",  # Angular 开发服务器
    ],
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
    "allow_headers": ["Content-Type", "Authorization"],
    "allow_credentials": True,
    "max_age": 600,
}


# ============================================================================
# 示例应用
# ============================================================================

# FastAPI 示例 - 使用内置 CORS 中间件（推荐）
fastapi_app = FastAPI(title="CORS 中间件示例")

# 方式 1: 使用 FastAPI 内置的 CORSMiddleware（推荐）
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# 方式 2: 使用自定义 CORS 中间件（注释掉，避免重复）
# fastapi_app.add_middleware(
#     CustomCORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=["*"],
#     allow_credentials=True,
#     expose_headers=["X-Request-ID"],
#     max_age=600,
#     log_requests=True
# )


@fastapi_app.get("/")
async def root():
    """根路径"""
    return {"message": "Hello World", "cors": "enabled"}


@fastapi_app.get("/api/users")
async def get_users():
    """获取用户列表"""
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }


@fastapi_app.post("/api/users")
async def create_user(user_data: dict):
    """创建用户"""
    return {"user": user_data, "status": "created"}


@fastapi_app.get("/api/protected")
async def protected_endpoint():
    """
    受保护的端点
    
    需要在请求头中包含 Authorization
    """
    return {"message": "This is a protected endpoint", "authenticated": True}


# Flask 示例
flask_app = Flask(__name__)

# 设置 CORS 中间件
setup_cors_middleware(
    flask_app,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["X-Request-ID"],
    max_age=600,
    log_requests=True
)


@flask_app.route("/")
def flask_root():
    """根路径"""
    return {"message": "Hello World", "cors": "enabled"}


@flask_app.route("/api/users")
def flask_get_users():
    """获取用户列表"""
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }


@flask_app.route("/api/users", methods=["POST"])
def flask_create_user():
    """创建用户"""
    user_data = flask_request.get_json()
    return {"user": user_data, "status": "created"}


@flask_app.route("/api/protected")
def flask_protected():
    """受保护的端点"""
    return {"message": "This is a protected endpoint", "authenticated": True}


# ============================================================================
# 运行说明
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CORS 跨域资源共享中间件示例")
    print("=" * 70)
    print("\n选择要运行的框架:")
    print("1. FastAPI (推荐使用 uvicorn 运行)")
    print("2. Flask")
    print("\nFastAPI 运行命令:")
    print("  uvicorn 04_cors_middleware:fastapi_app --reload")
    print("\nFlask 运行命令:")
    print("  python 04_cors_middleware.py")
    print("\n测试端点:")
    print("  GET  http://localhost:8000/")
    print("  GET  http://localhost:8000/api/users")
    print("  POST http://localhost:8000/api/users")
    print("  GET  http://localhost:8000/api/protected")
    print("\n测试方法:")
    print("1. 使用浏览器从不同域名访问 API")
    print("2. 使用 curl 发送带 Origin 头的请求:")
    print('   curl -H "Origin: http://example.com" http://localhost:8000/')
    print("3. 观察响应头中的 CORS 相关头部:")
    print("   - Access-Control-Allow-Origin")
    print("   - Access-Control-Allow-Methods")
    print("   - Access-Control-Allow-Headers")
    print("   - Access-Control-Allow-Credentials")
    print("\n前端测试示例 (JavaScript):")
    print("  fetch('http://localhost:8000/api/users', {")
    print("    method: 'GET',")
    print("    credentials: 'include',  // 发送凭证")
    print("    headers: {")
    print("      'Content-Type': 'application/json',")
    print("    }")
    print("  })")
    print("=" * 70)
    
    # 运行 Flask 应用
    flask_app.run(debug=True, port=5000)
