#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dask 并行计算基础教程

Dask 是一个用于并行计算的 Python 库，可以处理超出内存限制的大数据集。
本教程介绍 Dask 的基本概念和使用方法。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
import dask.array as da
from dask.distributed import Client
import time

print("=" * 60)
print("Dask 并行计算基础教程")
print("=" * 60)

# 1. Dask 基本概念
print("\n1. Dask 基本概念")
print("-" * 30)

print("Dask 是什么？")
print("- 并行计算库，支持大于内存的数据集")
print("- 延迟计算（Lazy Evaluation）")
print("- 与 Pandas/NumPy API 兼容")
print("- 支持分布式计算")

# 检查 Dask 版本
print(f"\nDask 版本: {dask.__version__}")

# 2. Dask DataFrame 基础
print("\n\n2. Dask DataFrame 基础")
print("-" * 30)

# 创建示例数据
print("创建示例数据...")
np.random.seed(42)

# 创建多个 CSV 文件模拟大数据
for i in range(3):
    df = pd.DataFrame({
        'id': range(i*1000, (i+1)*1000),
        'value': np.random.randn(1000),
        'category': np.random.choice(['A', 'B', 'C'], 1000),
        'date': pd.date_range('2024-01-01', periods=1000, freq='H')
    })
    df.to_csv(f'sample_data_{i}.csv', index=False)

print("已创建 3 个示例 CSV 文件")

# 读取数据为 Dask DataFrame
ddf = dd.read_csv('sample_data_*.csv')
print(f"\nDask DataFrame 信息:")
print(f"分区数: {ddf.npartitions}")
print(f"列名: {list(ddf.columns)}")

# 查看数据类型
print(f"\n数据类型:")
print(ddf.dtypes)

# 3. 延迟计算演示
print("\n\n3. 延迟计算演示")
print("-" * 30)

# Dask 操作是延迟的
print("创建延迟计算任务...")
result = ddf.value.sum()
print(f"延迟计算对象: {result}")
print(f"类型: {type(result)}")

# 执行计算
print("\n执行计算...")
start_time = time.time()
computed_result = result.compute()
end_time = time.time()

print(f"计算结果: {computed_result:.4f}")
print(f"计算时间: {end_time - start_time:.4f} 秒")

# 4. Dask DataFrame 操作
print("\n\n4. Dask DataFrame 操作")
print("-" * 30)

# 基本统计
print("基本统计信息:")
stats = ddf.describe().compute()
print(stats)

# 分组聚合
print("\n按类别分组:")
group_result = ddf.groupby('category').value.mean().compute()
print(group_result)

# 筛选操作
print("\n筛选操作:")
filtered = ddf[ddf.value > 0]
positive_count = len(filtered)
print(f"正值数量: {positive_count}")

# 5. Dask Array 基础
print("\n\n5. Dask Array 基础")
print("-" * 30)

# 创建 Dask Array
print("创建 Dask Array:")
x = da.random.random((10000, 10000), chunks=(1000, 1000))
print(f"数组形状: {x.shape}")
print(f"数组块: {x.chunks}")
print(f"数据类型: {x.dtype}")

# 数组操作
print("\n数组操作:")
y = x + 1
z = y ** 2
result_mean = z.mean()

print(f"延迟计算链: x -> x+1 -> (x+1)^2 -> mean")
print(f"计算结果: {result_mean.compute():.6f}")

# 6. 任务图可视化
print("\n\n6. 任务图可视化")
print("-" * 30)

# 创建简单的计算任务
simple_calc = ddf.value.std()

print("任务图信息:")
print(f"任务数量: {len(simple_calc.dask)}")

# 可视化任务图（需要 graphviz）
try:
    simple_calc.visualize('dask_graph.png', optimize_graph=True)
    print("任务图已保存为 'dask_graph.png'")
except ImportError:
    print("需要安装 graphviz 来可视化任务图")
    print("pip install graphviz")

# 7. 性能比较
print("\n\n7. 性能比较")
print("-" * 30)

# 创建较大的数据集进行比较
print("创建测试数据...")
large_df = pd.DataFrame({
    'x': np.random.randn(100000),
    'y': np.random.randn(100000),
    'group': np.random.choice(['A', 'B', 'C', 'D'], 100000)
})

# Pandas 计算
print("\nPandas 计算:")
start_time = time.time()
pandas_result = large_df.groupby('group').x.mean()
pandas_time = time.time() - start_time
print(f"Pandas 结果: {pandas_result.values}")
print(f"Pandas 时间: {pandas_time:.4f} 秒")

# Dask 计算
print("\nDask 计算:")
dask_df = dd.from_pandas(large_df, npartitions=4)
start_time = time.time()
dask_result = dask_df.groupby('group').x.mean().compute()
dask_time = time.time() - start_time
print(f"Dask 结果: {dask_result.values}")
print(f"Dask 时间: {dask_time:.4f} 秒")

# 8. 内存使用优化
print("\n\n8. 内存使用优化")
print("-" * 30)

# 检查内存使用
print("内存使用情况:")
print(f"Dask DataFrame 内存估计: {ddf.memory_usage(deep=True).sum().compute() / 1024**2:.2f} MB")

# 优化数据类型
print("\n优化数据类型:")
optimized_ddf = ddf.copy()
optimized_ddf['category'] = optimized_ddf['category'].astype('category')

print("优化前后内存对比:")
original_memory = ddf.memory_usage(deep=True).sum().compute()
optimized_memory = optimized_ddf.memory_usage(deep=True).sum().compute()
print(f"原始: {original_memory / 1024**2:.2f} MB")
print(f"优化后: {optimized_memory / 1024**2:.2f} MB")
print(f"节省: {(1 - optimized_memory/original_memory)*100:.1f}%")

