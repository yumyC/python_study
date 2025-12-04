"""
分布式追踪示例

本示例演示如何使用 OpenTelemetry 实现分布式追踪，包括：
1. OpenTelemetry 基础配置
2. 创建和管理 Span
3. Span 属性和事件
4. 上下文传播
5. FastAPI 和 Flask 集成
6. 数据库和外部 API 调用追踪

安装依赖：
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation

作者：Python 学习课程
"""

import time
from typing import Dict, Any
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    BatchSpanProcessor,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode


# ============================================================================
# 1. 基础配置
# ============================================================================

def configure_tracing(service_name: str = "my-service"):
    """
    配置 OpenTelemetry 追踪
    
    Args:
        service_name: 服务名称
    """
    # 创建资源（标识服务）
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": "development"
    })
    
    # 创建 TracerProvider
    provider = TracerProvider(resource=resource)
    
    # 添加 Span 处理器（这里使用控制台输出，生产环境使用 Jaeger/Zipkin）
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    
    # 设置全局 TracerProvider
    trace.set_tracer_provider(provider)
    
    print(f"✓ 追踪配置完成，服务名称: {service_name}")
    print()


# ============================================================================
# 2. 创建和使用 Span
# ============================================================================

def basic_span_example():
    """基础 Span 使用示例"""
    print("基础 Span 示例：")
    print("-" * 60)
    
    # 获取 Tracer
    tracer = trace.get_tracer(__name__)
    
    # 创建 Span
    with tracer.start_as_current_span("process_order") as span:
        print("✓ 开始处理订单")
        
        # 添加属性
        span.set_attribute("order.id", "ORD-12345")
        span.set_attribute("order.amount", 99.99)
        span.set_attribute("order.currency", "USD")
        
        # 模拟处理
        time.sleep(0.1)
        
        # 添加事件
        span.add_event("订单验证完成")
        
        print("✓ 订单处理完成")
    
    print()


# ============================================================================
# 3. 嵌套 Span（父子关系）
# ============================================================================

def nested_span_example():
    """嵌套 Span 示例"""
    print("嵌套 Span 示例：")
    print("-" * 60)
    
    tracer = trace.get_tracer(__name__)
    
    # 父 Span
    with tracer.start_as_current_span("handle_request") as parent_span:
        parent_span.set_attribute("http.method", "POST")
        parent_span.set_attribute("http.url", "/api/orders")
        
        print("✓ 开始处理请求")
        
        # 子 Span 1: 验证用户
        with tracer.start_as_current_span("authenticate_user") as auth_span:
            auth_span.set_attribute("user.id", 123)
            time.sleep(0.05)
            print("  ✓ 用户认证完成")
        
        # 子 Span 2: 查询数据库
        with tracer.start_as_current_span("database_query") as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.statement", "SELECT * FROM orders WHERE id = $1")
            time.sleep(0.03)
            print("  ✓ 数据库查询完成")
        
        # 子 Span 3: 调用外部 API
        with tracer.start_as_current_span("external_api_call") as api_span:
            api_span.set_attribute("http.url", "https://api.payment.com/charge")
            api_span.set_attribute("http.method", "POST")
            time.sleep(0.08)
            print("  ✓ 外部 API 调用完成")
        
        parent_span.set_attribute("http.status_code", 200)
        print("✓ 请求处理完成")
    
    print()


# ============================================================================
# 4. Span 属性和事件
# ============================================================================

