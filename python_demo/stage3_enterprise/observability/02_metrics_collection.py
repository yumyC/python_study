"""
指标收集示例

本示例演示如何使用 Prometheus 客户端收集应用指标，包括：
1. 四种基本指标类型（Counter、Gauge、Histogram、Summary）
2. HTTP 请求指标收集
3. 业务指标收集
4. 自定义指标和标签
5. FastAPI 和 Flask 集成

安装依赖：
pip install prometheus-client

作者：Python 学习课程
"""

import random
import time
from typing import Callable

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
    REGISTRY,
    CollectorRegistry,
    push_to_gateway,
)


# ============================================================================
# 1. Counter - 计数器（只增不减）
# ============================================================================

# 定义 Counter 指标
http_requests_total = Counter(
    'http_requests_total',
    'HTTP 请求总数',
    ['method', 'endpoint', 'status']  # 标签
)

user_login_total = Counter(
    'user_login_total',
    '用户登录总数',
    ['status']  # success 或 failure
)


def counter_example():
    """Counter 使用示例"""
    print("Counter 示例：")
    print("-" * 60)
    
    # 增加计数
    http_requests_total.labels(method='GET', endpoint='/api/users', status='200').inc()
    http_requests_total.labels(method='POST', endpoint='/api/users', status='201').inc()
    http_requests_total.labels(method='GET', endpoint='/api/users', status='200').inc()
    
    # 增加指定数量
    http_requests_total.labels(method='GET', endpoint='/api/orders', status='200').inc(5)
    
    # 用户登录统计
    user_login_total.labels(status='success').inc(10)
    user_login_total.labels(status='failure').inc(2)
    
    print("✓ 记录了多个 HTTP 请求")
    print("✓ 记录了用户登录统计")
    print()


# ============================================================================
# 2. Gauge - 仪表盘（可增可减）
# ============================================================================

# 定义 Gauge 指标
active_users = Gauge(
    'active_users',
    '当前在线用户数'
)

queue_size = Gauge(
    'queue_size',
    '队列大小',
    ['queue_name']
)

cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'CPU 使用率'
)


def gauge_example():
    """Gauge 使用示例"""
    print("Gauge 示例：")
    print("-" * 60)
    
    # 设置值
    active_users.set(150)
    print(f"✓ 当前在线用户数: {150}")
    
    # 增加
    active_users.inc(10)  # 增加 10
    print(f"✓ 用户上线，当前在线: {160}")
    
    # 减少
    active_users.dec(5)  # 减少 5
    print(f"✓ 用户下线，当前在线: {155}")
    
    # 带标签的 Gauge
    queue_size.labels(queue_name='email').set(25)
    queue_size.labels(queue_name='sms').set(10)
    print(f"✓ 邮件队列大小: 25")
    print(f"✓ 短信队列大小: 10")
    
    # 模拟 CPU 使用率
    cpu_usage_percent.set(random.uniform(20, 80))
    print(f"✓ CPU 使用率已更新")
    print()


# ============================================================================
# 3. Histogram - 直方图（记录数值分布）
# ============================================================================

# 定义 Histogram 指标
request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP 请求耗时（秒）',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)  # 自定义桶
)

response_size_bytes = Histogram(
    'response_size_bytes',
    'HTTP 响应大小（字节）',
    buckets=(100, 1000, 10000, 100000, 1000000)
)


def histogram_example():
    """Histogram 使用示例"""
    print("Histogram 示例：")
    print("-" * 60)
    
    # 记录请求耗时
    request_duration_seconds.labels(method='GET', endpoint='/api/users').observe(0.045)
    request_duration_seconds.labels(method='GET', endpoint='/api/users').observe(0.032)
    request_duration_seconds.labels(method='POST', endpoint='/api/orders').observe(0.156)
    request_duration_seconds.labels(method='GET', endpoint='/api/products').observe(0.089)
    
    print("✓ 记录了多个请求耗时")
    
    # 记录响应大小
    response_size_bytes.observe(1024)
    response_size_bytes.observe(5120)
    response_size_bytes.observe(15360)
    
    print("✓ 记录了响应大小")
    
    # 使用装饰器计时
    @request_duration_seconds.labels(method='GET', endpoint='/api/stats').time()
    def get_stats():
        """模拟 API 调用"""
        time.sleep(0.1)
        return {"status": "ok"}
    
    result = get_stats()
    print("✓ 使用装饰器自动计时")
    print()


