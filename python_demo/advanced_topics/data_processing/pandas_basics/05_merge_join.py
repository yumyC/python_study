#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas 数据合并和连接教程

数据合并是数据分析中的重要技能，包括 merge、join、concat 等操作。
本教程详细介绍各种数据合并技术和实际应用场景。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np

print("=" * 60)
print("Pandas 数据合并和连接教程")
print("=" * 60)

# 1. 创建示例数据
print("\n1. 创建示例数据")
print("-" * 30)

# 员工基本信息
employees = pd.DataFrame({
    'emp_id': [1, 2, 3, 4, 5],
    'name': ['张三', '李四', '王五', '赵六', '钱七'],
    'department_id': [101, 102, 101, 103, 102],
    'hire_date': pd.to_datetime(['2020-01-15', '2019-03-20', '2021-07-10', 
                                '2018-12-05', '2022-02-28'])
})

# 部门信息
departments = pd.DataFrame({
    'dept_id': [101, 102, 103, 104],
    'dept_name': ['IT部', '人事部', '财务部', '市场部'],
    'manager': ['张经理', '李经理', '王经理', '赵经理'],
    'budget': [1000000, 500000, 800000, 600000]
})

# 薪资信息
salaries = pd.DataFrame({
    'employee_id': [1, 2, 3, 4, 6],  # 注意：包含不存在的员工ID 6
    'base_salary': [8000, 6000, 9000, 7000, 8500],
    'bonus': [800, 600, 900, 700, 850],
    'year': [2024, 2024, 2024, 2024, 2024]
})

# 项目信息
projects = pd.DataFrame({
    'project_id': ['P001', 'P002', 'P003'],
    'project_name': ['网站重构', '移动应用', '数据分析'],
    'start_date': pd.to_datetime(['2024-01-01', '2024-02-15', '2024-03-01']),
    'budget': [500000, 300000, 200000]
})

# 员工项目分配
emp_projects = pd.DataFrame({
    'emp_id': [1, 1, 2, 3, 4, 5],
    'project_id': ['P001', 'P002', 'P001', 'P003', 'P002', 'P003'],
    'role': ['开发', '测试', '开发', '分析师', '项目经理', '分析师'],
    'allocation': [0.8, 0.2, 1.0, 0.6, 0.4, 1.0]
})

print("员工信息:")
print(employees)
print("\n部门信息:")
print(departments)
print("\n薪资信息:")
print(salaries)
print("\n项目信息:")
print(projects)
print("\n员工项目分配:")
print(emp_projects)

# 2. 基本 merge 操作
print("\n\n2. 基本 merge 操作")
print("-" * 30)

# 内连接 (inner join) - 默认
inner_merge = pd.merge(employees, departments, 
                      left_on='department_id', right_on='dept_id')
print("内连接 - 员工和部门:")
print(inner_merge)

# 左连接 (left join)
left_merge = pd.merge(employees, departments, 
                     left_on='department_id', right_on='dept_id', how='left')
print("\n左连接 - 保留所有员工:")
print(left_merge)

# 右连接 (right join)
right_merge = pd.merge(employees, departments, 
                      left_on='department_id', right_on='dept_id', how='right')
print("\n右连接 - 保留所有部门:")
print(right_merge)

# 外连接 (outer join)
outer_merge = pd.merge(employees, departments, 
                      left_on='department_id', right_on='dept_id', how='outer')
print("\n外连接 - 保留所有记录:")
print(outer_merge)

# 3. 处理重复列名
print("\n\n3. 处理重复列名")
print("-" * 30)

# 使用 suffixes 参数
merge_with_suffix = pd.merge(employees, salaries, 
                           left_on='emp_id', right_on='employee_id',
                           suffixes=('_emp', '_sal'))
print("使用后缀处理重复列名:")
print(merge_with_suffix)

# 4. 多列连接
print("\n\n4. 多列连接")
print("-" * 30)

# 创建包含多个键的数据
sales_data = pd.DataFrame({
    'year': [2023, 2023, 2024, 2024],
    'quarter': [1, 2, 1, 2],
    'region': ['北京', '上海', '北京', '上海'],
    'sales': [1000, 1200, 1100, 1300]
})