def span_attributes_events_example():
    """Span 属性和事件示例"""
    print("Span 属性和事件示例：")
    print("-" * 60)
    
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("process_payment") as span:
        # 设置多个属性
        span.set_attributes({
            "payment.method": "credit_card",
            "payment.amount": 199.99,
            "payment.currency": "USD",
            "customer.id": "CUST-456",
            "customer.tier": "premium"
        })
        
        print("✓ 开始处理支付")
        
        # 添加事件（带属性）
        span.add_event(
            "支付验证开始",
            attributes={
                "validation.type": "fraud_check",
                "validation.score": 0.95
            }
        )
        time.sleep(0.05)
        
        span.add_event(
            "支付验证通过",
            attributes={
                "validation.duration_ms": 50
            }
        )
        
        # 模拟支付处理
        time.sleep(0.1)
        
        span.add_event("支付处理完成")
        
        # 设置状态
        span.set_status(Status(StatusCode.OK))
        
        print("✓ 支付处理成功")
    
    print()


# ============================================================================
# 5. 错误处理和异常记录
# ============================================================================

def error_handling_example():
    """错误处理示例"""
    print("错误处理示例：")
    print("-" * 60)
    
    tracer = trace.get_tracer(__name__)
    
    # 成功的操作
    with tracer.start_as_current_span("successful_operation") as span:
        span.set_attribute("operation.type", "data_processing")
        time.sleep(0.05)
        span.set_status(Status(StatusCode.OK))
        print("✓ 操作成功")
    
    # 失败的操作
    with tracer.start_as_current_span("failed_operation") as span:
        span.set_attribute("operation.type", "database_write")
        
        try:
            # 模拟错误
            raise ValueError("数据库连接失败")
        except Exception as e:
            # 记录异常
            span.record_exception(e)
            
            # 设置错误状态
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            # 添加错误属性
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            
            print(f"✗ 操作失败: {e}")
    
    print()


# ============================================================================
# 6. 数据库操作追踪
# ============================================================================

class DatabaseTracer:
    """数据库操作追踪器"""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    @contextmanager
    def trace_query(self, query: str, params: Dict[str, Any] = None):
        """
        追踪数据库查询
        
        Args:
            query: SQL 查询语句
            params: 查询参数
        """
        with self.tracer.start_as_current_span("database.query") as span:
            # 设置数据库相关属性
            span.set_attribute("db.system", "postgresql")
            span.set_attribute("db.name", "myapp")
            span.set_attribute("db.statement", query)
            
            if params:
                span.set_attribute("db.params", str(params))
            
            start_time = time.time()
            
            try:
                yield span
                
                # 记录查询时间
                duration = time.time() - start_time
                span.set_attribute("db.duration_ms", duration * 1000)
                span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise


def database_tracing_example():
    """数据库追踪示例"""
    print("数据库追踪示例：")
    print("-" * 60)
    
    db_tracer = DatabaseTracer()
    
    # 查询操作
    with db_tracer.trace_query(
        "SELECT * FROM users WHERE id = $1",
        {"id": 123}
    ):
        time.sleep(0.02)  # 模拟查询
        print("✓ 查询用户信息")
    
    # 插入操作
    with db_tracer.trace_query(
        "INSERT INTO orders (user_id, amount) VALUES ($1, $2)",
        {"user_id": 123, "amount": 99.99}
    ):
        time.sleep(0.03)  # 模拟插入
        print("✓ 创建订单")
    
    # 更新操作
    with db_tracer.trace_query(
        "UPDATE orders SET status = $1 WHERE id = $2",
        {"status": "completed", "id": 456}
    ):
        time.sleep(0.025)  # 模拟更新
        print("✓ 更新订单状态")
    
    print()


# ============================================================================
# 7. HTTP 客户端追踪
# ============================================================================

class HTTPClientTracer:
    """HTTP 客户端追踪器"""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    @contextmanager
    def trace_request(self, method: str, url: str, headers: Dict[str, str] = None):
        """
        追踪 HTTP 请求
        
        Args:
            method: HTTP 方法
            url: 请求 URL
            headers: 请求头
        """
        with self.tracer.start_as_current_span("http.client.request") as span:
            # 设置 HTTP 相关属性
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", url)
            span.set_attribute("http.scheme", "https")
            
            if headers:
                span.set_attribute("http.request.headers", str(headers))
            
            start_time = time.time()
            
            try:
                yield span
                
                # 记录请求时间
                duration = time.time() - start_time
                span.set_attribute("http.duration_ms", duration * 1000)
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise


