# 异步任务模块

## 概述

异步任务（Async Tasks）是指在后台执行的非阻塞任务，不会影响主应用的响应速度。在 Web 应用中，某些操作可能需要较长时间才能完成（如发送邮件、生成报表、处理大文件等），如果在请求处理过程中同步执行这些操作，会导致用户等待时间过长，影响用户体验。通过异步任务，可以立即返回响应给用户，而将耗时操作放到后台执行。

## 学习目标

完成本模块学习后，你将能够：

- 理解异步任务的工作原理和应用场景
- 掌握 Celery 分布式任务队列的使用
- 配置 Redis 作为消息代理和结果后端
- 实现基本的异步任务
- 实现任务队列和任务优先级
- 实现定时任务和周期性任务
- 监控和管理异步任务的执行状态
- 处理任务失败和重试机制

## 异步任务工作原理

### 基本架构

```
Web 应用
    ↓ (发送任务)
消息代理 (Redis/RabbitMQ)
    ↓ (分发任务)
Celery Worker (多个)
    ↓ (执行任务)
结果后端 (Redis/Database)
    ↓ (查询结果)
Web 应用
```

### 核心组件

1. **任务生产者（Producer）**：Web 应用，负责创建和发送任务
2. **消息代理（Broker）**：Redis 或 RabbitMQ，负责存储和分发任务
3. **任务消费者（Worker）**：Celery Worker，负责执行任务
4. **结果后端（Backend）**：存储任务执行结果

## 模块内容

### 1. Celery 基础 (01_celery_basics.py)

**功能**：
- Celery 应用配置和初始化
- 创建简单的异步任务
- 调用异步任务
- 获取任务执行结果
- 任务状态查询

**核心概念**：
- Celery 应用实例
- 任务装饰器 `@task`
- 任务调用方法：`delay()` 和 `apply_async()`
- AsyncResult 对象

**应用场景**：
- 发送邮件通知
- 生成 PDF 报告
- 图片处理和压缩
- 数据导入导出

### 2. 任务队列 (02_task_queue.py)

**功能**：
- 配置多个任务队列
- 设置任务优先级
- 任务路由规则
- Worker 队列绑定
- 任务重试机制

**核心概念**：
- 队列（Queue）
- 路由（Routing）
- 优先级（Priority）
- 重试策略（Retry）

**应用场景**：
- 区分高优先级和低优先级任务
- 不同类型任务使用不同队列
- 任务失败自动重试
- 负载均衡和资源隔离

### 3. 定时任务 (03_scheduled_tasks.py)

**功能**：
- 配置 Celery Beat 调度器
- 创建定时任务
- 创建周期性任务
- Crontab 表达式
- 动态添加定时任务

**核心概念**：
- Celery Beat
- Schedule
- Crontab
- Periodic Tasks

**应用场景**：
- 定时数据备份
- 定时发送报表
- 定时清理过期数据
- 定时同步数据
- 健康检查和监控

## Celery 核心概念

### 任务（Task）

任务是 Celery 的基本执行单元，使用 `@app.task` 装饰器定义：

```python
@app.task
def add(x, y):
    return x + y
```

### 调用方式

**1. delay() - 简单调用**
```python
result = add.delay(4, 6)
```

**2. apply_async() - 高级调用**
```python
result = add.apply_async(
    args=(4, 6),
    countdown=10,  # 延迟 10 秒执行
    queue='high_priority'  # 指定队列
)
```

### 任务状态

- **PENDING**: 任务等待执行
- **STARTED**: 任务已开始执行
- **SUCCESS**: 任务成功完成
- **FAILURE**: 任务执行失败
- **RETRY**: 任务正在重试
- **REVOKED**: 任务被撤销

### 结果获取

```python
# 异步获取结果
result = add.delay(4, 6)
if result.ready():
    print(result.get())  # 获取结果

# 同步等待结果（会阻塞）
result = add.delay(4, 6)
value = result.get(timeout=10)  # 最多等待 10 秒
```

## 配置说明

### Celery 配置

```python
# Celery 应用配置
app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # 消息代理
    backend='redis://localhost:6379/1'  # 结果后端
)

# 配置选项
app.conf.update(
    task_serializer='json',           # 任务序列化格式
    accept_content=['json'],          # 接受的内容类型
    result_serializer='json',         # 结果序列化格式
    timezone='Asia/Shanghai',         # 时区
    enable_utc=True,                  # 启用 UTC
    task_track_started=True,          # 追踪任务开始状态
    task_time_limit=30 * 60,          # 任务超时时间（秒）
    task_soft_time_limit=25 * 60,     # 软超时时间
    worker_prefetch_multiplier=4,     # Worker 预取任务数
    worker_max_tasks_per_child=1000,  # Worker 重启前执行的任务数
)
```

