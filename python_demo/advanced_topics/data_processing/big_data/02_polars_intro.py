#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polars 高性能数据处理教程

Polars 是一个用 Rust 编写的高性能数据处理库，提供了类似 Pandas 的 API。
本教程介绍 Polars 的基本概念和使用方法。

注意：本教程需要安装 Polars: pip install polars

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import time

# 尝试导入 Polars
try:
    import polars as pl
    POLARS_AVAILABLE = True
    print(f"Polars 版本: {pl.__version__}")
except ImportError:
    POLARS_AVAILABLE = False
    print("Polars 未安装，请运行: pip install polars")

print("=" * 60)
print("Polars 高性能数据处理教程")
print("=" * 60)

if not POLARS_AVAILABLE:
    print("\n请先安装 Polars 库:")
    print("pip install polars")
    print("\n本教程将展示 Polars 的概念和代码示例")

# 1. Polars 基本概念
print("\n1. Polars 基本概念")
print("-" * 30)

print("Polars 的特点:")
print("- 用 Rust 编写，性能极高")
print("- 内存效率优秀")
print("- 支持延迟计算")
print("- 类似 Pandas 的 API")
print("- 内置并行处理")
print("- 支持 Arrow 格式")

if POLARS_AVAILABLE:
    # 2. 创建 DataFrame
    print("\n\n2. 创建 DataFrame")
    print("-" * 30)
    
    # 从字典创建
    data = {
        'name': ['张三', '李四', '王五', '赵六', '钱七'],
        'age': [25, 30, 35, 28, 32],
        'city': ['北京', '上海', '广州', '深圳', '杭州'],
        'salary': [8000, 12000, 15000, 10000, 11000]
    }
    
    df_pl = pl.DataFrame(data)
    print("Polars DataFrame:")
    print(df_pl)
    
    # 查看数据信息
    print(f"\n形状: {df_pl.shape}")
    print(f"列名: {df_pl.columns}")
    print(f"数据类型: {df_pl.dtypes}")
    
    # 3. 基本操作
    print("\n\n3. 基本操作")
    print("-" * 30)
    
    # 选择列
    print("选择列:")
    print(df_pl.select(['name', 'salary']))
    
    # 筛选行
    print("\n筛选行（薪资 > 10000）:")
    print(df_pl.filter(pl.col('salary') > 10000))
    
    # 排序
    print("\n按薪资排序:")
    print(df_pl.sort('salary', descending=True))
    
    # 4. 表达式系统
    print("\n\n4. 表达式系统")
    print("-" * 30)
    
    # Polars 的强大表达式系统
    result = df_pl.select([
        pl.col('name'),
        pl.col('salary'),
        (pl.col('salary') * 0.1).alias('bonus'),
        pl.col('age').mean().alias('avg_age')
    ])
    print("表达式计算:")
    print(result)
    
    # 条件表达式
    result_cond = df_pl.with_columns([
        pl.when(pl.col('salary') > 10000)
        .then(pl.lit('高薪'))
        .otherwise(pl.lit('普通'))
        .alias('salary_level')
    ])
    print("\n条件表达式:")
    print(result_cond)
    
    # 5. 聚合操作
    print("\n\n5. 聚合操作")
    print("-" * 30)
    
    # 基本聚合
    agg_result = df_pl.select([
        pl.col('salary').sum().alias('total_salary'),
        pl.col('salary').mean().alias('avg_salary'),
        pl.col('age').max().alias('max_age'),
        pl.col('name').count().alias('count')
    ])
    print("聚合统计:")
    print(agg_result)
    
    # 分组聚合
    # 首先添加一个分组列
    df_with_dept = df_pl.with_columns([
        pl.when(pl.col('salary') > 10000)
        .then(pl.lit('高级'))
        .otherwise(pl.lit('初级'))
        .alias('level')
    ])
    
    group_result = df_with_dept.group_by('level').agg([
        pl.col('salary').mean().alias('avg_salary'),
        pl.col('age').mean().alias('avg_age'),
        pl.col('name').count().alias('count')
    ])
    print("\n分组聚合:")
    print(group_result)
    
    # 6. 性能比较
    print("\n\n6. 性能比较")
    print("-" * 30)
    
    # 创建大数据集进行性能测试
    np.random.seed(42)
    n_rows = 1000000
    
    print(f"创建 {n_rows:,} 行数据进行性能测试...")
    
    # Pandas 数据
    pandas_data = {
        'id': range(n_rows),
        'value1': np.random.randn(n_rows),
        'value2': np.random.randn(n_rows),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n_rows)
    }
    df_pandas = pd.DataFrame(pandas_data)
    
    # Polars 数据
    df_polars = pl.DataFrame(pandas_data)
    
    # 测试操作：分组聚合
    print("\n测试操作：按类别分组计算平均值")
    
    # Pandas 性能
    start_time = time.time()
    pandas_result = df_pandas.groupby('category')['value1'].mean()
    pandas_time = time.time() - start_time
    print(f"Pandas 时间: {pandas_time:.4f} 秒")
    
    # Polars 性能
    start_time = time.time()
    polars_result = df_polars.group_by('category').agg(pl.col('value1').mean())
    polars_time = time.time() - start_time
    print(f"Polars 时间: {polars_time:.4f} 秒")
    
    if pandas_time > 0:
        speedup = pandas_time / polars_time
        print(f"Polars 比 Pandas 快 {speedup:.1f} 倍")
    
    # 7. 延迟计算
    print("\n\n7. 延迟计算")
    print("-" * 30)
    
    # Polars 支持延迟计算（LazyFrame）
    lazy_df = df_polars.lazy()
    
    # 构建计算链
    lazy_result = (
        lazy_df
        .filter(pl.col('value1') > 0)
        .group_by('category')
        .agg([
            pl.col('value1').mean().alias('avg_value1'),
            pl.col('value2').sum().alias('sum_value2')
        ])
        .sort('avg_value1', descending=True)
    )
    
    print("延迟计算查询计划:")
    print(lazy_result.explain())
    
    # 执行计算
    print("\n执行延迟计算:")
    eager_result = lazy_result.collect()
    print(eager_result)
    
    # 8. 数据类型优化
    print("\n\n8. 数据类型优化")
    print("-" * 30)
    
    # 查看内存使用
    print("原始数据类型:")
    print(df_polars.dtypes)
    
    # 优化数据类型
    optimized_df = df_polars.with_columns([
        pl.col('id').cast(pl.UInt32),
        pl.col('value1').cast(pl.Float32),
        pl.col('value2').cast(pl.Float32),
        pl.col('category').cast(pl.Categorical)
    ])
    
    print("\n优化后数据类型:")
    print(optimized_df.dtypes)
    
    # 9. 字符串操作
    print("\n\n9. 字符串操作")
    print("-" * 30)
    
    # 创建包含字符串的数据
    text_data = pl.DataFrame({
        'name': ['张三', '李四', '王五六', '赵七'],
        'email': ['zhang@company.com', 'li@company.com', 'wang@company.com', 'zhao@company.com'],
        'phone': ['138-1234-5678', '139-2345-6789', '137-3456-7890', '136-4567-8901']
    })
    
    # 字符串操作
    string_ops = text_data.with_columns([
        pl.col('name').str.len_chars().alias('name_length'),
        pl.col('email').str.split('@').list.get(0).alias('username'),
        pl.col('phone').str.replace('-', '').alias('phone_clean')
    ])
    
    print("字符串操作结果:")
    print(string_ops)
    
    # 10. 时间序列操作
    print("\n\n10. 时间序列操作")
    print("-" * 30)
    
    # 创建时间序列数据
    dates = pl.date_range(
        start=pl.date(2024, 1, 1),
        end=pl.date(2024, 12, 31),
        interval='1d'
    )
    
    ts_data = pl.DataFrame({
        'date': dates,
        'value': np.random.randn(len(dates)).cumsum()
    })
    
    # 时间序列操作
    ts_ops = ts_data.with_columns([
        pl.col('date').dt.year().alias('year'),
        pl.col('date').dt.month().alias('month'),
        pl.col('date').dt.weekday().alias('weekday'),
        pl.col('value').rolling_mean(window_size=7).alias('rolling_mean_7d')
    ])
    
    print("时间序列操作（前10行）:")
    print(ts_ops.head(10))
    
    # 按月聚合
    monthly_agg = ts_ops.group_by('month').agg([
        pl.col('value').mean().alias('avg_value'),
        pl.col('value').std().alias('std_value')
    ]).sort('month')
    
    print("\n按月聚合:")
    print(monthly_agg)
    
    # 11. 数据连接
    print("\n\n11. 数据连接")
    print("-" * 30)
    
    # 创建两个表进行连接
    employees = pl.DataFrame({
        'emp_id': [1, 2, 3, 4],
        'name': ['张三', '李四', '王五', '赵六'],
        'dept_id': [101, 102, 101, 103]
    })
    
    departments = pl.DataFrame({
        'dept_id': [101, 102, 103],
        'dept_name': ['IT部', '人事部', '财务部'],
        'manager': ['张经理', '李经理', '王经理']
    })
    
    # 内连接
    joined = employees.join(departments, on='dept_id', how='inner')
    print("内连接结果:")
    print(joined)
    
    # 12. 窗口函数
    print("\n\n12. 窗口函数")
    print("-" * 30)
    
    # 创建销售数据
    sales_data = pl.DataFrame({
        'salesperson': ['张三', '李四', '王五', '张三', '李四', '王五'] * 3,
        'month': [1, 1, 1, 2, 2, 2] * 3,
        'sales': [1000, 1200, 800, 1100, 1300, 900, 1050, 1250, 850]
    })
    
    # 窗口函数操作
    window_ops = sales_data.with_columns([
        pl.col('sales').rank().over('month').alias('rank_in_month'),
        pl.col('sales').sum().over('salesperson').alias('total_by_person'),
        pl.col('sales').mean().over('month').alias('avg_by_month')
    ])
    
    print("窗口函数结果:")
    print(window_ops)

