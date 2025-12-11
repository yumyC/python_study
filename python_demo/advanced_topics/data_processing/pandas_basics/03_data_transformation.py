#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas 数据转换教程

数据转换是数据分析的核心技能，包括数据重塑、透视表、数据聚合等操作。
本教程展示各种数据转换技术和实际应用场景。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("Pandas 数据转换教程")
print("=" * 60)

# 1. 创建示例数据
print("\n1. 创建示例数据")
print("-" * 30)

# 销售数据
sales_data = {
    'date': pd.date_range('2024-01-01', periods=20, freq='D'),
    'product': ['A', 'B', 'C', 'A', 'B'] * 4,
    'region': ['North', 'South', 'East', 'West', 'North'] * 4,
    'sales': np.random.randint(100, 1000, 20),
    'quantity': np.random.randint(10, 100, 20),
    'price': np.random.uniform(10, 50, 20).round(2)
}

df_sales = pd.DataFrame(sales_data)
print("销售数据:")
print(df_sales.head(10))

# 员工数据
employee_data = {
    'employee_id': range(1, 11),
    'name': [f'员工{i}' for i in range(1, 11)],
    'department': ['IT', 'HR', 'Finance', 'IT', 'HR', 'Finance', 'IT', 'HR', 'Finance', 'IT'],
    'salary': [8000, 6000, 7000, 9000, 6500, 7500, 8500, 6200, 7200, 9200],
    'bonus': [800, 600, 700, 900, 650, 750, 850, 620, 720, 920],
    'hire_year': [2020, 2019, 2021, 2018, 2022, 2020, 2019, 2021, 2018, 2022]
}

df_employees = pd.DataFrame(employee_data)
print("\n员工数据:")
print(df_employees)

# 2. 数据重塑 - 宽格式与长格式转换
print("\n\n2. 数据重塑 - 宽格式与长格式转换")
print("-" * 30)

# 创建宽格式数据
wide_data = {
    'name': ['张三', '李四', '王五'],
    'math': [85, 92, 78],
    'english': [88, 85, 90],
    'science': [92, 88, 85]
}
df_wide = pd.DataFrame(wide_data)
print("宽格式数据（每个科目一列）:")
print(df_wide)

# 宽格式转长格式 (melt)
df_long = pd.melt(df_wide, 
                  id_vars=['name'], 
                  value_vars=['math', 'english', 'science'],
                  var_name='subject', 
                  value_name='score')
print("\n长格式数据（使用 melt）:")
print(df_long)

# 长格式转宽格式 (pivot)
df_wide_back = df_long.pivot(index='name', columns='subject', values='score')
print("\n转回宽格式（使用 pivot）:")
print(df_wide_back)

# 重置索引使其更整洁
df_wide_back = df_wide_back.reset_index()
df_wide_back.columns.name = None  # 移除列索引名称
print("\n重置索引后:")
print(df_wide_back)

# 3. 透视表 (Pivot Table)
print("\n\n3. 透视表 (Pivot Table)")
print("-" * 30)

# 基本透视表
pivot_basic = df_sales.pivot_table(
    values='sales',
    index='product',
    columns='region',
    aggfunc='sum'
)
print("基本透视表（产品 vs 地区的销售额）:")
print(pivot_basic)

# 多值透视表
pivot_multi = df_sales.pivot_table(
    values=['sales', 'quantity'],
    index='product',
    columns='region',
    aggfunc='sum'
)
print("\n多值透视表（销售额和数量）:")
print(pivot_multi)

# 多聚合函数透视表
pivot_agg = df_sales.pivot_table(
    values='sales',
    index='product',
    columns='region',
    aggfunc=['sum', 'mean', 'count']
)
print("\n多聚合函数透视表:")
print(pivot_agg)

# 添加边际总计
pivot_margins = df_sales.pivot_table(
    values='sales',
    index='product',
    columns='region',
    aggfunc='sum',
    margins=True,
    margins_name='总计'
)
print("\n带边际总计的透视表:")
print(pivot_margins)

# 4. 交叉表 (Cross Tabulation)
print("\n\n4. 交叉表 (Cross Tabulation)")
print("-" * 30)

# 基本交叉表
crosstab_basic = pd.crosstab(df_sales['product'], df_sales['region'])
print("基本交叉表（产品 vs 地区的计数）:")
print(crosstab_basic)

