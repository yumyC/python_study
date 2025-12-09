# 完整测试示例项目

本目录包含一个完整的测试示例项目，展示如何为一个简单的博客应用编写全面的测试套件。

## 项目结构

```
examples/
├── README.md                    # 本文件
├── blog_app.py                  # 博客应用代码
├── test_blog_app.py             # 测试代码
├── conftest.py                  # 共享 fixtures
└── requirements.txt             # 依赖列表
```

## 应用功能

博客应用包含以下功能：
- 用户注册和登录
- 创建、编辑、删除文章
- 文章评论
- 文章搜索

## 测试覆盖

测试套件包含：
- 单元测试：测试独立的函数和类
- 集成测试：测试组件间的交互
- Fixture：管理测试数据和资源
- Mock：模拟外部依赖

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行并显示详细输出
```bash
pytest -v
```

### 生成覆盖率报告
```bash
pytest --cov=blog_app --cov-report=html
```

### 运行特定测试文件
```bash
pytest test_blog_app.py
```

### 运行特定测试类
```bash
pytest test_blog_app.py::TestUser -v
```

### 运行特定测试函数
```bash
pytest test_blog_app.py::test_user_registration -v
```

## 学习要点

1. **测试组织**: 如何组织测试代码，使其清晰易维护
2. **Fixture 使用**: 如何使用 fixture 管理测试数据
3. **Mock 技术**: 如何 Mock 外部依赖（如数据库、API）
4. **断言技巧**: 如何编写清晰有效的断言
5. **测试覆盖**: 如何确保测试覆盖核心功能

## 测试最佳实践示例

### 1. 测试命名
- 使用描述性的测试名称
- 清楚表达测试意图
- 例如：`test_user_cannot_login_with_wrong_password`

### 2. 测试独立性
- 每个测试独立运行
- 使用 fixture 的 setup 和 teardown
- 不依赖其他测试的结果

### 3. 测试数据
- 使用 fixture 提供测试数据
- 使用工厂模式创建测试对象
- 避免硬编码测试数据

### 4. 断言清晰
- 每个测试有明确的断言
- 使用描述性的断言消息
- 一个测试只测试一个概念

### 5. Mock 使用
- 只 Mock 外部依赖
- 验证 Mock 的调用
- 保持 Mock 简单

## 扩展练习

1. 为博客应用添加更多功能（如标签、分类）
2. 为新功能编写测试
3. 提高测试覆盖率到 90% 以上
4. 添加性能测试
5. 添加端到端测试

## 参考资源

- [pytest 官方文档](https://docs.pytest.org/)
- [Python 测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [测试驱动开发](https://en.wikipedia.org/wiki/Test-driven_development)
