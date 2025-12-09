# Python 测试模块

## 概述

本模块介绍 Python 中的自动化测试，包括单元测试、集成测试、测试夹具和 Mock 技术。通过学习本模块，你将掌握使用 pytest 框架编写高质量测试代码的能力。

## 学习目标

完成本模块学习后，你将能够：

- 使用 pytest 编写和运行单元测试
- 理解测试驱动开发 (TDD) 的基本原则
- 使用测试夹具 (fixtures) 管理测试数据和资源
- 使用 Mock 技术隔离外部依赖
- 编写集成测试验证模块间的交互
- 计算和分析代码覆盖率
- 组织和管理测试代码

## 前置知识

- Python 基础语法（第一阶段）
- 函数和类的使用
- 基本的面向对象编程概念

## 内容结构

### 1. 单元测试 (01_unit_testing.py)
- pytest 基础使用
- 测试函数的编写规范
- 断言方法
- 测试类的组织
- 参数化测试
- 测试标记和分组

### 2. 集成测试 (02_integration_testing.py)
- 集成测试的概念和目的
- API 端点测试
- 数据库集成测试
- 测试客户端的使用
- 测试数据库的配置

### 3. 测试夹具 (03_test_fixtures.py)
- Fixture 的概念和作用
- Fixture 的作用域
- Fixture 的依赖和组合
- 内置 fixture 的使用
- 自定义 fixture

### 4. Mock 技术 (04_mocking.py)
- Mock 的概念和使用场景
- unittest.mock 模块
- Mock 对象的创建和配置
- 模拟函数调用和返回值
- 验证 Mock 调用
- Patch 装饰器的使用

## 安装依赖

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定文件的测试
```bash
pytest 01_unit_testing.py
```

### 运行特定测试函数
```bash
pytest 01_unit_testing.py::test_function_name
```

### 显示详细输出
```bash
pytest -v
```

### 显示打印输出
```bash
pytest -s
```

### 生成覆盖率报告
```bash
pytest --cov=. --cov-report=html
```

## 测试最佳实践

### 1. 测试命名规范
- 测试文件以 `test_` 开头或 `_test.py` 结尾
- 测试函数以 `test_` 开头
- 测试类以 `Test` 开头
- 使用描述性的测试名称，清楚表达测试意图

### 2. 测试组织
- 每个模块对应一个测试文件
- 相关的测试放在同一个测试类中
- 使用 fixture 共享测试数据和设置

### 3. 测试独立性
- 每个测试应该独立运行
- 测试之间不应该有依赖关系
- 使用 fixture 的 setup 和 teardown 清理状态

### 4. 断言清晰
- 每个测试应该有明确的断言
- 使用描述性的断言消息
- 避免在一个测试中有太多断言

### 5. 测试覆盖率
- 目标覆盖率：80% 以上
- 重点测试核心业务逻辑
- 不要为了覆盖率而写无意义的测试

### 6. Mock 使用原则
- 只 Mock 外部依赖（数据库、API、文件系统等）
- 不要 Mock 被测试的代码
- 验证 Mock 的调用参数和次数

## 测试金字塔

```
       /\
      /  \     E2E 测试（少量）
     /____\    
    /      \   集成测试（适量）
   /________\  
  /          \ 单元测试（大量）
 /____________\
```

- **单元测试**: 测试单个函数或类，快速、独立
- **集成测试**: 测试模块间的交互，验证集成点
- **端到端测试**: 测试完整的用户流程，慢但全面

## 常见问题

### Q: 什么时候应该写测试？
A: 理想情况下，在编写代码之前或同时编写测试（TDD）。至少在功能完成后立即编写测试。

### Q: 如何测试异步代码？
A: 使用 `pytest-asyncio` 插件，在测试函数前添加 `@pytest.mark.asyncio` 装饰器。

### Q: 如何处理测试数据库？
A: 使用独立的测试数据库，在测试前创建，测试后清理。可以使用 fixture 管理数据库连接。

### Q: 测试覆盖率多少合适？
A: 80% 以上是一个好的目标，但不要盲目追求 100%。重点是测试核心业务逻辑。

### Q: 如何加速测试运行？
A: 使用 `pytest-xdist` 插件并行运行测试：`pytest -n auto`

## 学习资源

### 官方文档
- [pytest 官方文档](https://docs.pytest.org/)
- [unittest.mock 文档](https://docs.python.org/3/library/unittest.mock.html)

### 推荐阅读
- 《测试驱动开发：实战与模式解析》
- 《Python 测试驱动开发》

### 视频教程
- [pytest 完整教程](https://www.youtube.com/results?search_query=pytest+tutorial)
- [Python 单元测试最佳实践](https://www.youtube.com/results?search_query=python+unit+testing+best+practices)

## 下一步

完成本模块学习后，建议：
1. 为之前的项目添加测试
2. 学习 CI/CD 模块，了解如何在持续集成中运行测试
3. 实践测试驱动开发 (TDD) 方法
4. 探索更高级的测试技术（性能测试、安全测试等）

## 练习建议

1. 为第一阶段的计算器项目编写完整的测试套件
2. 为第二阶段的 CRUD 项目编写 API 集成测试
3. 使用 TDD 方法开发一个新的小功能
4. 分析现有项目的测试覆盖率，补充缺失的测试
