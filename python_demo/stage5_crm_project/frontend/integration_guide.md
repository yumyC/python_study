# CRM 前端集成指南

本文档详细介绍如何将 PureAdminThin 前端项目与 CRM 后端系统进行集成。

## 概述

CRM 前端项目基于 Vue 3 + TypeScript + Element Plus 构建，采用前后端分离架构，通过 RESTful API 与后端进行数据交互。

## 架构设计

### 前后端分离架构

```
┌─────────────────┐    HTTP/HTTPS     ┌─────────────────┐
│                 │ ◄──────────────► │                 │
│   前端 (Vue 3)   │                  │  后端 (FastAPI) │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
        │                                      │
        │                                      │
        ▼                                      ▼
┌─────────────────┐                  ┌─────────────────┐
│   静态资源服务   │                  │   数据库服务     │
│   (Nginx)       │                  │  (PostgreSQL)   │
└─────────────────┘                  └─────────────────┘
```

### 技术栈对应关系

| 层级 | 前端技术 | 后端技术 | 说明 |
|------|----------|----------|------|
| 表现层 | Vue 3 + Element Plus | - | 用户界面和交互 |
| 路由层 | Vue Router | FastAPI Router | 页面路由和 API 路由 |
| 状态管理 | Pinia | - | 前端状态管理 |
| 数据层 | Axios | SQLAlchemy | HTTP 请求和 ORM |
| 认证层 | JWT Token | JWT + RBAC | 身份认证和权限控制 |

## 环境搭建

### 前端环境

1. **安装 Node.js**
   ```bash
   # 推荐使用 Node.js 16+
   node --version
   npm --version
   ```

2. **安装项目依赖**
   ```bash
   cd frontend/pure-admin-thin
   npm install
   ```

3. **配置环境变量**
   ```bash
   # 创建 .env.local 文件
   VITE_API_BASE_URL=http://localhost:8000
   VITE_APP_TITLE=CRM 管理系统
   ```

### 后端环境

1. **启动后端服务**
   ```bash
   # FastAPI 版本
   cd backend/fastapi_version
   python -m uvicorn app.main:app --reload --port 8000
   
   # Flask 版本
   cd backend/flask_version
   python app.py
   ```

2. **验证后端服务**
   ```bash
   curl http://localhost:8000/api/health
   ```

## API 集成

### 认证流程

#### 1. 登录认证

**前端实现**:
```typescript
// stores/auth.ts
const login = async (loginForm: LoginForm) => {
  const response = await authApi.login(loginForm)
  const { access_token, user } = response.data
  
  token.value = access_token
  userInfo.value = user
  setToken(access_token)
}
```

**后端接口**:
```python
# FastAPI
@router.post("/login")
async def login(credentials: LoginRequest):
    user = authenticate_user(credentials.username, credentials.password)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "user": user}
```

#### 2. Token 管理

**自动添加 Token**:
```typescript
// utils/request.ts
service.interceptors.request.use((config) => {
  const token = getToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

**Token 过期处理**:
```typescript
service.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### 数据交互

#### 1. 员工管理集成

**前端 API 调用**:
```typescript
// api/employee.ts
export const employeeApi = {
  getEmployees(params: EmployeeSearchParams) {
    return request.get<PaginationResponse<Employee>>('/employees', { params })
  },
  
  createEmployee(data: EmployeeForm) {
    return request.post<Employee>('/employees', data)
  }
}
```

**后端 API 实现**:
```python
# FastAPI
@router.get("/employees")
async def get_employees(
    page: int = 1,
    size: int = 20,
    search: str = None,
    db: Session = Depends(get_db)
):
    employees = employee_service.get_employees(db, page, size, search)
    return PaginationResponse(
        items=employees.items,
        total=employees.total,
        page=page,
        size=size
    )
```

#### 2. 工作日志集成

**异步导出功能**:
```typescript
// 前端：启动导出任务
const handleExport = async () => {
  const response = await workLogApi.exportWorkLogs(params)
  const taskId = response.data.task_id
  
  // 轮询任务状态
  const checkStatus = async () => {
    const statusResponse = await workLogApi.getExportTaskStatus(taskId)
    if (statusResponse.data.status === 'completed') {
      // 下载文件
      downloadFile(statusResponse.data.download_url)
    } else {
      setTimeout(checkStatus, 2000)
    }
  }
  
  setTimeout(checkStatus, 2000)
}
```

