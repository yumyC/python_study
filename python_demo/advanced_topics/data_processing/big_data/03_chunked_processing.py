#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分块处理大文件教程

当数据文件太大无法一次性加载到内存时，需要使用分块处理技术。
本教程介绍各种分块处理方法和最佳实践。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import os
import time
from pathlib import Path
import sqlite3

print("=" * 60)
print("分块处理大文件教程")
print("=" * 60)

# 1. 创建大文件示例
print("\n1. 创建大文件示例")
print("-" * 30)

def create_large_csv(filename, num_rows=1000000):
    """创建大型 CSV 文件"""
    print(f"创建包含 {num_rows:,} 行的大文件: {filename}")
    
    # 分批写入以避免内存问题
    chunk_size = 100000
    
    with open(filename, 'w') as f:
        # 写入表头
        f.write('id,name,age,salary,department,date,value1,value2,category\n')
        
        for i in range(0, num_rows, chunk_size):
            current_chunk_size = min(chunk_size, num_rows - i)
            
            # 生成数据块
            ids = range(i, i + current_chunk_size)
            names = [f'Employee_{j}' for j in ids]
            ages = np.random.randint(22, 65, current_chunk_size)
            salaries = np.random.randint(30000, 150000, current_chunk_size)
            departments = np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], current_chunk_size)
            dates = pd.date_range('2020-01-01', periods=current_chunk_size, freq='D')
            values1 = np.random.randn(current_chunk_size)
            values2 = np.random.randn(current_chunk_size)
            categories = np.random.choice(['A', 'B', 'C'], current_chunk_size)
            
            # 写入数据
            for j in range(current_chunk_size):
                f.write(f'{ids[j]},{names[j]},{ages[j]},{salaries[j]},{departments[j]},'
                       f'{dates[j].strftime("%Y-%m-%d")},{values1[j]:.6f},{values2[j]:.6f},{categories[j]}\n')
    
    file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
    print(f"文件创建完成，大小: {file_size:.2f} MB")
    return filename

# 创建示例大文件
large_file = 'large_dataset.csv'
if not os.path.exists(large_file):
    create_large_csv(large_file, 500000)  # 50万行数据
else:
    print(f"使用现有文件: {large_file}")

# 2. 基本分块读取
print("\n\n2. 基本分块读取")
print("-" * 30)

def basic_chunked_reading(filename, chunk_size=10000):
    """基本的分块读取示例"""
    print(f"分块读取文件，每块 {chunk_size:,} 行")
    
    total_rows = 0
    total_salary = 0
    chunk_count = 0
    
    start_time = time.time()
    
    # 使用 pandas 分块读取
    for chunk in pd.read_csv(filename, chunksize=chunk_size):
        chunk_count += 1
        total_rows += len(chunk)
        total_salary += chunk['salary'].sum()
        
        if chunk_count <= 3:  # 只显示前3块的信息
            print(f"处理第 {chunk_count} 块: {len(chunk)} 行, "
                  f"平均薪资: {chunk['salary'].mean():.2f}")
    
    end_time = time.time()
    
    print(f"\n总计处理: {total_rows:,} 行")
    print(f"总薪资: ${total_salary:,}")
    print(f"平均薪资: ${total_salary/total_rows:.2f}")
    print(f"处理时间: {end_time - start_time:.2f} 秒")
    
    return total_rows, total_salary

# 执行基本分块读取
basic_chunked_reading(large_file)

# 3. 分块聚合计算
print("\n\n3. 分块聚合计算")
print("-" * 30)