else:
    # 如果 Polars 未安装，显示代码示例
    print("\n\n代码示例（需要安装 Polars）:")
    print("-" * 30)
    
    example_code = '''
# 安装 Polars
pip install polars

# 基本使用
import polars as pl

# 创建 DataFrame
df = pl.DataFrame({
    'name': ['张三', '李四', '王五'],
    'age': [25, 30, 35],
    'salary': [8000, 12000, 15000]
})

# 基本操作
result = df.select([
    pl.col('name'),
    pl.col('salary'),
    (pl.col('salary') * 0.1).alias('bonus')
]).filter(pl.col('salary') > 10000)

# 分组聚合
agg_result = df.group_by('department').agg([
    pl.col('salary').mean().alias('avg_salary'),
    pl.col('name').count().alias('count')
])

# 延迟计算
lazy_result = (
    df.lazy()
    .filter(pl.col('age') > 25)
    .select(['name', 'salary'])
    .collect()
)
'''
    print(example_code)

# 13. 最佳实践
print("\n\n13. 最佳实践")
print("-" * 30)

best_practices = [
    "1. 使用延迟计算（LazyFrame）优化查询",
    "2. 合理选择数据类型以节省内存",
    "3. 利用表达式系统进行复杂计算",
    "4. 使用 Categorical 类型处理重复字符串",
    "5. 避免不必要的数据复制",
    "6. 利用并行处理能力",
    "7. 使用 Parquet 格式存储数据",
    "8. 合理使用窗口函数"
]

