"""
错误处理中间件示例

本模块演示如何实现统一的错误处理中间件，用于捕获应用中的所有异常，
提供一致的错误响应格式，并记录详细的错误日志。

功能特点：
1. 捕获所有未处理的异常
2. 统一错误响应格式
3. 区分客户端错误（4xx）和服务器错误（5xx）
4. 记录详细的错误日志和堆栈信息
5. 防止敏感信息泄露
"""

import logging
import traceback
from typing import Callable, Dict, Any
from datetime import datetime

# ============================================================================
# FastAPI 实现
# ============================================================================

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 定义错误响应模型
class ErrorResponse(BaseModel):
    """统一错误响应格式"""
    error: Dict[str, Any]


class ErrorDetail(BaseModel):
    """错误详情"""
    code: str
    message: str
    details: Dict[str, Any] = {}
    timestamp: str
    path: str


# 自定义业务异常
class BusinessException(Exception):
    """业务逻辑异常基类"""
    
    def __init__(self, code: str, message: str, status_code: int = 400, details: Dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundException(BusinessException):
    """资源未找到异常"""
    
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} with id {resource_id} not found",
            status_code=404,
            details={"resource": resource, "resource_id": resource_id}
        )


class ValidationException(BusinessException):
    """数据验证异常"""
    
    def __init__(self, message: str, field_errors: Dict = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details={"field_errors": field_errors or {}}
        )


class UnauthorizedException(BusinessException):
    """未授权异常"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401
        )


class ForbiddenException(BusinessException):
    """禁止访问异常"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403
        )


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    FastAPI 错误处理中间件
    
    捕获所有异常并返回统一格式的错误响应
    """
    
    def __init__(self, app: ASGIApp, debug: bool = False):
        """
        初始化中间件
        
        Args:
            app: ASGI 应用实例
            debug: 是否启用调试模式（在响应中包含堆栈信息）
        """
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        处理请求并捕获异常
        
        Args:
            request: 请求对象
            call_next: 调用下一个中间件或路由处理函数
            
        Returns:
            JSONResponse: 响应对象
        """
        try:
            response = await call_next(request)
            return response
            
        except BusinessException as e:
            # 业务异常 - 客户端错误
            return self._create_error_response(
                request=request,
                code=e.code,
                message=e.message,
                status_code=e.status_code,
                details=e.details,
                log_level="warning"
            )
            
        except HTTPException as e:
            # FastAPI HTTP 异常
            return self._create_error_response(
                request=request,
                code="HTTP_EXCEPTION",
                message=e.detail,
                status_code=e.status_code,
                log_level="warning"
            )
            
        except RequestValidationError as e:
            # 请求验证错误
            return self._create_error_response(
                request=request,
                code="VALIDATION_ERROR",
                message="Request validation failed",
                status_code=422,
                details={"errors": e.errors()},
                log_level="warning"
            )
            
        except Exception as e:
            # 未预期的服务器错误
            return self._create_error_response(
                request=request,
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                status_code=500,
                details={"error_type": type(e).__name__},
                exception=e,
                log_level="error"
            )
    
    def _create_error_response(
        self,
        request: Request,
        code: str,
        message: str,
        status_code: int,
        details: Dict = None,
        exception: Exception = None,
        log_level: str = "error"
    ) -> JSONResponse:
        """
        创建统一格式的错误响应
        
        Args:
            request: 请求对象
            code: 错误代码
            message: 错误消息
            status_code: HTTP 状态码
            details: 错误详情
            exception: 异常对象
            log_level: 日志级别
            
        Returns:
            JSONResponse: 错误响应
        """
        # 构建错误响应
        error_detail = {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        }
        
        # 添加详情
        if details:
            error_detail["details"] = details
        
        # 调试模式下添加堆栈信息
        if self.debug and exception:
            error_detail["stack_trace"] = traceback.format_exc()
        
        # 记录日志
        log_message = f"错误处理: {code} - {message} - {request.method} {request.url.path}"
        if log_level == "error":
            logger.error(log_message, exc_info=exception)
        elif log_level == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # 返回 JSON 响应
        return JSONResponse(
            status_code=status_code,
            content={"error": error_detail}
        )


