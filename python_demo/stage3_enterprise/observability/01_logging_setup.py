"""
结构化日志配置示例

本示例演示如何使用 structlog 实现结构化日志记录，包括：
1. 基础的 structlog 配置
2. 多种输出格式（JSON、控制台）
3. 日志级别和过滤
4. 上下文信息绑定
5. FastAPI 和 Flask 集成

安装依赖：
pip install structlog python-json-logger

作者：Python 学习课程
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict

import structlog


# ============================================================================
# 1. 基础 structlog 配置
# ============================================================================

def configure_basic_logging():
    """
    配置基础的结构化日志
    
    特点：
    - 使用 JSON 格式输出
    - 包含时间戳
    - 自动添加日志级别
    """
    structlog.configure(
        processors=[
            # 添加日志级别
            structlog.stdlib.add_log_level,
            # 添加时间戳
            structlog.processors.TimeStamper(fmt="iso"),
            # 格式化堆栈信息
            structlog.processors.StackInfoRenderer(),
            # 格式化异常信息
            structlog.processors.format_exc_info,
            # JSON 格式输出
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def basic_logging_example():
    """基础日志记录示例"""
    configure_basic_logging()
    logger = structlog.get_logger()
    
    # 记录不同级别的日志
    logger.debug("调试信息", module="example", function="basic_logging")
    logger.info("用户登录", user_id=123, username="alice", ip="192.168.1.1")
    logger.warning("磁盘空间不足", disk="/dev/sda1", usage_percent=85)
    logger.error("数据库连接失败", database="postgres", error="connection timeout")
    
    # 记录异常
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.exception("计算错误", operation="division", exc_info=e)


# ============================================================================
# 2. 开发环境友好的控制台输出
# ============================================================================

def configure_console_logging():
    """
    配置适合开发环境的控制台日志
    
    特点：
    - 彩色输出
    - 易读的格式
    - 包含关键信息
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=True)  # 彩色控制台输出
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def console_logging_example():
    """控制台日志示例"""
    configure_console_logging()
    logger = structlog.get_logger("my_app")
    
    logger.info("应用启动", version="1.0.0", environment="development")
    logger.info("数据库连接成功", host="localhost", port=5432)
    logger.warning("配置文件缺失，使用默认配置", config_file="config.yaml")


# ============================================================================
# 3. 生产环境 JSON 日志配置
# ============================================================================

def configure_production_logging(log_level: str = "INFO"):
    """
    配置生产环境的 JSON 日志
    
    特点：
    - JSON 格式，易于日志收集系统解析
    - 包含完整的上下文信息
    - 支持日志级别过滤
    
    Args:
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    # 配置标准库 logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # 配置 structlog
    structlog.configure(
        processors=[
            # 过滤低于指定级别的日志
            structlog.stdlib.filter_by_level,
            # 添加日志级别
            structlog.stdlib.add_log_level,
            # 添加日志记录器名称
            structlog.stdlib.add_logger_name,
            # 添加时间戳（ISO 8601 格式）
            structlog.processors.TimeStamper(fmt="iso"),
            # 格式化堆栈信息
            structlog.processors.StackInfoRenderer(),
            # 格式化异常信息
            structlog.processors.format_exc_info,
            # 添加调用者信息（可选，会影响性能）
            # structlog.processors.CallsiteParameterAdder(),
            # JSON 格式输出
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def production_logging_example():
    """生产环境日志示例"""
    configure_production_logging(log_level="INFO")
    logger = structlog.get_logger("production_app")
    
    # DEBUG 日志不会输出（因为级别设置为 INFO）
    logger.debug("详细调试信息", detail="这条日志不会显示")
    
    # INFO 及以上级别会输出
    logger.info(
        "API 请求",
        method="GET",
        path="/api/users",
        status_code=200,
        response_time_ms=45,
        user_id=123
    )
    
    logger.error(
        "支付失败",
        order_id="ORD-12345",
        amount=99.99,
        currency="USD",
        error_code="INSUFFICIENT_FUNDS"
    )


# ============================================================================
# 4. 上下文信息绑定
# ============================================================================

def context_binding_example():
    """
    上下文信息绑定示例
    
    演示如何绑定上下文信息，避免重复传递参数
    """
    configure_production_logging()
    logger = structlog.get_logger()
    
    # 绑定请求上下文
    request_logger = logger.bind(
        request_id="req-abc-123",
        user_id=456,
        ip="192.168.1.100"
    )
    
    # 后续日志会自动包含绑定的上下文
    request_logger.info("开始处理请求", endpoint="/api/orders")
    request_logger.info("查询数据库", table="orders", query_time_ms=12)
    request_logger.info("请求处理完成", status="success", duration_ms=150)
    
    # 可以继续添加更多上下文
    order_logger = request_logger.bind(order_id="ORD-789")
    order_logger.info("订单创建成功", amount=199.99)
    order_logger.info("发送确认邮件", email="user@example.com")


# ============================================================================
# 5. 自定义处理器
# ============================================================================

def add_app_context(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """
    自定义处理器：添加应用上下文信息
    
    Args:
        logger: 日志记录器
        method_name: 方法名
        event_dict: 事件字典
    
    Returns:
        更新后的事件字典
    """
    event_dict["app_name"] = "my_application"
    event_dict["app_version"] = "1.0.0"
    event_dict["environment"] = "production"
    return event_dict


def censor_sensitive_data(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """
    自定义处理器：过滤敏感信息
    
    Args:
        logger: 日志记录器
        method_name: 方法名
        event_dict: 事件字典
    
    Returns:
        过滤后的事件字典
    """
    sensitive_keys = ["password", "token", "secret", "api_key"]
    
    for key in sensitive_keys:
        if key in event_dict:
            event_dict[key] = "***REDACTED***"
    
    return event_dict


def configure_custom_logging():
    """配置带自定义处理器的日志"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            # 添加自定义处理器
            add_app_context,
            censor_sensitive_data,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def custom_processor_example():
    """自定义处理器示例"""
    configure_custom_logging()
    logger = structlog.get_logger()
    
    # 应用上下文会自动添加
    logger.info("用户登录", username="alice", user_id=123)
    
    # 敏感信息会被过滤
    logger.info(
        "API 调用",
        endpoint="/api/payment",
        api_key="sk_live_1234567890",  # 会被过滤
        password="secret123"  # 会被过滤
    )


