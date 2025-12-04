"""
中间件集成示例应用

本模块演示如何在一个完整的应用中集成多个中间件，
展示中间件的执行顺序和协同工作。

集成的中间件：
1. CORS 中间件 - 处理跨域请求
2. Request ID 中间件 - 请求追踪
3. 请求日志中间件 - 记录请求信息
4. 错误处理中间件 - 统一错误处理
"""

import logging
import uuid
import time
from typing import Callable
from datetime import datetime
from contextvars import ContextVar

# ============================================================================
# FastAPI 完整集成示例
# ============================================================================

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s'
)


# Request ID 上下文变量
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)


class RequestIdFilter(logging.Filter):
    """日志过滤器，添加 Request ID"""
    def filter(self, record):
        record.request_id = request_id_var.get() or "N/A"
        return True


logger = logging.getLogger(__name__)
logger.addFilter(RequestIdFilter())


# 自定义异常
class BusinessException(Exception):
    """业务异常"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# 数据模型
class User(BaseModel):
    """用户模型"""
    name: str
    email: str
    age: int = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    name: str
    email: str
    age: int = None
    created_at: str


# ============================================================================
# 中间件实现
# ============================================================================

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Request ID 中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取或生成 Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求开始
        logger.info(
            f"请求开始: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        # 记录请求完成
        logger.info(
            f"请求完成: {request.method} {request.url.path} "
            f"- 状态码: {response.status_code} "
            f"- 耗时: {process_time:.3f}s"
        )
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except BusinessException as e:
            logger.warning(f"业务异常: {e.code} - {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.code,
                        "message": e.message,
                        "timestamp": datetime.utcnow().isoformat(),
                        "path": request.url.path,
                        "request_id": request_id_var.get(),
                    }
                }
            )
        except Exception as e:
            logger.error(f"未处理异常: {type(e).__name__} - {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "timestamp": datetime.utcnow().isoformat(),
                        "path": request.url.path,
                        "request_id": request_id_var.get(),
                    }
                }
            )


# ============================================================================
# 创建应用并配置中间件
# ============================================================================

app = FastAPI(
    title="中间件集成示例应用",
    description="演示多个中间件的集成和协同工作",
    version="1.0.0"
)

# 中间件注册顺序很重要！
# 按照以下顺序注册，确保正确的执行流程：

# 1. CORS 中间件（最先处理跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# 2. Request ID 中间件（尽早生成追踪 ID）
app.add_middleware(RequestIdMiddleware)

# 3. 请求日志中间件（记录完整请求信息）
app.add_middleware(RequestLoggingMiddleware)

# 4. 错误处理中间件（捕获所有异常）
app.add_middleware(ErrorHandlerMiddleware)


# ============================================================================
# 模拟数据存储
# ============================================================================

# 内存数据库
users_db = {}


# ============================================================================
# API 端点
# ============================================================================

@app.get("/")
async def root():
    """
    根路径
    
    返回 API 基本信息
    """
    logger.info("访问根路径")
    return {
        "message": "欢迎使用中间件集成示例 API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/api/users",
            "health": "/health",
            "error": "/error"
        }
    }


@app.get("/health")
async def health_check():
    """
    健康检查端点
    
    用于监控系统状态
    """
    logger.info("健康检查")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id_var.get()
    }


@app.get("/api/users", response_model=list[UserResponse])
async def get_users():
    """
    获取所有用户
    
    返回用户列表
    """
    logger.info(f"获取用户列表，当前用户数: {len(users_db)}")
    return list(users_db.values())


@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    获取指定用户
    
    Args:
        user_id: 用户 ID
        
    Returns:
        用户信息
        
    Raises:
        BusinessException: 用户不存在
    """
    logger.info(f"获取用户: {user_id}")
    
    if user_id not in users_db:
        raise BusinessException(
            code="USER_NOT_FOUND",
            message=f"User with id {user_id} not found",
            status_code=404
        )
    
    return users_db[user_id]