def chunked_aggregation(filename, chunk_size=50000):
    """分块聚合计算示例"""
    print("执行分块聚合计算...")
    
    # 初始化聚合结果
    dept_stats = {}
    age_groups = {'20-30': 0, '31-40': 0, '41-50': 0, '50+': 0}
    total_count = 0
    
    start_time = time.time()
    
    for chunk_num, chunk in enumerate(pd.read_csv(filename, chunksize=chunk_size), 1):
        total_count += len(chunk)
        
        # 按部门聚合
        dept_agg = chunk.groupby('department').agg({
            'salary': ['sum', 'count', 'mean'],
            'age': 'mean'
        }).round(2)
        
        # 合并部门统计
        for dept in dept_agg.index:
            if dept not in dept_stats:
                dept_stats[dept] = {
                    'total_salary': 0,
                    'count': 0,
                    'salary_sum_for_avg': 0,
                    'age_sum_for_avg': 0
                }
            
            dept_stats[dept]['total_salary'] += dept_agg.loc[dept, ('salary', 'sum')]
            dept_stats[dept]['count'] += dept_agg.loc[dept, ('salary', 'count')]
            dept_stats[dept]['salary_sum_for_avg'] += dept_agg.loc[dept, ('salary', 'sum')]
            dept_stats[dept]['age_sum_for_avg'] += dept_agg.loc[dept, ('age', 'mean')] * dept_agg.loc[dept, ('salary', 'count')]
        
        # 年龄分组统计
        age_bins = pd.cut(chunk['age'], bins=[20, 30, 40, 50, 100], 
                         labels=['20-30', '31-40', '41-50', '50+'], right=False)
        age_counts = age_bins.value_counts()
        
        for age_group, count in age_counts.items():
            if age_group in age_groups:
                age_groups[age_group] += count
        
        if chunk_num % 5 == 0:
            print(f"已处理 {chunk_num} 个块，共 {total_count:,} 行")
    
    end_time = time.time()
    
    # 计算最终结果
    print(f"\n聚合结果（总计 {total_count:,} 行）:")
    print("\n按部门统计:")
    for dept, stats in dept_stats.items():
        avg_salary = stats['salary_sum_for_avg'] / stats['count']
        avg_age = stats['age_sum_for_avg'] / stats['count']
        print(f"  {dept}: {stats['count']:,} 人, "
              f"平均薪资: ${avg_salary:.2f}, 平均年龄: {avg_age:.1f}")
    
    print(f"\n按年龄组统计:")
    for age_group, count in age_groups.items():
        percentage = count / total_count * 100
        print(f"  {age_group}: {count:,} 人 ({percentage:.1f}%)")
    
    print(f"\n处理时间: {end_time - start_time:.2f} 秒")

# 执行分块聚合
chunked_aggregation(large_file)

# 4. 分块过滤和转换
print("\n\n4. 分块过滤和转换")
print("-" * 30)

def chunked_filter_transform(input_file, output_file, chunk_size=50000):
    """分块过滤和转换数据"""
    print(f"分块过滤和转换: {input_file} -> {output_file}")
    
    processed_rows = 0
    filtered_rows = 0
    
    # 创建输出文件并写入表头
    first_chunk = True
    
    start_time = time.time()
    
    for chunk in pd.read_csv(input_file, chunksize=chunk_size):
        processed_rows += len(chunk)
        
        # 数据转换
        chunk['salary_level'] = pd.cut(chunk['salary'], 
                                     bins=[0, 50000, 100000, float('inf')],
                                     labels=['Low', 'Medium', 'High'])
        
        chunk['age_group'] = pd.cut(chunk['age'],
                                  bins=[0, 30, 45, 65],
                                  labels=['Young', 'Middle', 'Senior'])
        
        # 添加计算列
        chunk['bonus'] = chunk['salary'] * 0.1
        chunk['total_compensation'] = chunk['salary'] + chunk['bonus']
        
        # 过滤条件：只保留薪资大于40000的记录
        filtered_chunk = chunk[chunk['salary'] > 40000]
        filtered_rows += len(filtered_chunk)
        
        # 选择需要的列
        output_columns = ['id', 'name', 'age', 'age_group', 'salary', 
                         'salary_level', 'department', 'bonus', 'total_compensation']
        filtered_chunk = filtered_chunk[output_columns]
        
        # 写入文件
        if first_chunk:
            filtered_chunk.to_csv(output_file, index=False)
            first_chunk = False
        else:
            filtered_chunk.to_csv(output_file, mode='a', header=False, index=False)
    
    end_time = time.time()
    
    print(f"处理完成:")
    print(f"  原始行数: {processed_rows:,}")
    print(f"  过滤后行数: {filtered_rows:,}")
    print(f"  过滤比例: {filtered_rows/processed_rows*100:.1f}%")
    print(f"  处理时间: {end_time - start_time:.2f} 秒")
    
    # 检查输出文件
    output_size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"  输出文件大小: {output_size:.2f} MB")

