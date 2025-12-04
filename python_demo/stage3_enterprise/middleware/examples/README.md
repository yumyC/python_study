# 中间件集成示例

本目录包含完整的中间件集成示例，展示如何在实际应用中组合使用多个中间件。

## 示例应用

### integrated_app.py

一个完整的 FastAPI 应用，集成了以下中间件：

1. **CORS 中间件** - 处理跨域请求
2. **Request ID 中间件** - 为每个请求生成唯一标识符
3. **请求日志中间件** - 记录请求信息和处理时间
4. **错误处理中间件** - 统一处理异常和错误响应

## 运行示例

### 安装依赖

```bash
pip install fastapi uvicorn pydantic
```

### 启动应用

```bash
cd study/python_demo/stage3_enterprise/middleware/examples
uvicorn integrated_app:app --reload --port 8000
```

### 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

## 测试中间件功能

### 1. 测试 Request ID 中间件

不带 Request ID 的请求（自动生成）：
```bash
curl -v http://localhost:8000/
```

带自定义 Request ID 的请求：
```bash
curl -v -H "X-Request-ID: my-custom-id" http://localhost:8000/
```

观察响应头中的 `X-Request-ID`，以及日志中的 Request ID。

### 2. 测试请求日志中间件

发送请求并观察日志输出：
```bash
curl http://localhost:8000/slow
```

查看日志中的：
- 请求开始时间
- 请求完成时间
- 处理耗时
- 响应头中的 `X-Process-Time`

### 3. 测试错误处理中间件

触发业务异常（404）：
```bash
curl http://localhost:8000/api/users/999
```

触发服务器错误（500）：
```bash
curl http://localhost:8000/error
```

观察统一的错误响应格式，包含：
- 错误代码
- 错误消息
- 时间戳
- 请求路径
- Request ID

### 4. 测试 CORS 中间件

发送带 Origin 头的请求：
```bash
curl -v -H "Origin: http://example.com" http://localhost:8000/
```

观察响应头中的 CORS 相关头部：
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Credentials`
- `Access-Control-Expose-Headers`

发送预检请求：
```bash
curl -v -X OPTIONS \
  -H "Origin: http://example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  http://localhost:8000/api/users
```

### 5. 完整的 CRUD 操作测试

创建用户：
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "age": 25}'
```

获取所有用户：
```bash
curl http://localhost:8000/api/users
```

获取指定用户（使用上一步返回的 user_id）：
```bash
curl http://localhost:8000/api/users/{user_id}
```

更新用户：
```bash
curl -X PUT http://localhost:8000/api/users/{user_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Smith", "email": "alice@example.com", "age": 26}'
```

删除用户：
```bash
curl -X DELETE http://localhost:8000/api/users/{user_id}
```

## 中间件执行顺序

理解中间件的执行顺序对于正确配置非常重要：

```
请求流程：
客户端请求
  ↓
CORS 中间件（处理跨域）
  ↓
Request ID 中间件（生成追踪 ID）
  ↓
请求日志中间件（记录请求开始）
  ↓
错误处理中间件（try 块开始）
  ↓
路由处理函数
  ↓
错误处理中间件（try 块结束）
  ↓
请求日志中间件（记录请求完成）
  ↓
Request ID 中间件（添加响应头）
  ↓
CORS 中间件（添加 CORS 头）
  ↓
客户端响应
```

## 日志输出示例

正常请求的日志：
```
2024-01-01 10:00:00 - __main__ - [abc-123-def] - INFO - 请求开始: GET / from 127.0.0.1
2024-01-01 10:00:00 - __main__ - [abc-123-def] - INFO - 访问根路径
2024-01-01 10:00:00 - __main__ - [abc-123-def] - INFO - 请求完成: GET / - 状态码: 200 - 耗时: 0.001s
```

错误请求的日志：
```
2024-01-01 10:00:01 - __main__ - [def-456-ghi] - INFO - 请求开始: GET /api/users/999 from 127.0.0.1
2024-01-01 10:00:01 - __main__ - [def-456-ghi] - INFO - 获取用户: 999
2024-01-01 10:00:01 - __main__ - [def-456-ghi] - WARNING - 业务异常: USER_NOT_FOUND - User with id 999 not found
2024-01-01 10:00:01 - __main__ - [def-456-ghi] - INFO - 请求完成: GET /api/users/999 - 状态码: 404 - 耗时: 0.002s
```

## 学习要点

通过这个集成示例，你应该掌握：

1. **中间件注册顺序的重要性**
   - 不同的顺序会产生不同的效果
   - 某些中间件必须在其他中间件之前执行

2. **中间件之间的协作**
   - Request ID 在所有中间件中共享
   - 日志中间件记录错误处理中间件捕获的异常
   - CORS 中间件添加的头部对所有响应生效

3. **上下文变量的使用**
   - 使用 ContextVar 在异步环境中共享数据
   - Request ID 通过上下文变量在整个请求生命周期中可用

4. **统一的错误处理**
   - 所有异常都被错误处理中间件捕获
   - 返回一致的错误响应格式
   - 错误信息包含 Request ID 便于追踪

5. **可观测性**
   - 通过日志了解应用的运行状态
   - Request ID 关联所有相关日志
   - 处理时间帮助识别性能问题

## 扩展练习

1. **添加认证中间件**
   - 实现 JWT 认证中间件
   - 保护特定的 API 端点

2. **添加限流中间件**
   - 限制客户端的请求频率
   - 防止 API 滥用

3. **添加缓存中间件**
   - 缓存 GET 请求的响应
   - 提升 API 性能

4. **集成 OpenTelemetry**
   - 实现分布式追踪
   - 收集性能指标

5. **添加压缩中间件**
   - 压缩响应内容
   - 减少网络传输量

## 参考资源

- [FastAPI Middleware 文档](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Starlette Middleware 文档](https://www.starlette.io/middleware/)
- [ASGI 规范](https://asgi.readthedocs.io/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
