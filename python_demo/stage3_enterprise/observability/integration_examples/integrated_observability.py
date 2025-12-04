"""
完整的可观测性集成示例

本示例展示如何在实际应用中集成日志、指标和追踪，构建完整的可观测性体系。

包括：
1. 统一的可观测性配置
2. FastAPI 应用集成
3. Flask 应用集成
4. 可观测性中间件
5. 实际业务场景演示

安装依赖：
pip install structlog prometheus-client opentelemetry-api opentelemetry-sdk
pip install fastapi uvicorn flask

作者：Python 学习课程
"""

import time
import uuid
from typing import Callable
from contextlib import contextmanager

import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode


# ============================================================================
# 1. 统一的可观测性配置
# ============================================================================

class ObservabilityConfig:
    """可观测性配置类"""
    
    def __init__(self, service_name: str, environment: str = "development"):
        self.service_name = service_name
        self.environment = environment
        self.logger = None
        self.tracer = None
        
    def setup(self):
        """初始化所有可观测性组件"""
        self._setup_logging()
        self._setup_tracing()
        self._setup_metrics()
        
        print(f"✓ 可观测性配置完成")
        print(f"  服务名称: {self.service_name}")
        print(f"  环境: {self.environment}")
        print()
    
    def _setup_logging(self):
        """配置结构化日志"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger(self.service_name)
    
    def _setup_tracing(self):
        """配置分布式追踪"""
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": "1.0.0",
            "deployment.environment": self.environment
        })
        
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        self.tracer = trace.get_tracer(self.service_name)
    
    def _setup_metrics(self):
        """配置指标收集（指标在全局注册表中）"""
        pass  # Prometheus 指标是全局的，不需要特殊配置


# ============================================================================
# 2. 可观测性指标定义
# ============================================================================

class Metrics:
    """应用指标"""
    
    # HTTP 请求指标
    http_requests_total = Counter(
        'http_requests_total',
        'HTTP 请求总数',
        ['method', 'endpoint', 'status']
    )
    
    http_request_duration_seconds = Histogram(
        'http_request_duration_seconds',
        'HTTP 请求耗时',
        ['method', 'endpoint'],
        buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
    )
    
    http_requests_in_progress = Gauge(
        'http_requests_in_progress',
        '正在处理的请求数',
        ['method', 'endpoint']
    )
    
    # 业务指标
    orders_created_total = Counter(
        'orders_created_total',
        '创建的订单总数',
        ['status']
    )
    
    order_processing_duration_seconds = Histogram(
        'order_processing_duration_seconds',
        '订单处理耗时',
        buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
    )
    
    active_orders = Gauge(
        'active_orders',
        '当前活跃订单数'
    )


# ============================================================================
# 3. 可观测性中间件（通用）
# ============================================================================

class ObservabilityMiddleware:
    """可观测性中间件 - 集成日志、指标和追踪"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.logger = config.logger
        self.tracer = config.tracer
        self.metrics = Metrics()
    
    @contextmanager
    def track_request(self, method: str, path: str):
        """
        追踪请求的完整生命周期
        
        Args:
            method: HTTP 方法
            path: 请求路径
        """
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        
        # 绑定日志上下文
        logger = self.logger.bind(
            request_id=request_id,
            method=method,
            path=path
        )
        
        # 开始追踪
        with self.tracer.start_as_current_span(f"{method} {path}") as span:
            # 设置 Span 属性
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", path)
            span.set_attribute("request.id", request_id)
            
            # 增加进行中的请求数
            self.metrics.http_requests_in_progress.labels(
                method=method,
                endpoint=path
            ).inc()
            
            # 记录请求开始
            logger.info("请求开始")
            
            start_time = time.time()
            status_code = 500  # 默认错误状态
            
            try:
                # 执行请求处理
                yield {
                    'request_id': request_id,
                    'logger': logger,
                    'span': span
                }
                
                status_code = 200  # 成功状态
                span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                status_code = 500
                
                # 记录异常
                logger.exception("请求处理失败", error=str(e))
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                
                raise
            
            finally:
                # 计算耗时
                duration = time.time() - start_time
                
                # 记录指标
                self.metrics.http_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status=str(status_code)
                ).inc()
                
                self.metrics.http_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
                
                self.metrics.http_requests_in_progress.labels(
                    method=method,
                    endpoint=path
                ).dec()
                
                # 设置 Span 属性
                span.set_attribute("http.status_code", status_code)
                span.set_attribute("http.duration_ms", duration * 1000)
                
                # 记录请求完成
                logger.info(
                    "请求完成",
                    status_code=status_code,
                    duration_ms=duration * 1000
                )


# ============================================================================
# 4. 业务逻辑示例
# ============================================================================

