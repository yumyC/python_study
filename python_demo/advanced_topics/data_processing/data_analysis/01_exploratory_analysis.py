#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探索性数据分析 (EDA) 教程

探索性数据分析是数据科学项目的重要第一步，帮助理解数据的结构、
分布、关系和异常。本教程介绍系统性的 EDA 方法和技术。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8')

print("=" * 60)
print("探索性数据分析 (EDA) 教程")
print("=" * 60)

# 1. 创建示例数据集
print("\n1. 创建示例数据集")
print("-" * 30)

def create_sample_dataset():
    """创建用于 EDA 演示的示例数据集"""
    np.random.seed(42)
    
    n_samples = 1000
    
    # 基础数据
    data = {
        'customer_id': range(1, n_samples + 1),
        'age': np.random.normal(35, 12, n_samples).astype(int),
        'income': np.random.lognormal(10.5, 0.5, n_samples),
        'education': np.random.choice(['高中', '本科', '硕士', '博士'], n_samples, p=[0.3, 0.5, 0.15, 0.05]),
        'city_tier': np.random.choice([1, 2, 3], n_samples, p=[0.2, 0.3, 0.5]),
        'gender': np.random.choice(['男', '女'], n_samples, p=[0.52, 0.48]),
        'marital_status': np.random.choice(['单身', '已婚', '离异'], n_samples, p=[0.3, 0.6, 0.1]),
        'purchase_amount': np.random.exponential(500, n_samples),
        'purchase_frequency': np.random.poisson(3, n_samples),
        'satisfaction_score': np.random.normal(7.5, 1.5, n_samples),
        'days_since_last_purchase': np.random.exponential(30, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # 数据清理和调整
    df['age'] = np.clip(df['age'], 18, 80)
    df['income'] = np.clip(df['income'], 20000, 500000)
    df['satisfaction_score'] = np.clip(df['satisfaction_score'], 1, 10)
    df['purchase_amount'] = np.clip(df['purchase_amount'], 0, 5000)
    df['days_since_last_purchase'] = np.clip(df['days_since_last_purchase'], 0, 365)
    
    # 添加一些相关性
    df.loc[df['education'] == '博士', 'income'] *= 1.5
    df.loc[df['city_tier'] == 1, 'income'] *= 1.3
    df.loc[df['income'] > df['income'].quantile(0.8), 'purchase_amount'] *= 1.4
    
    # 引入一些缺失值
    missing_indices = np.random.choice(df.index, size=50, replace=False)
    df.loc[missing_indices, 'satisfaction_score'] = np.nan
    
    # 引入一些异常值
    outlier_indices = np.random.choice(df.index, size=20, replace=False)
    df.loc[outlier_indices, 'purchase_amount'] *= 5
    
    return df

# 创建数据集
df = create_sample_dataset()
print(f"数据集创建完成，包含 {len(df)} 行，{len(df.columns)} 列")
print("\n数据集预览:")
print(df.head())

# 2. 数据概览
print("\n\n2. 数据概览")
print("-" * 30)

def data_overview(df):
    """数据集基本概览"""
    print("=== 数据集基本信息 ===")
    print(f"数据形状: {df.shape}")
    print(f"内存使用: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\n=== 数据类型 ===")
    print(df.dtypes)
    
    print("\n=== 缺失值统计 ===")
    missing_stats = pd.DataFrame({
        '缺失数量': df.isnull().sum(),
        '缺失比例(%)': df.isnull().sum() / len(df) * 100
    })
    missing_stats = missing_stats[missing_stats['缺失数量'] > 0]
    if not missing_stats.empty:
        print(missing_stats)
    else:
        print("无缺失值")
    
    print("\n=== 重复值统计 ===")
    duplicates = df.duplicated().sum()
    print(f"重复行数: {duplicates}")
    
    print("\n=== 数值列基本统计 ===")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    print(df[numeric_cols].describe())
    
    print("\n=== 分类列基本统计 ===")
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        print(f"\n{col} 的唯一值:")
        print(df[col].value_counts())

# 执行数据概览
data_overview(df)

# 3. 单变量分析
print("\n\n3. 单变量分析")
print("-" * 30)

def univariate_analysis(df):
    """单变量分析"""
    
    # 数值变量分析
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # 创建图表
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    axes = axes.ravel()
    
    for i, col in enumerate(numeric_cols[:9]):  # 最多显示9个数值列
        if i < len(axes):
            # 直方图
            axes[i].hist(df[col].dropna(), bins=30, alpha=0.7, edgecolor='black')
            axes[i].set_title(f'{col} 分布')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('频数')
            
            # 添加统计信息
            mean_val = df[col].mean()
            median_val = df[col].median()
            axes[i].axvline(mean_val, color='red', linestyle='--', label=f'均值: {mean_val:.2f}')
            axes[i].axvline(median_val, color='green', linestyle='--', label=f'中位数: {median_val:.2f}')
            axes[i].legend()
    
    # 隐藏多余的子图
    for i in range(len(numeric_cols), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('univariate_numeric.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 分类变量分析
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    if len(categorical_cols) > 0:
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.ravel()
        
        for i, col in enumerate(categorical_cols[:4]):  # 最多显示4个分类列
            if i < len(axes):
                value_counts = df[col].value_counts()
                axes[i].bar(value_counts.index, value_counts.values)
                axes[i].set_title(f'{col} 分布')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('频数')
                
                # 旋转标签以避免重叠
                axes[i].tick_params(axis='x', rotation=45)
        
        # 隐藏多余的子图
        for i in range(len(categorical_cols), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig('univariate_categorical.png', dpi=300, bbox_inches='tight')
        plt.show()

# 执行单变量分析
univariate_analysis(df)

# 4. 异常值检测
print("\n\n4. 异常值检测")
print("-" * 30)

def detect_outliers(df):
    """检测异常值"""
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    print("=== 异常值检测结果 ===")
    
    outlier_summary = {}
    
    for col in numeric_cols:
        if col != 'customer_id':  # 跳过ID列
            # IQR 方法
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_iqr = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            # Z-score 方法
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers_zscore = df[z_scores > 3]
            
            outlier_summary[col] = {
                'IQR_outliers': len(outliers_iqr),
                'Z_score_outliers': len(outliers_zscore),
                'IQR_percentage': len(outliers_iqr) / len(df) * 100,
                'Z_score_percentage': len(outliers_zscore) / len(df) * 100
            }
            
            print(f"\n{col}:")
            print(f"  IQR方法: {len(outliers_iqr)} 个异常值 ({len(outliers_iqr)/len(df)*100:.2f}%)")
            print(f"  Z-score方法: {len(outliers_zscore)} 个异常值 ({len(outliers_zscore)/len(df)*100:.2f}%)")
    
    # 可视化异常值
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.ravel()
    
    for i, col in enumerate(numeric_cols[:6]):
        if col != 'customer_id' and i < len(axes):
            # 箱线图
            axes[i].boxplot(df[col].dropna())
            axes[i].set_title(f'{col} 箱线图')
            axes[i].set_ylabel(col)
    
    # 隐藏多余的子图
    for i in range(len([c for c in numeric_cols if c != 'customer_id']), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('outlier_detection.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return outlier_summary

# 执行异常值检测
outlier_results = detect_outliers(df)

# 5. 双变量分析
print("\n\n5. 双变量分析")
print("-" * 30)

def bivariate_analysis(df):
    """双变量分析"""
    
    # 数值变量相关性分析
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col != 'customer_id']
    
    # 相关性矩阵
    correlation_matrix = df[numeric_cols].corr()
    
    # 绘制相关性热力图
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.2f')
    plt.title('数值变量相关性矩阵')
    plt.tight_layout()
    plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 强相关性分析
    print("=== 强相关性分析 ===")
    strong_correlations = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) > 0.5:  # 相关系数绝对值大于0.5
                strong_correlations.append({
                    'var1': correlation_matrix.columns[i],
                    'var2': correlation_matrix.columns[j],
                    'correlation': corr_value
                })
    
    if strong_correlations:
        for corr in strong_correlations:
            print(f"{corr['var1']} vs {corr['var2']}: {corr['correlation']:.3f}")
    else:
        print("未发现强相关性（|r| > 0.5）")
    
    # 散点图矩阵（选择部分变量）
    key_vars = ['age', 'income', 'purchase_amount', 'satisfaction_score']
    if all(var in df.columns for var in key_vars):
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 收入 vs 购买金额
        axes[0, 0].scatter(df['income'], df['purchase_amount'], alpha=0.6)
        axes[0, 0].set_xlabel('收入')
        axes[0, 0].set_ylabel('购买金额')
        axes[0, 0].set_title('收入 vs 购买金额')
        
        # 年龄 vs 收入
        axes[0, 1].scatter(df['age'], df['income'], alpha=0.6)
        axes[0, 1].set_xlabel('年龄')
        axes[0, 1].set_ylabel('收入')
        axes[0, 1].set_title('年龄 vs 收入')
        
        # 购买金额 vs 满意度
        axes[1, 0].scatter(df['purchase_amount'], df['satisfaction_score'], alpha=0.6)
        axes[1, 0].set_xlabel('购买金额')
        axes[1, 0].set_ylabel('满意度评分')
        axes[1, 0].set_title('购买金额 vs 满意度')
        
        # 年龄 vs 满意度
        axes[1, 1].scatter(df['age'], df['satisfaction_score'], alpha=0.6)
        axes[1, 1].set_xlabel('年龄')
        axes[1, 1].set_ylabel('满意度评分')
        axes[1, 1].set_title('年龄 vs 满意度')
        
        plt.tight_layout()
        plt.savefig('scatter_plots.png', dpi=300, bbox_inches='tight')
        plt.show()

# 执行双变量分析
bivariate_analysis(df)

# 6. 分类变量与数值变量关系
print("\n\n6. 分类变量与数值变量关系")
print("-" * 30)

def categorical_numerical_analysis(df):
    """分析分类变量与数值变量的关系"""
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    numerical_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                     if col != 'customer_id']
    
    # 选择几个关键的组合进行分析
    key_combinations = [
        ('education', 'income'),
        ('gender', 'purchase_amount'),
        ('city_tier', 'income'),
        ('marital_status', 'satisfaction_score')
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.ravel()
    
    for i, (cat_var, num_var) in enumerate(key_combinations):
        if cat_var in df.columns and num_var in df.columns and i < len(axes):
            # 箱线图
            df.boxplot(column=num_var, by=cat_var, ax=axes[i])
            axes[i].set_title(f'{num_var} 按 {cat_var} 分组')
            axes[i].set_xlabel(cat_var)
            axes[i].set_ylabel(num_var)
            
            # 统计检验
            groups = [group[num_var].dropna() for name, group in df.groupby(cat_var)]
            if len(groups) > 1:
                # 方差分析 (ANOVA)
                f_stat, p_value = stats.f_oneway(*groups)
                axes[i].text(0.02, 0.98, f'ANOVA p-value: {p_value:.4f}', 
                           transform=axes[i].transAxes, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('categorical_numerical.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 统计摘要
    print("=== 分类变量与数值变量关系统计 ===")
    for cat_var, num_var in key_combinations:
        if cat_var in df.columns and num_var in df.columns:
            print(f"\n{cat_var} vs {num_var}:")
            group_stats = df.groupby(cat_var)[num_var].agg(['count', 'mean', 'std'])
            print(group_stats)

# 执行分类变量与数值变量关系分析
categorical_numerical_analysis(df)

# 7. 数据分布分析
print("\n\n7. 数据分布分析")
print("-" * 30)

def distribution_analysis(df):
    """数据分布分析"""
    
    numerical_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                     if col != 'customer_id']
    
    print("=== 数据分布分析 ===")
    
    for col in numerical_cols[:4]:  # 分析前4个数值列
        print(f"\n{col} 分布分析:")
        
        data = df[col].dropna()
        
        # 基本统计
        print(f"  均值: {data.mean():.2f}")
        print(f"  中位数: {data.median():.2f}")
        print(f"  标准差: {data.std():.2f}")
        print(f"  偏度: {stats.skew(data):.2f}")
        print(f"  峰度: {stats.kurtosis(data):.2f}")
        
        # 正态性检验
        _, p_value = stats.normaltest(data)
        print(f"  正态性检验 p-value: {p_value:.4f}")
        
        if p_value > 0.05:
            print(f"  {col} 可能服从正态分布")
        else:
            print(f"  {col} 不服从正态分布")
    
    # 可视化分布
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.ravel()
    
    for i, col in enumerate(numerical_cols[:4]):
        data = df[col].dropna()
        
        # 直方图 + 密度曲线
        axes[i].hist(data, bins=30, density=True, alpha=0.7, edgecolor='black')
        
        # 添加正态分布曲线用于比较
        mu, sigma = data.mean(), data.std()
        x = np.linspace(data.min(), data.max(), 100)
        normal_curve = stats.norm.pdf(x, mu, sigma)
        axes[i].plot(x, normal_curve, 'r-', linewidth=2, label='正态分布')
        
        axes[i].set_title(f'{col} 分布')
        axes[i].set_xlabel(col)
        axes[i].set_ylabel('密度')
        axes[i].legend()
    
    plt.tight_layout()
    plt.savefig('distribution_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

# 执行分布分析
distribution_analysis(df)

# 8. EDA 报告生成
print("\n\n8. EDA 报告生成")
print("-" * 30)

def generate_eda_report(df):
    """生成 EDA 报告"""
    
    report = {
        'dataset_info': {
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum()
        },
        'numerical_summary': {},
        'categorical_summary': {},
        'correlations': {},
        'outliers': {}
    }
    
    # 数值变量摘要
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    for col in numerical_cols:
        if col != 'customer_id':
            report['numerical_summary'][col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'skewness': stats.skew(df[col].dropna()),
                'kurtosis': stats.kurtosis(df[col].dropna())
            }
    
    # 分类变量摘要
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        report['categorical_summary'][col] = {
            'unique_count': df[col].nunique(),
            'most_frequent': df[col].mode().iloc[0] if not df[col].mode().empty else None,
            'most_frequent_count': df[col].value_counts().iloc[0] if not df[col].empty else 0
        }
    
    # 相关性分析
    corr_matrix = df[numerical_cols].corr()
    strong_corrs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) > 0.5:
                strong_corrs.append({
                    'var1': corr_matrix.columns[i],
                    'var2': corr_matrix.columns[j],
                    'correlation': corr_value
                })
    
    report['correlations']['strong_correlations'] = strong_corrs
    
    print("=== EDA 报告摘要 ===")
    print(f"数据集形状: {report['dataset_info']['shape']}")
    print(f"内存使用: {report['dataset_info']['memory_usage_mb']:.2f} MB")
    print(f"缺失值总数: {report['dataset_info']['missing_values']}")
    print(f"重复行数: {report['dataset_info']['duplicate_rows']}")
    
    print(f"\n数值变量数量: {len(report['numerical_summary'])}")
    print(f"分类变量数量: {len(report['categorical_summary'])}")
    print(f"强相关性对数: {len(report['correlations']['strong_correlations'])}")
    
    return report

# 生成 EDA 报告
eda_report = generate_eda_report(df)

# 9. EDA 最佳实践
print("\n\n9. EDA 最佳实践")
print("-" * 30)

best_practices = [
    "探索性数据分析最佳实践:",
    "",
    "1. 系统性方法:",
    "   - 从数据概览开始",
    "   - 逐步深入到细节分析",
    "   - 记录发现和假设",
    "",
    "2. 数据质量检查:",
    "   - 检查缺失值模式",
    "   - 识别异常值和离群点",
    "   - 验证数据一致性",
    "",
    "3. 可视化原则:",
    "   - 选择合适的图表类型",
    "   - 保持图表简洁清晰",
    "   - 添加必要的标注和说明",
    "",
    "4. 统计分析:",
    "   - 计算描述性统计",
    "   - 进行假设检验",
    "   - 分析变量关系",
    "",
    "5. 业务理解:",
    "   - 结合业务背景解释发现",
    "   - 识别业务相关的模式",
    "   - 提出可行的建议"
]

for practice in best_practices:
    print(practice)

# 10. 自动化 EDA 工具
print("\n\n10. 自动化 EDA 工具")
print("-" * 30)

class AutoEDA:
    """自动化 EDA 工具类"""
    
    def __init__(self, df):
        self.df = df
        self.numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    def quick_summary(self):
        """快速数据摘要"""
        print("=== 快速数据摘要 ===")
        print(f"数据形状: {self.df.shape}")
        print(f"数值列: {len(self.numerical_cols)}")
        print(f"分类列: {len(self.categorical_cols)}")
        print(f"缺失值: {self.df.isnull().sum().sum()}")
        print(f"重复行: {self.df.duplicated().sum()}")
    
    def detect_data_issues(self):
        """检测数据问题"""
        issues = []
        
        # 检查缺失值
        missing_cols = self.df.columns[self.df.isnull().any()].tolist()
        if missing_cols:
            issues.append(f"缺失值列: {missing_cols}")
        
        # 检查重复行
        if self.df.duplicated().sum() > 0:
            issues.append(f"发现 {self.df.duplicated().sum()} 行重复数据")
        
        # 检查异常值
        for col in self.numerical_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = self.df[(self.df[col] < Q1 - 1.5*IQR) | (self.df[col] > Q3 + 1.5*IQR)]
            if len(outliers) > len(self.df) * 0.05:  # 超过5%的异常值
                issues.append(f"{col} 列异常值较多: {len(outliers)} 个")
        
        return issues
    
    def suggest_next_steps(self):
        """建议下一步分析"""
        suggestions = []
        
        # 基于数据特征提供建议
        if len(self.numerical_cols) > 2:
            suggestions.append("进行主成分分析 (PCA) 降维")
        
        if len(self.categorical_cols) > 0:
            suggestions.append("分析分类变量对目标变量的影响")
        
        if self.df.isnull().sum().sum() > 0:
            suggestions.append("制定缺失值处理策略")
        
        # 检查是否有时间相关列
        date_like_cols = [col for col in self.df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_like_cols:
            suggestions.append("进行时间序列分析")
        
        return suggestions

# 使用自动化 EDA 工具
auto_eda = AutoEDA(df)
auto_eda.quick_summary()

print("\n=== 数据问题检测 ===")
issues = auto_eda.detect_data_issues()
for issue in issues:
    print(f"- {issue}")

print("\n=== 建议的下一步分析 ===")
suggestions = auto_eda.suggest_next_steps()
for suggestion in suggestions:
    print(f"- {suggestion}")

print("\n" + "=" * 60)
print("探索性数据分析教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 使用真实数据集进行完整的 EDA")
print("2. 学习使用 pandas-profiling 等自动化工具")
print("3. 练习不同类型数据的可视化技巧")
print("4. 结合业务背景解释数据发现")
print("5. 开发自定义的 EDA 工具和模板")