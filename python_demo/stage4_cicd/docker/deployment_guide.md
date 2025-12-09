# Docker 部署指南

本指南介绍如何使用 Docker 部署 Python 应用到不同环境。

## 目录

1. [本地开发环境](#本地开发环境)
2. [测试环境部署](#测试环境部署)
3. [生产环境部署](#生产环境部署)
4. [云平台部署](#云平台部署)
5. [故障排查](#故障排查)

## 本地开发环境

### 快速开始

1. **克隆项目**
   ```bash
   git clone https://github.com/yourname/yourproject.git
   cd yourproject
   ```

2. **创建环境变量文件**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置必要的环境变量
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **初始化数据库**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. **访问应用**
   - 应用: http://localhost:8000
   - 管理后台: http://localhost:8000/admin

### 开发工作流

**代码热重载**
```yaml
# docker-compose.dev.yml
services:
  web:
    volumes:
      - ./app:/app  # 挂载代码目录
    command: python app.py --reload
```

**查看日志**
```bash
# 所有服务的日志
docker-compose logs -f

# 特定服务的日志
docker-compose logs -f web

# 最近 100 行
docker-compose logs --tail=100 web
```

**执行命令**
```bash
# 运行测试
docker-compose exec web pytest

# 进入 Python shell
docker-compose exec web python

# 进入容器 shell
docker-compose exec web /bin/bash
```

**重启服务**
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart web
```

## 测试环境部署

### 准备工作

1. **服务器要求**
   - Ubuntu 20.04 或更高版本
   - 至少 2GB RAM
   - 至少 20GB 磁盘空间
   - Docker 和 Docker Compose 已安装

2. **安装 Docker**
   ```bash
   # 在服务器上执行
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **安装 Docker Compose**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

### 部署步骤

1. **克隆代码**
   ```bash
   git clone https://github.com/yourname/yourproject.git
   cd yourproject
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env.staging
   nano .env.staging
   ```

   ```env
   # .env.staging
   DEBUG=false
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:pass@db:5432/myapp
   ALLOWED_HOSTS=staging.example.com
   ```

3. **构建镜像**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.staging.yml build
   ```

4. **启动服务**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
   ```

5. **初始化数据库**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. **收集静态文件**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### 配置 Nginx

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name staging.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/myapp/static/;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 配置 SSL

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d staging.example.com

# 自动续期
sudo certbot renew --dry-run
```

## 生产环境部署

### 安全加固

1. **使用非 root 用户**
   ```dockerfile
   USER appuser
   ```

2. **限制资源**
   ```yaml
   services:
     web:
       deploy:
         resources:
           limits:
             cpus: '1.0'
             memory: 512M
           reservations:
             cpus: '0.5'
             memory: 256M
   ```

3. **使用 secrets**
   ```yaml
   services:
     web:
       secrets:
         - db_password
         - secret_key

   secrets:
     db_password:
       file: ./secrets/db_password.txt
     secret_key:
       file: ./secrets/secret_key.txt
   ```

4. **网络隔离**
   ```yaml
   networks:
     frontend:
       driver: bridge
     backend:
       driver: bridge
       internal: true  # 不允许外部访问
   ```

### 高可用配置

1. **多实例部署**
   ```yaml
   services:
     web:
       deploy:
         replicas: 3
         update_config:
           parallelism: 1
           delay: 10s
         restart_policy:
           condition: on-failure
   ```

2. **负载均衡**
   ```nginx
   upstream backend {
       least_conn;
       server web1:8000;
       server web2:8000;
       server web3:8000;
   }

   server {
       location / {
           proxy_pass http://backend;
       }
   }
   ```

3. **健康检查**
   ```yaml
   services:
     web:
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 3s
         retries: 3
         start_period: 40s
   ```

### 数据备份

1. **数据库备份脚本**
   ```bash
   #!/bin/bash
   # backup.sh

   BACKUP_DIR="/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

   # 创建备份
   docker-compose exec -T db pg_dump -U postgres myapp > $BACKUP_FILE

   # 压缩备份
   gzip $BACKUP_FILE

   # 删除 7 天前的备份
   find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

   echo "Backup completed: $BACKUP_FILE.gz"
   ```

2. **设置定时任务**
   ```bash
   # 添加到 crontab
   0 2 * * * /path/to/backup.sh
   ```

### 监控和日志

1. **日志配置**
   ```yaml
   services:
     web:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

2. **集成监控工具**
   ```yaml
   services:
     prometheus:
       image: prom/prometheus
       volumes:
         - ./prometheus.yml:/etc/prometheus/prometheus.yml
       ports:
         - "9090:9090"

     grafana:
       image: grafana/grafana
       ports:
         - "3000:3000"
       depends_on:
         - prometheus
   ```

## 云平台部署

### AWS ECS

1. **创建 ECR 仓库**
   ```bash
   aws ecr create-repository --repository-name myapp
   ```

2. **推送镜像**
   ```bash
   # 登录 ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

   # 构建并推送
   docker build -t myapp .
   docker tag myapp:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
   docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
   ```

3. **创建 ECS 任务定义**
   ```json
   {
     "family": "myapp",
     "containerDefinitions": [
       {
         "name": "web",
         "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest",
         "memory": 512,
         "cpu": 256,
         "essential": true,
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ]
       }
     ]
   }
   ```

### Google Cloud Run

```bash
# 构建并推送到 GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/myapp

# 部署到 Cloud Run
gcloud run deploy myapp \
  --image gcr.io/PROJECT_ID/myapp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku

```bash
# 登录 Heroku
heroku login

# 创建应用
heroku create myapp

# 设置容器栈
heroku stack:set container

# 部署
git push heroku main
```

### DigitalOcean App Platform

1. 连接 GitHub 仓库
2. 选择 Dockerfile
3. 配置环境变量
4. 部署

## 零停机部署

### 蓝绿部署

```bash
# 部署新版本（绿）
docker-compose -f docker-compose.green.yml up -d

# 健康检查
curl -f http://green.example.com/health

# 切换流量
# 更新 Nginx 配置指向绿环境

# 停止旧版本（蓝）
docker-compose -f docker-compose.blue.yml down
```

### 滚动更新

```yaml
services:
  web:
    deploy:
      update_config:
        parallelism: 1  # 一次更新一个容器
        delay: 10s      # 更新间隔
        order: start-first  # 先启动新容器
```

## 故障排查

### 容器无法启动

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs web

# 检查配置
docker-compose config

# 验证镜像
docker images
```

### 网络问题

```bash
# 检查网络
docker network ls
docker network inspect myapp_default

# 测试连接
docker-compose exec web ping db
docker-compose exec web curl http://redis:6379
```

### 性能问题

```bash
# 查看资源使用
docker stats

# 查看容器进程
docker-compose top

# 检查磁盘空间
df -h
docker system df
```

### 数据库问题

```bash
# 进入数据库
docker-compose exec db psql -U postgres -d myapp

# 检查连接
docker-compose exec web python -c "from app import db; print(db.engine.url)"

# 查看数据库日志
docker-compose logs db
```

## 最佳实践总结

1. **使用多阶段构建**减小镜像大小
2. **使用 .dockerignore**排除不需要的文件
3. **固定依赖版本**确保可重复性
4. **使用非 root 用户**提高安全性
5. **配置健康检查**自动恢复故障
6. **实施日志管理**便于问题排查
7. **定期备份数据**防止数据丢失
8. **监控资源使用**及时发现问题
9. **使用 secrets**管理敏感信息
10. **实施 CI/CD**自动化部署流程

## 检查清单

部署前检查：
- [ ] 所有环境变量已配置
- [ ] 数据库已初始化
- [ ] 静态文件已收集
- [ ] SSL 证书已配置
- [ ] 防火墙规则已设置
- [ ] 备份策略已实施
- [ ] 监控已配置
- [ ] 日志已配置
- [ ] 健康检查已配置
- [ ] 文档已更新

## 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Docker 安全最佳实践](https://docs.docker.com/engine/security/)
- [12-Factor App](https://12factor.net/)
