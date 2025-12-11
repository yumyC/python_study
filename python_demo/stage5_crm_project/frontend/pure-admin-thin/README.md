# CRM 前端项目

基于 Vue 3 + TypeScript + Element Plus + PureAdminThin 的 CRM 管理系统前端。

## 技术栈

- **框架**: Vue 3.3+
- **语言**: TypeScript 5.1+
- **构建工具**: Vite 4.4+
- **UI 组件库**: Element Plus 2.3+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP 客户端**: Axios 1.4+
- **图标**: Element Plus Icons
- **样式**: SCSS

## 功能特性

### 🔐 认证授权
- JWT Token 认证
- 自动 Token 刷新
- 路由权限控制
- 登录状态持久化

### 📊 仪表盘
- 数据统计展示
- 快速操作入口
- 系统信息概览

### 👥 员工管理
- 员工信息 CRUD
- 搜索和分页
- 批量操作
- 密码重置

### 📝 工作日志
- 日志记录和管理
- 自评和上级评分
- 状态跟踪
- Excel 导出

### 🏢 组织架构
- 岗位管理（树形结构）
- 角色管理
- 菜单管理
- 权限配置

### 🎨 界面特性
- 响应式设计
- 暗色主题支持
- 国际化准备
- 优雅的加载状态

## 项目结构

```
src/
├── api/                    # API 接口
│   ├── auth.ts            # 认证相关
│   ├── employee.ts        # 员工管理
│   ├── menu.ts            # 菜单管理
│   └── worklog.ts         # 工作日志
├── components/            # 公共组件
├── layout/               # 布局组件
│   └── index.vue         # 主布局
├── router/               # 路由配置
│   └── index.ts          # 路由定义
├── stores/               # 状态管理
│   ├── auth.ts           # 认证状态
│   └── menu.ts           # 菜单状态
├── styles/               # 样式文件
│   └── index.scss        # 全局样式
├── types/                # TypeScript 类型定义
│   ├── auth.ts           # 认证类型
│   ├── common.ts         # 通用类型
│   ├── employee.ts       # 员工类型
│   ├── menu.ts           # 菜单类型
│   └── worklog.ts        # 工作日志类型
├── utils/                # 工具函数
│   ├── auth.ts           # 认证工具
│   ├── export.ts         # 导出工具
│   └── request.ts        # HTTP 请求
├── views/                # 页面组件
│   ├── dashboard/        # 仪表盘
│   ├── employees/        # 员工管理
│   ├── login/            # 登录页面
│   ├── menus/            # 菜单管理
│   ├── permissions/      # 权限管理
│   ├── positions/        # 岗位管理
│   ├── roles/            # 角色管理
│   ├── work-logs/        # 工作日志
│   └── error/            # 错误页面
├── App.vue               # 根组件
└── main.ts               # 入口文件
```

## 快速开始

### 环境要求

- Node.js 16+
- npm 或 yarn 或 pnpm

### 安装依赖

```bash
# 使用 npm
npm install

# 使用 yarn
yarn install

# 使用 pnpm
pnpm install
```

### 开发环境

```bash
# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### 构建部署

```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

### 代码规范

```bash
# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 配置说明

### 环境变量

创建 `.env.local` 文件配置环境变量：

```bash
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# 应用标题
VITE_APP_TITLE=CRM 管理系统
```

### 代理配置

开发环境下，API 请求会自动代理到后端服务器（默认 `http://localhost:8000`）。

可以在 `vite.config.ts` 中修改代理配置：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## API 接口

### 认证接口

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户退出
- `GET /api/auth/me` - 获取用户信息
- `POST /api/auth/refresh` - 刷新 Token

### 员工管理

- `GET /api/employees` - 获取员工列表
- `POST /api/employees` - 创建员工
- `PUT /api/employees/:id` - 更新员工
- `DELETE /api/employees/:id` - 删除员工

### 工作日志

- `GET /api/work-logs` - 获取工作日志列表
- `POST /api/work-logs` - 创建工作日志
- `PUT /api/work-logs/:id` - 更新工作日志
- `POST /api/work-logs/:id/rate` - 上级评分
- `POST /api/work-logs/export` - 导出日志

更多接口详情请参考后端 API 文档。

## 开发指南

### 添加新页面

1. 在 `src/views/` 下创建页面组件
2. 在 `src/router/index.ts` 中添加路由
3. 在 `src/types/` 中定义相关类型
4. 在 `src/api/` 中添加 API 接口

### 状态管理

使用 Pinia 进行状态管理，示例：

```typescript
// stores/example.ts
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', () => {
  const state = ref('')
  
  const action = async () => {
    // 异步操作
  }
  
  return { state, action }
})
```

### HTTP 请求

使用封装的 request 工具：

```typescript
import { request } from '@/utils/request'

// GET 请求
const response = await request.get('/api/data')

// POST 请求
const response = await request.post('/api/data', { name: 'test' })
```

### 类型定义

为 API 响应和组件 Props 定义 TypeScript 类型：

```typescript
// types/example.ts
export interface ExampleData {
  id: string
  name: string
  created_at: string
}

export interface ExampleForm {
  name: string
}
```

## 部署指南

### 构建优化

项目已配置了以下优化：

- 代码分割和懒加载
- 静态资源压缩
- Tree Shaking
- 生产环境去除 console

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    # 处理 Vue Router 的 History 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://backend-server:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker 部署

```dockerfile
# Dockerfile
FROM node:16-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 测试账号

开发环境默认测试账号：

- **用户名**: admin
- **密码**: 123456

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 常见问题

### Q: 登录后页面空白？

A: 检查后端 API 是否正常运行，确认 API 地址配置正确。

### Q: 开发环境跨域问题？

A: 确认 `vite.config.ts` 中的代理配置是否正确。

### Q: 构建后路由 404？

A: 确认服务器配置了 History 模式的回退规则。

### Q: 样式不生效？

A: 检查 SCSS 语法是否正确，确认样式文件已正确导入。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0 (2024-01-01)

- ✨ 初始版本发布
- 🔐 完整的认证授权系统
- 👥 员工管理功能
- 📝 工作日志管理
- 🏢 组织架构管理
- 🎨 响应式 UI 设计

## 技术支持

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 技术交流群

---

感谢使用 CRM 管理系统！🎉