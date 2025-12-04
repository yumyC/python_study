# 可观测性模块

## 概述

可观测性（Observability）是指通过系统的外部输出来理解系统内部状态的能力。在现代分布式系统和微服务架构中，可观测性是保证系统稳定运行、快速定位问题的关键能力。可观测性的三大支柱是：日志（Logging）、指标（Metrics）和追踪（Tracing）。

## 学习目标

完成本模块学习后，你将能够：

- 理解可观测性的核心概念和三大支柱
- 使用 structlog 实现结构化日志记录
- 实现应用指标收集和监控
- 实现分布式追踪和链路追踪
- 集成多种可观测性工具构建完整的监控体系
- 掌握可观测性的最佳实践

## 可观测性三大支柱

### 1. 日志（Logging）

**定义**：记录系统运行过程中发生的离散事件

**特点**：
- 提供详细的上下文信息
- 适合问题排查和调试
- 可以记录任意格式的数据
- 存储成本相对较高

**应用场景**：
- 错误和异常追踪
- 业务事件记录
- 审计和合规
- 调试和问题定位

### 2. 指标（Metrics）

**定义**：系统在特定时间点的数值度量

**特点**：
- 数据量小，存储成本低
- 适合趋势分析和告警
- 可以进行聚合和统计
- 实时性强

**应用场景**：
- 性能监控（响应时间、吞吐量）
- 资源使用监控（CPU、内存、磁盘）
- 业务指标监控（订单量、用户数）
- 告警和自动化运维

### 3. 追踪（Tracing）

**定义**：记录请求在分布式系统中的完整调用链路

**特点**：
- 展示请求的完整生命周期
- 识别性能瓶颈
- 理解服务间依赖关系
- 适合分布式系统

**应用场景**：
- 分布式系统调试
- 性能优化
- 服务依赖分析
- 故障根因分析

## 可观测性架构

```
应用程序
    ├── 日志 → structlog → 日志收集器 → Elasticsearch/Loki
    ├── 指标 → Prometheus Client → Prometheus → Grafana
    └── 追踪 → OpenTelemetry → Jaeger/Zipkin
```

## 模块内容

### 1. 日志配置示例 (01_logging_setup.py)

**功能**：
- 配置 structlog 结构化日志
- 实现多种日志输出格式（JSON、控制台）
- 配置日志级别和过滤器
- 集成上下文信息（Request ID、用户信息）

**核心概念**：
- 结构化日志 vs 非结构化日志
- 日志级别（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- 日志处理器和格式化器
- 上下文变量绑定

### 2. 指标收集示例 (02_metrics_collection.py)

**功能**：
- 使用 Prometheus 客户端收集指标
- 实现常见指标类型（Counter、Gauge、Histogram、Summary）
- 收集 HTTP 请求指标
- 收集业务指标

**核心概念**：
- Counter：只增不减的计数器
- Gauge：可增可减的仪表盘
- Histogram：直方图，记录数值分布
- Summary：摘要，记录分位数

### 3. 追踪示例 (03_tracing.py)

**功能**：
- 使用 OpenTelemetry 实现分布式追踪
- 创建和管理 Span
- 记录追踪上下文
- 集成到 FastAPI/Flask 应用

**核心概念**：
- Trace：完整的请求链路
- Span：链路中的一个操作单元
- Context Propagation：上下文传播
- Sampling：采样策略

### 4. 可观测性工具集成示例

**功能**：
- 集成日志、指标和追踪
- 实现统一的可观测性中间件
- 配置多种后端存储
- 提供完整的监控方案

## 结构化日志最佳实践

### 1. 使用结构化格式

**推荐**：
```python
logger.info("user_login", user_id=123, ip="192.168.1.1", success=True)
```

**不推荐**：
```python
logger.info(f"User {user_id} logged in from {ip}")
```

### 2. 包含关键上下文

- Request ID：追踪请求链路
- User ID：识别用户行为
- Timestamp：精确时间戳
- Environment：环境标识（dev/staging/prod）

### 3. 合理使用日志级别

- **DEBUG**：详细的调试信息，仅开发环境使用
- **INFO**：重要的业务事件
- **WARNING**：警告信息，不影响正常运行
- **ERROR**：错误信息，需要关注
- **CRITICAL**：严重错误，需要立即处理

### 4. 避免敏感信息

不要记录：
- 密码和密钥
- 个人身份信息（PII）
- 信用卡号
- 其他敏感数据

## 指标收集最佳实践

### 1. 选择合适的指标类型

- **Counter**：请求总数、错误总数
- **Gauge**：当前在线用户数、队列长度
- **Histogram**：请求延迟、响应大小
- **Summary**：请求延迟的分位数

### 2. 使用有意义的标签

```python
http_requests_total.labels(
    method="GET",
    endpoint="/api/users",
    status="200"
).inc()
```

### 3. 避免高基数标签

不要使用：
- User ID
- Request ID
- Timestamp

这些会导致指标数量爆炸。

### 4. 监控关键业务指标

- 请求速率（RPS）
- 错误率
- 响应时间（P50、P95、P99）
- 资源使用率

## 分布式追踪最佳实践

### 1. 合理设置采样率

- 开发环境：100%
- 测试环境：50-100%
- 生产环境：1-10%（根据流量调整）

### 2. 记录关键操作

- HTTP 请求
- 数据库查询
- 外部 API 调用
- 消息队列操作

### 3. 添加有用的属性

```python
span.set_attribute("user.id", user_id)
span.set_attribute("db.query", query)
span.set_attribute("http.status_code", 200)
```

### 4. 处理错误

```python
try:
    # 业务逻辑
    pass
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR))
    raise
```