### Redis 配置

```python
# Redis 连接配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

# Redis 连接池配置
BROKER_POOL_LIMIT = 10
BROKER_CONNECTION_MAX_RETRIES = 10
```

### 队列配置

```python
# 定义多个队列
app.conf.task_queues = (
    Queue('default', routing_key='default'),
    Queue('high_priority', routing_key='high'),
    Queue('low_priority', routing_key='low'),
)

# 任务路由规则
app.conf.task_routes = {
    'tasks.send_email': {'queue': 'high_priority'},
    'tasks.generate_report': {'queue': 'low_priority'},
}
```

## 启动和运行

### 启动 Redis

```bash
# 使用 Docker 启动 Redis
docker run -d -p 6379:6379 redis:latest

# 或使用本地 Redis
redis-server
```

### 启动 Celery Worker

```bash
# 启动默认 Worker
celery -A tasks worker --loglevel=info

# 启动指定队列的 Worker
celery -A tasks worker -Q high_priority,default --loglevel=info

# 启动多个 Worker 进程
celery -A tasks worker --concurrency=4 --loglevel=info
```

### 启动 Celery Beat（定时任务）

```bash
# 启动 Beat 调度器
celery -A tasks beat --loglevel=info

# 同时启动 Worker 和 Beat
celery -A tasks worker --beat --loglevel=info
```

### 监控工具

```bash
# Flower - Web 监控界面
pip install flower
celery -A tasks flower

# 访问 http://localhost:5555 查看监控界面
```

## 最佳实践

### 1. 任务设计原则

**保持任务简单**：
- 每个任务只做一件事
- 避免任务之间的强依赖
- 任务应该是幂等的（多次执行结果相同）

**合理设置超时**：
```python
@app.task(time_limit=300, soft_time_limit=270)
def long_running_task():
    # 任务逻辑
    pass
```

**实现重试机制**：
```python
@app.task(bind=True, max_retries=3)
def unreliable_task(self):
    try:
        # 可能失败的操作
        pass
    except Exception as exc:
        # 5 秒后重试
        raise self.retry(exc=exc, countdown=5)
```

### 2. 错误处理

**捕获异常**：
```python
@app.task
def safe_task():
    try:
        # 任务逻辑
        pass
    except Exception as e:
        # 记录错误日志
        logger.error(f"Task failed: {e}")
        # 可以选择重试或返回错误信息
        raise
```

**任务失败回调**：
```python
@app.task
def on_failure_callback(task_id, exception, traceback):
    # 任务失败时的处理逻辑
    logger.error(f"Task {task_id} failed: {exception}")
```

### 3. 性能优化

**批量处理**：
```python
@app.task
def process_batch(items):
    # 批量处理多个项目
    for item in items:
        process_item(item)
```

**使用 Canvas 组合任务**：
```python
from celery import chain, group, chord

# 链式任务
result = chain(task1.s(), task2.s(), task3.s())()

# 并行任务
result = group(task1.s(), task2.s(), task3.s())()

# Chord（并行后聚合）
result = chord([task1.s(), task2.s()])(callback_task.s())
```

### 4. 监控和日志

**结构化日志**：
```python
import structlog

logger = structlog.get_logger()

@app.task
def monitored_task():
    logger.info("task_started", task_id=monitored_task.request.id)
    # 任务逻辑
    logger.info("task_completed", task_id=monitored_task.request.id)
```

**任务追踪**：
```python
@app.task(bind=True)
def tracked_task(self):
    # 更新任务状态
    self.update_state(
        state='PROGRESS',
        meta={'current': 50, 'total': 100}
    )
```

## 常见应用场景

### 1. 邮件发送

```python
@app.task
def send_email(to, subject, body):
    # 发送邮件逻辑
    pass

# 调用
send_email.delay('user@example.com', 'Welcome', 'Hello!')
```

### 2. 报表生成

```python
@app.task
def generate_report(user_id, report_type):
    # 生成报表
    report = create_report(user_id, report_type)
    # 保存到文件系统或云存储
    save_report(report)
    return report.url
```

### 3. 数据处理

```python
@app.task
def process_uploaded_file(file_path):
    # 读取文件
    data = read_file(file_path)
    # 处理数据
    processed_data = process_data(data)
    # 保存结果
    save_results(processed_data)
```

### 4. 定时清理

```python
@app.task
def cleanup_old_files():
    # 删除 30 天前的临时文件
    cutoff_date = datetime.now() - timedelta(days=30)
    delete_files_before(cutoff_date)
```

