# FastAPI 异步任务和中间件实现指南

本文档介绍了 CRM 系统中异步任务和中间件的实现，包括 Celery 配置、工作日志导出、请求日志记录、Request ID 追踪和错误处理。

## 🏗️ 架构概览

```
FastAPI 应用
├── 中间件层
│   ├── RequestIDMiddleware (Request ID 生成)
│   ├── RequestLoggingMiddleware (请求日志)
│   └── ErrorHandlerMiddleware (错误处理)
├── API 层
│   ├── 业务 API (员工、岗位等)
│   └── 任务管理 API
└── 异步任务层
    ├── Celery 应用
    ├── Redis 消息队列
    └── 工作日志导出任务
```

## 🔧 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

关键配置项：
- `REDIS_URL`: Redis 连接地址
- `DATABASE_URL`: 数据库连接地址
- `SECRET_KEY`: JWT 密钥

### 3. 启动 Redis 服务

使用 Docker Compose：
```bash
docker-compose -f docker-compose.dev.yml up -d redis
```

或手动启动 Redis：
```bash
redis-server
```

## 🚀 快速启动

### 方式一：使用启动脚本

```bash
./start_dev.sh
```

### 方式二：手动启动

1. 启动 FastAPI 服务器：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. 启动 Celery Worker：
```bash
python celery_worker.py
```

## 📋 异步任务功能

### 工作日志导出

#### 创建导出任务

```http
POST /api/tasks/export-work-logs
```

参数：
- `employee_id` (可选): 员工ID
- `start_date` (可选): 开始日期 (YYYY-MM-DD)
- `end_date` (可选): 结束日期 (YYYY-MM-DD)
- `export_format`: 导出格式 (默认 xlsx)

响应：
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "PENDING",
    "message": "导出任务已创建，正在处理中...",
    "created_at": "2024-01-01T10:00:00",
    "filters": {
        "employee_id": null,
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "export_format": "xlsx"
    }
}
```

#### 查询任务状态

```http
GET /api/tasks/{task_id}/status
```

响应：
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "SUCCESS",
    "message": "任务完成",
    "result": {
        "success": true,
        "message": "成功导出 150 条工作日志",
        "file_name": "work_logs_export_20240101_100000_abc123.xlsx",
        "record_count": 150
    },
    "download_url": "/api/tasks/550e8400-e29b-41d4-a716-446655440000/download"
}
```

#### 下载导出文件

```http
GET /api/tasks/{task_id}/download
```

返回 Excel 文件下载。

#### 取消任务

```http
POST /api/tasks/{task_id}/cancel?terminate=false
```

### 任务管理

#### 查看活跃任务

```http
GET /api/tasks/active
```

#### 获取任务统计

```http
GET /api/tasks/stats
```

#### 清理过期文件

```http
POST /api/tasks/cleanup-files?max_age_hours=24
```

## 🛡️ 中间件功能

### 1. Request ID 中间件

**功能**：
- 为每个请求生成唯一 ID
- 支持从请求头提取已有 ID
- 将 ID 添加到响应头
- 提供上下文变量访问

**使用**：
```python
from app.middleware.request_id import get_request_id

# 在任何地方获取当前请求 ID
request_id = get_request_id()
```

**配置**：
```python
app.add_middleware(
    RequestIDMiddleware,
    header_name="X-Request-ID",
    response_header_name="X-Request-ID"
)
```

### 2. 请求日志中间件

**功能**：
- 记录所有 HTTP 请求信息
- 计算请求处理时间
- 过滤敏感信息
- 支持跳过特定路径

**日志格式**：
```json
{
    "request": {
        "method": "POST",
        "path": "/api/employees",
        "client_ip": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "request_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "response": {
        "status_code": 201,
        "process_time": "0.1234s"
    }
}
```

**配置**：
```python
app.add_middleware(
    RequestLoggingMiddleware,
    skip_paths=["/health", "/docs"],
    log_request_body=False,
    max_body_size=1024
)
```

### 3. 错误处理中间件

**功能**：
- 统一异常处理
- 标准化错误响应格式
- 详细错误日志记录
- 区分不同异常类型