def http_client_tracing_example():
    """HTTP 客户端追踪示例"""
    print("HTTP 客户端追踪示例：")
    print("-" * 60)
    
    http_tracer = HTTPClientTracer()
    
    # GET 请求
    with http_tracer.trace_request("GET", "https://api.example.com/users/123") as span:
        time.sleep(0.05)  # 模拟请求
        span.set_attribute("http.status_code", 200)
        span.set_attribute("http.response.size", 1024)
        span.set_status(Status(StatusCode.OK))
        print("✓ GET 请求成功")
    
    # POST 请求
    with http_tracer.trace_request(
        "POST",
        "https://api.example.com/orders",
        headers={"Content-Type": "application/json"}
    ) as span:
        time.sleep(0.08)  # 模拟请求
        span.set_attribute("http.status_code", 201)
        span.set_status(Status(StatusCode.OK))
        print("✓ POST 请求成功")
    
    print()


# ============================================================================
# 8. FastAPI 集成
# ============================================================================

def setup_fastapi_tracing():
    """
    FastAPI 应用的追踪配置
    
    使用方法：
    from fastapi import FastAPI, Request
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    
    app = FastAPI()
    
    # 配置追踪
    configure_tracing("my-fastapi-service")
    
    # 自动注入追踪（推荐）
    FastAPIInstrumentor.instrument_app(app)
    
    # 或者手动实现中间件
    @app.middleware("http")
    async def tracing_middleware(request: Request, call_next):
        tracer = trace.get_tracer(__name__)
        
        with tracer.start_as_current_span(
            f"{request.method} {request.url.path}"
        ) as span:
            # 设置请求属性
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.scheme", request.url.scheme)
            span.set_attribute("http.host", request.url.hostname)
            
            # 处理请求
            response = await call_next(request)
            
            # 设置响应属性
            span.set_attribute("http.status_code", response.status_code)
            
            return response
    
    @app.get("/api/users/{user_id}")
    async def get_user(user_id: int):
        tracer = trace.get_tracer(__name__)
        
        # 在路由处理中创建子 Span
        with tracer.start_as_current_span("get_user_from_db"):
            # 数据库查询逻辑
            pass
        
        return {"user_id": user_id}
    """
    print("FastAPI 追踪配置：")
    print("-" * 60)
    print("✓ 配置完成")
    print("✓ 推荐使用 FastAPIInstrumentor 自动注入")
    print("✓ 请参考函数文档字符串中的使用示例")
    print()


# ============================================================================
# 9. Flask 集成
# ============================================================================

def setup_flask_tracing():
    """
    Flask 应用的追踪配置
    
    使用方法：
    from flask import Flask, request, g
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    
    app = Flask(__name__)
    
    # 配置追踪
    configure_tracing("my-flask-service")
    
    # 自动注入追踪（推荐）
    FlaskInstrumentor().instrument_app(app)
    
    # 或者手动实现
    @app.before_request
    def before_request():
        tracer = trace.get_tracer(__name__)
        g.span = tracer.start_span(f"{request.method} {request.path}")
        g.span.__enter__()
        
        # 设置请求属性
        g.span.set_attribute("http.method", request.method)
        g.span.set_attribute("http.url", request.url)
        g.span.set_attribute("http.scheme", request.scheme)
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'span'):
            # 设置响应属性
            g.span.set_attribute("http.status_code", response.status_code)
            g.span.__exit__(None, None, None)
        
        return response
    
    @app.route("/api/users/<int:user_id>")
    def get_user(user_id):
        tracer = trace.get_tracer(__name__)
        
        # 在路由处理中创建子 Span
        with tracer.start_as_current_span("get_user_from_db"):
            # 数据库查询逻辑
            pass
        
        return {"user_id": user_id}
    """
    print("Flask 追踪配置：")
    print("-" * 60)
    print("✓ 配置完成")
    print("✓ 推荐使用 FlaskInstrumentor 自动注入")
    print("✓ 请参考函数文档字符串中的使用示例")
    print()