## 可观测性工具栈

### 日志工具

- **structlog**: Python 结构化日志库
- **python-json-logger**: JSON 格式日志
- **Elasticsearch**: 日志存储和搜索
- **Loki**: 轻量级日志聚合系统
- **Fluentd/Fluent Bit**: 日志收集器

### 指标工具

- **Prometheus**: 指标收集和存储
- **Grafana**: 指标可视化
- **StatsD**: 指标聚合
- **InfluxDB**: 时序数据库

### 追踪工具

- **OpenTelemetry**: 统一的可观测性框架
- **Jaeger**: 分布式追踪系统
- **Zipkin**: 分布式追踪系统
- **Tempo**: Grafana 的追踪后端

### 一体化方案

- **Datadog**: 商业 APM 平台
- **New Relic**: 商业 APM 平台
- **Elastic APM**: Elastic Stack 的 APM 方案
- **Grafana Stack**: Loki + Prometheus + Tempo

## FastAPI vs Flask 可观测性实现

### FastAPI 实现

**优势**：
- 原生支持异步
- 内置 OpenAPI 文档
- 更容易集成现代可观测性工具

**示例**：
```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# 自动收集指标
Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def add_observability(request: Request, call_next):
    # 添加追踪和日志
    response = await call_next(request)
    return response
```

### Flask 实现

**优势**：
- 生态成熟，扩展丰富
- 社区支持好

**示例**：
```python
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# 自动收集指标
metrics = PrometheusMetrics(app)

@app.before_request
def before_request():
    # 添加追踪和日志
    pass
```

## 实际应用场景

### 1. 问题排查

**场景**：用户报告某个 API 响应缓慢

**排查步骤**：
1. 查看日志，找到对应的 Request ID
2. 查看追踪，分析调用链路
3. 查看指标，确认是否有性能异常
4. 定位瓶颈，优化代码

### 2. 性能优化

**场景**：系统整体响应时间偏高

**优化步骤**：
1. 查看 P95/P99 响应时间指标
2. 分析追踪数据，找出慢查询
3. 查看日志，确认业务逻辑
4. 优化数据库查询或缓存策略

### 3. 容量规划

**场景**：预估系统能承载的最大流量

**分析步骤**：
1. 查看历史指标数据
2. 分析资源使用趋势
3. 进行压力测试
4. 制定扩容计划

### 4. 故障告警

**场景**：自动检测和通知系统异常

**实现方式**：
1. 配置告警规则（错误率、响应时间）
2. 设置告警阈值
3. 集成通知渠道（邮件、短信、Slack）
4. 建立值班和响应流程

## 学习资源

### 官方文档

- [structlog Documentation](https://www.structlog.org/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [FastAPI Observability](https://fastapi.tiangolo.com/advanced/middleware/)

### 推荐阅读

- 《Distributed Systems Observability》by Cindy Sridharan
- Google SRE Book - Monitoring Distributed Systems
- The Three Pillars of Observability
- OpenTelemetry 规范和最佳实践

### 相关工具

- **Grafana**: 可视化平台
- **Prometheus**: 指标监控
- **Jaeger**: 分布式追踪
- **ELK Stack**: 日志分析
- **OpenTelemetry**: 统一可观测性

## 实践建议

1. **从日志开始**：先实现结构化日志，这是最基础也是最重要的
2. **逐步添加指标**：识别关键业务指标，逐步完善监控体系
3. **引入追踪**：在分布式系统中引入追踪，理解服务依赖
4. **建立告警**：配置合理的告警规则，避免告警疲劳
5. **持续优化**：根据实际使用情况，不断优化可观测性配置
6. **团队培训**：确保团队成员都理解和使用可观测性工具

## 下一步

完成本模块学习后，建议：

1. 在 CRM 项目中集成完整的可观测性方案
2. 学习异步任务模块，了解后台任务的监控
3. 探索更多高级功能（如分布式追踪的采样策略）
4. 研究生产环境的可观测性最佳实践

## 常见问题

### Q1: 日志、指标和追踪应该选择哪个？

**A**: 三者不是互斥的，而是互补的。日志提供详细信息，指标提供趋势分析，追踪提供调用链路。建议都实现，构建完整的可观测性体系。

### Q2: 结构化日志和普通日志有什么区别？

**A**: 结构化日志使用键值对格式，易于机器解析和查询。普通日志是纯文本，难以自动化分析。结构化日志更适合现代日志分析系统。

### Q3: 如何选择指标类型？

**A**: Counter 用于累计值，Gauge 用于瞬时值，Histogram 用于分布统计，Summary 用于分位数计算。根据业务需求选择合适的类型。

### Q4: 分布式追踪会影响性能吗？

**A**: 会有一定影响，但通常很小（<1%）。可以通过采样策略降低影响，生产环境通常只追踪 1-10% 的请求。

### Q5: 如何避免日志过多？

**A**: 合理设置日志级别，生产环境使用 INFO 或 WARNING 级别。避免在循环中打印日志，使用采样或限流策略。

### Q6: 可观测性数据应该保存多久？

**A**: 根据需求和成本决定。建议：日志保存 7-30 天，指标保存 30-90 天，追踪保存 7-14 天。重要数据可以归档到冷存储。

## 总结

可观测性是构建可靠系统的基础，掌握可观测性技术能够帮助你：

- 快速定位和解决问题
- 理解系统的运行状态
- 优化系统性能
- 提升系统可靠性
- 支持数据驱动的决策

通过本模块的学习和实践，你将具备构建生产级可观测性系统的能力，为开发和运维高质量的应用打下坚实基础。

记住：**没有可观测性，就没有可靠性。**
