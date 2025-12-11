#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas 数据清洗教程

数据清洗是数据分析的重要步骤，包括处理缺失值、重复数据、异常值等。
本教程展示常见的数据清洗技术和最佳实践。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 设置中文字体（如果需要显示中文图表）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("Pandas 数据清洗教程")
print("=" * 60)

# 1. 创建包含各种问题的示例数据
print("\n1. 创建包含问题的示例数据")
print("-" * 30)

# 创建一个包含各种数据质量问题的数据集
np.random.seed(42)  # 设置随机种子以确保结果可重现

data = {
    'employee_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 11],  # 包含重复ID
    'name': ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', 
             '郑十一', '王十二', '王十二', '李十三'],  # 包含重复姓名
    'age': [25, 30, -5, 35, 28, 150, 32, np.nan, 29, 31, 31, 27],  # 包含异常值和缺失值
    'salary': [8000, 12000, 15000, np.nan, 10000, 9000, 11000, 13000, 
               999999, 8500, 8500, 9500],  # 包含缺失值和异常值
    'department': ['IT', 'HR', 'Finance', 'IT', 'HR', '', 'Finance', 
                   'IT', 'HR', 'Finance', 'Finance', None],  # 包含空字符串和None
    'hire_date': ['2020-01-15', '2019-03-20', '2021-07-10', '2018-12-05',
                  '2022-02-28', 'invalid_date', '2020-09-15', '2021-11-30',
                  '2019-08-12', '2023-01-10', '2023-01-10', '2022-06-15'],  # 包含无效日期
    'email': ['zhang@company.com', 'li@company.com', 'wang@company.com',
              'zhao@company.com', 'qian@company.com', 'sun@company.com',
              'zhou@company.com', 'wu@company.com', 'zheng@company.com',
              'wang2@company.com', 'wang2@company.com', 'invalid_email']  # 包含无效邮箱
}

df = pd.DataFrame(data)
print("原始数据（包含各种问题）:")
print(df)
print(f"\n数据形状: {df.shape}")

# 2. 数据质量检查
print("\n\n2. 数据质量检查")
print("-" * 30)

# 基本信息
print("数据基本信息:")
df.info()

# 缺失值检查
print("\n缺失值统计:")
missing_stats = pd.DataFrame({
    '缺失数量': df.isnull().sum(),
    '缺失比例': df.isnull().sum() / len(df) * 100
})
print(missing_stats)

# 重复值检查
print(f"\n重复行数量: {df.duplicated().sum()}")
print("重复行:")
print(df[df.duplicated(keep=False)])

# 数据类型检查
print("\n数据类型:")
print(df.dtypes)

# 3. 处理缺失值
print("\n\n3. 处理缺失值")
print("-" * 30)

# 创建副本进行操作
df_clean = df.copy()

# 检查每列的缺失值情况
print("各列缺失值详情:")
for col in df_clean.columns:
    missing_count = df_clean[col].isnull().sum()
    if missing_count > 0:
        print(f"{col}: {missing_count} 个缺失值")
        print(f"  缺失值位置: {df_clean[df_clean[col].isnull()].index.tolist()}")

# 处理不同类型的缺失值
print("\n处理缺失值:")

# 年龄缺失值用中位数填充
age_median = df_clean['age'].median()
df_clean['age'].fillna(age_median, inplace=True)
print(f"年龄缺失值用中位数 {age_median} 填充")

# 薪资缺失值用同部门平均值填充
def fill_salary_by_dept(row):
    if pd.isnull(row['salary']):
        dept_avg = df_clean[df_clean['department'] == row['department']]['salary'].mean()
        return dept_avg if not pd.isnan(dept_avg) else df_clean['salary'].mean()
    return row['salary']

df_clean['salary'] = df_clean.apply(fill_salary_by_dept, axis=1)
print("薪资缺失值用同部门平均值填充")

