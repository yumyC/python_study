# CRM 系统 API 文档

## 概述

本文档详细描述 CRM 系统的 RESTful API 接口规范，包含认证、员工管理、岗位管理、菜单管理、角色权限管理、工作日志管理等核心功能。

**Base URL**: `http://localhost:8000/api`

**API 版本**: v1

**认证方式**: JWT Bearer Token

**请求格式**: JSON

**响应格式**: JSON

**字符编码**: UTF-8

## 通用说明

### 请求头

所有需要认证的接口都需要在请求头中包含 JWT Token：

```http
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json
```

### 响应格式

#### 成功响应

```json
{
  "data": {
    // 响应数据
  },
  "message": "操作成功",
  "request_id": "uuid"
}
```

#### 分页响应

```json
{
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
  },
  "message": "查询成功",
  "request_id": "uuid"
}
```

#### 错误响应

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {},
    "request_id": "uuid"
  }
}
```

## 认证接口

### 登录

**接口**: `POST /auth/login`

**描述**: 用户登录获取 Token

**请求体**:
```json
{
  "username": "admin",
  "password": "Admin123456"
}
```

**响应**:
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 7200
  }
}
```

### 刷新 Token

**接口**: `POST /auth/refresh`

**描述**: 使用 Refresh Token 获取新的 Access Token

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 获取当前用户信息

**接口**: `GET /auth/me`

**描述**: 获取当前登录用户的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": "uuid",
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "系统管理员",
    "position": {
      "id": "uuid",
      "name": "CEO"
    },
    "role": {
      "id": "uuid",
      "name": "系统管理员",
      "code": "admin"
    },
    "permissions": [...]
  }
}
```

## 员工管理接口

### 创建员工

**接口**: `POST /employees`

**权限**: 需要 `employees:create` 权限

**请求体**:
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "Password123",
  "full_name": "张三",
  "position_id": "uuid",
  "role_id": "uuid",
  "status": "active"
}
```