@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: User):
    """
    创建新用户
    
    Args:
        user: 用户信息
        
    Returns:
        创建的用户信息
        
    Raises:
        BusinessException: 邮箱已存在
    """
    logger.info(f"创建用户: {user.email}")
    
    # 检查邮箱是否已存在
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise BusinessException(
                code="EMAIL_EXISTS",
                message=f"User with email {user.email} already exists",
                status_code=400
            )
    
    # 创建用户
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "created_at": datetime.utcnow().isoformat()
    }
    
    users_db[user_id] = user_data
    logger.info(f"用户创建成功: {user_id}")
    
    return user_data


@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: User):
    """
    更新用户信息
    
    Args:
        user_id: 用户 ID
        user: 更新的用户信息
        
    Returns:
        更新后的用户信息
        
    Raises:
        BusinessException: 用户不存在
    """
    logger.info(f"更新用户: {user_id}")
    
    if user_id not in users_db:
        raise BusinessException(
            code="USER_NOT_FOUND",
            message=f"User with id {user_id} not found",
            status_code=404
        )
    
    # 更新用户信息
    users_db[user_id].update({
        "name": user.name,
        "email": user.email,
        "age": user.age,
    })
    
    logger.info(f"用户更新成功: {user_id}")
    return users_db[user_id]


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str):
    """
    删除用户
    
    Args:
        user_id: 用户 ID
        
    Returns:
        删除确认信息
        
    Raises:
        BusinessException: 用户不存在
    """
    logger.info(f"删除用户: {user_id}")
    
    if user_id not in users_db:
        raise BusinessException(
            code="USER_NOT_FOUND",
            message=f"User with id {user_id} not found",
            status_code=404
        )
    
    del users_db[user_id]
    logger.info(f"用户删除成功: {user_id}")
    
    return {"message": "User deleted successfully", "user_id": user_id}


@app.get("/error")
async def trigger_error():
    """
    触发错误端点
    
    用于测试错误处理中间件
    """
    logger.info("触发错误")
    # 故意触发异常
    raise Exception("This is a test error")


@app.get("/slow")
async def slow_endpoint():
    """
    慢速端点
    
    用于测试请求日志中间件的时间记录
    """
    logger.info("处理慢速请求")
    import asyncio
    await asyncio.sleep(2)
    return {"message": "This took 2 seconds"}


# ============================================================================
# 运行说明
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("中间件集成示例应用")
    print("=" * 70)
    print("\n运行命令:")
    print("  uvicorn integrated_app:app --reload --port 8000")
    print("\nAPI 文档:")
    print("  http://localhost:8000/docs")
    print("\n测试端点:")
    print("  GET    http://localhost:8000/")
    print("  GET    http://localhost:8000/health")
    print("  GET    http://localhost:8000/api/users")
    print("  POST   http://localhost:8000/api/users")
    print("  GET    http://localhost:8000/api/users/{user_id}")
    print("  PUT    http://localhost:8000/api/users/{user_id}")
    print("  DELETE http://localhost:8000/api/users/{user_id}")
    print("  GET    http://localhost:8000/error")
    print("  GET    http://localhost:8000/slow")
    print("\n测试示例:")
    print("\n1. 创建用户:")
    print('  curl -X POST http://localhost:8000/api/users \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"name": "Alice", "email": "alice@example.com", "age": 25}\'')
    print("\n2. 获取所有用户:")
    print('  curl http://localhost:8000/api/users')
    print("\n3. 测试错误处理:")
    print('  curl http://localhost:8000/api/users/999')
    print('  curl http://localhost:8000/error')
    print("\n4. 测试 Request ID:")
    print('  curl -H "X-Request-ID: my-custom-id" http://localhost:8000/')
    print("\n5. 测试跨域:")
    print('  curl -H "Origin: http://example.com" http://localhost:8000/')
    print("\n观察日志输出，查看中间件的执行过程：")
    print("  - Request ID 的生成和传递")
    print("  - 请求的开始和完成时间")
    print("  - 错误的捕获和处理")
    print("  - CORS 头的添加")
    print("=" * 70)