# 部门缺失值处理
df_clean['department'].fillna('Unknown', inplace=True)
df_clean['department'] = df_clean['department'].replace('', 'Unknown')
print("部门缺失值和空字符串替换为 'Unknown'")

print("\n处理缺失值后:")
print(df_clean.isnull().sum())

# 4. 处理重复数据
print("\n\n4. 处理重复数据")
print("-" * 30)

print(f"处理前重复行数: {df_clean.duplicated().sum()}")

# 删除完全重复的行
df_clean = df_clean.drop_duplicates()
print(f"删除完全重复行后: {len(df_clean)} 行")

# 处理基于特定列的重复（如员工ID重复）
print("\n基于 employee_id 的重复检查:")
id_duplicates = df_clean[df_clean.duplicated(['employee_id'], keep=False)]
if not id_duplicates.empty:
    print("employee_id 重复的记录:")
    print(id_duplicates)
    
    # 保留最新的记录（假设基于hire_date）
    df_clean['hire_date_parsed'] = pd.to_datetime(df_clean['hire_date'], errors='coerce')
    df_clean = df_clean.sort_values('hire_date_parsed').drop_duplicates(['employee_id'], keep='last')
    print("保留最新记录后的数据量:", len(df_clean))

# 5. 处理异常值
print("\n\n5. 处理异常值")
print("-" * 30)

# 年龄异常值检测和处理
print("年龄分布统计:")
print(df_clean['age'].describe())

