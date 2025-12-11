#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas GroupBy 和聚合操作教程

GroupBy 是 Pandas 中最强大的功能之一，用于分组数据并进行聚合计算。
本教程详细介绍各种分组和聚合技术。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("Pandas GroupBy 和聚合操作教程")
print("=" * 60)

# 1. 创建示例数据
print("\n1. 创建示例数据")
print("-" * 30)

# 创建销售数据
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=100, freq='D')
sales_data = {
    'date': np.random.choice(dates, 200),
    'salesperson': np.random.choice(['张三', '李四', '王五', '赵六', '钱七'], 200),
    'product': np.random.choice(['笔记本', '手机', '平板', '耳机', '鼠标'], 200),
    'category': np.random.choice(['电子产品', '配件'], 200),
    'region': np.random.choice(['北京', '上海', '广州', '深圳'], 200),
    'sales_amount': np.random.uniform(100, 5000, 200).round(2),
    'quantity': np.random.randint(1, 20, 200),
    'cost': np.random.uniform(50, 2500, 200).round(2)
}

df = pd.DataFrame(sales_data)
df['profit'] = df['sales_amount'] - df['cost']
df['profit_margin'] = (df['profit'] / df['sales_amount'] * 100).round(2)

print("销售数据样本:")
print(df.head(10))
print(f"\n数据形状: {df.shape}")

# 2. 基本 GroupBy 操作
print("\n\n2. 基本 GroupBy 操作")
print("-" * 30)

# 单列分组
print("按销售员分组的销售额:")
sales_by_person = df.groupby('salesperson')['sales_amount'].sum()
print(sales_by_person)

print("\n按产品分组的平均销售额:")
avg_sales_by_product = df.groupby('product')['sales_amount'].mean().round(2)
print(avg_sales_by_product)

# 查看分组对象
print("\n分组对象信息:")
grouped = df.groupby('salesperson')
print(f"分组数量: {grouped.ngroups}")
print(f"分组大小: {grouped.size()}")

# 3. 多列分组
print("\n\n3. 多列分组")
print("-" * 30)

# 按多列分组
multi_group = df.groupby(['region', 'product'])['sales_amount'].sum()
print("按地区和产品分组的销售额:")
print(multi_group.head(10))

# 转换为 DataFrame 格式
multi_group_df = multi_group.reset_index()
print("\n转换为 DataFrame 格式:")
print(multi_group_df.head(10))

# 4. 多种聚合函数
print("\n\n4. 多种聚合函数")
print("-" * 30)

# 单列多种聚合
single_col_agg = df.groupby('salesperson')['sales_amount'].agg(['sum', 'mean', 'std', 'count'])
print("销售员的销售额统计:")
print(single_col_agg.round(2))

# 多列多种聚合
multi_col_agg = df.groupby('salesperson').agg({
    'sales_amount': ['sum', 'mean', 'count'],
    'quantity': ['sum', 'mean'],
    'profit': ['sum', 'mean'],
    'profit_margin': 'mean'
})
print("\n销售员的综合统计:")
print(multi_col_agg.round(2))

# 重命名聚合列
renamed_agg = df.groupby('salesperson').agg({
    'sales_amount': ['sum', 'mean'],
    'quantity': 'sum',
    'profit': 'sum'
}).round(2)

# 扁平化列名
renamed_agg.columns = ['总销售额', '平均销售额', '总数量', '总利润']
print("\n重命名后的聚合结果:")
print(renamed_agg)

# 5. 自定义聚合函数
print("\n\n5. 自定义聚合函数")
print("-" * 30)

# 定义自定义函数
def sales_range(series):
    """计算销售额范围"""
    return series.max() - series.min()

def top_product_sales(group):
    """返回最高销售额的产品"""
    return group.loc[group['sales_amount'].idxmax(), 'product']

# 使用自定义函数
custom_agg = df.groupby('salesperson').agg({
    'sales_amount': ['sum', 'mean', sales_range],
    'profit': 'sum'
})
print("使用自定义聚合函数:")
print(custom_agg.round(2))

# 应用自定义函数到整个分组
top_products = df.groupby('salesperson').apply(top_product_sales)
print("\n每个销售员的最高销售额产品:")
print(top_products)

# 6. 条件聚合
print("\n\n6. 条件聚合")
print("-" * 30)

# 筛选后聚合
high_value_sales = df[df['sales_amount'] > 1000].groupby('salesperson')['sales_amount'].sum()
print("高价值销售（>1000）按销售员统计:")
print(high_value_sales)

# 使用 query 方法
electronics_sales = df.query('category == "电子产品"').groupby('region')['sales_amount'].sum()
print("\n电子产品按地区销售额:")
print(electronics_sales)

# 7. 时间序列分组
print("\n\n7. 时间序列分组")
print("-" * 30)

# 按日期分组
daily_sales = df.groupby('date')['sales_amount'].sum().sort_index()
print("每日销售额（前10天）:")
print(daily_sales.head(10))

# 按月份分组
df['month'] = df['date'].dt.to_period('M')
monthly_sales = df.groupby('month')['sales_amount'].sum()
print("\n按月销售额:")
print(monthly_sales)

# 按星期几分组
df['weekday'] = df['date'].dt.day_name()
weekday_sales = df.groupby('weekday')['sales_amount'].mean().round(2)
print("\n按星期几的平均销售额:")
print(weekday_sales)

# 8. 分组转换 (Transform)
print("\n\n8. 分组转换 (Transform)")
print("-" * 30)

# 计算每个销售员的销售额占比
df['sales_pct_by_person'] = df.groupby('salesperson')['sales_amount'].transform(
    lambda x: x / x.sum() * 100
).round(2)

