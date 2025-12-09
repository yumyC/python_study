# CI/CD 模块

## 概述

本模块介绍持续集成和持续部署 (CI/CD) 的概念和实践，重点讲解如何使用 GitHub Actions 自动化测试、构建和部署流程。

## 学习目标

完成本模块学习后，你将能够：

- 理解 CI/CD 的概念和重要性
- 使用 GitHub Actions 创建自动化工作流
- 配置自动化测试流程
- 实现自动化构建和部署
- 管理环境变量和密钥
- 监控和调试 CI/CD 流程

## 前置知识

- Git 和 GitHub 基础
- Python 测试（第四阶段测试模块）
- Docker 基础（可选）

## 内容结构

### 1. GitHub Actions 工作流配置
- `basic_workflow.yml` - 基础工作流示例
- `test_workflow.yml` - 自动化测试工作流
- `build_workflow.yml` - 构建工作流
- `deploy_workflow.yml` - 部署工作流

### 2. 文档
- `video_tutorial.md` - 视频教程说明
- `best_practices.md` - CI/CD 最佳实践

## CI/CD 概念

### 什么是 CI/CD？

**持续集成 (Continuous Integration, CI)**
- 开发者频繁地将代码集成到主分支
- 每次集成都通过自动化构建和测试验证
- 快速发现和修复集成问题

**持续部署 (Continuous Deployment, CD)**
- 自动将通过测试的代码部署到生产环境
- 减少手动部署的错误和时间
- 实现快速迭代和交付

### CI/CD 的好处

1. **提高代码质量**
   - 自动化测试确保代码质量
   - 及早发现 bug
   - 强制代码审查

2. **加快开发速度**
   - 自动化重复任务
   - 减少手动操作
   - 快速反馈

3. **降低风险**
   - 小步快跑，降低每次发布的风险
   - 快速回滚
   - 环境一致性

4. **提高团队协作**
   - 统一的工作流程
   - 透明的构建和部署状态
   - 减少沟通成本

## GitHub Actions 基础

### 核心概念

**Workflow（工作流）**
- 自动化流程的定义
- 由一个或多个 job 组成
- 存储在 `.github/workflows/` 目录

**Job（任务）**
- 工作流中的一组步骤
- 在同一个运行器上执行
- 可以并行或串行执行

**Step（步骤）**
- Job 中的单个任务
- 可以运行命令或使用 Action

**Action（动作）**
- 可重用的任务单元
- 可以是官方的、社区的或自定义的

**Runner（运行器）**
- 执行工作流的服务器
- GitHub 提供托管的运行器
- 也可以使用自托管运行器

### 触发器

工作流可以由以下事件触发：

- `push` - 代码推送
- `pull_request` - Pull Request 创建或更新
- `schedule` - 定时触发
- `workflow_dispatch` - 手动触发
- `release` - 发布创建

## 工作流示例

### 基础工作流结构

```yaml
name: 工作流名称

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  job-name:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v3
    
    - name: 设置 Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: 安装依赖
      run: |
        pip install -r requirements.txt
    
    - name: 运行测试
      run: |
        pytest
```

## 使用方法

### 1. 创建工作流文件

在项目根目录创建 `.github/workflows/` 目录：

```bash
mkdir -p .github/workflows
```

### 2. 添加工作流配置

将本模块中的 YAML 文件复制到 `.github/workflows/` 目录：

```bash
cp github_actions/test_workflow.yml .github/workflows/
```

### 3. 提交并推送

```bash
git add .github/workflows/
git commit -m "Add CI workflow"
git push
```

### 4. 查看工作流运行

在 GitHub 仓库页面，点击 "Actions" 标签查看工作流运行状态。

## 环境变量和密钥

### 使用环境变量

```yaml
env:
  DATABASE_URL: postgresql://localhost/testdb
  DEBUG: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: 运行测试
      run: pytest
      env:
        API_KEY: ${{ secrets.API_KEY }}
```

### 配置 GitHub Secrets

1. 进入仓库的 Settings
2. 选择 Secrets and variables > Actions
3. 点击 "New repository secret"
4. 添加密钥名称和值

### 使用 Secrets

```yaml
- name: 部署
  run: |
    echo "Deploying..."
  env:
    DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
```

## 常见工作流模式

### 1. 测试矩阵

在多个 Python 版本上测试：

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Run tests
      run: pytest
```

### 2. 缓存依赖

加速工作流执行：

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### 3. 条件执行

根据条件执行步骤：

```yaml
- name: Deploy to production
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: |
    echo "Deploying to production..."
```

### 4. Job 依赖

串行执行 jobs：

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - name: Run tests
      run: pytest
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy
      run: echo "Deploying..."
```

## 调试技巧

### 1. 启用调试日志

在仓库 Secrets 中添加：
- `ACTIONS_STEP_DEBUG`: true
- `ACTIONS_RUNNER_DEBUG`: true

### 2. 使用 tmate 进行交互式调试

```yaml
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
```

### 3. 查看工作流日志

在 GitHub Actions 页面查看详细的执行日志。

## 最佳实践

### 1. 工作流设计
- 保持工作流简单和专注
- 使用有意义的名称
- 添加注释说明复杂的步骤

### 2. 性能优化
- 使用缓存加速构建
- 并行执行独立的 jobs
- 只在必要时运行工作流

### 3. 安全性
- 使用 Secrets 管理敏感信息
- 限制工作流权限
- 审查第三方 Actions

### 4. 可维护性
- 使用可重用的工作流
- 版本化 Actions
- 定期更新依赖

## 常见问题

### Q: 工作流运行失败怎么办？
A: 查看详细日志，检查错误信息。常见原因包括依赖安装失败、测试失败、权限问题等。

### Q: 如何加速工作流执行？
A: 使用缓存、并行执行、减少不必要的步骤、使用更快的运行器。

### Q: 如何在本地测试工作流？
A: 可以使用 [act](https://github.com/nektos/act) 工具在本地运行 GitHub Actions。

### Q: 工作流的执行时间有限制吗？
A: 是的，GitHub 免费账户每个 job 最多运行 6 小时，每个工作流最多运行 72 小时。

### Q: 如何通知团队工作流状态？
A: 可以使用 Slack、Email 等通知 Actions，或者配置 GitHub 通知。

## 学习资源

### 官方文档
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [工作流语法](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Actions 市场](https://github.com/marketplace?type=actions)

### 推荐阅读
- 《持续交付》
- 《DevOps 实践指南》

### 视频教程
- [GitHub Actions 完整教程](https://www.youtube.com/results?search_query=github+actions+tutorial)
- [CI/CD 最佳实践](https://www.youtube.com/results?search_query=cicd+best+practices)

## 下一步

完成本模块学习后，建议：
1. 为自己的项目添加 CI/CD 工作流
2. 学习 Docker 模块，了解容器化部署
3. 探索更高级的 CI/CD 工具（Jenkins, GitLab CI, CircleCI）
4. 学习基础设施即代码（Terraform, Ansible）

## 练习建议

1. 为第二阶段的 CRUD 项目添加 CI 工作流
2. 配置自动化测试和代码覆盖率报告
3. 实现自动部署到测试环境
4. 添加代码质量检查（linting, formatting）
5. 配置多环境部署（开发、测试、生产）
