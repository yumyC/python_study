#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内存优化技巧教程

在处理大数据时，内存优化是关键技能。本教程介绍各种内存优化技术，
包括数据类型优化、内存监控、垃圾回收等。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import psutil
import gc
import sys
import time
from memory_profiler import profile
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("内存优化技巧教程")
print("=" * 60)

# 1. 内存监控工具
print("\n1. 内存监控工具")
print("-" * 30)

def get_memory_usage():
    """获取当前内存使用情况"""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        'rss': memory_info.rss / (1024 * 1024),  # 物理内存 MB
        'vms': memory_info.vms / (1024 * 1024),  # 虚拟内存 MB
        'percent': process.memory_percent()       # 内存使用百分比
    }

def print_memory_usage(label=""):
    """打印内存使用情况"""
    mem = get_memory_usage()
    print(f"{label} - 物理内存: {mem['rss']:.2f} MB, "
          f"虚拟内存: {mem['vms']:.2f} MB, "
          f"使用率: {mem['percent']:.2f}%")

def memory_usage_decorator(func):
    """内存使用监控装饰器"""
    def wrapper(*args, **kwargs):
        print(f"\n执行函数: {func.__name__}")
        print_memory_usage("执行前")
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print_memory_usage("执行后")
        print(f"执行时间: {end_time - start_time:.2f} 秒")
        return result
    return wrapper

# 显示初始内存状态
print_memory_usage("初始状态")

# 2. 数据类型优化
print("\n\n2. 数据类型优化")
print("-" * 30)

@memory_usage_decorator
def demonstrate_dtype_optimization():
    """演示数据类型优化"""
    
    # 创建示例数据
    n_rows = 1000000
    
    print(f"创建 {n_rows:,} 行数据进行优化演示")
    
    # 原始数据类型（默认）
    data_original = pd.DataFrame({
        'id': range(n_rows),                                    # int64
        'age': np.random.randint(18, 80, n_rows),              # int64
        'salary': np.random.randint(30000, 150000, n_rows),    # int64
        'score': np.random.random(n_rows),                     # float64
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], n_rows),  # object
        'active': np.random.choice([True, False], n_rows)      # bool
    })
    
    print("\n原始数据类型和内存使用:")
    print(data_original.dtypes)
    original_memory = data_original.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"总内存使用: {original_memory:.2f} MB")
    
    # 优化数据类型
    data_optimized = data_original.copy()
    
    # 整数类型优化
    data_optimized['id'] = data_optimized['id'].astype('uint32')        # 0 到 4B
    data_optimized['age'] = data_optimized['age'].astype('uint8')       # 0 到 255
    data_optimized['salary'] = data_optimized['salary'].astype('uint32') # 0 到 4B
    
    # 浮点数类型优化
    data_optimized['score'] = data_optimized['score'].astype('float32')
    
    # 分类数据优化
    data_optimized['department'] = data_optimized['department'].astype('category')
    
    print("\n优化后数据类型和内存使用:")
    print(data_optimized.dtypes)
    optimized_memory = data_optimized.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"总内存使用: {optimized_memory:.2f} MB")
    
    # 计算节省的内存
    memory_saved = original_memory - optimized_memory
    percentage_saved = (memory_saved / original_memory) * 100
    
    print(f"\n内存优化结果:")
    print(f"节省内存: {memory_saved:.2f} MB")
    print(f"节省比例: {percentage_saved:.1f}%")
    
    return data_original, data_optimized

# 执行数据类型优化演示
original_df, optimized_df = demonstrate_dtype_optimization()

# 3. 自动数据类型优化
print("\n\n3. 自动数据类型优化")
print("-" * 30)