print("销售员内部销售额占比:")
print(df[['salesperson', 'sales_amount', 'sales_pct_by_person']].head(10))

# 计算与组内平均值的差异
df['sales_diff_from_avg'] = df.groupby('product')['sales_amount'].transform(
    lambda x: x - x.mean()
).round(2)

print("\n与产品平均销售额的差异:")
print(df[['product', 'sales_amount', 'sales_diff_from_avg']].head(10))

# 9. 分组过滤 (Filter)
print("\n\n9. 分组过滤 (Filter)")
print("-" * 30)

# 筛选销售记录超过10条的销售员
active_salespeople = df.groupby('salesperson').filter(lambda x: len(x) > 10)
print(f"活跃销售员的记录数: {len(active_salespeople)}")
print("活跃销售员列表:")
print(active_salespeople['salesperson'].unique())

# 筛选平均销售额超过1000的产品
high_value_products = df.groupby('product').filter(lambda x: x['sales_amount'].mean() > 1000)
print(f"\n高价值产品的记录数: {len(high_value_products)}")
print("高价值产品列表:")
print(high_value_products['product'].unique())

# 10. 滚动窗口聚合
print("\n\n10. 滚动窗口聚合")
print("-" * 30)

# 按日期排序
df_sorted = df.sort_values('date')

# 计算滚动平均
df_sorted['rolling_avg_3d'] = df_sorted.groupby('salesperson')['sales_amount'].transform(
    lambda x: x.rolling(window=3, min_periods=1).mean()
).round(2)

print("3日滚动平均销售额:")
print(df_sorted[['date', 'salesperson', 'sales_amount', 'rolling_avg_3d']].head(15))

# 11. 分位数和排名
print("\n\n11. 分位数和排名")
print("-" * 30)

# 计算分位数
quantiles = df.groupby('product')['sales_amount'].quantile([0.25, 0.5, 0.75]).unstack()
print("产品销售额分位数:")
print(quantiles.round(2))

# 组内排名
df['rank_in_product'] = df.groupby('product')['sales_amount'].rank(ascending=False)
print("\n产品内销售额排名:")
print(df[['product', 'sales_amount', 'rank_in_product']].head(15))

# 12. 复杂聚合示例
print("\n\n12. 复杂聚合示例")
print("-" * 30)

# 创建复杂的聚合报告
def create_sales_report(group):
    """创建详细的销售报告"""
    return pd.Series({
        '总销售额': group['sales_amount'].sum(),
        '平均销售额': group['sales_amount'].mean(),
        '销售次数': len(group),
        '最高单笔': group['sales_amount'].max(),
        '最低单笔': group['sales_amount'].min(),
        '总利润': group['profit'].sum(),
        '平均利润率': group['profit_margin'].mean(),
        '主要产品': group['product'].mode().iloc[0] if not group['product'].mode().empty else 'N/A',
        '活跃天数': group['date'].nunique()
    })

sales_report = df.groupby('salesperson').apply(create_sales_report).round(2)
print("销售员详细报告:")
print(sales_report)

# 13. 性能优化技巧
print("\n\n13. 性能优化技巧")
print("-" * 30)

# 使用 agg 比多次调用 groupby 更高效
print("高效的聚合方式:")
efficient_agg = df.groupby('region').agg({
    'sales_amount': ['sum', 'mean', 'count'],
    'profit': 'sum',
    'quantity': 'sum'
}).round(2)
print(efficient_agg)

# 14. 实际业务场景应用
print("\n\n14. 实际业务场景应用")
print("-" * 30)

# 场景1: 销售绩效分析
def analyze_performance(df):
    """分析销售绩效"""
    performance = df.groupby('salesperson').agg({
        'sales_amount': ['sum', 'count'],
        'profit': 'sum'
    }).round(2)
    
    performance.columns = ['总销售额', '销售次数', '总利润']
    performance['平均客单价'] = (performance['总销售额'] / performance['销售次数']).round(2)
    performance['利润率'] = (performance['总利润'] / performance['总销售额'] * 100).round(2)
    
    return performance.sort_values('总销售额', ascending=False)

performance_analysis = analyze_performance(df)
print("销售绩效分析:")
print(performance_analysis)

# 场景2: 产品分析
def analyze_products(df):
    """分析产品表现"""
    product_analysis = df.groupby('product').agg({
        'sales_amount': ['sum', 'mean', 'count'],
        'quantity': 'sum',
        'profit_margin': 'mean'
    }).round(2)
    
    product_analysis.columns = ['总销售额', '平均销售额', '销售次数', '总销量', '平均利润率']
    return product_analysis.sort_values('总销售额', ascending=False)

product_analysis = analyze_products(df)
print("\n产品分析:")
print(product_analysis)

# 场景3: 地区分析
def analyze_regions(df):
    """分析地区表现"""
    region_analysis = df.groupby('region').agg({
        'sales_amount': 'sum',
        'salesperson': 'nunique',
        'product': 'nunique'
    }).round(2)
    
    region_analysis.columns = ['总销售额', '销售员数量', '产品种类']
    region_analysis['人均销售额'] = (region_analysis['总销售额'] / region_analysis['销售员数量']).round(2)
    
    return region_analysis.sort_values('总销售额', ascending=False)

region_analysis = analyze_regions(df)
print("\n地区分析:")
print(region_analysis)

print("\n" + "=" * 60)
print("GroupBy 和聚合操作教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试更复杂的多级分组")
print("2. 实现自定义的聚合函数")
print("3. 练习时间序列的分组聚合")
print("4. 结合条件筛选和聚合操作")
print("5. 创建完整的业务分析报告")