class OrderService:
    """订单服务 - 演示业务逻辑中的可观测性"""
    
    def __init__(self, config: ObservabilityConfig):
        self.logger = config.logger
        self.tracer = config.tracer
        self.metrics = Metrics()
    
    def create_order(self, user_id: int, amount: float, request_context: dict):
        """
        创建订单
        
        Args:
            user_id: 用户 ID
            amount: 订单金额
            request_context: 请求上下文（包含 logger 和 span）
        """
        logger = request_context['logger'].bind(
            user_id=user_id,
            amount=amount
        )
        
        # 创建子 Span
        with self.tracer.start_as_current_span("create_order") as span:
            span.set_attribute("user.id", user_id)
            span.set_attribute("order.amount", amount)
            
            logger.info("开始创建订单")
            
            try:
                # 1. 验证用户
                self._validate_user(user_id, logger, span)
                
                # 2. 检查库存
                self._check_inventory(logger, span)
                
                # 3. 创建订单记录
                order_id = self._create_order_record(user_id, amount, logger, span)
                
                # 4. 处理支付
                self._process_payment(order_id, amount, logger, span)
                
                # 记录成功指标
                self.metrics.orders_created_total.labels(status='success').inc()
                self.metrics.active_orders.inc()
                
                logger.info("订单创建成功", order_id=order_id)
                span.set_status(Status(StatusCode.OK))
                
                return {"order_id": order_id, "status": "success"}
                
            except Exception as e:
                # 记录失败指标
                self.metrics.orders_created_total.labels(status='failure').inc()
                
                logger.error("订单创建失败", error=str(e))
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                
                raise
    
    def _validate_user(self, user_id: int, logger, parent_span):
        """验证用户"""
        with self.tracer.start_as_current_span("validate_user") as span:
            span.set_attribute("user.id", user_id)
            logger.info("验证用户", user_id=user_id)
            time.sleep(0.02)  # 模拟验证
            logger.info("用户验证通过")
    
    def _check_inventory(self, logger, parent_span):
        """检查库存"""
        with self.tracer.start_as_current_span("check_inventory") as span:
            logger.info("检查库存")
            time.sleep(0.03)  # 模拟检查
            logger.info("库存充足")
    
    def _create_order_record(self, user_id: int, amount: float, logger, parent_span):
        """创建订单记录"""
        with self.tracer.start_as_current_span("create_order_record") as span:
            span.set_attribute("db.system", "postgresql")
            span.set_attribute("db.statement", "INSERT INTO orders ...")
            
            logger.info("创建订单记录")
            time.sleep(0.05)  # 模拟数据库操作
            
            order_id = f"ORD-{uuid.uuid4().hex[:8]}"
            span.set_attribute("order.id", order_id)
            
            logger.info("订单记录已创建", order_id=order_id)
            return order_id
    
    def _process_payment(self, order_id: str, amount: float, logger, parent_span):
        """处理支付"""
        with self.tracer.start_as_current_span("process_payment") as span:
            span.set_attribute("payment.amount", amount)
            span.set_attribute("payment.method", "credit_card")
            
            logger.info("处理支付", order_id=order_id, amount=amount)
            time.sleep(0.08)  # 模拟支付处理
            logger.info("支付成功")


# ============================================================================
# 5. FastAPI 集成示例
# ============================================================================

def create_fastapi_app():
    """
    创建集成可观测性的 FastAPI 应用
    
    使用方法：
    from fastapi import FastAPI, Request
    from prometheus_client import make_asgi_app
    
    # 初始化可观测性
    config = ObservabilityConfig("my-fastapi-service", "production")
    config.setup()
    
    middleware = ObservabilityMiddleware(config)
    order_service = OrderService(config)
    
    app = FastAPI()
    
    # 添加可观测性中间件
    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        with middleware.track_request(request.method, request.url.path) as context:
            # 将上下文传递给请求
            request.state.observability = context
            response = await call_next(request)
            return response
    
    # 业务端点
    @app.post("/api/orders")
    async def create_order(request: Request, user_id: int, amount: float):
        context = request.state.observability
        result = order_service.create_order(user_id, amount, context)
        return result
    
    # 健康检查端点
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    # 指标端点
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    return app
    """
    print("FastAPI 集成示例：")
    print("-" * 60)
    print("✓ 请参考函数文档字符串中的完整示例")
    print("✓ 运行: uvicorn app:app --reload")
    print("✓ 访问: http://localhost:8000/docs")
    print("✓ 指标: http://localhost:8000/metrics")
    print()


# ============================================================================
# 6. Flask 集成示例
# ============================================================================