# ============================================================================
# 10. 完整的请求追踪示例
# ============================================================================

def complete_request_tracing_example():
    """完整的请求追踪示例"""
    print("完整的请求追踪示例：")
    print("-" * 60)
    
    tracer = trace.get_tracer(__name__)
    db_tracer = DatabaseTracer()
    http_tracer = HTTPClientTracer()
    
    # 模拟完整的 API 请求处理流程
    with tracer.start_as_current_span("POST /api/orders") as root_span:
        root_span.set_attributes({
            "http.method": "POST",
            "http.url": "/api/orders",
            "http.scheme": "https",
            "user.id": 123
        })
        
        print("✓ 收到创建订单请求")
        
        # 1. 认证用户
        with tracer.start_as_current_span("authenticate") as auth_span:
            auth_span.set_attribute("auth.method", "jwt")
            time.sleep(0.02)
            print("  ✓ 用户认证成功")
        
        # 2. 验证库存（调用外部服务）
        with http_tracer.trace_request(
            "GET",
            "https://inventory.example.com/api/check"
        ) as inventory_span:
            time.sleep(0.05)
            inventory_span.set_attribute("http.status_code", 200)
            inventory_span.set_status(Status(StatusCode.OK))
            print("  ✓ 库存验证通过")
        
        # 3. 创建订单（数据库操作）
        with db_tracer.trace_query(
            "INSERT INTO orders (user_id, amount, status) VALUES ($1, $2, $3)",
            {"user_id": 123, "amount": 99.99, "status": "pending"}
        ):
            time.sleep(0.03)
            print("  ✓ 订单创建成功")
        
        # 4. 处理支付（调用支付服务）
        with http_tracer.trace_request(
            "POST",
            "https://payment.example.com/api/charge"
        ) as payment_span:
            time.sleep(0.08)
            payment_span.set_attribute("http.status_code", 200)
            payment_span.set_attribute("payment.amount", 99.99)
            payment_span.set_status(Status(StatusCode.OK))
            print("  ✓ 支付处理成功")
        
        # 5. 更新订单状态
        with db_tracer.trace_query(
            "UPDATE orders SET status = $1 WHERE id = $2",
            {"status": "completed", "id": 456}
        ):
            time.sleep(0.02)
            print("  ✓ 订单状态已更新")
        
        # 6. 发送通知
        with tracer.start_as_current_span("send_notification") as notif_span:
            notif_span.set_attribute("notification.type", "email")
            notif_span.set_attribute("notification.recipient", "user@example.com")
            time.sleep(0.04)
            print("  ✓ 通知已发送")
        
        root_span.set_attribute("http.status_code", 201)
        root_span.set_attribute("order.id", "ORD-456")
        root_span.set_status(Status(StatusCode.OK))
        
        print("✓ 订单创建流程完成")
    
    print()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("=" * 80)
    print("OpenTelemetry 分布式追踪示例")
    print("=" * 80)
    print()
    
    # 配置追踪
    configure_tracing("demo-service")
    
    # 运行示例
    basic_span_example()
    nested_span_example()
    span_attributes_events_example()
    error_handling_example()
    database_tracing_example()
    http_client_tracing_example()
    setup_fastapi_tracing()
    setup_flask_tracing()
    complete_request_tracing_example()
    
    print("=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)
    print()
    print("提示：")
    print("1. 生产环境中，使用 Jaeger 或 Zipkin 作为追踪后端")
    print("2. 配置合理的采样率，避免性能影响")
    print("3. 使用自动注入库简化集成（FastAPIInstrumentor、FlaskInstrumentor）")
    print("4. 在分布式系统中，确保上下文正确传播")


if __name__ == "__main__":
    main()