# 带比例的交叉表
crosstab_prop = pd.crosstab(df_sales['product'], df_sales['region'], normalize='index')
print("\n行比例交叉表:")
print(crosstab_prop.round(3))

# 带值的交叉表
crosstab_values = pd.crosstab(df_sales['product'], df_sales['region'], 
                             values=df_sales['sales'], aggfunc='sum')
print("\n带销售额值的交叉表:")
print(crosstab_values)

# 5. 数据分组和聚合
print("\n\n5. 数据分组和聚合")
print("-" * 30)

# 单列分组
group_product = df_sales.groupby('product')['sales'].sum()
print("按产品分组的销售额:")
print(group_product)

# 多列分组
group_multi = df_sales.groupby(['product', 'region'])['sales'].sum()
print("\n按产品和地区分组的销售额:")
print(group_multi)

# 多种聚合函数
agg_multi = df_sales.groupby('product').agg({
    'sales': ['sum', 'mean', 'std'],
    'quantity': ['sum', 'mean'],
    'price': 'mean'
})
print("\n多种聚合函数:")
print(agg_multi.round(2))

# 自定义聚合函数
def sales_range(series):
    return series.max() - series.min()

custom_agg = df_sales.groupby('product').agg({
    'sales': ['sum', 'mean', sales_range],
    'quantity': 'sum'
})
print("\n自定义聚合函数（销售额范围）:")
print(custom_agg)

# 6. 时间序列数据转换
print("\n\n6. 时间序列数据转换")
print("-" * 30)

# 设置日期为索引
df_ts = df_sales.set_index('date')
print("时间序列数据（前5行）:")
print(df_ts.head())

# 按时间重采样
daily_sales = df_ts.groupby('date')['sales'].sum()
print("\n每日总销售额:")
print(daily_sales.head())

# 滚动窗口计算
rolling_mean = daily_sales.rolling(window=3).mean()
print("\n3日滚动平均:")
print(rolling_mean.head(10))

# 累计计算
cumulative_sales = daily_sales.cumsum()
print("\n累计销售额:")
print(cumulative_sales.head(10))

# 7. 数据分箱和分类
print("\n\n7. 数据分箱和分类")
print("-" * 30)

# 等宽分箱
df_employees['salary_bins'] = pd.cut(df_employees['salary'], 
                                   bins=3, 
                                   labels=['低', '中', '高'])
print("薪资等宽分箱:")
print(df_employees[['name', 'salary', 'salary_bins']])

# 等频分箱
df_employees['salary_quantiles'] = pd.qcut(df_employees['salary'], 
                                         q=3, 
                                         labels=['Q1', 'Q2', 'Q3'])
print("\n薪资等频分箱:")
print(df_employees[['name', 'salary', 'salary_quantiles']])

# 自定义分箱
bins = [0, 6500, 8000, float('inf')]
labels = ['初级', '中级', '高级']
df_employees['salary_level'] = pd.cut(df_employees['salary'], 
                                    bins=bins, 
                                    labels=labels)
print("\n自定义薪资等级:")
print(df_employees[['name', 'salary', 'salary_level']])

# 8. 字符串操作和转换
print("\n\n8. 字符串操作和转换")
print("-" * 30)

# 创建包含字符串的数据
text_data = {
    'name': ['张三', '李四', '王五六', '赵七'],
    'email': ['zhang@company.com', 'li@company.com', 'wang@company.com', 'zhao@company.com'],
    'phone': ['138-1234-5678', '139-2345-6789', '137-3456-7890', '136-4567-8901']
}
df_text = pd.DataFrame(text_data)
print("文本数据:")
print(df_text)

# 字符串长度
df_text['name_length'] = df_text['name'].str.len()
print("\n添加姓名长度:")
print(df_text)

# 提取邮箱用户名
df_text['username'] = df_text['email'].str.split('@').str[0]
print("\n提取邮箱用户名:")
print(df_text[['email', 'username']])

# 格式化电话号码
df_text['phone_formatted'] = df_text['phone'].str.replace('-', '')
print("\n格式化电话号码:")
print(df_text[['phone', 'phone_formatted']])

# 9. 条件转换
print("\n\n9. 条件转换")
print("-" * 30)