# ============================================================================
# 4. Summary - 摘要（记录分位数）
# ============================================================================

# 定义 Summary 指标
request_latency_seconds = Summary(
    'request_latency_seconds',
    'HTTP 请求延迟（秒）',
    ['endpoint']
)

database_query_duration = Summary(
    'database_query_duration_seconds',
    '数据库查询耗时（秒）',
    ['query_type']
)


def summary_example():
    """Summary 使用示例"""
    print("Summary 示例：")
    print("-" * 60)
    
    # 记录请求延迟
    for _ in range(100):
        latency = random.uniform(0.01, 0.5)
        request_latency_seconds.labels(endpoint='/api/users').observe(latency)
    
    print("✓ 记录了 100 个请求延迟样本")
    
    # 记录数据库查询耗时
    database_query_duration.labels(query_type='SELECT').observe(0.023)
    database_query_duration.labels(query_type='INSERT').observe(0.045)
    database_query_duration.labels(query_type='UPDATE').observe(0.038)
    
    print("✓ 记录了数据库查询耗时")
    
    # 使用装饰器计时
    @database_query_duration.labels(query_type='SELECT').time()
    def query_users():
        """模拟数据库查询"""
        time.sleep(0.02)
        return []
    
    query_users()
    print("✓ 使用装饰器自动计时")
    print()


# ============================================================================
# 5. 业务指标示例
# ============================================================================

# 订单相关指标
orders_created_total = Counter(
    'orders_created_total',
    '创建的订单总数',
    ['status']
)

order_amount_total = Counter(
    'order_amount_total',
    '订单总金额',
    ['currency']
)

active_orders = Gauge(
    'active_orders',
    '当前活跃订单数'
)

order_processing_duration = Histogram(
    'order_processing_duration_seconds',
    '订单处理耗时（秒）',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)


def business_metrics_example():
    """业务指标示例"""
    print("业务指标示例：")
    print("-" * 60)
    
    # 模拟订单创建
    orders_created_total.labels(status='success').inc()
    order_amount_total.labels(currency='USD').inc(99.99)
    active_orders.inc()
    
    print("✓ 订单创建成功，金额: $99.99")
    
    # 模拟订单处理
    start_time = time.time()
    time.sleep(0.1)  # 模拟处理时间
    duration = time.time() - start_time
    order_processing_duration.observe(duration)
    
    print(f"✓ 订单处理完成，耗时: {duration:.3f}秒")
    
    # 订单完成
    active_orders.dec()
    print("✓ 订单已完成，活跃订单数减少")
    print()


# ============================================================================
# 6. HTTP 请求指标收集（通用模式）
# ============================================================================

class HTTPMetrics:
    """HTTP 请求指标收集器"""
    
    def __init__(self):
        self.requests_total = Counter(
            'http_requests_total',
            'HTTP 请求总数',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP 请求耗时',
            ['method', 'endpoint'],
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
        )
        
        self.requests_in_progress = Gauge(
            'http_requests_in_progress',
            '正在处理的 HTTP 请求数',
            ['method', 'endpoint']
        )
        
        self.response_size = Histogram(
            'http_response_size_bytes',
            'HTTP 响应大小',
            ['method', 'endpoint']
        )
    
    def track_request(self, method: str, endpoint: str, status: int, 
                     duration: float, response_size: int):
        """
        记录 HTTP 请求指标
        
        Args:
            method: HTTP 方法
            endpoint: 端点路径
            status: 状态码
            duration: 请求耗时（秒）
            response_size: 响应大小（字节）
        """
        self.requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        self.response_size.labels(
            method=method,
            endpoint=endpoint
        ).observe(response_size)


def http_metrics_example():
    """HTTP 指标收集示例"""
    print("HTTP 指标收集示例：")
    print("-" * 60)
    
    metrics = HTTPMetrics()
    
    # 模拟多个 HTTP 请求
    requests = [
        ('GET', '/api/users', 200, 0.045, 1024),
        ('GET', '/api/users', 200, 0.032, 2048),
        ('POST', '/api/users', 201, 0.156, 512),
        ('GET', '/api/orders', 200, 0.089, 4096),
        ('DELETE', '/api/orders/123', 204, 0.023, 0),
    ]
    
    for method, endpoint, status, duration, size in requests:
        metrics.track_request(method, endpoint, status, duration, size)
        print(f"✓ {method} {endpoint} - {status} ({duration}s, {size} bytes)")
    
    print()


