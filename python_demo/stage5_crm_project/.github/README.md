# CRM 项目 CI/CD 配置说明

## 概述

本目录包含了 CRM 项目的完整 CI/CD 配置，采用 GitHub Actions 实现自动化的构建、测试和部署流程。

## 工作流程概览

### 1. 后端 CI 流程 (`backend_ci.yml`)

**触发条件:**
- 推送到 `main` 或 `develop` 分支
- 对 `backend/` 目录的 Pull Request
- 修改 CI 配置文件

**执行步骤:**
1. **多版本测试**: 在 Python 3.9, 3.10, 3.11 上测试
2. **代码质量检查**: Black 格式化、Flake8 风格检查、MyPy 类型检查
3. **单元测试**: 运行 pytest 测试套件，生成覆盖率报告
4. **安全扫描**: Bandit 安全漏洞扫描、Safety 依赖安全检查
5. **Docker 构建**: 构建并推送 Docker 镜像到 Docker Hub

**支持的后端版本:**
- FastAPI 版本
- Flask 版本

### 2. 前端 CI 流程 (`frontend_ci.yml`)

**触发条件:**
- 推送到 `main` 或 `develop` 分支
- 对 `frontend/` 目录的 Pull Request
- 修改 CI 配置文件

**执行步骤:**
1. **多版本测试**: 在 Node.js 18.x, 20.x 上测试
2. **代码质量检查**: ESLint 检查、Prettier 格式检查、TypeScript 类型检查
3. **构建测试**: 执行生产构建
4. **性能审计**: Lighthouse CI 性能测试 (仅 PR)
5. **安全扫描**: npm audit 依赖安全检查
6. **Docker 构建**: 构建并推送前端 Docker 镜像

### 3. 部署流程 (`deploy.yml`)

**触发条件:**
- 推送到 `main` 分支 (自动部署到测试环境)
- 创建版本标签 `v*` (自动部署到生产环境)
- 手动触发 (可选择环境)

**部署环境:**
- **Staging**: 测试环境，用于验证功能
- **Production**: 生产环境，面向最终用户

**部署步骤:**
1. **镜像构建**: 构建最新的 Docker 镜像
2. **服务器部署**: SSH 连接到目标服务器执行部署脚本
3. **健康检查**: 验证服务是否正常启动
4. **回滚机制**: 部署失败时自动回滚到上一版本
5. **通知**: 发送部署状态通知到 Slack

## 配置要求

### GitHub Secrets

在仓库的 `Settings > Secrets and variables > Actions` 中配置以下密钥:

#### Docker Hub 配置
```
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_password_or_token
```

#### 服务器配置
```
# 测试环境
STAGING_HOST=staging.example.com
STAGING_USER=deploy
STAGING_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
STAGING_PORT=22

# 生产环境
PRODUCTION_HOST=production.example.com
PRODUCTION_USER=deploy
PRODUCTION_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
PRODUCTION_PORT=22
```

#### 环境变量
```
PROD_DATABASE_URL=postgresql://user:pass@host:5432/db
PROD_REDIS_URL=redis://user:pass@host:6379/0
PROD_SECRET_KEY=your-production-secret-key
```

#### 通知配置 (可选)
```
SLACK_WEBHOOK=https://hooks.slack.com/services/...
LHCI_GITHUB_APP_TOKEN=your_lighthouse_token
```

### 服务器准备

#### 1. 安装 Docker 和 Docker Compose

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 创建部署用户

```bash
# 创建部署用户
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# 配置 SSH 密钥
sudo mkdir -p /home/deploy/.ssh
sudo chown deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh

# 添加公钥到 authorized_keys
echo "your-public-key" | sudo tee /home/deploy/.ssh/authorized_keys
sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

#### 3. 创建项目目录

```bash
# 创建项目目录
sudo mkdir -p /opt/crm-app
sudo chown deploy:deploy /opt/crm-app

# 克隆项目 (首次部署)
cd /opt/crm-app
git clone https://github.com/your-username/crm-project.git .
```

## 工作流程详解

### 代码质量检查

#### 后端代码质量标准
- **Black**: 代码格式化，确保一致的代码风格
- **Flake8**: 代码风格检查，遵循 PEP 8 规范
- **MyPy**: 静态类型检查，提高代码可靠性
- **Bandit**: 安全漏洞扫描，识别潜在安全问题
- **Safety**: 依赖安全检查，检测已知漏洞

#### 前端代码质量标准
- **ESLint**: JavaScript/TypeScript 代码检查
- **Prettier**: 代码格式化
- **TypeScript**: 类型检查
- **npm audit**: 依赖安全检查

### 测试策略

#### 后端测试
```bash
# 单元测试
pytest tests/unit/ -v --cov=app