**响应**:
```json
{
  "data": {
    "id": "uuid",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "full_name": "张三",
    "position": {
      "id": "uuid",
      "name": "高级开发工程师"
    },
    "role": {
      "id": "uuid",
      "name": "开发人员"
    },
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 查询员工列表

**接口**: `GET /employees`

**权限**: 需要 `employees:view` 权限

**查询参数**:
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20，最大 100）
- `search`: 搜索关键词（用户名、姓名、邮箱）
- `position_id`: 岗位 ID 筛选
- `role_id`: 角色 ID 筛选
- `status`: 状态筛选（active/inactive）
- `sort_by`: 排序字段（created_at/full_name/username）
- `sort_order`: 排序方向（asc/desc）

**响应**:
```json
{
  "data": {
    "items": [
      {
        "id": "uuid",
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "full_name": "张三",
        "position": {
          "id": "uuid",
          "name": "高级开发工程师",
          "level": 3
        },
        "role": {
          "id": "uuid",
          "name": "开发人员",
          "code": "developer"
        },
        "status": "active",
        "created_at": "2024-01-15T10:30:00Z",
        "last_login": "2024-01-20T09:15:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20,
    "pages": 3
  }
}
```

### 查询员工详情

**接口**: `GET /employees/{id}`

**权限**: 需要 `employees:view` 权限

**响应**:
```json
{
  "data": {
    "id": "uuid",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "full_name": "张三",
    "position": {
      "id": "uuid",
      "name": "高级开发工程师",
      "code": "senior_developer",
      "level": 3,
      "department": "技术部"
    },
    "role": {
      "id": "uuid",
      "name": "开发人员",
      "code": "developer",
      "permissions": [...]
    },
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:20:00Z",
    "last_login": "2024-01-20T09:15:00Z",
    "work_logs_count": 25,
    "avg_self_rating": 4.2,
    "avg_supervisor_rating": 4.5
  }
}
```

### 更新员工信息

**接口**: `PUT /employees/{id}`

**权限**: 需要 `employees:update` 权限

**请求体**:
```json
{
  "email": "zhangsan.new@example.com",
  "full_name": "张三丰",
  "position_id": "new_uuid",
  "role_id": "new_uuid",
  "status": "active"
}
```

### 删除员工

**接口**: `DELETE /employees/{id}`

**权限**: 需要 `employees:delete` 权限

**响应**: `204 No Content`

### 重置员工密码

**接口**: `POST /employees/{id}/reset-password`

**权限**: 需要 `employees:update` 权限

**请求体**:
```json
{
  "new_password": "NewPassword123"
}
```

### 批量操作

**接口**: `POST /employees/batch`

**权限**: 需要相应的批量操作权限

**请求体**:
```json
{
  "action": "delete|activate|deactivate",
  "employee_ids": ["uuid1", "uuid2", "uuid3"]
}
```

## 岗位管理接口

### 创建岗位

**接口**: `POST /positions`

**权限**: 需要 `positions:create` 权限

**请求体**:
```json
{
  "name": "高级开发工程师",
  "code": "senior_developer",
  "description": "负责核心业务系统开发",
  "level": 3,
  "parent_id": "uuid"  // 可选，上级岗位ID
}
```

**响应**:
```json
{
  "data": {
    "id": "uuid",
    "name": "高级开发工程师",
    "code": "senior_developer",
    "description": "负责核心业务系统开发",
    "level": 3,
    "parent_id": "uuid",
    "parent": {
      "id": "uuid",
      "name": "技术总监"
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 查询岗位列表

**接口**: `GET /positions`

**权限**: 需要 `positions:view` 权限

**查询参数**:
- `tree`: 是否返回树形结构（true/false，默认 false）
- `level`: 岗位级别筛选
- `parent_id`: 上级岗位 ID 筛选
- `search`: 搜索关键词（岗位名称、编码）

**响应（列表格式）**:
```json
{
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "高级开发工程师",
        "code": "senior_developer",
        "level": 3,
        "parent": {
          "id": "uuid",
          "name": "技术总监"
        },
        "employee_count": 5,
        "children_count": 2
      }
    ]
  }
}
```

**响应（树形格式）**:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "CEO",
      "code": "ceo",
      "level": 1,
      "employee_count": 1,
      "children": [
        {
          "id": "uuid",
          "name": "技术总监",
          "code": "cto",
          "level": 2,
          "employee_count": 1,
          "children": [
            {
              "id": "uuid",
              "name": "高级开发工程师",
              "code": "senior_developer",
              "level": 3,
              "employee_count": 5,
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

### 查询岗位详情

**接口**: `GET /positions/{id}`

**权限**: 需要 `positions:view` 权限

**响应**:
```json
{
  "data": {
    "id": "uuid",
    "name": "高级开发工程师",
    "code": "senior_developer",
    "description": "负责核心业务系统开发",
    "level": 3,
    "parent_id": "uuid",
    "parent": {
      "id": "uuid",
      "name": "技术总监",
      "full_path": "CEO > 技术总监"
    },
    "children": [
      {
        "id": "uuid",
        "name": "开发工程师"
      }
    ],
    "employees": [
      {
        "id": "uuid",
        "full_name": "张三",
        "username": "zhangsan"
      }
    ],
    "full_path": "CEO > 技术总监 > 高级开发工程师",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:20:00Z"
  }
}
```

### 更新岗位信息

**接口**: `PUT /positions/{id}`

**权限**: 需要 `positions:update` 权限

**请求体**:
```json
{
  "name": "资深开发工程师",
  "description": "负责核心业务系统开发和技术架构设计",
  "level": 4,
  "parent_id": "new_uuid"
}
```

### 删除岗位

**接口**: `DELETE /positions/{id}`

**权限**: 需要 `positions:delete` 权限

**注意**: 如果岗位下有员工或子岗位，将无法删除

**响应**: `204 No Content`

### 岗位层级操作

**接口**: `POST /positions/{id}/move`

**权限**: 需要 `positions:update` 权限

**请求体**:
```json
{
  "new_parent_id": "uuid",  // null 表示移动到根级别
  "new_level": 3
}
```

## 菜单管理接口

### 创建菜单

**接口**: `POST /menus`

### 查询菜单列表

**接口**: `GET /menus`

### 查询用户菜单

**接口**: `GET /menus/user`

**描述**: 根据当前用户角色返回有权限的菜单树

### 更新菜单信息

**接口**: `PUT /menus/{id}`

### 删除菜单

**接口**: `DELETE /menus/{id}`

## 角色管理接口

### 创建角色

**接口**: `POST /roles`

### 查询角色列表

**接口**: `GET /roles`

### 查询角色详情

**接口**: `GET /roles/{id}`

### 更新角色信息

**接口**: `PUT /roles/{id}`

### 删除角色

**接口**: `DELETE /roles/{id}`

## 权限管理接口

### 分配角色权限

**接口**: `POST /permissions/assign`

**请求体**:
```json
{
  "role_id": "uuid",
  "permissions": [
    {
      "menu_id": "uuid",
      "actions": ["view", "create", "update", "delete"]
    }
  ]
}
```

### 查询角色权限

**接口**: `GET /permissions/role/{role_id}`

## 工作日志接口

### 创建工作日志

**接口**: `POST /worklogs`

### 查询工作日志列表

**接口**: `GET /worklogs`

**查询参数**:
- `page`: 页码
- `page_size`: 每页数量
- `employee_id`: 员工 ID
- `start_date`: 开始日期
- `end_date`: 结束日期
- `completion_status`: 完成情况

### 查询工作日志详情

**接口**: `GET /worklogs/{id}`

### 更新工作日志

**接口**: `PUT /worklogs/{id}`

### 上级评分

**接口**: `POST /worklogs/{id}/rate`

**请求体**:
```json
{
  "supervisor_rating": 5,
  "supervisor_comment": "完成质量很高"
}
```

### 导出工作日志

**接口**: `POST /worklogs/export`

**请求体**:
```json
{
  "employee_id": "uuid",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**响应**:
```json
{
  "data": {
    "task_id": "uuid"
  }
}
```

### 查询导出任务状态

**接口**: `GET /tasks/{task_id}`

**响应**:
```json
{
  "data": {
    "task_id": "uuid",
    "status": "completed",
    "progress": 100,
    "file_url": "http://localhost:8000/downloads/worklogs_20240115.xlsx"
  }
}
```

## 错误响应格式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {},
    "request_id": "uuid"
  }
}
```

## 状态码说明

- `200 OK`: 成功
- `201 Created`: 创建成功
- `204 No Content`: 删除成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 无权限
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 验证失败
- `500 Internal Server Error`: 服务器错误

## 交互式文档

启动服务后访问：
- FastAPI: `http://localhost:8000/docs`
- Flask: 需要集成 Swagger UI

## 系统监控接口

### 健康检查

**接口**: `GET /health`

**描述**: 检查系统各组件健康状态

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "celery": "healthy"
  },
  "uptime": 86400
}
```

### 系统信息

**接口**: `GET /info`

**响应**:
```json
{
  "data": {
    "app_name": "CRM System",
    "version": "1.0.0",
    "environment": "production",
    "build_time": "2024-01-15T08:00:00Z",
    "python_version": "3.11.0",
    "fastapi_version": "0.104.1"
  }
}
```

## 文件上传接口

### 上传文件

**接口**: `POST /upload`

**权限**: 需要登录

**请求**: `multipart/form-data`

**参数**:
- `file`: 文件对象
- `category`: 文件分类（avatar/document/export）

**响应**:
```json
{
  "data": {
    "file_id": "uuid",
    "filename": "document.pdf",
    "original_name": "原始文件名.pdf",
    "size": 1024000,
    "mime_type": "application/pdf",
    "url": "http://localhost:8000/uploads/uuid/document.pdf",
    "category": "document",
    "uploaded_at": "2024-01-20T10:30:00Z"
  }
}
```

### 下载文件

**接口**: `GET /uploads/{file_id}/{filename}`

**描述**: 下载已上传的文件

## WebSocket 接口

### 实时通知

**接口**: `WS /ws/notifications`

**描述**: 接收实时系统通知

**消息格式**:
```json
{
  "type": "notification",
  "data": {
    "id": "uuid",
    "title": "新的工作日志评分",
    "message": "您的工作日志已被上级评分",
    "category": "work_log",
    "timestamp": "2024-01-20T10:30:00Z",
    "read": false
  }
}
```

## 错误码说明

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| AUTH_001 | 401 | Token 无效或已过期 |
| AUTH_002 | 401 | 用户名或密码错误 |
| AUTH_003 | 403 | 权限不足 |
| VALID_001 | 422 | 请求参数验证失败 |
| VALID_002 | 422 | 数据格式错误 |
| RESOURCE_001 | 404 | 资源不存在 |
| RESOURCE_002 | 409 | 资源冲突（如用户名已存在） |
| BUSINESS_001 | 400 | 业务逻辑错误 |
| SYSTEM_001 | 500 | 系统内部错误 |
| SYSTEM_002 | 503 | 服务暂时不可用 |

## 限流说明

为保护系统稳定性，API 实施了限流策略：

- **登录接口**: 每分钟最多 5 次尝试
- **普通接口**: 每分钟最多 100 次请求
- **文件上传**: 每分钟最多 10 次上传
- **导出接口**: 每小时最多 5 次导出

超出限制时返回 `429 Too Many Requests`。

## SDK 和示例

### Python SDK 示例

```python
import requests

class CRMClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def login(self, username, password):
        response = self.session.post(
            f'{self.base_url}/auth/login',
            json={'username': username, 'password': password}
        )
        data = response.json()
        self.token = data['data']['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        return data
    
    def get_employees(self, page=1, page_size=20):
        response = self.session.get(
            f'{self.base_url}/employees',
            params={'page': page, 'page_size': page_size}
        )
        return response.json()

# 使用示例
client = CRMClient('http://localhost:8000/api')
client.login('admin', 'admin123')
employees = client.get_employees()
```

### JavaScript SDK 示例

```javascript
class CRMClient {
    constructor(baseUrl, token = null) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async request(method, endpoint, data = null) {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const config = {
            method,
            headers,
        };
        
        if (data) {
            config.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, config);
        return response.json();
    }
    
    async login(username, password) {
        const result = await this.request('POST', '/auth/login', {
            username,
            password
        });
        this.token = result.data.access_token;
        return result;
    }
    
    async getEmployees(page = 1, pageSize = 20) {
        return this.request('GET', `/employees?page=${page}&page_size=${pageSize}`);
    }
}

// 使用示例
const client = new CRMClient('http://localhost:8000/api');
await client.login('admin', 'admin123');
const employees = await client.getEmployees();
```

## 版本更新日志

### v1.0.0 (2024-01-20)
- 初始版本发布
- 实现基础的 CRUD 功能
- 支持 JWT 认证
- 实现 RBAC 权限控制
- 支持异步任务处理

### 计划功能
- 消息推送系统
- 数据统计分析
- 移动端 API 优化
- GraphQL 支持

---

**注意事项**:
1. 所有时间戳均使用 UTC 时区
2. 文件上传大小限制为 10MB
3. API 响应时间目标为 < 200ms
4. 详细的交互式文档请访问：http://localhost:8000/docs
5. 生产环境请使用 HTTPS 协议