```python
# 后端：Celery 异步任务
@celery_app.task
def export_work_logs_task(params):
    # 生成 Excel 文件
    file_path = generate_excel_report(params)
    return {"status": "completed", "file_path": file_path}
```

## 权限控制

### 路由权限

**前端路由守卫**:
```typescript
// router/index.ts
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth !== false) {
    if (!authStore.isAuthenticated) {
      await authStore.checkAuth()
      if (!authStore.isAuthenticated) {
        next('/login')
        return
      }
    }
  }
  
  next()
})
```

**后端权限验证**:
```python
# FastAPI 依赖注入
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = get_user_by_username(username)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/employees")
async def get_employees(current_user: User = Depends(get_current_user)):
    # 检查用户权限
    if not has_permission(current_user, "employees", "view"):
        raise HTTPException(status_code=403, detail="Permission denied")
    # 返回数据
```

### 菜单权限

**动态菜单加载**:
```typescript
// stores/menu.ts
const getUserMenus = async () => {
  const response = await menuApi.getUserMenus()
  const menuTree = buildMenuTree(response.data)
  return menuTree
}
```

**权限配置界面**:
```typescript
// views/permissions/index.vue
const handleSave = async () => {
  const permissions = Object.entries(rolePermissions).map(([menuId, perms]) => ({
    menu_id: menuId,
    permissions: perms
  }))
  
  await permissionApi.updateRolePermissions(selectedRoleId.value, permissions)
}
```

## 部署集成

### 开发环境

**Docker Compose 配置**:
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  frontend:
    build: ./frontend/pure-admin-thin
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://backend:8000

  backend:
    build: ./backend/fastapi_version
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: crm_db
      POSTGRES_USER: crm_user
      POSTGRES_PASSWORD: crm_pass

  redis:
    image: redis:6-alpine
```

### 生产环境

**Nginx 配置**:
```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持（如需要）
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 数据格式规范

### API 响应格式

**成功响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "example"
  }
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "Validation error",
  "data": {
    "field": "username",
    "error": "Username is required"
  }
}
```

**分页响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

### 日期时间格式

- **前端显示**: `YYYY-MM-DD HH:mm:ss`
- **API 传输**: ISO 8601 格式 `2024-01-01T00:00:00Z`
- **数据库存储**: UTC 时间戳

### 状态码规范

| 状态码 | 说明 | 前端处理 |
|--------|------|----------|
| 200 | 成功 | 正常处理 |
| 400 | 请求错误 | 显示错误信息 |
| 401 | 未认证 | 跳转登录页 |
| 403 | 无权限 | 显示权限错误 |
| 404 | 资源不存在 | 显示 404 页面 |
| 500 | 服务器错误 | 显示系统错误 |

## 性能优化

### 前端优化

1. **代码分割**:
   ```typescript
   // 路由懒加载
   const Dashboard = () => import('@/views/dashboard/index.vue')
   ```

2. **请求优化**:
   ```typescript
   // 请求缓存
   const cache = new Map()
   
   const cachedRequest = async (url: string) => {
     if (cache.has(url)) {
       return cache.get(url)
     }
     
     const response = await request.get(url)
     cache.set(url, response)
     return response
   }
   ```

3. **虚拟滚动**:
   ```vue
   <!-- 大数据量表格 -->
   <el-table-v2
     :columns="columns"
     :data="tableData"
     :width="800"
     :height="400"
   />
   ```

### 后端优化

1. **数据库查询优化**:
   ```python
   # 使用 select_related 减少查询次数
   employees = db.query(Employee)\
     .options(selectinload(Employee.position))\
     .options(selectinload(Employee.role))\
     .all()
   ```

2. **缓存策略**:
   ```python
   # Redis 缓存
   @cache.memoize(timeout=300)
   def get_user_permissions(user_id: str):
       return permission_service.get_user_permissions(user_id)
   ```

## 测试集成

### 前端测试

**单元测试**:
```typescript
// tests/stores/auth.test.ts
import { describe, it, expect } from 'vitest'
import { useAuthStore } from '@/stores/auth'