# 集成测试
pytest tests/integration/ -v

# API 测试
pytest tests/api/ -v
```

#### 前端测试
```bash
# 单元测试 (如果配置)
npm run test:unit

# 端到端测试 (如果配置)
npm run test:e2e

# 类型检查
npx vue-tsc --noEmit
```

### Docker 镜像构建

#### 后端镜像
- **基础镜像**: Python 3.11-slim
- **多阶段构建**: 优化镜像大小
- **安全扫描**: 构建时进行安全检查
- **标签策略**: `latest` 和 `git-sha` 标签

#### 前端镜像
- **构建阶段**: Node.js 20-alpine
- **运行阶段**: Nginx Alpine
- **静态文件优化**: Gzip 压缩、缓存配置
- **单页应用支持**: History 模式路由配置

### 部署策略

#### 蓝绿部署
1. 构建新版本镜像
2. 启动新版本容器
3. 健康检查通过后切换流量
4. 停止旧版本容器

#### 滚动更新
1. 逐个更新服务实例
2. 确保服务可用性
3. 自动回滚机制

#### 数据库迁移
```bash
# 自动执行数据库迁移
docker-compose exec backend alembic upgrade head
```

## 监控和告警

### 部署监控
- **健康检查**: 自动验证服务状态
- **性能监控**: 响应时间和错误率
- **资源监控**: CPU、内存、磁盘使用率

### 告警通知
- **Slack 集成**: 部署状态实时通知
- **邮件通知**: 关键错误邮件提醒
- **GitHub 状态**: PR 状态检查

## 故障排除

### 常见问题

#### 1. Docker 构建失败
```bash
# 检查 Dockerfile 语法
docker build --no-cache -t test-image .

# 查看构建日志
docker build --progress=plain -t test-image .
```

#### 2. 测试失败
```bash
# 本地运行测试
pytest -v --tb=short

# 检查测试覆盖率
pytest --cov=app --cov-report=html
```

#### 3. 部署失败
```bash
# 检查服务器连接
ssh deploy@server-ip "docker --version"

# 查看部署日志
ssh deploy@server-ip "cd /opt/crm-app && docker-compose logs"
```

#### 4. 权限问题
```bash
# 检查 SSH 密钥权限
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub

# 检查服务器用户权限
sudo usermod -aG docker deploy
```

### 调试技巧

#### 1. 本地模拟 CI 环境
```bash
# 使用 act 工具本地运行 GitHub Actions
act -j test-fastapi
```

#### 2. 查看详细日志
```bash
# GitHub Actions 日志
# 在 Actions 页面点击具体的工作流查看详细日志

# 服务器日志
ssh deploy@server "journalctl -u docker -f"
```

#### 3. 手动部署测试
```bash
# 手动执行部署脚本
ssh deploy@server "cd /opt/crm-app && ./deploy.sh"
```

## 最佳实践

### 1. 分支策略
- `main`: 生产环境代码，每次提交触发部署
- `develop`: 开发环境代码，用于集成测试
- `feature/*`: 功能分支，创建 PR 时触发测试

### 2. 版本管理
- 使用语义化版本号: `v1.2.3`
- 标签触发生产部署
- 保持版本历史记录

### 3. 安全考虑
- 定期更新依赖包
- 使用最小权限原则
- 敏感信息使用 Secrets 管理
- 定期轮换密钥

### 4. 性能优化
- 使用 Docker 层缓存
- 并行执行测试
- 优化镜像大小
- 使用 CDN 加速

## 扩展配置

### 添加新的测试环境
1. 复制现有的部署配置
2. 修改环境变量
3. 添加新的 GitHub Secrets
4. 更新工作流程文件

### 集成其他工具
- **SonarQube**: 代码质量分析
- **Snyk**: 安全漏洞扫描
- **Datadog**: 应用性能监控
- **Sentry**: 错误追踪

### 自定义通知
```yaml
# 添加自定义通知步骤
- name: Custom Notification
  if: always()
  run: |
    curl -X POST ${{ secrets.WEBHOOK_URL }} \
      -H "Content-Type: application/json" \
      -d '{"status": "${{ job.status }}", "commit": "${{ github.sha }}"}'
```

## 维护和更新

### 定期维护任务
1. **更新依赖**: 每月检查并更新依赖包
2. **清理镜像**: 定期清理旧的 Docker 镜像
3. **备份验证**: 定期测试备份恢复流程
4. **性能调优**: 根据监控数据优化配置

### 升级指南
1. **GitHub Actions**: 关注 Actions 版本更新
2. **Docker**: 保持 Docker 和 Compose 最新版本
3. **依赖包**: 使用 Dependabot 自动更新依赖

---

**注意**: 请根据实际项目需求调整配置参数，确保所有敏感信息的安全性。