# 使用 IQR 方法检测异常值
def detect_outliers_iqr(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (series < lower_bound) | (series > upper_bound)

# 检测年龄异常值
age_outliers = detect_outliers_iqr(df_clean['age'])
print(f"\n年龄异常值数量: {age_outliers.sum()}")
if age_outliers.sum() > 0:
    print("年龄异常值:")
    print(df_clean[age_outliers][['name', 'age']])
    
    # 处理年龄异常值：设置合理范围
    df_clean.loc[df_clean['age'] < 18, 'age'] = 18
    df_clean.loc[df_clean['age'] > 65, 'age'] = 65
    print("年龄异常值已调整到合理范围 [18, 65]")

# 薪资异常值检测和处理
print("\n薪资分布统计:")
print(df_clean['salary'].describe())

salary_outliers = detect_outliers_iqr(df_clean['salary'])
print(f"\n薪资异常值数量: {salary_outliers.sum()}")
if salary_outliers.sum() > 0:
    print("薪资异常值:")
    print(df_clean[salary_outliers][['name', 'salary']])
    
    # 处理薪资异常值：用中位数替换
    salary_median = df_clean['salary'].median()
    df_clean.loc[salary_outliers, 'salary'] = salary_median
    print(f"薪资异常值已替换为中位数: {salary_median}")

# 6. 数据类型转换和格式化
print("\n\n6. 数据类型转换和格式化")
print("-" * 30)

# 转换日期格式
print("处理日期格式:")
df_clean['hire_date'] = pd.to_datetime(df_clean['hire_date'], errors='coerce')
invalid_dates = df_clean['hire_date'].isnull().sum()
if invalid_dates > 0:
    print(f"发现 {invalid_dates} 个无效日期，将用默认日期替换")
    df_clean['hire_date'].fillna(pd.to_datetime('2020-01-01'), inplace=True)

# 邮箱格式验证
print("\n验证邮箱格式:")
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
valid_emails = df_clean['email'].str.match(email_pattern, na=False)
invalid_email_count = (~valid_emails).sum()
print(f"无效邮箱数量: {invalid_email_count}")
if invalid_email_count > 0:
    print("无效邮箱:")
    print(df_clean[~valid_emails][['name', 'email']])

# 7. 数据标准化和规范化
print("\n\n7. 数据标准化和规范化")
print("-" * 30)

# 姓名格式标准化
df_clean['name'] = df_clean['name'].str.strip()  # 去除首尾空格
print("姓名已去除首尾空格")

# 部门名称标准化
dept_mapping = {
    'IT': 'Information Technology',
    'HR': 'Human Resources',
    'Finance': 'Finance',
    'Unknown': 'Unknown'
}
df_clean['department_full'] = df_clean['department'].map(dept_mapping)
print("部门名称已标准化")

# 添加计算列
df_clean['years_of_service'] = (datetime.now() - df_clean['hire_date']).dt.days / 365.25
df_clean['years_of_service'] = df_clean['years_of_service'].round(1)
print("添加工作年限计算列")

# 8. 数据验证
print("\n\n8. 数据验证")
print("-" * 30)

# 验证数据完整性
print("数据完整性检查:")
print(f"总行数: {len(df_clean)}")
print(f"缺失值总数: {df_clean.isnull().sum().sum()}")
print(f"重复行数: {df_clean.duplicated().sum()}")

# 验证数据范围
print("\n数据范围验证:")
print(f"年龄范围: {df_clean['age'].min()} - {df_clean['age'].max()}")
print(f"薪资范围: {df_clean['salary'].min()} - {df_clean['salary'].max()}")
print(f"入职日期范围: {df_clean['hire_date'].min()} - {df_clean['hire_date'].max()}")

# 验证业务逻辑
print("\n业务逻辑验证:")
# 检查是否有不合理的薪资（如低于最低工资）
min_salary = 5000
low_salary_count = (df_clean['salary'] < min_salary).sum()
print(f"低于最低工资 ({min_salary}) 的员工数: {low_salary_count}")

# 9. 清洗后的数据展示
print("\n\n9. 清洗后的数据")
print("-" * 30)

# 删除临时列
if 'hire_date_parsed' in df_clean.columns:
    df_clean = df_clean.drop('hire_date_parsed', axis=1)

print("清洗后的数据:")
print(df_clean)

print("\n清洗后数据统计:")
print(df_clean.describe())

# 10. 数据质量报告
print("\n\n10. 数据质量报告")
print("-" * 30)

def generate_quality_report(original_df, cleaned_df):
    """生成数据质量报告"""
    report = {
        '原始数据行数': len(original_df),
        '清洗后数据行数': len(cleaned_df),
        '删除的行数': len(original_df) - len(cleaned_df),
        '原始缺失值数量': original_df.isnull().sum().sum(),
        '清洗后缺失值数量': cleaned_df.isnull().sum().sum(),
        '原始重复行数': original_df.duplicated().sum(),
        '清洗后重复行数': cleaned_df.duplicated().sum()
    }
    return report

quality_report = generate_quality_report(df, df_clean)
print("数据质量报告:")
for key, value in quality_report.items():
    print(f"{key}: {value}")

# 11. 保存清洗后的数据
print("\n\n11. 保存清洗后的数据")
print("-" * 30)

# 保存为 CSV 文件（示例）
# df_clean.to_csv('cleaned_employee_data.csv', index=False, encoding='utf-8')
print("数据清洗完成！可以保存为 CSV 文件:")
print("df_clean.to_csv('cleaned_employee_data.csv', index=False, encoding='utf-8')")

# 12. 数据清洗最佳实践总结
print("\n\n12. 数据清洗最佳实践")
print("-" * 30)

best_practices = [
    "1. 始终保留原始数据的备份",
    "2. 记录所有清洗步骤和决策理由",
    "3. 根据业务逻辑处理异常值，不要盲目删除",
    "4. 缺失值处理要考虑数据的分布和业务含义",
    "5. 验证清洗后数据的完整性和一致性",
    "6. 建立数据质量监控机制",
    "7. 文档化清洗过程，便于重现和审查"
]

for practice in best_practices:
    print(practice)

print("\n" + "=" * 60)
print("数据清洗教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试处理更复杂的缺失值模式")
print("2. 实现自定义的异常值检测算法")
print("3. 练习不同类型数据的格式化")
print("4. 建立数据质量评估指标")
print("5. 处理真实世界的脏数据集")