def create_flask_app():
    """
    创建集成可观测性的 Flask 应用
    
    使用方法：
    from flask import Flask, request, g, jsonify
    from prometheus_client import make_wsgi_app
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    
    # 初始化可观测性
    config = ObservabilityConfig("my-flask-service", "production")
    config.setup()
    
    middleware = ObservabilityMiddleware(config)
    order_service = OrderService(config)
    
    app = Flask(__name__)
    
    # 请求前处理
    @app.before_request
    def before_request():
        g.observability_context = middleware.track_request(
            request.method,
            request.path
        ).__enter__()
    
    # 请求后处理
    @app.after_request
    def after_request(response):
        if hasattr(g, 'observability_context'):
            # 这里需要手动处理上下文管理器的退出
            pass
        return response
    
    # 业务端点
    @app.route("/api/orders", methods=["POST"])
    def create_order():
        data = request.get_json()
        result = order_service.create_order(
            data['user_id'],
            data['amount'],
            g.observability_context
        )
        return jsonify(result)
    
    # 健康检查端点
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"})
    
    # 添加指标端点
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })
    
    return app
    """
    print("Flask 集成示例：")
    print("-" * 60)
    print("✓ 请参考函数文档字符串中的完整示例")
    print("✓ 运行: flask run")
    print("✓ 访问: http://localhost:5000")
    print("✓ 指标: http://localhost:5000/metrics")
    print()


# ============================================================================
# 7. 完整的业务场景演示
# ============================================================================

def demo_complete_observability():
    """演示完整的可观测性集成"""
    print("完整的可观测性演示：")
    print("=" * 80)
    
    # 初始化可观测性
    config = ObservabilityConfig("demo-service", "development")
    config.setup()
    
    middleware = ObservabilityMiddleware(config)
    order_service = OrderService(config)
    
    # 模拟多个请求
    print("\n模拟 API 请求：")
    print("-" * 60)
    
    # 请求 1: 成功创建订单
    with middleware.track_request("POST", "/api/orders") as context:
        try:
            result = order_service.create_order(123, 99.99, context)
            print(f"✓ 订单创建成功: {result['order_id']}")
        except Exception as e:
            print(f"✗ 订单创建失败: {e}")
    
    time.sleep(0.1)
    
    # 请求 2: 另一个成功的订单
    with middleware.track_request("POST", "/api/orders") as context:
        try:
            result = order_service.create_order(456, 199.99, context)
            print(f"✓ 订单创建成功: {result['order_id']}")
        except Exception as e:
            print(f"✗ 订单创建失败: {e}")
    
    time.sleep(0.1)
    
    # 请求 3: 查询订单（模拟）
    with middleware.track_request("GET", "/api/orders/123") as context:
        context['logger'].info("查询订单", order_id="123")
        time.sleep(0.02)
        print("✓ 订单查询成功")
    
    # 导出指标
    print("\n" + "=" * 80)
    print("Prometheus 指标（部分）：")
    print("-" * 60)
    metrics_output = generate_latest(REGISTRY).decode('utf-8')
    
    # 只显示我们定义的指标
    for line in metrics_output.split('\n'):
        if any(metric in line for metric in [
            'http_requests_total',
            'http_request_duration',
            'orders_created_total',
            'active_orders'
        ]) and not line.startswith('#'):
            print(line)
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("=" * 80)
    print("完整的可观测性集成示例")
    print("=" * 80)
    print()
    
    # 运行演示
    demo_complete_observability()
    
    print("\n" + "=" * 80)
    print("框架集成示例：")
    print("=" * 80)
    print()
    
    create_fastapi_app()
    create_flask_app()
    
    print("=" * 80)
    print("总结")
    print("=" * 80)
    print()
    print("本示例展示了如何构建完整的可观测性体系：")
    print()
    print("1. 日志（Logging）")
    print("   - 使用 structlog 实现结构化日志")
    print("   - 绑定请求上下文（Request ID、用户信息等）")
    print("   - 记录关键业务事件")
    print()
    print("2. 指标（Metrics）")
    print("   - 使用 Prometheus 收集 HTTP 请求指标")
    print("   - 收集业务指标（订单数、处理时间等）")
    print("   - 暴露 /metrics 端点供 Prometheus 抓取")
    print()
    print("3. 追踪（Tracing）")
    print("   - 使用 OpenTelemetry 实现分布式追踪")
    print("   - 创建父子 Span 展示调用链路")
    print("   - 记录详细的操作属性和事件")
    print()
    print("4. 统一集成")
    print("   - 通过中间件统一处理可观测性")
    print("   - 自动关联日志、指标和追踪")
    print("   - 提供一致的开发体验")
    print()
    print("下一步：")
    print("- 在实际项目中应用这些模式")
    print("- 配置 Prometheus、Grafana、Jaeger 等后端")
    print("- 建立告警规则和监控仪表板")
    print("- 持续优化可观测性配置")


if __name__ == "__main__":
    main()