# 执行分块过滤转换
filtered_file = 'filtered_dataset.csv'
chunked_filter_transform(large_file, filtered_file)

# 5. 内存监控
print("\n\n5. 内存监控")
print("-" * 30)

import psutil
import gc

def monitor_memory_usage(func, *args, **kwargs):
    """监控函数执行时的内存使用"""
    process = psutil.Process()
    
    # 执行前内存
    gc.collect()  # 强制垃圾回收
    mem_before = process.memory_info().rss / (1024 * 1024)  # MB
    
    print(f"执行前内存使用: {mem_before:.2f} MB")
    
    # 执行函数
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    
    # 执行后内存
    mem_after = process.memory_info().rss / (1024 * 1024)  # MB
    mem_peak = mem_after  # 简化版，实际应该监控峰值
    
    print(f"执行后内存使用: {mem_after:.2f} MB")
    print(f"内存增长: {mem_after - mem_before:.2f} MB")
    print(f"执行时间: {end_time - start_time:.2f} 秒")
    
    return result

# 比较不同方法的内存使用
print("\n比较内存使用:")

def load_all_at_once(filename):
    """一次性加载所有数据"""
    df = pd.read_csv(filename)
    return df['salary'].mean()

def load_chunked(filename, chunk_size=50000):
    """分块加载数据"""
    total_salary = 0
    total_count = 0
    
    for chunk in pd.read_csv(filename, chunksize=chunk_size):
        total_salary += chunk['salary'].sum()
        total_count += len(chunk)
    
    return total_salary / total_count

print("\n一次性加载:")
try:
    monitor_memory_usage(load_all_at_once, large_file)
except MemoryError:
    print("内存不足，无法一次性加载")

print("\n分块加载:")
monitor_memory_usage(load_chunked, large_file)

# 6. 数据库分块处理
print("\n\n6. 数据库分块处理")
print("-" * 30)