def optimize_dtypes(df):
    """自动优化 DataFrame 的数据类型"""
    optimized_df = df.copy()
    
    for col in optimized_df.columns:
        col_type = optimized_df[col].dtype
        
        if col_type != 'object':
            # 数值类型优化
            if str(col_type).startswith('int'):
                # 整数类型优化
                min_val = optimized_df[col].min()
                max_val = optimized_df[col].max()
                
                if min_val >= 0:
                    # 无符号整数
                    if max_val < 255:
                        optimized_df[col] = optimized_df[col].astype('uint8')
                    elif max_val < 65535:
                        optimized_df[col] = optimized_df[col].astype('uint16')
                    elif max_val < 4294967295:
                        optimized_df[col] = optimized_df[col].astype('uint32')
                else:
                    # 有符号整数
                    if min_val > -128 and max_val < 127:
                        optimized_df[col] = optimized_df[col].astype('int8')
                    elif min_val > -32768 and max_val < 32767:
                        optimized_df[col] = optimized_df[col].astype('int16')
                    elif min_val > -2147483648 and max_val < 2147483647:
                        optimized_df[col] = optimized_df[col].astype('int32')
            
            elif str(col_type).startswith('float'):
                # 浮点数类型优化
                optimized_df[col] = optimized_df[col].astype('float32')
        
        else:
            # 字符串类型优化
            unique_count = optimized_df[col].nunique()
            total_count = len(optimized_df[col])
            
            # 如果唯一值比例小于50%，转换为分类类型
            if unique_count / total_count < 0.5:
                optimized_df[col] = optimized_df[col].astype('category')
    
    return optimized_df

# 测试自动优化
print("自动数据类型优化:")
auto_optimized = optimize_dtypes(original_df)

original_memory = original_df.memory_usage(deep=True).sum() / (1024 * 1024)
auto_memory = auto_optimized.memory_usage(deep=True).sum() / (1024 * 1024)

print(f"原始内存: {original_memory:.2f} MB")
print(f"自动优化后: {auto_memory:.2f} MB")
print(f"节省: {((original_memory - auto_memory) / original_memory * 100):.1f}%")

# 4. 内存使用分析
print("\n\n4. 内存使用分析")
print("-" * 30)

def analyze_memory_usage(df, name="DataFrame"):
    """分析 DataFrame 的内存使用情况"""
    print(f"\n{name} 内存使用分析:")
    
    # 总体内存使用
    total_memory = df.memory_usage(deep=True).sum()
    print(f"总内存使用: {total_memory / (1024 * 1024):.2f} MB")
    
    # 按列分析
    print("\n各列内存使用:")
    memory_by_column = df.memory_usage(deep=True)
    for col, memory in memory_by_column.items():
        if col != 'Index':
            percentage = (memory / total_memory) * 100
            print(f"  {col:12}: {memory / (1024 * 1024):6.2f} MB ({percentage:5.1f}%)")
    
    # 按数据类型分析
    print("\n按数据类型分组:")
    dtype_memory = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        col_memory = df[col].memory_usage(deep=True)
        if dtype in dtype_memory:
            dtype_memory[dtype] += col_memory
        else:
            dtype_memory[dtype] = col_memory
    
    for dtype, memory in sorted(dtype_memory.items(), key=lambda x: x[1], reverse=True):
        percentage = (memory / total_memory) * 100
        print(f"  {dtype:12}: {memory / (1024 * 1024):6.2f} MB ({percentage:5.1f}%)")

# 分析原始和优化后的内存使用
analyze_memory_usage(original_df, "原始数据")
analyze_memory_usage(optimized_df, "优化数据")

# 5. 垃圾回收优化
print("\n\n5. 垃圾回收优化")
print("-" * 30)

@memory_usage_decorator
def demonstrate_garbage_collection():
    """演示垃圾回收的重要性"""
    
    print("创建大量临时对象...")
    
    # 创建大量临时 DataFrame
    temp_dfs = []
    for i in range(10):
        temp_df = pd.DataFrame(np.random.randn(100000, 10))
        temp_dfs.append(temp_df)
        
        if i % 3 == 0:
            print_memory_usage(f"创建第 {i+1} 个 DataFrame")
    
    print_memory_usage("创建完成，垃圾回收前")
    
    # 删除引用
    del temp_dfs
    
    print_memory_usage("删除引用后，强制垃圾回收前")
    
    # 强制垃圾回收
    collected = gc.collect()
    print(f"垃圾回收清理了 {collected} 个对象")
    
    print_memory_usage("强制垃圾回收后")

# 执行垃圾回收演示
demonstrate_garbage_collection()

# 6. 内存映射文件
print("\n\n6. 内存映射文件")
print("-" * 30)

def create_large_array_file(filename, shape=(10000, 1000)):
    """创建大型数组文件"""
    print(f"创建大型数组文件: {filename}")
    
    # 创建并保存大型数组
    large_array = np.random.randn(*shape).astype(np.float32)
    np.save(filename, large_array)
    
    file_size = os.path.getsize(filename + '.npy') / (1024 * 1024)
    print(f"文件大小: {file_size:.2f} MB")
    
    return filename + '.npy'

