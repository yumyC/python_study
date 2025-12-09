# Docker 容器化模块

## 概述

本模块介绍 Docker 容器化技术，学习如何将 Python 应用打包成 Docker 镜像并部署。Docker 是现代应用部署的标准方式，能够确保应用在不同环境中的一致性。

## 学习目标

完成本模块学习后，你将能够：

- 理解容器化的概念和优势
- 编写 Dockerfile 构建镜像
- 使用 docker-compose 管理多容器应用
- 优化 Docker 镜像大小和构建速度
- 部署容器化应用
- 理解容器网络和数据持久化

## 前置知识

- Linux 基础命令
- Python 应用开发
- 基本的网络知识

## 内容结构

### 1. Docker 基础
- Docker 概念和架构
- 镜像和容器的区别
- Docker 命令

### 2. Dockerfile
- Dockerfile 语法
- 多阶段构建
- 最佳实践

### 3. Docker Compose
- docker-compose.yml 配置
- 服务编排
- 网络和卷管理

### 4. 部署
- 容器部署策略
- 生产环境配置
- 监控和日志

## Docker 基础概念

### 什么是 Docker？

Docker 是一个开源的容器化平台，允许开发者将应用及其依赖打包到一个轻量级、可移植的容器中。

### 核心概念

**镜像 (Image)**
- 只读的模板，包含运行应用所需的一切
- 由多个层组成
- 可以从 Dockerfile 构建或从仓库拉取

**容器 (Container)**
- 镜像的运行实例
- 轻量级、隔离的运行环境
- 可以启动、停止、删除

**仓库 (Registry)**
- 存储和分发镜像的服务
- Docker Hub 是公共仓库
- 可以搭建私有仓库

**Dockerfile**
- 定义如何构建镜像的文本文件
- 包含一系列指令
- 自动化构建过程

### Docker vs 虚拟机

| 特性 | Docker 容器 | 虚拟机 |
|------|------------|--------|
| 启动速度 | 秒级 | 分钟级 |
| 资源占用 | 少 | 多 |
| 隔离级别 | 进程级 | 系统级 |
| 性能 | 接近原生 | 有损耗 |
| 镜像大小 | MB 级 | GB 级 |

## 安装 Docker

### Linux
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
```

### macOS
下载并安装 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

### Windows
下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

### 验证安装
```bash
docker --version
docker run hello-world
```

## 常用 Docker 命令

### 镜像操作
```bash
# 拉取镜像
docker pull python:3.9

# 列出镜像
docker images

# 构建镜像
docker build -t myapp:latest .

# 删除镜像
docker rmi myapp:latest

# 查看镜像历史
docker history myapp:latest
```

### 容器操作
```bash
# 运行容器
docker run -d -p 8000:8000 --name myapp myapp:latest

# 列出运行中的容器
docker ps

# 列出所有容器
docker ps -a

# 停止容器
docker stop myapp

# 启动容器
docker start myapp

# 重启容器
docker restart myapp

# 删除容器
docker rm myapp

# 查看容器日志
docker logs myapp

# 进入容器
docker exec -it myapp /bin/bash
```

### 清理命令
```bash
# 删除所有停止的容器
docker container prune

# 删除未使用的镜像
docker image prune

# 删除所有未使用的资源
docker system prune -a
```

## Dockerfile 最佳实践

### 1. 使用官方基础镜像
```dockerfile
# ✅ 使用官方镜像
FROM python:3.9-slim