describe('Auth Store', () => {
  it('should login successfully', async () => {
    const authStore = useAuthStore()
    const result = await authStore.login({
      username: 'admin',
      password: '123456'
    })
    expect(result.success).toBe(true)
  })
})
```

**E2E 测试**:
```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[placeholder="请输入用户名"]', 'admin')
  await page.fill('[placeholder="请输入密码"]', '123456')
  await page.click('button:has-text("登录")')
  await expect(page).toHaveURL('/')
})
```

### API 测试

**接口测试**:
```python
# tests/test_api.py
def test_login_api(client):
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## 故障排除

### 常见问题

1. **CORS 跨域问题**:
   ```python
   # FastAPI 后端配置
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **代理配置问题**:
   ```typescript
   // vite.config.ts
   export default defineConfig({
     server: {
       proxy: {
         '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true,
           rewrite: (path) => path.replace(/^\/api/, '/api')
         }
       }
     }
   })
   ```

3. **Token 过期处理**:
   ```typescript
   // 自动刷新 Token
   let isRefreshing = false
   let failedQueue: any[] = []
   
   service.interceptors.response.use(
     (response) => response,
     async (error) => {
       if (error.response?.status === 401 && !isRefreshing) {
         isRefreshing = true
         try {
           await authStore.refreshToken()
           // 重试失败的请求
           failedQueue.forEach(({ resolve, config }) => {
             resolve(service(config))
           })
         } catch (refreshError) {
           await authStore.logout()
         } finally {
           isRefreshing = false
           failedQueue = []
         }
       }
       return Promise.reject(error)
     }
   )
   ```

### 调试技巧

1. **网络请求调试**:
   ```typescript
   // 开发环境下打印请求日志
   if (import.meta.env.DEV) {
     service.interceptors.request.use((config) => {
       console.log('Request:', config)
       return config
     })
     
     service.interceptors.response.use((response) => {
       console.log('Response:', response)
       return response
     })
   }
   ```

2. **状态调试**:
   ```typescript
   // Pinia 开发工具
   import { createPinia } from 'pinia'
   
   const pinia = createPinia()
   
   if (import.meta.env.DEV) {
     pinia.use(({ store }) => {
       store.$subscribe((mutation, state) => {
         console.log('Store mutation:', mutation, state)
       })
     })
   }
   ```

## 最佳实践

### 代码规范

1. **TypeScript 类型定义**:
   ```typescript
   // 严格的类型定义
   interface ApiResponse<T> {
     code: number
     message: string
     data: T
   }
   
   // 使用泛型
   const request = <T>(url: string): Promise<ApiResponse<T>> => {
     return axios.get(url)
   }
   ```

2. **错误处理**:
   ```typescript
   // 统一错误处理
   const handleApiError = (error: any) => {
     if (error.response) {
       ElMessage.error(error.response.data.message)
     } else if (error.request) {
       ElMessage.error('网络错误，请检查网络连接')
     } else {
       ElMessage.error('请求失败')
     }
   }
   ```

3. **组件设计**:
   ```vue
   <!-- 可复用的表格组件 -->
   <template>
     <el-table :data="data" v-bind="$attrs">
       <slot />
     </el-table>
   </template>
   
   <script setup lang="ts">
   interface Props {
     data: any[]
   }
   
   defineProps<Props>()
   </script>
   ```

### 安全考虑

1. **XSS 防护**:
   ```typescript
   // 输入验证和转义
   const sanitizeInput = (input: string) => {
     return input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
   }
   ```

2. **CSRF 防护**:
   ```typescript
   // 添加 CSRF Token
   service.interceptors.request.use((config) => {
     const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
     if (csrfToken) {
       config.headers['X-CSRF-Token'] = csrfToken
     }
     return config
   })
   ```

## 总结

通过本集成指南，您可以：

1. ✅ 理解前后端分离架构设计
2. ✅ 掌握 API 接口集成方法
3. ✅ 实现完整的认证授权流程
4. ✅ 配置开发和生产环境
5. ✅ 处理常见的集成问题
6. ✅ 遵循最佳实践和安全规范

如有其他问题，请参考项目文档或联系技术支持团队。