# 使用 np.where 进行条件转换
df_employees['performance'] = np.where(df_employees['salary'] > 8000, '优秀', '良好')
print("基于薪资的绩效评级:")
print(df_employees[['name', 'salary', 'performance']])

# 多条件转换
conditions = [
    df_employees['salary'] < 7000,
    (df_employees['salary'] >= 7000) & (df_employees['salary'] < 8500),
    df_employees['salary'] >= 8500
]
choices = ['C级', 'B级', 'A级']
df_employees['grade'] = np.select(conditions, choices, default='未知')
print("\n多条件薪资等级:")
print(df_employees[['name', 'salary', 'grade']])

# 使用 apply 和 lambda
df_employees['bonus_rate'] = df_employees['salary'].apply(
    lambda x: 0.15 if x > 8000 else 0.10
)
print("\n奖金比例:")
print(df_employees[['name', 'salary', 'bonus_rate']])

# 10. 数据合并和连接
print("\n\n10. 数据合并和连接")
print("-" * 30)

# 创建部门信息数据
dept_data = {
    'department': ['IT', 'HR', 'Finance'],
    'manager': ['张经理', '李经理', '王经理'],
    'budget': [1000000, 500000, 800000]
}
df_dept = pd.DataFrame(dept_data)
print("部门信息:")
print(df_dept)

# 内连接
merged_inner = pd.merge(df_employees, df_dept, on='department', how='inner')
print("\n内连接结果:")
print(merged_inner[['name', 'department', 'manager', 'salary']])

# 左连接
merged_left = pd.merge(df_employees, df_dept, on='department', how='left')
print("\n左连接结果:")
print(merged_left[['name', 'department', 'manager', 'salary']])

# 11. 数据标准化和归一化
print("\n\n11. 数据标准化和归一化")
print("-" * 30)

# Z-score 标准化
df_employees['salary_zscore'] = (df_employees['salary'] - df_employees['salary'].mean()) / df_employees['salary'].std()
print("薪资 Z-score 标准化:")
print(df_employees[['name', 'salary', 'salary_zscore']].round(3))

# Min-Max 归一化
df_employees['salary_minmax'] = (df_employees['salary'] - df_employees['salary'].min()) / (df_employees['salary'].max() - df_employees['salary'].min())
print("\n薪资 Min-Max 归一化:")
print(df_employees[['name', 'salary', 'salary_minmax']].round(3))

# 12. 数据排名
print("\n\n12. 数据排名")
print("-" * 30)

# 简单排名
df_employees['salary_rank'] = df_employees['salary'].rank(ascending=False)
print("薪资排名:")
print(df_employees[['name', 'salary', 'salary_rank']].sort_values('salary_rank'))

# 分组排名
df_employees['dept_rank'] = df_employees.groupby('department')['salary'].rank(ascending=False)
print("\n部门内薪资排名:")
print(df_employees[['name', 'department', 'salary', 'dept_rank']].sort_values(['department', 'dept_rank']))

# 13. 实际应用示例：销售报告生成
print("\n\n13. 实际应用示例：销售报告生成")
print("-" * 30)

# 生成综合销售报告
def generate_sales_report(df):
    """生成销售报告"""
    report = {}
    
    # 总体统计
    report['总销售额'] = df['sales'].sum()
    report['平均销售额'] = df['sales'].mean()
    report['销售记录数'] = len(df)
    
    # 按产品统计
    product_stats = df.groupby('product').agg({
        'sales': ['sum', 'mean', 'count'],
        'quantity': 'sum'
    }).round(2)
    
    # 按地区统计
    region_stats = df.groupby('region').agg({
        'sales': ['sum', 'mean'],
        'quantity': 'sum'
    }).round(2)
    
    return report, product_stats, region_stats

report, product_stats, region_stats = generate_sales_report(df_sales)

print("销售总体报告:")
for key, value in report.items():
    print(f"{key}: {value}")

print("\n按产品统计:")
print(product_stats)

print("\n按地区统计:")
print(region_stats)

print("\n" + "=" * 60)
print("数据转换教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试更复杂的透视表操作")
print("2. 练习时间序列数据的重采样")
print("3. 实现自定义的数据转换函数")
print("4. 练习多表连接操作")
print("5. 创建完整的数据分析报告")