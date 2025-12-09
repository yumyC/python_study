# CI/CD 最佳实践

本文档总结了 CI/CD 实践中的最佳实践和常见模式，帮助你构建高效、可靠的自动化流程。

## 目录

1. [工作流设计原则](#工作流设计原则)
2. [测试策略](#测试策略)
3. [构建优化](#构建优化)
4. [部署策略](#部署策略)
5. [安全实践](#安全实践)
6. [监控和日志](#监控和日志)
7. [团队协作](#团队协作)

## 工作流设计原则

### 1. 保持简单

**原则**: 工作流应该简单、清晰、易于理解

**实践**:
- 每个工作流专注于一个目标（测试、构建、部署）
- 避免过度复杂的逻辑
- 使用有意义的名称
- 添加注释说明复杂的步骤

**示例**:
```yaml
# ❌ 不好的做法：一个工作流做所有事情
name: Everything
on: [push]
jobs:
  do-everything:
    steps:
    - run: test
    - run: build
    - run: deploy
    - run: notify
    # ... 太多步骤

# ✅ 好的做法：分离关注点
name: Test
on: [push]
jobs:
  test:
    steps:
    - run: pytest
```

### 2. 快速反馈

**原则**: 尽快给开发者反馈

**实践**:
- 最重要的检查放在前面
- 并行执行独立的任务
- 使用缓存加速构建
- 失败时快速失败

**示例**:
```yaml
jobs:
  # 快速检查（2-3分钟）
  quick-checks:
    steps:
    - name: Lint
      run: flake8 .
    - name: Type check
      run: mypy .
  
  # 完整测试（10-15分钟）
  full-tests:
    needs: quick-checks
    steps:
    - name: Run all tests
      run: pytest
```

### 3. 可重复性

**原则**: 工作流应该产生一致的结果

**实践**:
- 固定依赖版本
- 使用相同的环境
- 避免依赖外部状态
- 使用确定性的构建过程

**示例**:
```yaml
# ✅ 固定版本
- uses: actions/setup-python@v4
  with:
    python-version: '3.9.16'  # 具体版本

# ❌ 避免使用 latest
- uses: actions/setup-python@latest  # 不确定的版本
```

### 4. 可维护性

**原则**: 工作流应该易于维护和更新

**实践**:
- 使用可重用的工作流
- 提取公共步骤
- 版本化 Actions
- 定期更新依赖

**示例**:
```yaml
# 可重用的工作流
# .github/workflows/reusable-test.yml
name: Reusable Test
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ inputs.python-version }}
    - run: pytest
```

## 测试策略

### 1. 测试金字塔

**原则**: 大量单元测试，适量集成测试，少量端到端测试

**实践**:
```yaml
jobs:
  unit-tests:
    # 快速、大量
    runs-on: ubuntu-latest
    steps:
    - run: pytest tests/unit/ -v
  
  integration-tests:
    # 中等速度、适量
    needs: unit-tests
    runs-on: ubuntu-latest
    steps:
    - run: pytest tests/integration/ -v
  
  e2e-tests:
    # 慢速、少量、关键路径
    needs: integration-tests
    runs-on: ubuntu-latest
    steps:
    - run: pytest tests/e2e/ -v
```

### 2. 测试矩阵

**原则**: 在多个环境中测试

**实践**:
```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11']
    os: [ubuntu-latest, windows-latest, macos-latest]
  # 允许某些组合失败
  fail-fast: false
  # 标记实验性组合
  include:
    - python-version: '3.12-dev'
      experimental: true
```

### 3. 测试覆盖率

**原则**: 监控测试覆盖率，但不盲目追求 100%

**实践**:
```yaml
- name: Run tests with coverage
  run: pytest --cov=. --cov-report=xml --cov-report=term

- name: Check coverage threshold
  run: |
    coverage report --fail-under=80

- name: Upload to Codecov
  uses: codecov/codecov-action@v3
  with:
    fail_ci_if_error: false  # 不因上传失败而失败
```

### 4. 测试隔离

**原则**: 测试应该独立，不依赖执行顺序

**实践**:
- 使用测试数据库
- 清理测试数据
- 使用 fixtures
- 避免共享状态

## 构建优化

### 1. 使用缓存

**原则**: 缓存不变的依赖

**实践**:
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-
```

### 2. 并行执行

**原则**: 并行执行独立的任务

**实践**:
```yaml
jobs:
  # 这些任务可以并行执行
  lint:
    runs-on: ubuntu-latest
    steps:
    - run: flake8 .
  
  type-check:
    runs-on: ubuntu-latest
    steps:
    - run: mypy .
  
  test:
    runs-on: ubuntu-latest
    steps:
    - run: pytest
  
  # 这个任务等待上面的任务完成
  build:
    needs: [lint, type-check, test]
    runs-on: ubuntu-latest
    steps:
    - run: docker build .
```

### 3. 条件执行

**原则**: 只在必要时运行步骤

**实践**:
```yaml
# 只在主分支运行部署
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: ./deploy.sh

# 只在标签时发布
- name: Publish
  if: startsWith(github.ref, 'refs/tags/v')
  run: ./publish.sh

# 只在文件变化时运行
- name: Build docs
  if: contains(github.event.head_commit.modified, 'docs/')
  run: make docs
```

### 4. 增量构建

**原则**: 只构建变化的部分

**实践**:
```yaml
- name: Get changed files
  id: changed-files
  uses: tj-actions/changed-files@v35

- name: Run tests for changed files
  if: steps.changed-files.outputs.any_changed == 'true'
  run: |
    pytest ${{ steps.changed-files.outputs.all_changed_files }}
```

## 部署策略

### 1. 环境分离

**原则**: 使用不同的环境进行开发、测试和生产

**实践**:
```yaml
jobs:
  deploy-dev:
    environment: development
    if: github.ref == 'refs/heads/develop'
    steps:
    - run: deploy to dev
  
  deploy-staging:
    environment: staging
    if: github.ref == 'refs/heads/main'
    steps:
    - run: deploy to staging
  
  deploy-prod:
    environment: production
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
    - run: deploy to production
```

### 2. 蓝绿部署

**原则**: 保持两个相同的生产环境，切换流量

**实践**:
```yaml
- name: Deploy to blue environment
  run: |
    deploy_to_environment blue
    wait_for_health_check blue

- name: Switch traffic to blue
  run: |
    switch_traffic blue

- name: Keep green as backup
  run: |
    keep_environment green
```

### 3. 金丝雀部署

**原则**: 逐步将流量切换到新版本

**实践**:
```yaml
- name: Deploy canary (10% traffic)
  run: deploy_canary 10

- name: Monitor metrics
  run: check_error_rate

- name: Increase to 50%
  if: success()
  run: deploy_canary 50

- name: Full rollout
  if: success()
  run: deploy_canary 100
```

### 4. 回滚机制

**原则**: 能够快速回滚到上一个稳定版本

**实践**:
```yaml
- name: Backup current version
  run: |
    backup_current_version

- name: Deploy new version
  id: deploy
  run: |
    deploy_new_version

- name: Rollback on failure
  if: failure()
  run: |
    rollback_to_backup
```

## 安全实践

### 1. 密钥管理

**原则**: 永远不要在代码中硬编码密钥

**实践**:
```yaml
# ✅ 使用 Secrets
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  run: ./deploy.sh

# ❌ 不要硬编码
- name: Deploy
  env:
    API_KEY: "abc123"  # 不要这样做！
  run: ./deploy.sh
```

### 2. 权限最小化

**原则**: 只授予必要的权限

**实践**:
```yaml
permissions:
  contents: read  # 只读代码
  packages: write  # 写入包
  # 不授予其他权限

jobs:
  build:
    permissions:
      contents: read
      packages: write
```

### 3. 依赖扫描

**原则**: 定期扫描依赖的安全漏洞

**实践**:
```yaml
- name: Scan dependencies
  run: |
    pip install safety
    safety check

- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myimage:latest
    format: 'sarif'
    output: 'trivy-results.sarif'
```

### 4. 代码签名

**原则**: 对发布的代码进行签名

**实践**:
```yaml
- name: Sign artifacts
  run: |
    gpg --sign artifact.tar.gz

- name: Verify signature
  run: |
    gpg --verify artifact.tar.gz.sig
```

## 监控和日志

### 1. 结构化日志

**原则**: 使用结构化的日志格式

**实践**:
```yaml
- name: Run with structured logging
  run: |
    python app.py --log-format=json
```

### 2. 通知机制

**原则**: 及时通知团队重要事件

**实践**:
```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Build failed!'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}

- name: Notify on success
  if: success()
  run: |
    send_email "Deployment successful"
```

### 3. 指标收集

**原则**: 收集关键指标

**实践**:
```yaml
- name: Collect metrics
  run: |
    echo "build_duration_seconds ${{ job.duration }}" >> metrics.txt
    echo "test_count ${{ steps.test.outputs.count }}" >> metrics.txt

- name: Send to monitoring
  run: |
    curl -X POST monitoring.example.com/metrics -d @metrics.txt
```

### 4. 审计日志

**原则**: 记录所有重要操作

**实践**:
```yaml
- name: Log deployment
  run: |
    echo "$(date) - Deployed version ${{ github.sha }} by ${{ github.actor }}" >> audit.log
```

## 团队协作

### 1. 代码审查

**原则**: 所有代码变更都应该经过审查

**实践**:
```yaml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review-checks:
    steps:
    - name: Run automated checks
      run: |
        pytest
        flake8
        mypy
```

### 2. 分支策略

**原则**: 使用清晰的分支策略

**实践**:
- `main`: 生产代码
- `develop`: 开发代码
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复

```yaml
on:
  push:
    branches:
      - main
      - develop
      - 'feature/**'
      - 'hotfix/**'
```

### 3. 文档

**原则**: 文档化工作流和流程

**实践**:
- 在 README 中说明 CI/CD 流程
- 注释复杂的工作流步骤
- 维护故障排查指南
- 记录部署流程

### 4. 持续改进

**原则**: 定期回顾和优化流程

**实践**:
- 监控工作流执行时间
- 收集团队反馈
- 定期更新依赖
- 学习新的最佳实践

## 常见反模式

### ❌ 不要做的事情

1. **在工作流中硬编码密钥**
   ```yaml
   # ❌ 不要这样做
   env:
     API_KEY: "secret123"
   ```

2. **忽略测试失败**
   ```yaml
   # ❌ 不要这样做
   - run: pytest
     continue-on-error: true
   ```

3. **过度复杂的工作流**
   ```yaml
   # ❌ 避免过度复杂
   - run: |
       if [ condition1 ]; then
         if [ condition2 ]; then
           if [ condition3 ]; then
             # 太多嵌套
           fi
         fi
       fi
   ```

4. **不使用缓存**
   ```yaml
   # ❌ 每次都重新安装
   - run: pip install -r requirements.txt
   ```

5. **串行执行可并行的任务**
   ```yaml
   # ❌ 不必要的串行
   jobs:
     lint:
       steps: [...]
     test:
       needs: lint  # 不必要的依赖
   ```

## 检查清单

使用这个清单检查你的 CI/CD 流程：

### 基础
- [ ] 所有代码变更都触发 CI
- [ ] 测试在合并前运行
- [ ] 构建失败时阻止合并
- [ ] 使用版本控制管理配置

### 测试
- [ ] 有单元测试
- [ ] 有集成测试
- [ ] 测试覆盖率 > 80%
- [ ] 测试在多个环境运行

### 构建
- [ ] 使用缓存加速构建
- [ ] 并行执行独立任务
- [ ] 构建产物可追溯
- [ ] 构建时间 < 15分钟

### 部署
- [ ] 有多个环境（dev, staging, prod）
- [ ] 生产部署需要审批
- [ ] 有回滚机制
- [ ] 部署后运行健康检查

### 安全
- [ ] 使用 Secrets 管理密钥
- [ ] 定期扫描依赖漏洞
- [ ] 最小权限原则
- [ ] 审计日志

### 监控
- [ ] 构建失败时通知
- [ ] 部署成功时通知
- [ ] 收集关键指标
- [ ] 有故障排查文档

## 总结

好的 CI/CD 实践应该：
- **快速**: 快速反馈，快速部署
- **可靠**: 一致的结果，可重复的过程
- **安全**: 保护密钥，扫描漏洞
- **可维护**: 清晰的结构，良好的文档
- **可扩展**: 易于添加新的检查和流程

记住：CI/CD 是一个持续改进的过程，不断学习和优化！