targets = pd.DataFrame({
    'year': [2023, 2023, 2024, 2024],
    'quarter': [1, 2, 1, 2],
    'region': ['北京', '上海', '北京', '上海'],
    'target': [950, 1150, 1050, 1250]
})

multi_key_merge = pd.merge(sales_data, targets, on=['year', 'quarter', 'region'])
print("多列连接:")
print(multi_key_merge)

# 5. 索引连接
print("\n\n5. 索引连接")
print("-" * 30)

# 设置索引
emp_indexed = employees.set_index('emp_id')
sal_indexed = salaries.set_index('employee_id')

# 基于索引连接
index_merge = pd.merge(emp_indexed, sal_indexed, left_index=True, right_index=True, how='left')
print("基于索引的连接:")
print(index_merge)

# 6. join 方法
print("\n\n6. join 方法")
print("-" * 30)

# join 是基于索引的简化连接方法
joined = emp_indexed.join(sal_indexed, how='left', rsuffix='_sal')
print("使用 join 方法:")
print(joined)

# 7. concat 操作
print("\n\n7. concat 操作")
print("-" * 30)

# 垂直拼接
emp1 = employees.iloc[:3]
emp2 = employees.iloc[3:]

vertical_concat = pd.concat([emp1, emp2], ignore_index=True)
print("垂直拼接:")
print(vertical_concat)

# 水平拼接
emp_basic = employees[['emp_id', 'name']]
emp_details = employees[['emp_id', 'department_id', 'hire_date']]

horizontal_concat = pd.concat([emp_basic, emp_details.drop('emp_id', axis=1)], axis=1)
print("\n水平拼接:")
print(horizontal_concat)

# 8. 复杂的多表连接
print("\n\n8. 复杂的多表连接")
print("-" * 30)

# 连接员工、部门和薪资信息
step1 = pd.merge(employees, departments, 
                left_on='department_id', right_on='dept_id', how='left')
step2 = pd.merge(step1, salaries, 
                left_on='emp_id', right_on='employee_id', how='left')

# 清理列名
complete_info = step2.drop(['dept_id', 'employee_id'], axis=1)
print("完整的员工信息:")
print(complete_info)

# 9. 一对多和多对多连接
print("\n\n9. 一对多和多对多连接")
print("-" * 30)

# 一对多：一个员工对应多个项目
emp_project_info = pd.merge(employees, emp_projects, on='emp_id', how='inner')
print("员工项目分配（一对多）:")
print(emp_project_info)

# 多对多：员工-项目-项目详情
full_project_info = pd.merge(emp_project_info, projects, on='project_id', how='left')
print("\n完整项目信息（多对多）:")
print(full_project_info[['name', 'project_name', 'role', 'allocation', 'budget']])

# 10. 处理缺失值的连接
print("\n\n10. 处理缺失值的连接")
print("-" * 30)

# 创建包含缺失值的数据
incomplete_data = pd.DataFrame({
    'id': [1, 2, 3, None, 5],
    'value': ['A', 'B', 'C', 'D', 'E']
})

reference_data = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'description': ['First', 'Second', 'Third', 'Fourth']
})

# 连接时处理缺失值
merge_with_na = pd.merge(incomplete_data, reference_data, on='id', how='left')
print("包含缺失值的连接:")
print(merge_with_na)

# 11. 条件连接
print("\n\n11. 条件连接")
print("-" * 30)

# 使用 merge_asof 进行时间序列连接
dates1 = pd.DataFrame({
    'date': pd.to_datetime(['2024-01-01', '2024-01-03', '2024-01-05']),
    'value1': [10, 20, 30]
})

dates2 = pd.DataFrame({
    'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-04', '2024-01-06']),
    'value2': [100, 200, 300, 400]
})

# 向后查找最近的匹配
asof_merge = pd.merge_asof(dates1, dates2, on='date')
print("时间序列向后连接:")
print(asof_merge)

# 12. 性能优化技巧
print("\n\n12. 性能优化技巧")
print("-" * 30)

# 对于大数据集，预先排序可以提高性能
large_df1 = pd.DataFrame({
    'key': np.random.randint(1, 1000, 10000),
    'value1': np.random.randn(10000)
}).sort_values('key')

large_df2 = pd.DataFrame({
    'key': np.random.randint(1, 1000, 5000),
    'value2': np.random.randn(5000)
}).sort_values('key')