# ❌ 避免使用 latest 标签
FROM python:latest
```

### 2. 最小化层数
```dockerfile
# ✅ 合并 RUN 命令
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# ❌ 避免多个 RUN 命令
RUN apt-get update
RUN apt-get install -y gcc
RUN rm -rf /var/lib/apt/lists/*
```

### 3. 利用构建缓存
```dockerfile
# ✅ 先复制依赖文件
COPY requirements.txt .
RUN pip install -r requirements.txt

# 然后复制代码
COPY . .

# ❌ 避免一次性复制所有文件
COPY . .
RUN pip install -r requirements.txt
```

### 4. 使用 .dockerignore
```
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git
.gitignore
.dockerignore
Dockerfile
docker-compose.yml
.pytest_cache
.coverage
htmlcov/
```

### 5. 多阶段构建
```dockerfile
# 构建阶段
FROM python:3.9 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

### 6. 非 root 用户运行
```dockerfile
# 创建非 root 用户
RUN useradd -m -u 1000 appuser

# 切换用户
USER appuser

# 运行应用
CMD ["python", "app.py"]
```

## Docker Compose 使用

### 基本配置
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 常用命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 执行命令
docker-compose exec web python manage.py migrate
```

## 容器网络

### 网络类型

**bridge（默认）**
- 容器间可以通过容器名通信
- 适合单主机部署

**host**
- 容器使用主机网络
- 性能最好，但隔离性差

**none**
- 容器没有网络
- 完全隔离

### 创建自定义网络
```bash
# 创建网络
docker network create mynetwork

# 运行容器并连接到网络
docker run -d --network mynetwork --name web myapp

# 查看网络
docker network ls

# 查看网络详情
docker network inspect mynetwork
```

## 数据持久化

### 卷 (Volumes)
```bash
# 创建卷
docker volume create mydata

# 使用卷
docker run -v mydata:/app/data myapp

# 列出卷
docker volume ls

# 删除卷
docker volume rm mydata
```

### 绑定挂载 (Bind Mounts)
```bash
# 挂载主机目录
docker run -v /host/path:/container/path myapp

# 只读挂载
docker run -v /host/path:/container/path:ro myapp
```

## 镜像优化

### 1. 选择合适的基础镜像
```dockerfile
# 标准镜像（~900MB）
FROM python:3.9

# Slim 镜像（~150MB）
FROM python:3.9-slim

# Alpine 镜像（~50MB，但可能有兼容性问题）
FROM python:3.9-alpine
```

### 2. 清理缓存
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

### 3. 使用 .dockerignore
排除不需要的文件，减小构建上下文。

### 4. 多阶段构建
只保留运行时需要的文件。

## 安全最佳实践

### 1. 使用非 root 用户
```dockerfile
USER appuser
```

### 2. 扫描漏洞
```bash
# 使用 Trivy 扫描
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image myapp:latest
```

### 3. 使用可信镜像
- 使用官方镜像
- 验证镜像签名
- 定期更新镜像

### 4. 限制资源
```bash
docker run --memory="512m" --cpus="1.0" myapp
```

## 监控和日志

### 查看容器资源使用
```bash
docker stats
```

### 查看日志
```bash
# 实时日志
docker logs -f myapp

# 最近 100 行
docker logs --tail 100 myapp

# 带时间戳
docker logs -t myapp
```

### 日志驱动
```yaml
# docker-compose.yml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 常见问题

### Q: 容器启动后立即退出？
A: 检查日志 `docker logs container_name`，通常是应用错误或配置问题。

### Q: 如何进入运行中的容器？
A: 使用 `docker exec -it container_name /bin/bash`

### Q: 如何在容器间共享数据？
A: 使用 Docker 卷或绑定挂载。

### Q: 镜像太大怎么办？
A: 使用 slim 基础镜像、多阶段构建、清理缓存。

### Q: 如何更新运行中的容器？
A: 构建新镜像，停止旧容器，启动新容器。使用 docker-compose 可以简化这个过程。

## 学习资源

### 官方文档
- [Docker 官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Dockerfile 参考](https://docs.docker.com/engine/reference/builder/)

### 推荐阅读
- 《Docker 实战》
- 《Docker 深入浅出》

### 视频教程
- [Docker 完整教程](https://www.youtube.com/results?search_query=docker+tutorial)
- [Docker Compose 教程](https://www.youtube.com/results?search_query=docker+compose+tutorial)

## 下一步

完成本模块学习后，建议：
1. 为自己的项目编写 Dockerfile
2. 使用 docker-compose 部署完整应用
3. 学习 Kubernetes（容器编排）
4. 探索 Docker Swarm
5. 学习容器安全最佳实践

## 练习建议

1. 为第二阶段的 CRUD 项目创建 Dockerfile
2. 使用 docker-compose 部署应用和数据库
3. 优化镜像大小到 200MB 以下
4. 实现零停机部署
5. 配置日志收集和监控
