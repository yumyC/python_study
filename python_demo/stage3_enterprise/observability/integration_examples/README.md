# 可观测性集成示例

本目录包含完整的可观测性集成示例，展示如何在实际应用中同时使用日志、指标和追踪。

## 示例列表

### 1. integrated_observability.py

完整的可观测性集成示例，包括：
- 统一的日志、指标和追踪配置
- FastAPI 应用集成
- Flask 应用集成
- 中间件实现
- 实际业务场景演示

## 运行示例

### 安装依赖

```bash
pip install structlog prometheus-client opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-flask
pip install fastapi flask uvicorn
```

### 运行集成示例

```bash
python integrated_observability.py
```

## 生产环境部署

### 1. 日志收集

使用 Elasticsearch + Kibana 或 Loki + Grafana：

```yaml
# docker-compose.yml
version: '3'
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
  
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
```

### 2. 指标收集

使用 Prometheus + Grafana：

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'my-app'
    static_configs:
      - targets: ['localhost:8000']
```

### 3. 追踪收集

使用 Jaeger：

```yaml
# docker-compose.yml
version: '3'
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # Collector
```

## 最佳实践

1. **统一配置**：使用配置文件或环境变量管理可观测性配置
2. **采样策略**：生产环境使用合理的采样率（1-10%）
3. **告警规则**：配置关键指标的告警规则
4. **数据保留**：根据需求设置合理的数据保留期
5. **性能影响**：监控可观测性组件的性能影响

## 相关资源

- [OpenTelemetry 文档](https://opentelemetry.io/docs/)
- [Prometheus 文档](https://prometheus.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [Jaeger 文档](https://www.jaegertracing.io/docs/)
