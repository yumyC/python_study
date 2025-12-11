"""
错误处理中间件

统一处理应用中的异常，提供友好的错误响应格式
"""

import logging
import traceback
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

from .request_id import get_request_id, get_logger_with_request_id

# 配置错误日志记录器
error_logger = logging.getLogger("error_handler")
error_logger.setLevel(logging.ERROR)

if not error_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    error_logger.addHandler(console_handler)

# 使用带 Request ID 的日志记录器
logger = get_logger_with_request_id(error_logger)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    错误处理中间件
    
    功能：
    1. 捕获所有未处理的异常
    2. 返回统一格式的错误响应
    3. 记录详细的错误日志
    4. 区分不同类型的异常并给出相应的处理
    5. 在生产环境中隐藏敏感的错误信息
    """
    
    def __init__(
        self,
        app: ASGIApp,
        debug: bool = False,
        include_traceback: bool = False
    ):
        """
        初始化错误处理中间件
        
        Args:
            app: ASGI 应用
            debug: 是否为调试模式
            include_traceback: 是否在响应中包含堆栈跟踪信息
        """
        super().__init__(app)
        self.debug = debug
        self.include_traceback = include_traceback or debug
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并捕获异常
        
        Args:
            request: HTTP 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            HTTP 响应对象
        """
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as exc:
            # FastAPI HTTP 异常，直接返回
            return await self._handle_http_exception(request, exc)
            
        except ValidationError as exc:
            # Pydantic 验证错误
            return await self._handle_validation_error(request, exc)
            
        except SQLAlchemyError as exc:
            # 数据库相关错误
            return await self._handle_database_error(request, exc)
            
        except Exception as exc:
            # 其他未知异常
            return await self._handle_generic_error(request, exc)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """
        处理 HTTP 异常
        
        Args:
            request: HTTP 请求对象
            exc: HTTP 异常
            
        Returns:
            JSON 响应
        """
        request_id = get_request_id()
        
        # 记录日志（4xx 错误用 warning，5xx 错误用 error）
        if exc.status_code >= 500:
            logger.error(f"HTTP {exc.status_code} error: {exc.detail}")
        else:
            logger.warning(f"HTTP {exc.status_code} error: {exc.detail}")
        
        error_response = {
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "request_id": request_id
            }
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )
    
    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """
        处理数据验证错误
        
        Args:
            request: HTTP 请求对象
            exc: 验证异常
            
        Returns:
            JSON 响应
        """
        request_id = get_request_id()
        
        logger.warning(f"Validation error: {str(exc)}")
        
        # 格式化验证错误信息
        errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"]
            })
        
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求数据验证失败",
                "details": errors,
                "request_id": request_id
            }
        }
        
        return JSONResponse(
            status_code=422,
            content=error_response
        )
    
    async def _handle_database_error(self, request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """
        处理数据库错误
        
        Args:
            request: HTTP 请求对象
            exc: 数据库异常
            
        Returns:
            JSON 响应
        """
        request_id = get_request_id()
        
        logger.error(f"Database error: {str(exc)}")
        
        # 根据异常类型返回不同的错误信息
        if isinstance(exc, IntegrityError):
            error_code = "INTEGRITY_ERROR"
            error_message = "数据完整性约束违反，可能存在重复数据或外键约束问题"
            status_code = 409  # Conflict
        else:
            error_code = "DATABASE_ERROR"
            error_message = "数据库操作失败"
            status_code = 500
        
        error_response = {
            "error": {
                "code": error_code,
                "message": error_message,
                "request_id": request_id
            }
        }
        
        # 在调试模式下包含详细错误信息
        if self.debug:
            error_response["error"]["details"] = str(exc)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    async def _handle_generic_error(self, request: Request, exc: Exception) -> JSONResponse:
        """
        处理通用异常
        
        Args:
            request: HTTP 请求对象
            exc: 异常对象
            
        Returns:
            JSON 响应
        """
        request_id = get_request_id()
        
        # 记录完整的错误信息和堆栈跟踪
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误",
                "request_id": request_id
            }
        }
        
        # 在调试模式下包含详细错误信息
        if self.debug:
            error_response["error"]["details"] = str(exc)
            
            if self.include_traceback:
                error_response["error"]["traceback"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )


class CustomException(Exception):
    """
    自定义异常基类
    
    用于定义业务相关的异常
    """
    
    def __init__(
        self,
        message: str,
        code: str = "CUSTOM_ERROR",
        status_code: int = 400,
        details: Dict[str, Any] = None
    ):
        """
        初始化自定义异常
        
        Args:
            message: 错误消息
            code: 错误代码
            status_code: HTTP 状态码
            details: 详细信息
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessLogicError(CustomException):
    """业务逻辑错误"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            code="BUSINESS_LOGIC_ERROR",
            status_code=400,
            details=details
        )


class ResourceNotFoundError(CustomException):
    """资源未找到错误"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} 未找到"
        if identifier:
            message += f"：{identifier}"
        
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier}
        )


class PermissionDeniedError(CustomException):
    """权限拒绝错误"""
    
    def __init__(self, action: str = None, resource: str = None):
        message = "权限不足"
        if action and resource:
            message += f"，无法对 {resource} 执行 {action} 操作"
        
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=403,
            details={"action": action, "resource": resource}
        )


async def handle_custom_exception(request: Request, exc: CustomException) -> JSONResponse:
    """
    处理自定义异常的函数
    
    Args:
        request: HTTP 请求对象
        exc: 自定义异常
        
    Returns:
        JSON 响应
    """
    request_id = get_request_id()
    
    logger.warning(f"Custom exception: {exc.code} - {exc.message}")
    
    error_response = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "request_id": request_id
        }
    }
    
    if exc.details:
        error_response["error"]["details"] = exc.details
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


def setup_error_handler(app, **kwargs):
    """
    设置错误处理中间件的便捷函数
    
    Args:
        app: FastAPI 应用实例
        **kwargs: 中间件配置参数
    """
    # 添加中间件
    app.add_middleware(ErrorHandlerMiddleware, **kwargs)
    
    # 注册自定义异常处理器
    app.add_exception_handler(CustomException, handle_custom_exception)
    app.add_exception_handler(BusinessLogicError, handle_custom_exception)
    app.add_exception_handler(ResourceNotFoundError, handle_custom_exception)
    app.add_exception_handler(PermissionDeniedError, handle_custom_exception)