# 使用异常处理器方式（推荐）
def setup_exception_handlers(app: FastAPI, debug: bool = False):
    """
    为 FastAPI 应用设置异常处理器
    
    Args:
        app: FastAPI 应用实例
        debug: 是否启用调试模式
    """
    
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        """处理业务异常"""
        logger.warning(
            f"业务异常: {exc.code} - {exc.message} - {request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path,
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求验证错误"""
        logger.warning(
            f"验证错误: {request.method} {request.url.path} - {exc.errors()}"
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {"errors": exc.errors()},
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path,
                }
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理 HTTP 异常"""
        logger.warning(
            f"HTTP 异常: {exc.status_code} - {exc.detail} - {request.method} {request.url.path}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_EXCEPTION",
                    "message": exc.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path,
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理所有未捕获的异常"""
        logger.error(
            f"未处理异常: {type(exc).__name__} - {str(exc)} - {request.method} {request.url.path}",
            exc_info=True
        )
        
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path,
            }
        }
        
        # 调试模式下添加详细信息
        if debug:
            error_response["error"]["details"] = {
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "stack_trace": traceback.format_exc()
            }
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )


# ============================================================================
# Flask 实现
# ============================================================================

from flask import Flask, request as flask_request, jsonify


def setup_error_handlers(app: Flask, debug: bool = False):
    """
    为 Flask 应用设置错误处理器
    
    Args:
        app: Flask 应用实例
        debug: 是否启用调试模式
    """
    
    @app.errorhandler(BusinessException)
    def handle_business_exception(error: BusinessException):
        """处理业务异常"""
        logger.warning(
            f"业务异常: {error.code} - {error.message} - "
            f"{flask_request.method} {flask_request.path}"
        )
        
        response = jsonify({
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
                "timestamp": datetime.utcnow().isoformat(),
                "path": flask_request.path,
            }
        })
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """处理 404 错误"""
        logger.warning(f"404 错误: {flask_request.method} {flask_request.path}")
        
        response = jsonify({
            "error": {
                "code": "NOT_FOUND",
                "message": "The requested resource was not found",
                "timestamp": datetime.utcnow().isoformat(),
                "path": flask_request.path,
            }
        })
        response.status_code = 404
        return response
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """处理 405 错误"""
        logger.warning(
            f"405 错误: {flask_request.method} {flask_request.path} - "
            f"方法不允许"
        )
        
        response = jsonify({
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": f"Method {flask_request.method} is not allowed for this endpoint",
                "timestamp": datetime.utcnow().isoformat(),
                "path": flask_request.path,
            }
        })
        response.status_code = 405
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        """处理所有未捕获的异常"""
        logger.error(
            f"未处理异常: {type(error).__name__} - {str(error)} - "
            f"{flask_request.method} {flask_request.path}",
            exc_info=True
        )
        
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "path": flask_request.path,
            }
        }
        
        # 调试模式下添加详细信息
        if debug:
            error_response["error"]["details"] = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "stack_trace": traceback.format_exc()
            }
        
        response = jsonify(error_response)
        response.status_code = 500
        return response


# ============================================================================
# 示例应用
# ============================================================================

# FastAPI 示例
fastapi_app = FastAPI(title="错误处理中间件示例")

# 方式 1: 使用中间件
# fastapi_app.add_middleware(ErrorHandlerMiddleware, debug=True)

# 方式 2: 使用异常处理器（推荐）
setup_exception_handlers(fastapi_app, debug=True)


@fastapi_app.get("/")
async def root():
    """正常端点"""
    return {"message": "Hello World"}


@fastapi_app.get("/users/{user_id}")
async def get_user(user_id: str):
    """模拟获取用户 - 可能抛出资源未找到异常"""
    if user_id == "999":
        raise ResourceNotFoundException("User", user_id)
    return {"user_id": user_id, "name": "John Doe"}


@fastapi_app.post("/users")
async def create_user(user_data: dict):
    """模拟创建用户 - 可能抛出验证异常"""
    if "email" not in user_data:
        raise ValidationException(
            "Email is required",
            field_errors={"email": "This field is required"}
        )
    return {"user": user_data, "status": "created"}


@fastapi_app.get("/protected")
async def protected_endpoint():
    """模拟受保护端点 - 抛出未授权异常"""
    raise UnauthorizedException("Please login to access this resource")


@fastapi_app.get("/admin")
async def admin_endpoint():
    """模拟管理员端点 - 抛出禁止访问异常"""
    raise ForbiddenException("You don't have permission to access this resource")


@fastapi_app.get("/error")
async def error_endpoint():
    """模拟服务器错误"""
    # 故意触发除零错误
    result = 1 / 0
    return {"result": result}


# Flask 示例
flask_app = Flask(__name__)

# 设置错误处理器
setup_error_handlers(flask_app, debug=True)


@flask_app.route("/")
def flask_root():
    """正常端点"""
    return {"message": "Hello World"}


@flask_app.route("/users/<user_id>")
def flask_get_user(user_id):
    """模拟获取用户"""
    if user_id == "999":
        raise ResourceNotFoundException("User", user_id)
    return {"user_id": user_id, "name": "John Doe"}


@flask_app.route("/users", methods=["POST"])
def flask_create_user():
    """模拟创建用户"""
    user_data = flask_request.get_json()
    if not user_data or "email" not in user_data:
        raise ValidationException(
            "Email is required",
            field_errors={"email": "This field is required"}
        )
    return {"user": user_data, "status": "created"}


@flask_app.route("/protected")
def flask_protected():
    """模拟受保护端点"""
    raise UnauthorizedException("Please login to access this resource")


@flask_app.route("/admin")
def flask_admin():
    """模拟管理员端点"""
    raise ForbiddenException("You don't have permission to access this resource")


@flask_app.route("/error")
def flask_error():
    """模拟服务器错误"""
    result = 1 / 0
    return {"result": result}


# ============================================================================
# 运行说明
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("错误处理中间件示例")
    print("=" * 70)
    print("\n选择要运行的框架:")
    print("1. FastAPI (推荐使用 uvicorn 运行)")
    print("2. Flask")
    print("\nFastAPI 运行命令:")
    print("  uvicorn 02_error_handler:fastapi_app --reload")
    print("\nFlask 运行命令:")
    print("  python 02_error_handler.py")
    print("\n测试端点:")
    print("  GET  http://localhost:8000/              (正常响应)")
    print("  GET  http://localhost:8000/users/123     (正常响应)")
    print("  GET  http://localhost:8000/users/999     (404 错误)")
    print("  POST http://localhost:8000/users         (验证错误)")
    print("  GET  http://localhost:8000/protected     (401 错误)")
    print("  GET  http://localhost:8000/admin         (403 错误)")
    print("  GET  http://localhost:8000/error         (500 错误)")
    print("\n观察不同类型错误的统一响应格式")
    print("=" * 70)
    
    # 运行 Flask 应用
    flask_app.run(debug=True, port=5000)
