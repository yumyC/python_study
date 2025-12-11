#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas DataFrame 基础操作教程

本教程涵盖 DataFrame 的创建、基本属性、索引操作等核心概念。
DataFrame 是 Pandas 中最重要的数据结构，类似于 Excel 表格或 SQL 表。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("Pandas DataFrame 基础操作教程")
print("=" * 60)

# 1. DataFrame 创建方法
print("\n1. DataFrame 创建方法")
print("-" * 30)

# 方法1: 从字典创建
data_dict = {
    'name': ['张三', '李四', '王五', '赵六'],
    'age': [25, 30, 35, 28],
    'city': ['北京', '上海', '广州', '深圳'],
    'salary': [8000, 12000, 15000, 10000]
}
df1 = pd.DataFrame(data_dict)
print("从字典创建 DataFrame:")
print(df1)

# 方法2: 从列表创建
data_list = [
    ['张三', 25, '北京', 8000],
    ['李四', 30, '上海', 12000],
    ['王五', 35, '广州', 15000],
    ['赵六', 28, '深圳', 10000]
]
columns = ['name', 'age', 'city', 'salary']
df2 = pd.DataFrame(data_list, columns=columns)
print("\n从列表创建 DataFrame:")
print(df2)

# 方法3: 从 NumPy 数组创建
np_data = np.random.randn(4, 3)
df3 = pd.DataFrame(np_data, 
                   columns=['A', 'B', 'C'],
                   index=['row1', 'row2', 'row3', 'row4'])
print("\n从 NumPy 数组创建 DataFrame:")
print(df3)

# 2. DataFrame 基本属性
print("\n\n2. DataFrame 基本属性")
print("-" * 30)

# 使用第一个 DataFrame 进行演示
df = df1.copy()

print(f"形状 (行数, 列数): {df.shape}")
print(f"行数: {len(df)}")
print(f"列数: {len(df.columns)}")
print(f"总元素个数: {df.size}")

print(f"\n列名: {list(df.columns)}")
print(f"索引: {list(df.index)}")
print(f"数据类型:\n{df.dtypes}")

# 3. 查看数据
print("\n\n3. 查看数据")
print("-" * 30)

print("前 2 行:")
print(df.head(2))

print("\n后 2 行:")
print(df.tail(2))

print("\n数据信息:")
df.info()

print("\n数值列的统计信息:")
print(df.describe())

# 4. 索引和选择
print("\n\n4. 索引和选择")
print("-" * 30)

# 选择单列
print("选择 'name' 列:")
print(df['name'])
print(f"类型: {type(df['name'])}")

# 选择多列
print("\n选择多列 ['name', 'salary']:")
print(df[['name', 'salary']])

# 选择行
print("\n选择第 0 行:")
print(df.iloc[0])

print("\n选择前 2 行:")
print(df.iloc[0:2])

# 选择特定行和列
print("\n选择前 2 行的 'name' 和 'age' 列:")
print(df.loc[0:1, ['name', 'age']])

# 5. 条件筛选
print("\n\n5. 条件筛选")
print("-" * 30)

# 单条件筛选
print("年龄大于 28 的员工:")
condition1 = df['age'] > 28
print(df[condition1])

# 多条件筛选
print("\n年龄大于 25 且薪资大于 10000 的员工:")
condition2 = (df['age'] > 25) & (df['salary'] > 10000)
print(df[condition2])

# 使用 isin 方法
print("\n城市为北京或上海的员工:")
condition3 = df['city'].isin(['北京', '上海'])
print(df[condition3])

# 6. 添加和删除列
print("\n\n6. 添加和删除列")
print("-" * 30)

# 添加新列
df['bonus'] = df['salary'] * 0.1  # 奖金为薪资的 10%
df['total_income'] = df['salary'] + df['bonus']  # 总收入
print("添加奖金和总收入列后:")
print(df)

# 删除列
df_dropped = df.drop(['bonus'], axis=1)  # axis=1 表示删除列
print("\n删除奖金列后:")
print(df_dropped)

# 7. 排序
print("\n\n7. 排序")
print("-" * 30)

# 按单列排序
print("按年龄升序排序:")
df_sorted_age = df.sort_values('age')
print(df_sorted_age)

print("\n按薪资降序排序:")
df_sorted_salary = df.sort_values('salary', ascending=False)
print(df_sorted_salary)

# 按多列排序
print("\n按年龄升序，薪资降序排序:")
df_sorted_multi = df.sort_values(['age', 'salary'], ascending=[True, False])
print(df_sorted_multi)

# 8. 重置索引
print("\n\n8. 重置索引")
print("-" * 30)

# 设置新索引
df_indexed = df.set_index('name')
print("以姓名为索引:")
print(df_indexed)

# 重置索引
df_reset = df_indexed.reset_index()
print("\n重置索引:")
print(df_reset)

# 9. 处理缺失值
print("\n\n9. 处理缺失值")
print("-" * 30)

# 创建包含缺失值的 DataFrame
data_with_nan = {
    'A': [1, 2, np.nan, 4],
    'B': [5, np.nan, 7, 8],
    'C': [9, 10, 11, np.nan]
}
df_nan = pd.DataFrame(data_with_nan)
print("包含缺失值的 DataFrame:")
print(df_nan)

# 检查缺失值
print("\n缺失值检查:")
print(df_nan.isnull())
print("\n每列缺失值数量:")
print(df_nan.isnull().sum())

# 删除包含缺失值的行
print("\n删除包含缺失值的行:")
print(df_nan.dropna())

# 填充缺失值
print("\n用 0 填充缺失值:")
print(df_nan.fillna(0))

print("\n用前一个值填充缺失值:")
print(df_nan.fillna(method='ffill'))

# 10. 数据类型转换
print("\n\n10. 数据类型转换")
print("-" * 30)

# 创建示例数据
df_types = pd.DataFrame({
    'numbers_as_str': ['1', '2', '3', '4'],
    'dates_as_str': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
    'categories': ['A', 'B', 'A', 'C']
})

print("原始数据类型:")
print(df_types.dtypes)

# 转换数据类型
df_types['numbers_as_str'] = df_types['numbers_as_str'].astype(int)
df_types['dates_as_str'] = pd.to_datetime(df_types['dates_as_str'])
df_types['categories'] = df_types['categories'].astype('category')

print("\n转换后的数据类型:")
print(df_types.dtypes)
print("\n转换后的数据:")
print(df_types)

# 11. 实用技巧
print("\n\n11. 实用技巧")
print("-" * 30)

# 快速统计
print("数值列的快速统计:")
print(f"平均年龄: {df['age'].mean():.1f}")
print(f"最高薪资: {df['salary'].max()}")
print(f"薪资标准差: {df['salary'].std():.2f}")

# 值计数
print("\n城市分布:")
print(df['city'].value_counts())

# 唯一值
print(f"\n唯一城市数量: {df['city'].nunique()}")
print(f"唯一城市: {df['city'].unique()}")

# 应用函数
print("\n薪资等级分类:")
def salary_grade(salary):
    if salary < 9000:
        return '初级'
    elif salary < 12000:
        return '中级'
    else:
        return '高级'

df['grade'] = df['salary'].apply(salary_grade)
print(df[['name', 'salary', 'grade']])

print("\n" + "=" * 60)
print("DataFrame 基础操作教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试创建自己的 DataFrame")
print("2. 练习不同的筛选条件")
print("3. 尝试更复杂的排序操作")
print("4. 练习处理真实数据中的缺失值")
print("5. 探索更多的数据类型转换方法")