# 9. 分布式计算
print("\n\n9. 分布式计算")
print("-" * 30)

# 启动本地集群
print("启动本地 Dask 集群...")
try:
    client = Client(processes=False, threads_per_worker=2, n_workers=2)
    print(f"集群信息: {client}")
    
    # 在集群上执行计算
    print("\n在集群上执行计算:")
    cluster_result = ddf.value.var().compute()
    print(f"方差计算结果: {cluster_result:.6f}")
    
    # 查看集群状态
    print(f"\n集群状态:")
    print(f"工作节点数: {len(client.scheduler_info()['workers'])}")
    
    # 关闭客户端
    client.close()
    print("集群已关闭")
    
except Exception as e:
    print(f"集群启动失败: {e}")
    print("可能需要安装额外依赖: pip install dask[distributed]")

# 10. 数据持久化
print("\n\n10. 数据持久化")
print("-" * 30)

# 保存 Dask DataFrame
print("保存数据:")
output_path = 'dask_output'

# 保存为 Parquet 格式（推荐）
try:
    ddf.to_parquet(output_path)
    print(f"数据已保存到 {output_path}")
    
    # 读取保存的数据
    loaded_ddf = dd.read_parquet(output_path)
    print(f"重新加载的数据形状: {loaded_ddf.compute().shape}")
    
except ImportError:
    print("需要安装 pyarrow 来支持 Parquet 格式")
    print("pip install pyarrow")
    
    # 使用 CSV 格式作为备选
    ddf.to_csv('dask_output_csv', index=False)
    print("数据已保存为 CSV 格式")

# 11. 实际应用场景
print("\n\n11. 实际应用场景")
print("-" * 30)

def process_large_dataset():
    """处理大数据集的示例"""
    print("场景：处理大型销售数据")
    
    # 模拟大型数据集
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
    
    # 创建分块数据
    chunks = []
    for i in range(0, len(dates), 365):
        chunk_dates = dates[i:i+365]
        chunk_data = pd.DataFrame({
            'date': chunk_dates,
            'sales': np.random.uniform(1000, 10000, len(chunk_dates)),
            'region': np.random.choice(['North', 'South', 'East', 'West'], len(chunk_dates)),
            'product': np.random.choice(['A', 'B', 'C'], len(chunk_dates))
        })
        chunks.append(chunk_data)
    
    # 转换为 Dask DataFrame
    sales_ddf = dd.from_pandas(pd.concat(chunks), npartitions=4)
    
    # 分析操作
    print("\n执行分析:")
    
    # 1. 总销售额
    total_sales = sales_ddf.sales.sum().compute()
    print(f"总销售额: ${total_sales:,.2f}")
    
    # 2. 按地区分组
    region_sales = sales_ddf.groupby('region').sales.sum().compute()
    print(f"\n按地区销售额:")
    for region, sales in region_sales.items():
        print(f"  {region}: ${sales:,.2f}")
    
    # 3. 月度趋势
    sales_ddf['month'] = sales_ddf.date.dt.to_period('M')
    monthly_trend = sales_ddf.groupby('month').sales.mean().compute()
    print(f"\n月度平均销售额（前6个月）:")
    for month, avg_sales in monthly_trend.head(6).items():
        print(f"  {month}: ${avg_sales:,.2f}")
    
    return sales_ddf

# 执行大数据处理示例
large_sales_data = process_large_dataset()

# 12. 最佳实践
print("\n\n12. 最佳实践")
print("-" * 30)

best_practices = [
    "1. 合理设置分区大小（100MB-1GB 每个分区）",
    "2. 尽量使用 Parquet 格式存储数据",
    "3. 避免频繁的 compute() 调用",
    "4. 使用 persist() 缓存中间结果",
    "5. 优化数据类型以减少内存使用",
    "6. 利用索引加速查询",
    "7. 监控内存使用情况",
    "8. 合理配置集群资源"
]

for practice in best_practices:
    print(practice)

# 13. 性能监控
print("\n\n13. 性能监控")
print("-" * 30)

# 使用 persist 缓存数据
print("缓存数据以提高性能:")
cached_ddf = ddf.persist()

# 多次计算比较
operations = [
    ("求和", lambda x: x.value.sum()),
    ("平均值", lambda x: x.value.mean()),
    ("标准差", lambda x: x.value.std()),
    ("最大值", lambda x: x.value.max())
]

print("\n性能测试（缓存 vs 非缓存）:")
for op_name, op_func in operations:
    # 非缓存版本
    start_time = time.time()
    result1 = op_func(ddf).compute()
    time1 = time.time() - start_time
    
    # 缓存版本
    start_time = time.time()
    result2 = op_func(cached_ddf).compute()
    time2 = time.time() - start_time
    
    print(f"{op_name}: 非缓存 {time1:.4f}s, 缓存 {time2:.4f}s, 提升 {time1/time2:.1f}x")

# 清理临时文件
import os
import shutil

print("\n\n清理临时文件...")
for i in range(3):
    if os.path.exists(f'sample_data_{i}.csv'):
        os.remove(f'sample_data_{i}.csv')

if os.path.exists('dask_output'):
    shutil.rmtree('dask_output')

if os.path.exists('dask_output_csv'):
    shutil.rmtree('dask_output_csv')

print("临时文件已清理")

print("\n" + "=" * 60)
print("Dask 并行计算基础教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试处理更大的数据集")
print("2. 实验不同的分区策略")
print("3. 学习 Dask 的机器学习功能")
print("4. 探索分布式计算集群配置")
print("5. 比较 Dask 与其他大数据工具的性能")