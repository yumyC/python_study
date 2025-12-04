# 异步任务完整示例

本目录包含异步任务的完整集成示例，展示如何在实际项目中应用 Celery。

## 示例说明

### integrated_example.py

这是一个完整的 FastAPI + Celery 集成示例，模拟 CRM 项目中的工作日志导出功能。

**功能特性**：
- FastAPI Web 应用
- Celery 异步任务处理
- 任务状态追踪和进度更新
- 文件生成和下载
- 多队列配置
- 任务重试机制
- 定时清理任务

**应用场景**：
- 工作日志批量导出
- 通知发送
- 文件清理

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi celery redis uvicorn openpyxl
```

### 2. 启动 Redis

```bash
docker run -d -p 6379:6379 redis:latest
```

### 3. 启动 Celery Worker

在项目根目录下运行：

```bash
# 启动默认 Worker
celery -A python_demo.stage3_enterprise.async_tasks.examples.integrated_example worker --loglevel=info

# 或启动多个队列的 Worker
celery -A python_demo.stage3_enterprise.async_tasks.examples.integrated_example worker \
  -Q high_priority,default,export --loglevel=info
```

### 4. 启动 FastAPI 应用

```bash
uvicorn python_demo.stage3_enterprise.async_tasks.examples.integrated_example:app --reload
```

### 5. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

## API 端点

### 1. 创建导出任务

**POST** `/api/export/work-logs`

请求体：
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "employee_ids": ["emp_001", "emp_002"],
  "export_format": "xlsx"
}
```

响应：
```json
{
  "task_id": "abc123...",
  "status": "processing",
  "message": "导出任务已提交，请使用 task_id 查询进度",
  "status_url": "/api/tasks/abc123..."
}
```

### 2. 查询任务状态

**GET** `/api/tasks/{task_id}`

响应：
```json
{
  "task_id": "abc123...",
  "status": "processing",
  "progress": 45,
  "result": {
    "message": "正在写入 Excel 文件... (30/50)"
  }
}
```

任务状态：
- `pending`: 等待执行
- `processing`: 执行中
- `completed`: 已完成
- `failed`: 失败

### 3. 下载文件

**GET** `/api/download/{file_name}`

直接下载导出的文件。

### 4. 发送通知

**POST** `/api/notifications`

请求体：
```json
{
  "user_id": "user_001",
  "message": "您的报表已生成",
  "notification_type": "email"
}
```

### 5. 列出导出文件

**GET** `/api/exports`

响应：
```json
{
  "count": 3,
  "files": [
    {
      "file_name": "work_logs_2024-01-01_2024-01-31_1234567890.xlsx",
      "size": 15234,
      "created_at": "2024-01-15T10:30:00",
      "download_url": "/api/download/work_logs_2024-01-01_2024-01-31_1234567890.xlsx"
    }
  ]
}
```

### 6. 手动触发清理

**POST** `/api/cleanup?days_old=7`

清理 7 天前的导出文件。

## 使用流程

### 完整的导出流程

1. **提交导出任务**
   ```bash
   curl -X POST "http://localhost:8000/api/export/work-logs" \
     -H "Content-Type: application/json" \
     -d '{
       "start_date": "2024-01-01",
       "end_date": "2024-01-31"
     }'
   ```

2. **轮询任务状态**
   ```bash
   curl "http://localhost:8000/api/tasks/{task_id}"
   ```

3. **下载文件**
   ```bash
   curl -O "http://localhost:8000/api/download/{file_name}"
   ```

### 前端集成示例

```javascript
// 1. 提交导出任务
async function exportWorkLogs(startDate, endDate) {
  const response = await fetch('/api/export/work-logs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_date: startDate, end_date: endDate })
  });
  const data = await response.json();
  return data.task_id;
}

// 2. 轮询任务状态
async function pollTaskStatus(taskId) {
  const response = await fetch(`/api/tasks/${taskId}`);
  const data = await response.json();
  
  if (data.status === 'completed') {
    // 任务完成，下载文件
    const fileName = data.result.file_name;
    window.location.href = `/api/download/${fileName}`;
  } else if (data.status === 'failed') {
    // 任务失败
    console.error('导出失败:', data.error);
  } else {
    // 继续轮询
    console.log('进度:', data.progress + '%');
    setTimeout(() => pollTaskStatus(taskId), 1000);
  }
}

// 3. 使用
const taskId = await exportWorkLogs('2024-01-01', '2024-01-31');
pollTaskStatus(taskId);
```

## 监控和调试

### 使用 Flower 监控

Flower 是 Celery 的 Web 监控工具：

```bash
# 安装 Flower
pip install flower

# 启动 Flower
celery -A python_demo.stage3_enterprise.async_tasks.examples.integrated_example flower

# 访问 http://localhost:5555
```

Flower 提供：
- 实时任务监控
- Worker 状态查看
- 任务历史记录
- 任务重试和撤销
- 性能统计

### 查看日志

Worker 日志：
```bash
celery -A python_demo.stage3_enterprise.async_tasks.examples.integrated_example worker --loglevel=debug
```

FastAPI 日志：
```bash
uvicorn python_demo.stage3_enterprise.async_tasks.examples.integrated_example:app --log-level debug
```

## 性能优化

### 1. 调整 Worker 并发数

```bash
# 使用多进程
celery -A ... worker --concurrency=4

# 使用协程（适合 I/O 密集型任务）
celery -A ... worker --pool=gevent --concurrency=100
```

### 2. 配置任务预取

```python
app.conf.worker_prefetch_multiplier = 4  # 每个 Worker 预取 4 个任务
```

### 3. 使用任务优先级

```python
task.apply_async(args=(...), priority=9)  # 0-9，9 最高
```

### 4. 批量处理

将多个小任务合并为一个大任务，减少任务调度开销。

## 常见问题

### Q1: 任务一直处于 PENDING 状态？

**A**: 检查 Worker 是否正在运行，以及任务是否路由到正确的队列。

### Q2: 如何取消正在执行的任务？

**A**: 
```python
from celery.result import AsyncResult
result = AsyncResult(task_id)
result.revoke(terminate=True)
```

### Q3: 如何处理任务超时？

**A**: 
```python
@app.task(time_limit=300, soft_time_limit=270)
def my_task():
    # 任务逻辑
    pass
```

### Q4: 如何保证任务只执行一次？

**A**: 使用分布式锁或数据库唯一约束。

## 扩展建议

1. **添加认证授权**：保护 API 端点
2. **实现 WebSocket**：实时推送任务进度
3. **使用数据库**：持久化任务记录
4. **添加日志系统**：使用 structlog 记录详细日志
5. **实现文件存储**：使用云存储（S3、OSS）
6. **添加监控告警**：集成 Prometheus 和 Grafana

## 相关资源

- [Celery 官方文档](https://docs.celeryq.dev/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Flower 文档](https://flower.readthedocs.io/)
- [Redis 文档](https://redis.io/documentation)

## 总结

这个集成示例展示了如何在实际项目中使用 Celery 处理异步任务。通过这个示例，你可以学习到：

- FastAPI 与 Celery 的集成方式
- 任务状态追踪和进度更新
- 文件生成和下载流程
- 多队列和任务路由
- 错误处理和重试机制
- 定时任务配置

这些技术可以直接应用到 CRM 项目和其他企业级应用中。