print("大数据集连接示例（已排序）:")
print(f"DataFrame 1 形状: {large_df1.shape}")
print(f"DataFrame 2 形状: {large_df2.shape}")

# 执行连接
large_merge = pd.merge(large_df1, large_df2, on='key', how='inner')
print(f"连接结果形状: {large_merge.shape}")

# 13. 实际业务场景
print("\n\n13. 实际业务场景")
print("-" * 30)

# 场景1: 销售分析报告
def create_sales_report():
    """创建销售分析报告"""
    # 模拟销售数据
    sales = pd.DataFrame({
        'order_id': range(1, 11),
        'customer_id': [1, 2, 1, 3, 2, 4, 3, 1, 4, 2],
        'product_id': [101, 102, 103, 101, 102, 103, 101, 102, 103, 101],
        'quantity': [2, 1, 3, 1, 2, 1, 4, 1, 2, 3],
        'order_date': pd.date_range('2024-01-01', periods=10, freq='D')
    })
    
    customers = pd.DataFrame({
        'customer_id': [1, 2, 3, 4],
        'customer_name': ['客户A', '客户B', '客户C', '客户D'],
        'city': ['北京', '上海', '广州', '深圳']
    })
    
    products = pd.DataFrame({
        'product_id': [101, 102, 103],
        'product_name': ['笔记本', '手机', '平板'],
        'price': [5000, 3000, 2000],
        'category': ['电脑', '通讯', '电脑']
    })
    
    # 多表连接创建完整报告
    report = sales.merge(customers, on='customer_id') \
                 .merge(products, on='product_id')
    
    report['total_amount'] = report['quantity'] * report['price']
    
    return report

sales_report = create_sales_report()
print("销售报告:")
print(sales_report[['customer_name', 'product_name', 'quantity', 'price', 'total_amount']])

# 场景2: 员工绩效分析
def analyze_employee_performance():
    """分析员工绩效"""
    # 连接所有相关信息
    performance_data = employees.merge(departments, left_on='department_id', right_on='dept_id', how='left') \
                               .merge(salaries, left_on='emp_id', right_on='employee_id', how='left')
    
    # 计算项目参与情况
    project_stats = emp_projects.groupby('emp_id').agg({
        'project_id': 'count',
        'allocation': 'sum'
    }).rename(columns={'project_id': 'project_count', 'allocation': 'total_allocation'})
    
    # 合并项目统计
    final_analysis = performance_data.merge(project_stats, left_on='emp_id', right_index=True, how='left')
    
    # 填充缺失值
    final_analysis['project_count'] = final_analysis['project_count'].fillna(0)
    final_analysis['total_allocation'] = final_analysis['total_allocation'].fillna(0)
    
    return final_analysis[['name', 'dept_name', 'base_salary', 'bonus', 'project_count', 'total_allocation']]

performance_analysis = analyze_employee_performance()
print("\n员工绩效分析:")
print(performance_analysis)

# 14. 连接验证和质量检查
print("\n\n14. 连接验证和质量检查")
print("-" * 30)

def validate_merge(left_df, right_df, merge_result, left_key, right_key):
    """验证连接结果的质量"""
    print(f"左表记录数: {len(left_df)}")
    print(f"右表记录数: {len(right_df)}")
    print(f"连接结果记录数: {len(merge_result)}")
    
    # 检查键的唯一性
    left_unique = left_df[left_key].nunique()
    right_unique = right_df[right_key].nunique()
    print(f"左表键唯一值数: {left_unique}")
    print(f"右表键唯一值数: {right_unique}")
    
    # 检查匹配情况
    matched_keys = set(left_df[left_key]) & set(right_df[right_key])
    print(f"匹配的键数量: {len(matched_keys)}")
    
    return {
        'left_records': len(left_df),
        'right_records': len(right_df),
        'result_records': len(merge_result),
        'matched_keys': len(matched_keys)
    }

# 验证员工和部门的连接
validation_result = validate_merge(employees, departments, inner_merge, 
                                 'department_id', 'dept_id')

print("\n" + "=" * 60)
print("数据合并和连接教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试更复杂的多表连接场景")
print("2. 练习处理不同数据类型的键连接")
print("3. 实现自定义的连接验证函数")
print("4. 处理大数据集的连接性能优化")
print("5. 创建完整的数据仓库连接流程")