@memory_usage_decorator
def compare_loading_methods(filename):
    """比较不同的数组加载方法"""
    
    print("\n方法1: 直接加载到内存")
    array_loaded = np.load(filename)
    print(f"数组形状: {array_loaded.shape}")
    print(f"数组大小: {array_loaded.nbytes / (1024 * 1024):.2f} MB")
    
    # 执行一些计算
    result1 = np.mean(array_loaded)
    print(f"平均值: {result1:.6f}")
    
    del array_loaded
    gc.collect()
    
    print("\n方法2: 内存映射")
    array_mapped = np.load(filename, mmap_mode='r')
    print(f"映射数组形状: {array_mapped.shape}")
    
    # 执行相同计算
    result2 = np.mean(array_mapped)
    print(f"平均值: {result2:.6f}")
    
    del array_mapped

# 创建并比较加载方法
import os
array_file = create_large_array_file('large_array')
compare_loading_methods(array_file)

# 7. 分块计算优化
print("\n\n7. 分块计算优化")
print("-" * 30)

@memory_usage_decorator
def chunked_computation_demo():
    """演示分块计算的内存优势"""
    
    n_rows = 1000000
    
    print(f"处理 {n_rows:,} 行数据的统计计算")
    
    # 方法1: 一次性计算
    print("\n方法1: 一次性加载和计算")
    large_df = pd.DataFrame({
        'value1': np.random.randn(n_rows),
        'value2': np.random.randn(n_rows),
        'group': np.random.choice(['A', 'B', 'C', 'D'], n_rows)
    })
    
    result1 = large_df.groupby('group').agg({
        'value1': ['mean', 'std'],
        'value2': ['mean', 'std']
    })
    
    print("一次性计算结果:")
    print(result1)
    
    del large_df
    gc.collect()
    
    print("\n方法2: 分块计算")
    
    # 分块计算聚合结果
    chunk_size = 100000
    chunk_results = []
    
    for i in range(0, n_rows, chunk_size):
        current_size = min(chunk_size, n_rows - i)
        
        chunk_df = pd.DataFrame({
            'value1': np.random.randn(current_size),
            'value2': np.random.randn(current_size),
            'group': np.random.choice(['A', 'B', 'C', 'D'], current_size)
        })
        
        # 计算块级统计
        chunk_stats = chunk_df.groupby('group').agg({
            'value1': ['sum', 'count', 'mean'],
            'value2': ['sum', 'count', 'mean']
        })
        
        chunk_results.append(chunk_stats)
        
        del chunk_df  # 立即删除块数据
    
    # 合并块结果
    combined_stats = pd.concat(chunk_results).groupby(level=0).sum()
    
    print("分块计算结果:")
    print(combined_stats)

# 执行分块计算演示
chunked_computation_demo()

# 8. 内存泄漏检测
print("\n\n8. 内存泄漏检测")
print("-" * 30)

def detect_memory_leaks():
    """检测潜在的内存泄漏"""
    
    print("内存泄漏检测示例:")
    
    # 记录初始内存
    initial_memory = get_memory_usage()['rss']
    
    # 模拟可能导致内存泄漏的操作
    leaked_objects = []
    
    for i in range(5):
        # 创建大对象但不正确清理
        large_data = pd.DataFrame(np.random.randn(50000, 20))
        
        # 模拟循环引用（可能导致内存泄漏）
        large_data.circular_ref = large_data
        
        leaked_objects.append(large_data)
        
        current_memory = get_memory_usage()['rss']
        memory_increase = current_memory - initial_memory
        
        print(f"迭代 {i+1}: 内存增长 {memory_increase:.2f} MB")
    
    print(f"\n清理前总内存增长: {get_memory_usage()['rss'] - initial_memory:.2f} MB")
    
    # 正确清理
    for obj in leaked_objects:
        if hasattr(obj, 'circular_ref'):
            delattr(obj, 'circular_ref')  # 打破循环引用
    
    del leaked_objects
    gc.collect()
    
    final_memory = get_memory_usage()['rss']
    print(f"清理后内存: {final_memory - initial_memory:.2f} MB")

# 执行内存泄漏检测
detect_memory_leaks()

# 9. 最佳实践总结
print("\n\n9. 最佳实践总结")
print("-" * 30)