## FastAPI 集成

### 配置 Celery

```python
# celery_app.py
from celery import Celery

celery_app = Celery(
    'fastapi_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)
```

### 在 FastAPI 中使用

```python
from fastapi import FastAPI, BackgroundTasks
from celery_app import celery_app

app = FastAPI()

@app.post("/send-email")
async def send_email_endpoint(email: str):
    # 发送异步任务
    task = send_email.delay(email)
    return {"task_id": task.id, "status": "processing"}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    # 查询任务状态
    task = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

## Flask 集成

### 配置 Celery

```python
# celery_app.py
from celery import Celery
from flask import Flask

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    return celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/1'

celery = make_celery(app)
```

### 在 Flask 中使用

```python
@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    email = request.json.get('email')
    task = send_email.delay(email)
    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })

@app.route('/task/<task_id>')
def get_task_status(task_id):
    task = celery.AsyncResult(task_id)
    return jsonify({
        'task_id': task_id,
        'status': task.status,
        'result': task.result if task.ready() else None
    })
```

## 学习资源

### 官方文档

- [Celery 官方文档](https://docs.celeryq.dev/)
- [Redis 官方文档](https://redis.io/documentation)
- [Flower 监控工具](https://flower.readthedocs.io/)

### 推荐阅读

- 分布式任务队列原理
- 消息队列对比（Redis vs RabbitMQ）
- 异步编程最佳实践
- 微服务中的异步通信

### 相关工具

- **Celery**: 分布式任务队列
- **Redis**: 消息代理和结果后端
- **RabbitMQ**: 高级消息代理
- **Flower**: Celery 监控工具
- **Dramatiq**: 轻量级任务队列

## 实践建议

1. **从简单开始**：先实现基本的异步任务，理解工作流程
2. **本地测试**：使用 Docker 快速搭建 Redis 环境
3. **监控观察**：使用 Flower 观察任务执行情况
4. **错误处理**：实践各种错误场景和重试机制
5. **性能测试**：测试不同并发度下的性能表现
6. **实际应用**：在 CRM 项目中实现工作日志导出功能

## 下一步

完成本模块学习后，建议：

1. 在 CRM 项目中实现异步任务功能
2. 学习更高级的 Celery 特性（Canvas、Workflow）
3. 探索其他消息队列（RabbitMQ、Kafka）
4. 研究分布式系统中的异步通信模式
5. 学习微服务架构中的事件驱动设计

## 常见问题

### Q1: Celery 和 Python 的 asyncio 有什么区别？

**A**: asyncio 是 Python 的异步 I/O 库，用于在单个进程中实现并发。Celery 是分布式任务队列，可以在多个进程、多台机器上执行任务。asyncio 适合 I/O 密集型任务，Celery 适合需要分布式执行的长时间任务。

### Q2: 为什么选择 Redis 而不是 RabbitMQ？

**A**: Redis 配置简单，性能优秀，适合大多数场景。RabbitMQ 功能更强大，支持更复杂的路由和消息确认机制，适合对消息可靠性要求极高的场景。对于学习和中小型项目，Redis 是更好的选择。

### Q3: 如何处理任务执行失败？

**A**: 可以使用重试机制、设置最大重试次数、实现失败回调函数、记录详细的错误日志。对于关键任务，可以实现死信队列（Dead Letter Queue）来处理多次失败的任务。

### Q4: Worker 应该启动多少个？

**A**: 取决于任务类型和服务器资源。对于 CPU 密集型任务，Worker 数量应该接近 CPU 核心数。对于 I/O 密集型任务，可以启动更多 Worker。建议从少量开始，根据监控数据逐步调整。

### Q5: 如何保证任务的幂等性？

**A**: 使用唯一的任务 ID、在数据库中记录任务执行状态、使用分布式锁、设计可重复执行的任务逻辑。幂等性对于任务重试和系统可靠性非常重要。

### Q6: 任务结果应该保存多久？

**A**: 取决于业务需求。可以配置 `result_expires` 参数设置结果过期时间。对于不需要查询结果的任务，可以设置 `ignore_result=True` 提升性能。

## 总结

异步任务是构建高性能、可扩展 Web 应用的关键技术。通过本模块的学习，你将掌握：

- 使用 Celery 实现分布式任务队列
- 配置和管理异步任务的执行
- 实现定时任务和周期性任务
- 监控和调试异步任务
- 在实际项目中应用异步任务

异步任务能够显著提升应用的响应速度和用户体验，是企业级应用开发的必备技能。通过实践和应用，你将能够构建更加健壮和高效的 Web 应用。