# ============================================================================
# 6. FastAPI 集成
# ============================================================================

def setup_fastapi_logging():
    """
    FastAPI 应用的日志配置
    
    使用方法：
    from fastapi import FastAPI, Request
    import uuid
    
    app = FastAPI()
    setup_fastapi_logging()
    
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        
        # 绑定请求上下文
        logger = structlog.get_logger().bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host
        )
        
        # 记录请求开始
        logger.info("请求开始")
        
        # 处理请求
        response = await call_next(request)
        
        # 记录请求完成
        logger.info("请求完成", status_code=response.status_code)
        
        # 添加请求 ID 到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
    """
    configure_production_logging()
    
    # 示例代码（需要在实际 FastAPI 应用中使用）
    print("FastAPI 日志配置完成")
    print("请参考函数文档字符串中的使用示例")


# ============================================================================
# 7. Flask 集成
# ============================================================================

def setup_flask_logging():
    """
    Flask 应用的日志配置
    
    使用方法：
    from flask import Flask, request, g
    import uuid
    
    app = Flask(__name__)
    setup_flask_logging()
    
    @app.before_request
    def before_request():
        # 生成请求 ID
        g.request_id = str(uuid.uuid4())
        
        # 绑定请求上下文
        g.logger = structlog.get_logger().bind(
            request_id=g.request_id,
            method=request.method,
            path=request.path,
            client_ip=request.remote_addr
        )
        
        # 记录请求开始
        g.logger.info("请求开始")
    
    @app.after_request
    def after_request(response):
        # 记录请求完成
        g.logger.info("请求完成", status_code=response.status_code)
        
        # 添加请求 ID 到响应头
        response.headers["X-Request-ID"] = g.request_id
        
        return response
    """
    configure_production_logging()
    
    # 示例代码（需要在实际 Flask 应用中使用）
    print("Flask 日志配置完成")
    print("请参考函数文档字符串中的使用示例")


# ============================================================================
# 8. 日志轮转和文件输出
# ============================================================================

def configure_file_logging(log_file: str = "app.log"):
    """
    配置文件日志输出（带轮转）
    
    Args:
        log_file: 日志文件路径
    """
    from logging.handlers import RotatingFileHandler
    
    # 创建文件处理器（最大 10MB，保留 5 个备份）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # 配置标准库 logging
    logging.basicConfig(
        format="%(message)s",
        handlers=[file_handler, logging.StreamHandler(sys.stdout)],
        level=logging.INFO,
    )
    
    # 配置 structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def file_logging_example():
    """文件日志示例"""
    configure_file_logging("example.log")
    logger = structlog.get_logger()
    
    logger.info("日志将同时输出到控制台和文件")
    logger.info("文件会自动轮转，避免占用过多磁盘空间")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("=" * 80)
    print("1. 基础日志记录示例")
    print("=" * 80)
    basic_logging_example()
    
    print("\n" + "=" * 80)
    print("2. 控制台日志示例（开发环境）")
    print("=" * 80)
    console_logging_example()
    
    print("\n" + "=" * 80)
    print("3. 生产环境日志示例")
    print("=" * 80)
    production_logging_example()
    
    print("\n" + "=" * 80)
    print("4. 上下文信息绑定示例")
    print("=" * 80)
    context_binding_example()
    
    print("\n" + "=" * 80)
    print("5. 自定义处理器示例")
    print("=" * 80)
    custom_processor_example()
    
    print("\n" + "=" * 80)
    print("6. FastAPI 集成")
    print("=" * 80)
    setup_fastapi_logging()
    
    print("\n" + "=" * 80)
    print("7. Flask 集成")
    print("=" * 80)
    setup_flask_logging()
    
    print("\n" + "=" * 80)
    print("8. 文件日志示例")
    print("=" * 80)
    file_logging_example()
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