for practice in best_practices:
    print(practice)

# 14. Polars vs Pandas 对比
print("\n\n14. Polars vs Pandas 对比")
print("-" * 30)

comparison = {
    '特性': ['性能', '内存使用', '并行处理', '延迟计算', '类型系统', '生态系统'],
    'Polars': ['极快', '高效', '内置', '支持', '严格', '新兴'],
    'Pandas': ['较慢', '一般', '有限', '不支持', '灵活', '成熟']
}

print("功能对比:")
for i, feature in enumerate(comparison['特性']):
    print(f"{feature:8}: Polars({comparison['Polars'][i]:6}) vs Pandas({comparison['Pandas'][i]:6})")

# 15. 使用场景建议
print("\n\n15. 使用场景建议")
print("-" * 30)

scenarios = [
    "适合 Polars 的场景:",
    "- 大数据集处理（GB 级别）",
    "- 性能要求高的应用",
    "- 需要复杂数据转换的 ETL 流程",
    "- 新项目开发",
    "",
    "适合 Pandas 的场景:",
    "- 小到中等数据集",
    "- 需要丰富的第三方库支持",
    "- 现有项目迁移成本高",
    "- 快速原型开发"
]

for scenario in scenarios:
    print(scenario)

print("\n" + "=" * 60)
print("Polars 高性能数据处理教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 安装 Polars 并运行本教程的代码")
print("2. 比较 Polars 和 Pandas 在大数据集上的性能")
print("3. 学习 Polars 的延迟计算优化")
print("4. 尝试将现有 Pandas 代码迁移到 Polars")
print("5. 探索 Polars 的高级功能和插件")