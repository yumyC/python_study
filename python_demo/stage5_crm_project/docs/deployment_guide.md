# CRM 项目部署指南

## 概述

本文档详细介绍了 CRM 项目的部署流程，包括开发环境、测试环境和生产环境的部署配置。项目采用 Docker 容器化部署，支持 CI/CD 自动化流程。

## 目录

- [环境要求](#环境要求)
- [开发环境部署](#开发环境部署)
- [测试环境部署](#测试环境部署)
- [生产环境部署](#生产环境部署)
- [CI/CD 配置](#cicd-配置)
- [监控和日志](#监控和日志)
- [故障排除](#故障排除)

## 环境要求

### 基础环境

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Docker 支持的其他 Linux 发行版
- **Docker**: 24.0+
- **Docker Compose**: 2.0+
- **内存**: 最小 4GB，推荐 8GB+
- **存储**: 最小 20GB，推荐 50GB+
- **网络**: 稳定的互联网连接

### 端口要求

- **80**: HTTP (重定向到 HTTPS)
- **443**: HTTPS
- **5432**: PostgreSQL (可选，仅开发环境)
- **6379**: Redis (可选，仅开发环境)
- **3000**: Grafana 监控
- **9090**: Prometheus 监控
- **5555**: Flower Celery 监控

## 开发环境部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd crm-project
```

### 2. 环境配置

#### FastAPI 版本

```bash
cd backend/fastapi_version

# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

#### Flask 版本

```bash
cd backend/flask_version

# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

### 3. 启动开发环境

#### 使用 Docker Compose

```bash
# FastAPI 版本
cd backend/fastapi_version
docker-compose up -d

# Flask 版本
cd backend/flask_version
docker-compose up -d
```

#### 本地开发

```bash
# 后端
cd backend/fastapi_version
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend/pure-admin-thin
npm install
npm run dev
```

### 4. 初始化数据库

```bash
# 创建数据库表
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
"

# 创建初始用户 (可选)
python init_db.py

# 创建演示数据 (可选)
python create_demo_data.py
```

### 5. 访问应用

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 测试环境部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建项目目录
sudo mkdir -p /opt/crm-app
sudo chown $USER:$USER /opt/crm-app
```

### 2. 部署配置

```bash
cd /opt/crm-app

# 克隆项目
git clone <repository-url> .

# 配置环境变量
cp .env.example .env
vim .env
```

### 3. 启动服务

```bash
# 构建并启动服务
docker-compose -f docker-compose.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 生产环境部署

### 1. 服务器配置

#### 系统优化

```bash
# 内核参数优化
sudo tee /etc/sysctl.d/99-crm.conf << EOF
# 网络优化
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200

# 文件描述符限制
fs.file-max = 2097152
EOF

sudo sysctl -p /etc/sysctl.d/99-crm.conf

# 用户限制
sudo tee /etc/security/limits.d/99-crm.conf << EOF
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
EOF
```

#### 防火墙配置

```bash
# 安装 UFW
sudo apt install ufw

# 配置防火墙规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
```

### 2. SSL 证书配置

#### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo mkdir -p /opt/crm-app/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/crm-app/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/crm-app/ssl/key.pem
sudo chown -R $USER:$USER /opt/crm-app/ssl
```

#### 自动续期

```bash
# 添加 cron 任务
sudo crontab -e

# 添加以下行 (每月 1 号凌晨 2 点检查续期)
0 2 1 * * /usr/bin/certbot renew --quiet && /usr/bin/docker-compose -f /opt/crm-app/docker-compose.prod.yml restart nginx
```

### 3. 生产环境配置

```bash
cd /opt/crm-app

# 配置生产环境变量
cat > .env << EOF
# 数据库配置
DATABASE_URL=postgresql://username:password@postgres:5432/crm_db
POSTGRES_DB=crm_db
POSTGRES_USER=username
POSTGRES_PASSWORD=strong_password

# Redis 配置
REDIS_URL=redis://:redis_password@redis:6379/0
REDIS_PASSWORD=redis_password

# 应用配置
SECRET_KEY=your-super-secret-key-here
ENVIRONMENT=production

# Docker 配置
DOCKER_USERNAME=your-docker-username
DOCKER_IMAGE_TAG=latest

# 监控配置
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin_password
FLOWER_USER=admin
FLOWER_PASSWORD=flower_password
EOF

# 设置文件权限
chmod 600 .env
```

### 4. 启动生产服务

```bash
# 拉取最新镜像
docker-compose -f docker-compose.prod.yml pull

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. 数据库初始化

```bash
# 进入后端容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 初始化数据库
python -c "
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
"

# 创建管理员用户
python init_db.py

# 可选：创建演示数据
python create_demo_data.py
```

## CI/CD 配置

### 1. GitHub Secrets 配置

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加以下密钥：

#### Docker Hub 配置
- `DOCKER_USERNAME`: Docker Hub 用户名
- `DOCKER_PASSWORD`: Docker Hub 密码或访问令牌

#### 服务器配置
- `STAGING_HOST`: 测试服务器 IP 地址
- `STAGING_USER`: 测试服务器用户名
- `STAGING_SSH_KEY`: 测试服务器 SSH 私钥
- `STAGING_PORT`: 测试服务器 SSH 端口 (默认 22)

- `PRODUCTION_HOST`: 生产服务器 IP 地址
- `PRODUCTION_USER`: 生产服务器用户名
- `PRODUCTION_SSH_KEY`: 生产服务器 SSH 私钥
- `PRODUCTION_PORT`: 生产服务器 SSH 端口 (默认 22)

#### 生产环境变量
- `PROD_DATABASE_URL`: 生产数据库连接字符串
- `PROD_REDIS_URL`: 生产 Redis 连接字符串
- `PROD_SECRET_KEY`: 生产环境密钥

#### 通知配置 (可选)
- `SLACK_WEBHOOK`: Slack 通知 Webhook URL
- `LHCI_GITHUB_APP_TOKEN`: Lighthouse CI GitHub App Token

### 2. SSH 密钥配置

```bash
# 在本地生成 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "ci-cd@crm-project"

# 将公钥添加到服务器
ssh-copy-id -i ~/.ssh/id_rsa.pub user@server-ip

# 将私钥内容添加到 GitHub Secrets
cat ~/.ssh/id_rsa
```

### 3. 服务器部署脚本

在服务器上创建部署脚本：

```bash
# 创建部署脚本
sudo tee /opt/crm-app/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting deployment..."

# 拉取最新代码
git pull origin main

# 更新 Docker 镜像
docker-compose -f docker-compose.prod.yml pull

# 重启服务
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
sleep 30

# 健康检查
if curl -f http://localhost/api/health; then
    echo "Deployment successful"
else
    echo "Deployment failed"
    exit 1
fi
EOF

chmod +x /opt/crm-app/deploy.sh
```

## 监控和日志

### 1. 日志配置

```bash
# 创建日志目录
mkdir -p /opt/crm-app/logs/{nginx,backend,celery}

# 配置日志轮转
sudo tee /etc/logrotate.d/crm-app << EOF
/opt/crm-app/logs/*/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/crm-app/docker-compose.prod.yml restart nginx
    endscript
}
EOF
```

### 2. 监控配置

#### Prometheus 配置

```bash
mkdir -p /opt/crm-app/monitoring

cat > /opt/crm-app/monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'crm-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
```

#### Grafana 仪表板

访问 http://your-domain:3000 配置 Grafana 仪表板：

1. 添加 Prometheus 数据源: http://prometheus:9090
2. 导入预配置的仪表板
3. 配置告警规则

### 3. 健康检查

```bash
# 创建健康检查脚本
cat > /opt/crm-app/health_check.sh << 'EOF'
#!/bin/bash

# 检查服务状态
services=("nginx" "backend" "postgres" "redis" "celery_worker")

for service in "${services[@]}"; do
    if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        exit 1
    fi
done

# 检查 API 健康状态
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    echo "✓ API health check passed"
else
    echo "✗ API health check failed"
    exit 1
fi

echo "All services are healthy"
EOF

chmod +x /opt/crm-app/health_check.sh

# 添加到 cron 任务 (每 5 分钟检查一次)
echo "*/5 * * * * /opt/crm-app/health_check.sh >> /opt/crm-app/logs/health_check.log 2>&1" | crontab -
```

## 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器日志
docker-compose -f docker-compose.prod.yml logs service_name

# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart service_name
```

#### 2. 数据库连接问题

```bash
# 检查数据库容器
docker-compose -f docker-compose.prod.yml exec postgres psql -U username -d crm_db

# 检查网络连接
docker-compose -f docker-compose.prod.yml exec backend ping postgres
```

#### 3. Redis 连接问题

```bash
# 检查 Redis 容器
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# 检查 Redis 配置
docker-compose -f docker-compose.prod.yml exec redis redis-cli config get "*"
```

#### 4. Nginx 配置问题

```bash
# 测试 Nginx 配置
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# 重新加载 Nginx 配置
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 性能优化

#### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_employee_username ON employees(username);
CREATE INDEX idx_worklog_date ON work_logs(log_date);
CREATE INDEX idx_worklog_employee ON work_logs(employee_id);

-- 分析表统计信息
ANALYZE employees;
ANALYZE work_logs;
```

#### 2. Redis 优化

```bash
# Redis 配置优化
cat >> /opt/crm-app/redis.conf << EOF
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF
```

#### 3. 应用优化

- 启用数据库连接池
- 配置 Redis 缓存
- 使用 CDN 加速静态资源
- 启用 Gzip 压缩
- 优化数据库查询

### 备份和恢复

#### 数据库备份

```bash
# 自动备份脚本
cat > /opt/crm-app/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/crm-app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U username crm_db > $BACKUP_DIR/db_backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 删除 7 天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
EOF

chmod +x /opt/crm-app/backup.sh

# 添加到 cron 任务 (每天凌晨 2 点备份)
echo "0 2 * * * /opt/crm-app/backup.sh" | crontab -
```

#### 数据恢复

```bash
# 恢复数据库
gunzip -c /opt/crm-app/backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U username crm_db
```

## 安全建议

1. **定期更新**: 保持系统和 Docker 镜像的最新版本
2. **访问控制**: 使用防火墙限制不必要的端口访问
3. **SSL/TLS**: 始终使用 HTTPS 加密传输
4. **密码策略**: 使用强密码和定期更换
5. **监控日志**: 定期检查访问日志和错误日志
6. **备份验证**: 定期测试备份文件的完整性
7. **安全扫描**: 定期进行安全漏洞扫描

## 联系支持

如果在部署过程中遇到问题，请：

1. 查看相关日志文件
2. 检查 GitHub Issues
3. 联系技术支持团队

---

**注意**: 本部署指南适用于 CRM 项目的标准部署场景。根据具体的基础设施和需求，可能需要调整配置参数。