def csv_to_database_chunked(csv_file, db_file, chunk_size=50000):
    """分块将 CSV 数据导入数据库"""
    print(f"分块导入数据到数据库: {db_file}")
    
    # 连接数据库
    conn = sqlite3.connect(db_file)
    
    # 创建表
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        salary REAL,
        department TEXT,
        date TEXT,
        value1 REAL,
        value2 REAL,
        category TEXT
    )
    '''
    conn.execute(create_table_sql)
    
    total_inserted = 0
    start_time = time.time()
    
    # 分块读取并插入
    for chunk_num, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunk_size), 1):
        # 插入数据库
        chunk.to_sql('employees', conn, if_exists='append', index=False)
        total_inserted += len(chunk)
        
        if chunk_num % 5 == 0:
            print(f"已插入 {total_inserted:,} 行")
    
    end_time = time.time()
    
    # 验证插入结果
    cursor = conn.execute("SELECT COUNT(*) FROM employees")
    db_count = cursor.fetchone()[0]
    
    print(f"导入完成:")
    print(f"  总插入行数: {total_inserted:,}")
    print(f"  数据库记录数: {db_count:,}")
    print(f"  导入时间: {end_time - start_time:.2f} 秒")
    
    conn.close()
    return db_count

# 执行数据库导入
db_file = 'employees.db'
if os.path.exists(db_file):
    os.remove(db_file)  # 删除旧数据库

csv_to_database_chunked(large_file, db_file)

# 7. 并行分块处理
print("\n\n7. 并行分块处理")
print("-" * 30)

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

def process_chunk_parallel(chunk_info):
    """并行处理单个数据块"""
    chunk_id, start_row, chunk_size, filename = chunk_info
    
    # 读取指定范围的数据
    chunk = pd.read_csv(filename, skiprows=range(1, start_row + 1), nrows=chunk_size)
    
    # 执行计算
    result = {
        'chunk_id': chunk_id,
        'row_count': len(chunk),
        'avg_salary': chunk['salary'].mean(),
        'max_salary': chunk['salary'].max(),
        'dept_counts': chunk['department'].value_counts().to_dict()
    }
    
    return result

def parallel_chunked_processing(filename, chunk_size=50000):
    """并行分块处理"""
    print("执行并行分块处理...")
    
    # 获取文件总行数
    with open(filename, 'r') as f:
        total_rows = sum(1 for line in f) - 1  # 减去表头
    
    # 创建块信息
    chunks_info = []
    for i in range(0, total_rows, chunk_size):
        chunk_id = i // chunk_size
        start_row = i
        actual_chunk_size = min(chunk_size, total_rows - i)
        chunks_info.append((chunk_id, start_row, actual_chunk_size, filename))
    
    print(f"总行数: {total_rows:,}, 分为 {len(chunks_info)} 个块")
    
    # 并行处理
    start_time = time.time()
    results = []
    
    # 使用进程池
    max_workers = min(multiprocessing.cpu_count(), len(chunks_info))
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务
        future_to_chunk = {executor.submit(process_chunk_parallel, chunk_info): chunk_info 
                          for chunk_info in chunks_info}
        
        # 收集结果
        for future in as_completed(future_to_chunk):
            try:
                result = future.result()
                results.append(result)
                print(f"完成块 {result['chunk_id']}: {result['row_count']} 行")
            except Exception as e:
                print(f"处理块时出错: {e}")
    
    end_time = time.time()
    
    # 汇总结果
    total_processed = sum(r['row_count'] for r in results)
    avg_salary_overall = sum(r['avg_salary'] * r['row_count'] for r in results) / total_processed
    max_salary_overall = max(r['max_salary'] for r in results)
    
    print(f"\n并行处理结果:")
    print(f"  处理行数: {total_processed:,}")
    print(f"  平均薪资: ${avg_salary_overall:.2f}")
    print(f"  最高薪资: ${max_salary_overall:.2f}")
    print(f"  处理时间: {end_time - start_time:.2f} 秒")
    print(f"  使用进程数: {max_workers}")

# 执行并行处理（注意：这可能需要较长时间）
try:
    parallel_chunked_processing(large_file, chunk_size=100000)
except Exception as e:
    print(f"并行处理失败: {e}")
    print("可能是由于文件大小或系统限制")

# 8. 最佳实践总结
print("\n\n8. 最佳实践总结")
print("-" * 30)

best_practices = [
    "1. 根据可用内存选择合适的块大小",
    "2. 使用生成器避免一次性加载所有数据",
    "3. 对于聚合操作，在每个块中进行部分计算",
    "4. 使用数据库存储中间结果",
    "5. 监控内存使用情况",
    "6. 考虑使用并行处理加速计算",
    "7. 选择合适的文件格式（Parquet vs CSV）",
    "8. 实现进度监控和错误处理"
]

for practice in best_practices:
    print(practice)

# 9. 性能优化技巧
print("\n\n9. 性能优化技巧")
print("-" * 30)

def optimized_chunked_processing(filename, chunk_size=50000):
    """优化的分块处理"""
    print("执行优化的分块处理...")
    
    # 预先指定数据类型以提高性能
    dtypes = {
        'id': 'int32',
        'name': 'string',
        'age': 'int8',
        'salary': 'int32',
        'department': 'category',
        'value1': 'float32',
        'value2': 'float32',
        'category': 'category'
    }
    
    # 只读取需要的列
    usecols = ['id', 'age', 'salary', 'department']
    
    start_time = time.time()
    
    results = []
    for chunk in pd.read_csv(filename, chunksize=chunk_size, 
                           dtype=dtypes, usecols=usecols):
        # 使用向量化操作
        dept_stats = chunk.groupby('department', observed=True).agg({
            'salary': ['mean', 'count']
        })
        results.append(dept_stats)
    
    # 合并结果
    final_result = pd.concat(results).groupby(level=0).sum()
    
    end_time = time.time()
    
    print(f"优化处理完成，耗时: {end_time - start_time:.2f} 秒")
    print("部门统计结果:")
    print(final_result)

# 执行优化处理
optimized_chunked_processing(large_file)

# 清理临时文件
print("\n\n清理临时文件...")
temp_files = [large_file, filtered_file, db_file]
for file in temp_files:
    if os.path.exists(file):
        os.remove(file)
        print(f"已删除: {file}")

print("\n" + "=" * 60)
print("分块处理大文件教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试处理更大的数据文件（GB 级别）")
print("2. 实现自定义的分块处理框架")
print("3. 比较不同块大小对性能的影响")
print("4. 学习使用 Dask 进行自动分块处理")
print("5. 实现分布式分块处理系统")