**错误响应格式**：
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "请求数据验证失败",
        "details": [
            {
                "field": "email",
                "message": "field required",
                "type": "value_error.missing"
            }
        ],
        "request_id": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

**自定义异常**：
```python
from app.middleware.error_handler import BusinessLogicError

# 抛出业务逻辑异常
raise BusinessLogicError("用户名已存在")
```

## 🔍 监控和调试

### 查看日志

应用日志会输出到控制台，包含：
- 请求处理日志
- 错误异常日志
- 任务执行日志

### Redis 监控

访问 Redis Commander 管理界面：
```
http://localhost:8081
```

### Celery 监控

查看 Celery Worker 状态：
```bash
celery -A app.tasks.celery_app inspect active
celery -A app.tasks.celery_app inspect stats
```

## 🧪 测试示例

### 测试异步任务

```python
import requests

# 创建导出任务
response = requests.post(
    "http://localhost:8000/api/tasks/export-work-logs",
    params={"start_date": "2024-01-01", "end_date": "2024-01-31"},
    headers={"Authorization": "Bearer your-token"}
)
task_id = response.json()["task_id"]

# 查询任务状态
status_response = requests.get(
    f"http://localhost:8000/api/tasks/{task_id}/status",
    headers={"Authorization": "Bearer your-token"}
)

# 下载文件（任务完成后）
if status_response.json()["status"] == "SUCCESS":
    file_response = requests.get(
        f"http://localhost:8000/api/tasks/{task_id}/download",
        headers={"Authorization": "Bearer your-token"}
    )
    with open("work_logs.xlsx", "wb") as f:
        f.write(file_response.content)
```

### 测试中间件

```python
import requests

# 发送带 Request ID 的请求
response = requests.get(
    "http://localhost:8000/api/employees",
    headers={
        "Authorization": "Bearer your-token",
        "X-Request-ID": "custom-request-id-123"
    }
)

# 检查响应头中的 Request ID
print(response.headers.get("X-Request-ID"))
```

## 🚨 故障排除

### 常见问题

1. **Redis 连接失败**
   ```
   ConnectionError: Error 111 connecting to localhost:6379
   ```
   解决：确保 Redis 服务正在运行

2. **Celery Worker 无法启动**
   ```
   ImportError: No module named 'app'
   ```
   解决：确保在项目根目录启动 Worker

3. **任务状态一直是 PENDING**
   - 检查 Celery Worker 是否运行
   - 检查 Redis 连接配置
   - 查看 Worker 日志

4. **文件下载失败**
   ```
   FileNotFoundError: No such file or directory
   ```
   解决：检查导出目录权限和磁盘空间

### 调试技巧

1. **启用详细日志**：
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查 Celery 队列**：
   ```bash
   celery -A app.tasks.celery_app inspect reserved
   ```

3. **清理 Redis 数据**：
   ```bash
   redis-cli FLUSHALL
   ```

## 📚 扩展功能

### 添加新的异步任务

1. 在 `app/tasks/` 目录创建新任务文件
2. 使用 `@celery_app.task` 装饰器
3. 在 `celery_app.py` 中注册任务
4. 创建对应的 API 端点

### 自定义中间件

1. 继承 `BaseHTTPMiddleware`
2. 实现 `dispatch` 方法
3. 在 `main.py` 中注册中间件

### 添加任务调度

使用 Celery Beat 实现定时任务：
```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-files-daily': {
        'task': 'cleanup_export_files',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
    },
}
```

## 🔐 安全考虑

1. **文件访问控制**：确保只有授权用户能下载文件
2. **任务权限验证**：验证用户是否有权限执行特定任务
3. **敏感信息过滤**：在日志中过滤密码等敏感信息
4. **文件清理**：定期清理过期的导出文件
5. **错误信息**：在生产环境中隐藏详细的错误堆栈

## 📈 性能优化

1. **任务队列分离**：将不同类型的任务分配到不同队列
2. **并发控制**：根据服务器资源调整 Worker 并发数
3. **文件压缩**：对大文件进行压缩以减少存储空间
4. **缓存策略**：缓存频繁查询的数据
5. **异步 I/O**：使用异步数据库操作

这个实现提供了完整的异步任务处理和中间件功能，可以作为企业级应用的基础架构。