best_practices = [
    "内存优化最佳实践:",
    "",
    "1. 数据类型优化:",
    "   - 使用最小的数据类型",
    "   - 将重复字符串转换为 category 类型",
    "   - 使用 float32 而不是 float64（如果精度允许）",
    "",
    "2. 内存管理:",
    "   - 及时删除不需要的变量",
    "   - 使用 del 语句和 gc.collect()",
    "   - 避免循环引用",
    "",
    "3. 分块处理:",
    "   - 对大数据集使用分块读取",
    "   - 实现流式处理",
    "   - 使用生成器而不是列表",
    "",
    "4. 监控和调试:",
    "   - 定期监控内存使用",
    "   - 使用内存分析工具",
    "   - 实现内存使用警告",
    "",
    "5. 高级技术:",
    "   - 使用内存映射文件",
    "   - 考虑使用 Dask 或 Polars",
    "   - 利用数据库进行大数据处理"
]

for practice in best_practices:
    print(practice)

# 10. 内存优化工具函数
print("\n\n10. 内存优化工具函数")
print("-" * 30)

class MemoryOptimizer:
    """内存优化工具类"""
    
    @staticmethod
    def optimize_dataframe(df, aggressive=False):
        """优化 DataFrame 的内存使用"""
        optimized_df = df.copy()
        
        print(f"优化前内存使用: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
        
        for col in optimized_df.columns:
            col_type = optimized_df[col].dtype
            
            if str(col_type) == 'object':
                # 尝试转换为数值类型
                try:
                    optimized_df[col] = pd.to_numeric(optimized_df[col])
                    continue
                except:
                    pass
                
                # 检查是否适合转换为分类类型
                unique_ratio = optimized_df[col].nunique() / len(optimized_df[col])
                if unique_ratio < 0.5 or aggressive:
                    optimized_df[col] = optimized_df[col].astype('category')
            
            elif 'int' in str(col_type):
                # 整数优化
                min_val = optimized_df[col].min()
                max_val = optimized_df[col].max()
                
                if min_val >= 0:
                    if max_val < 255:
                        optimized_df[col] = optimized_df[col].astype('uint8')
                    elif max_val < 65535:
                        optimized_df[col] = optimized_df[col].astype('uint16')
                    elif max_val < 4294967295:
                        optimized_df[col] = optimized_df[col].astype('uint32')
                else:
                    if min_val > -128 and max_val < 127:
                        optimized_df[col] = optimized_df[col].astype('int8')
                    elif min_val > -32768 and max_val < 32767:
                        optimized_df[col] = optimized_df[col].astype('int16')
                    elif min_val > -2147483648 and max_val < 2147483647:
                        optimized_df[col] = optimized_df[col].astype('int32')
            
            elif 'float' in str(col_type):
                # 浮点数优化
                if aggressive or col_type == 'float64':
                    optimized_df[col] = optimized_df[col].astype('float32')
        
        print(f"优化后内存使用: {optimized_df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
        
        return optimized_df
    
    @staticmethod
    def memory_report(df):
        """生成内存使用报告"""
        print("\n=== 内存使用报告 ===")
        
        total_memory = df.memory_usage(deep=True).sum()
        print(f"总内存使用: {total_memory / (1024**2):.2f} MB")
        print(f"行数: {len(df):,}")
        print(f"列数: {len(df.columns)}")
        print(f"平均每行内存: {total_memory / len(df):.2f} bytes")
        
        print("\n各列内存使用:")
        for col in df.columns:
            col_memory = df[col].memory_usage(deep=True)
            percentage = (col_memory / total_memory) * 100
            print(f"  {col:15}: {col_memory / (1024**2):6.2f} MB ({percentage:5.1f}%) - {df[col].dtype}")

# 使用内存优化工具
print("\n使用内存优化工具:")
optimizer = MemoryOptimizer()

# 创建测试数据
test_df = pd.DataFrame({
    'id': range(100000),
    'category': np.random.choice(['A', 'B', 'C'], 100000),
    'value': np.random.randn(100000),
    'flag': np.random.choice([True, False], 100000)
})

# 生成报告
optimizer.memory_report(test_df)

# 优化数据
optimized_test_df = optimizer.optimize_dataframe(test_df)

# 清理临时文件
if os.path.exists(array_file):
    os.remove(array_file)

print("\n" + "=" * 60)
print("内存优化技巧教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 在实际项目中应用内存优化技术")
print("2. 开发自动化的内存优化工具")
print("3. 学习使用专业的内存分析工具")
print("4. 实践大数据集的内存管理")
print("5. 研究不同数据格式的内存效率")