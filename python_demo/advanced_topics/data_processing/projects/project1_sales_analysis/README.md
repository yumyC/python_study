# 销售数据分析项目

## 项目概述

本项目是一个完整的销售数据分析案例，展示了从数据收集、清洗、分析到可视化的完整数据分析流程。通过分析虚拟电商公司的销售数据，我们将发现业务洞察并提供决策建议。

## 项目目标

1. **数据理解**: 深入了解销售数据的结构和特征
2. **业务洞察**: 发现销售趋势、客户行为和产品表现
3. **预测分析**: 建立简单的销售预测模型
4. **可视化报告**: 创建直观的数据可视化和报告
5. **决策支持**: 为业务决策提供数据驱动的建议

## 数据集描述

### 数据来源
- 虚拟电商公司 2022-2024 年销售数据
- 包含订单、客户、产品和地区信息

### 数据字段
- `order_id`: 订单唯一标识
- `customer_id`: 客户唯一标识
- `product_id`: 产品唯一标识
- `product_name`: 产品名称
- `category`: 产品类别
- `quantity`: 购买数量
- `unit_price`: 单价
- `total_amount`: 总金额
- `order_date`: 订单日期
- `customer_age`: 客户年龄
- `customer_gender`: 客户性别
- `customer_city`: 客户城市
- `sales_channel`: 销售渠道（线上/线下）
- `discount_rate`: 折扣率
- `profit_margin`: 利润率

## 分析框架

### 1. 数据准备阶段
- 数据加载和初步检查
- 数据清洗和预处理
- 数据质量评估

### 2. 探索性数据分析 (EDA)
- 销售趋势分析
- 客户行为分析
- 产品表现分析
- 地区分析
- 渠道分析

### 3. 深度分析
- 客户细分分析
- 产品关联分析
- 季节性分析
- 价格敏感性分析

### 4. 预测建模
- 销售预测模型
- 客户价值预测
- 产品需求预测

### 5. 可视化和报告
- 交互式仪表板
- 业务报告
- 决策建议

## 技术栈

### 核心库
- **pandas**: 数据处理和分析
- **numpy**: 数值计算
- **matplotlib**: 基础可视化
- **seaborn**: 统计可视化
- **plotly**: 交互式可视化

### 分析工具
- **scipy**: 统计分析
- **scikit-learn**: 机器学习
- **statsmodels**: 统计建模

### 可选工具
- **jupyter**: 交互式开发
- **streamlit**: Web 应用
- **dash**: 仪表板

## 项目结构

```
project1_sales_analysis/
├── README.md                    # 项目说明
├── requirements.txt             # 依赖包
├── data/                        # 数据文件
│   ├── raw/                     # 原始数据
│   ├── processed/               # 处理后数据
│   └── external/                # 外部数据
├── notebooks/                   # Jupyter 笔记本
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_sales_analysis.ipynb
│   ├── 04_customer_analysis.ipynb
│   └── 05_predictive_modeling.ipynb
├── src/                         # 源代码
│   ├── data_generator.py        # 数据生成器
│   ├── data_processor.py        # 数据处理
│   ├── analyzer.py              # 分析器
│   ├── visualizer.py            # 可视化
│   └── utils.py                 # 工具函数
├── reports/                     # 报告和图表
│   ├── figures/                 # 图表文件
│   ├── sales_report.html        # HTML 报告
│   └── executive_summary.md     # 执行摘要
└── tests/                       # 测试文件
    └── test_analysis.py
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv sales_analysis_env
source sales_analysis_env/bin/activate  # Linux/Mac
# sales_analysis_env\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据生成

```python
# 运行数据生成器
python src/data_generator.py
```

### 3. 运行分析

```python
# 执行完整分析流程
python src/main_analysis.py
```

### 4. 查看结果

- 打开 `reports/sales_report.html` 查看详细报告
- 查看 `reports/figures/` 目录中的图表
- 阅读 `reports/executive_summary.md` 了解关键发现

## 关键分析问题

### 业务问题
1. 哪些产品和类别销售最好？
2. 客户购买行为有什么特点？
3. 销售趋势如何变化？
4. 不同地区的表现如何？
5. 线上线下渠道的差异是什么？

### 分析问题
1. 如何识别高价值客户？
2. 什么因素影响客户购买决策？
3. 如何优化产品组合？
4. 如何提高客户留存率？
5. 如何预测未来销售？

## 预期成果

### 数据洞察
- 销售趋势和季节性模式
- 客户细分和行为特征
- 产品表现和关联关系
- 地区和渠道差异分析

### 业务建议
- 产品策略优化建议
- 客户营销策略
- 库存管理建议
- 渠道优化策略

### 技术产出
- 可重用的分析代码
- 自动化报告生成
- 预测模型和评估
- 可视化模板

## 学习目标

通过完成这个项目，你将学会：

1. **数据分析流程**: 掌握完整的数据分析项目流程
2. **业务理解**: 学会从业务角度思考数据问题
3. **技术技能**: 提高 Python 数据分析技能
4. **可视化**: 创建有效的数据可视化
5. **报告撰写**: 编写清晰的分析报告
6. **项目管理**: 组织和管理数据分析项目

## 扩展方向

### 高级分析
- 客户生命周期价值分析
- 推荐系统开发
- 价格优化模型
- 库存优化算法

### 技术提升
- 实时数据处理
- 大数据技术应用
- 机器学习模型优化
- 自动化报告系统

### 业务应用
- A/B 测试设计
- 营销效果评估
- 风险分析模型
- 竞争分析框架

## 注意事项

1. **数据隐私**: 本项目使用虚拟数据，实际项目中需注意数据隐私保护
2. **业务背景**: 分析时要结合具体的业务背景和目标
3. **结果验证**: 分析结果需要与业务专家验证
4. **持续改进**: 根据反馈不断优化分析方法和结果

## 贡献指南

欢迎贡献代码、建议和改进：

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 许可证

本项目仅用于学习目的，请遵循相关开源协议。

---

开始你的销售数据分析之旅吧！记住，好的数据分析不仅仅是技术，更重要的是洞察和价值创造。