# ============================================================================
# 7. FastAPI 集成
# ============================================================================

def setup_fastapi_metrics():
    """
    FastAPI 应用的指标收集配置
    
    使用方法：
    from fastapi import FastAPI, Request
    from prometheus_client import make_asgi_app
    import time
    
    app = FastAPI()
    
    # 创建指标收集器
    metrics = HTTPMetrics()
    
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        # 记录开始时间
        start_time = time.time()
        
        # 增加进行中的请求数
        metrics.requests_in_progress.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算耗时
        duration = time.time() - start_time
        
        # 记录指标
        metrics.track_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration,
            response_size=int(response.headers.get('content-length', 0))
        )
        
        # 减少进行中的请求数
        metrics.requests_in_progress.labels(
            method=request.method,
            endpoint=request.url.path
        ).dec()
        
        return response
    
    # 暴露指标端点
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    """
    print("FastAPI 指标收集配置：")
    print("-" * 60)
    print("✓ 配置完成")
    print("✓ 指标端点: /metrics")
    print("✓ 请参考函数文档字符串中的使用示例")
    print()


# ============================================================================
# 8. Flask 集成
# ============================================================================

def setup_flask_metrics():
    """
    Flask 应用的指标收集配置
    
    使用方法：
    from flask import Flask, request, g
    from prometheus_client import make_wsgi_app
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    import time
    
    app = Flask(__name__)
    
    # 创建指标收集器
    metrics = HTTPMetrics()
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        metrics.requests_in_progress.labels(
            method=request.method,
            endpoint=request.path
        ).inc()
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        
        metrics.track_request(
            method=request.method,
            endpoint=request.path,
            status=response.status_code,
            duration=duration,
            response_size=response.content_length or 0
        )
        
        metrics.requests_in_progress.labels(
            method=request.method,
            endpoint=request.path
        ).dec()
        
        return response
    
    # 暴露指标端点
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })
    """
    print("Flask 指标收集配置：")
    print("-" * 60)
    print("✓ 配置完成")
    print("✓ 指标端点: /metrics")
    print("✓ 请参考函数文档字符串中的使用示例")
    print()


# ============================================================================
# 9. 导出指标
# ============================================================================

def export_metrics():
    """导出 Prometheus 格式的指标"""
    print("导出指标：")
    print("-" * 60)
    
    # 生成 Prometheus 格式的指标
    metrics_output = generate_latest(REGISTRY)
    
    print("Prometheus 格式指标（部分）：")
    print(metrics_output.decode('utf-8')[:500])
    print("...")
    print()
    
    # 保存到文件
    with open('metrics.txt', 'wb') as f:
        f.write(metrics_output)
    
    print("✓ 指标已保存到 metrics.txt")
    print()


# ============================================================================
# 10. 推送指标到 Pushgateway（可选）
# ============================================================================

def push_metrics_example():
    """
    推送指标到 Pushgateway
    
    适用场景：
    - 短期运行的批处理任务
    - 无法被 Prometheus 主动抓取的服务
    
    使用方法：
    from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
    
    registry = CollectorRegistry()
    g = Gauge('job_last_success_unixtime', 'Last time a job succeeded', registry=registry)
    g.set_to_current_time()
    
    push_to_gateway('localhost:9091', job='batch_job', registry=registry)
    """
    print("推送指标到 Pushgateway：")
    print("-" * 60)
    print("✓ 适用于批处理任务和短期运行的服务")
    print("✓ 请参考函数文档字符串中的使用示例")
    print("✓ 需要先启动 Pushgateway 服务")
    print()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("=" * 80)
    print("Prometheus 指标收集示例")
    print("=" * 80)
    print()
    
    counter_example()
    gauge_example()
    histogram_example()
    summary_example()
    business_metrics_example()
    http_metrics_example()
    setup_fastapi_metrics()
    setup_flask_metrics()
    export_metrics()
    push_metrics_example()
    
    print("=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)
    print()
    print("提示：")
    print("1. 在生产环境中，Prometheus 会定期抓取 /metrics 端点")
    print("2. 使用 Grafana 可视化这些指标")
    print("3. 配置告警规则，在指标异常时发送通知")
    print("4. 查看 metrics.txt 文件了解 Prometheus 格式")


if __name__ == "__main__":
    main()
