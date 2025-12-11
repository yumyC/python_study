#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
销售数据分析项目 - 主分析脚本

这是销售数据分析项目的主要分析脚本，展示了完整的数据分析流程，
从数据生成、清洗、分析到可视化和报告生成。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
import os

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

print("=" * 60)
print("销售数据分析项目")
print("=" * 60)

# 1. 数据生成器
print("\n1. 数据生成")
print("-" * 30)

def generate_sales_data(n_orders=10000, start_date='2022-01-01', end_date='2024-12-31'):
    """生成虚拟销售数据"""
    
    np.random.seed(42)
    
    # 日期范围
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 产品信息
    products = {
        '电子产品': ['iPhone 14', 'Samsung Galaxy', 'iPad Pro', 'MacBook Air', 'AirPods', 'Apple Watch'],
        '服装': ['T恤', '牛仔裤', '连衣裙', '运动鞋', '外套', '帽子'],
        '家居': ['沙发', '床垫', '台灯', '餐桌', '书架', '地毯'],
        '图书': ['小说', '技术书籍', '教材', '漫画', '杂志', '儿童读物'],
        '运动': ['跑步机', '哑铃', '瑜伽垫', '篮球', '网球拍', '游泳镜']
    }
    
    # 城市信息
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆']
    
    # 生成订单数据
    orders = []
    
    for i in range(n_orders):
        # 基本订单信息
        order_id = f'ORD{i+1:06d}'
        customer_id = f'CUST{np.random.randint(1, n_orders//3):05d}'
        
        # 随机选择产品
        category = np.random.choice(list(products.keys()))
        product_name = np.random.choice(products[category])
        product_id = f'PROD{hash(product_name) % 10000:04d}'
        
        # 订单日期（工作日概率更高）
        order_date = np.random.choice(date_range)
        if order_date.weekday() >= 5:  # 周末
            if np.random.random() > 0.3:  # 70%概率重新选择
                order_date = np.random.choice(date_range)
        
        # 数量和价格（根据产品类别调整）
        if category == '电子产品':
            base_price = np.random.uniform(500, 8000)
            quantity = np.random.choice([1, 2], p=[0.8, 0.2])
        elif category == '服装':
            base_price = np.random.uniform(50, 500)
            quantity = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
        elif category == '家居':
            base_price = np.random.uniform(200, 3000)
            quantity = np.random.choice([1, 2], p=[0.9, 0.1])
        elif category == '图书':
            base_price = np.random.uniform(20, 200)
            quantity = np.random.choice([1, 2, 3, 4], p=[0.5, 0.3, 0.15, 0.05])
        else:  # 运动
            base_price = np.random.uniform(100, 2000)
            quantity = np.random.choice([1, 2], p=[0.8, 0.2])
        
        # 折扣率（节假日和促销期间更高）
        if order_date.month in [6, 11, 12]:  # 促销月份
            discount_rate = np.random.uniform(0, 0.3)
        else:
            discount_rate = np.random.uniform(0, 0.1)
        
        unit_price = base_price * (1 - discount_rate)
        total_amount = unit_price * quantity
        
        # 客户信息
        customer_age = np.random.randint(18, 70)
        customer_gender = np.random.choice(['男', '女'])
        customer_city = np.random.choice(cities)
        
        # 销售渠道
        sales_channel = np.random.choice(['线上', '线下'], p=[0.7, 0.3])
        
        # 利润率（根据类别和渠道调整）
        base_margin = 0.3
        if category == '电子产品':
            base_margin = 0.15
        elif category == '图书':
            base_margin = 0.4
        
        if sales_channel == '线上':
            base_margin *= 1.2  # 线上利润率更高
        
        profit_margin = base_margin + np.random.uniform(-0.05, 0.05)
        profit_margin = max(0.05, min(0.6, profit_margin))  # 限制在合理范围
        
        orders.append({
            'order_id': order_id,
            'customer_id': customer_id,
            'product_id': product_id,
            'product_name': product_name,
            'category': category,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'total_amount': round(total_amount, 2),
            'order_date': order_date,
            'customer_age': customer_age,
            'customer_gender': customer_gender,
            'customer_city': customer_city,
            'sales_channel': sales_channel,
            'discount_rate': round(discount_rate, 3),
            'profit_margin': round(profit_margin, 3)
        })
    
    return pd.DataFrame(orders)

# 生成数据
print("正在生成销售数据...")
df = generate_sales_data(n_orders=15000)
print(f"生成了 {len(df)} 条销售记录")
print(f"时间范围: {df['order_date'].min()} 到 {df['order_date'].max()}")
print(f"客户数量: {df['customer_id'].nunique()}")
print(f"产品数量: {df['product_id'].nunique()}")

# 2. 数据概览
print("\n\n2. 数据概览")
print("-" * 30)

print("数据基本信息:")
print(df.info())

print("\n数据样本:")
print(df.head())

print("\n基本统计:")
print(df.describe())

# 3. 数据清洗和预处理
print("\n\n3. 数据清洗和预处理")
print("-" * 30)

# 检查数据质量
print("数据质量检查:")
print(f"缺失值: {df.isnull().sum().sum()}")
print(f"重复行: {df.duplicated().sum()}")

# 添加派生字段
df['profit_amount'] = df['total_amount'] * df['profit_margin']
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month
df['quarter'] = df['order_date'].dt.quarter
df['weekday'] = df['order_date'].dt.day_name()
df['is_weekend'] = df['order_date'].dt.weekday >= 5

# 客户年龄分组
df['age_group'] = pd.cut(df['customer_age'], 
                        bins=[0, 25, 35, 45, 55, 100], 
                        labels=['18-25', '26-35', '36-45', '46-55', '55+'])

print("\n添加了派生字段:")
print("- profit_amount: 利润金额")
print("- year, month, quarter: 时间维度")
print("- weekday, is_weekend: 星期维度")
print("- age_group: 年龄分组")

# 4. 销售趋势分析
print("\n\n4. 销售趋势分析")
print("-" * 30)

# 月度销售趋势
monthly_sales = df.groupby(['year', 'month']).agg({
    'total_amount': 'sum',
    'order_id': 'count',
    'profit_amount': 'sum'
}).reset_index()

monthly_sales['date'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))

print("月度销售趋势:")
print(monthly_sales.tail(10))

# 可视化月度趋势
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 销售额趋势
axes[0, 0].plot(monthly_sales['date'], monthly_sales['total_amount'], marker='o')
axes[0, 0].set_title('月度销售额趋势')
axes[0, 0].set_ylabel('销售额')
axes[0, 0].tick_params(axis='x', rotation=45)

# 订单数量趋势
axes[0, 1].plot(monthly_sales['date'], monthly_sales['order_id'], marker='s', color='orange')
axes[0, 1].set_title('月度订单数量趋势')
axes[0, 1].set_ylabel('订单数量')
axes[0, 1].tick_params(axis='x', rotation=45)

# 利润趋势
axes[1, 0].plot(monthly_sales['date'], monthly_sales['profit_amount'], marker='^', color='green')
axes[1, 0].set_title('月度利润趋势')
axes[1, 0].set_ylabel('利润金额')
axes[1, 0].tick_params(axis='x', rotation=45)

# 平均订单价值趋势
monthly_sales['avg_order_value'] = monthly_sales['total_amount'] / monthly_sales['order_id']
axes[1, 1].plot(monthly_sales['date'], monthly_sales['avg_order_value'], marker='d', color='red')
axes[1, 1].set_title('月度平均订单价值趋势')
axes[1, 1].set_ylabel('平均订单价值')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('sales_trends.png', dpi=300, bbox_inches='tight')
plt.show()

# 5. 产品分析
print("\n\n5. 产品分析")
print("-" * 30)

# 产品类别分析
category_analysis = df.groupby('category').agg({
    'total_amount': ['sum', 'mean'],
    'order_id': 'count',
    'profit_amount': 'sum',
    'quantity': 'sum'
}).round(2)

category_analysis.columns = ['总销售额', '平均订单金额', '订单数量', '总利润', '总销量']
category_analysis['利润率'] = (category_analysis['总利润'] / category_analysis['总销售额'] * 100).round(2)

print("产品类别分析:")
print(category_analysis.sort_values('总销售额', ascending=False))

# 产品类别可视化
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 销售额分布
category_analysis['总销售额'].plot(kind='bar', ax=axes[0, 0], color='skyblue')
axes[0, 0].set_title('各类别总销售额')
axes[0, 0].set_ylabel('销售额')
axes[0, 0].tick_params(axis='x', rotation=45)

# 订单数量分布
category_analysis['订单数量'].plot(kind='bar', ax=axes[0, 1], color='lightcoral')
axes[0, 1].set_title('各类别订单数量')
axes[0, 1].set_ylabel('订单数量')
axes[0, 1].tick_params(axis='x', rotation=45)

# 利润率比较
category_analysis['利润率'].plot(kind='bar', ax=axes[1, 0], color='lightgreen')
axes[1, 0].set_title('各类别利润率')
axes[1, 0].set_ylabel('利润率 (%)')
axes[1, 0].tick_params(axis='x', rotation=45)

# 平均订单金额
category_analysis['平均订单金额'].plot(kind='bar', ax=axes[1, 1], color='gold')
axes[1, 1].set_title('各类别平均订单金额')
axes[1, 1].set_ylabel('平均订单金额')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('product_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# 6. 客户分析
print("\n\n6. 客户分析")
print("-" * 30)

# 客户价值分析
customer_analysis = df.groupby('customer_id').agg({
    'total_amount': ['sum', 'mean', 'count'],
    'profit_amount': 'sum',
    'order_date': ['min', 'max']
}).round(2)

customer_analysis.columns = ['总消费', '平均订单金额', '订单次数', '总利润贡献', '首次购买', '最近购买']
customer_analysis['客户生命周期'] = (customer_analysis['最近购买'] - customer_analysis['首次购买']).dt.days

# 客户分层（RFM简化版）
customer_analysis['消费等级'] = pd.qcut(customer_analysis['总消费'], 
                                   q=4, labels=['低价值', '中低价值', '中高价值', '高价值'])

print("客户价值分析（前10名）:")
top_customers = customer_analysis.sort_values('总消费', ascending=False).head(10)
print(top_customers[['总消费', '订单次数', '平均订单金额', '消费等级']])

# 客户分布分析
print("\n客户分层分布:")
customer_segments = customer_analysis['消费等级'].value_counts()
print(customer_segments)

# 年龄和性别分析
demographic_analysis = df.groupby(['age_group', 'customer_gender']).agg({
    'total_amount': 'sum',
    'order_id': 'count'
}).unstack()

print("\n年龄和性别分析:")
print(demographic_analysis)

# 客户分析可视化
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 客户价值分布
customer_analysis['总消费'].hist(bins=50, ax=axes[0, 0], alpha=0.7)
axes[0, 0].set_title('客户消费金额分布')
axes[0, 0].set_xlabel('总消费金额')
axes[0, 0].set_ylabel('客户数量')

# 客户分层饼图
customer_segments.plot(kind='pie', ax=axes[0, 1], autopct='%1.1f%%')
axes[0, 1].set_title('客户价值分层')
axes[0, 1].set_ylabel('')

# 年龄组消费分析
age_spending = df.groupby('age_group')['total_amount'].sum()
age_spending.plot(kind='bar', ax=axes[1, 0], color='purple')
axes[1, 0].set_title('各年龄组总消费')
axes[1, 0].set_ylabel('总消费金额')
axes[1, 0].tick_params(axis='x', rotation=45)

# 性别消费比较
gender_spending = df.groupby('customer_gender')['total_amount'].sum()
gender_spending.plot(kind='bar', ax=axes[1, 1], color=['pink', 'lightblue'])
axes[1, 1].set_title('性别消费比较')
axes[1, 1].set_ylabel('总消费金额')
axes[1, 1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('customer_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# 7. 地区和渠道分析
print("\n\n7. 地区和渠道分析")
print("-" * 30)

# 地区分析
city_analysis = df.groupby('customer_city').agg({
    'total_amount': 'sum',
    'order_id': 'count',
    'customer_id': 'nunique'
}).round(2)

city_analysis.columns = ['总销售额', '订单数量', '客户数量']
city_analysis['人均消费'] = (city_analysis['总销售额'] / city_analysis['客户数量']).round(2)

print("城市销售分析:")
print(city_analysis.sort_values('总销售额', ascending=False))

# 渠道分析
channel_analysis = df.groupby('sales_channel').agg({
    'total_amount': ['sum', 'mean'],
    'order_id': 'count',
    'profit_amount': 'sum'
}).round(2)

channel_analysis.columns = ['总销售额', '平均订单金额', '订单数量', '总利润']
channel_analysis['利润率'] = (channel_analysis['总利润'] / channel_analysis['总销售额'] * 100).round(2)

print("\n销售渠道分析:")
print(channel_analysis)

# 渠道-类别交叉分析
channel_category = pd.crosstab(df['sales_channel'], df['category'], 
                              values=df['total_amount'], aggfunc='sum')

print("\n渠道-类别交叉分析:")
print(channel_category)

# 8. 时间模式分析
print("\n\n8. 时间模式分析")
print("-" * 30)

# 星期模式
weekday_pattern = df.groupby('weekday').agg({
    'total_amount': 'sum',
    'order_id': 'count'
}).round(2)

# 重新排序星期
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_pattern = weekday_pattern.reindex(weekday_order)

print("星期销售模式:")
print(weekday_pattern)

# 季度模式
quarterly_pattern = df.groupby(['year', 'quarter']).agg({
    'total_amount': 'sum',
    'order_id': 'count'
}).round(2)

print("\n季度销售模式:")
print(quarterly_pattern)

# 时间模式可视化
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 星期模式
weekday_pattern['total_amount'].plot(kind='bar', ax=axes[0, 0], color='teal')
axes[0, 0].set_title('星期销售模式')
axes[0, 0].set_ylabel('销售额')
axes[0, 0].tick_params(axis='x', rotation=45)

# 月份模式
monthly_pattern = df.groupby('month')['total_amount'].sum()
monthly_pattern.plot(kind='line', ax=axes[0, 1], marker='o', color='navy')
axes[0, 1].set_title('月份销售模式')
axes[0, 1].set_ylabel('销售额')
axes[0, 1].set_xlabel('月份')

# 工作日 vs 周末
weekend_comparison = df.groupby('is_weekend')['total_amount'].sum()
weekend_comparison.index = ['工作日', '周末']
weekend_comparison.plot(kind='bar', ax=axes[1, 0], color=['orange', 'red'])
axes[1, 0].set_title('工作日 vs 周末销售')
axes[1, 0].set_ylabel('销售额')
axes[1, 0].tick_params(axis='x', rotation=0)

# 小时模式（模拟）
# 为演示目的，我们创建一个模拟的小时模式
hour_pattern = pd.Series([100, 80, 60, 40, 50, 70, 120, 200, 300, 350, 400, 450, 
                         500, 480, 460, 440, 420, 400, 380, 300, 250, 200, 150, 120],
                        index=range(24))
hour_pattern.plot(kind='line', ax=axes[1, 1], marker='s', color='purple')
axes[1, 1].set_title('小时销售模式（模拟）')
axes[1, 1].set_ylabel('订单数量')
axes[1, 1].set_xlabel('小时')

plt.tight_layout()
plt.savefig('time_patterns.png', dpi=300, bbox_inches='tight')
plt.show()

# 9. 关键业务指标
print("\n\n9. 关键业务指标")
print("-" * 30)

# 计算关键指标
total_revenue = df['total_amount'].sum()
total_profit = df['profit_amount'].sum()
total_orders = len(df)
unique_customers = df['customer_id'].nunique()
avg_order_value = df['total_amount'].mean()
overall_profit_margin = (total_profit / total_revenue * 100)

# 客户指标
avg_customer_value = total_revenue / unique_customers
avg_orders_per_customer = total_orders / unique_customers

# 产品指标
avg_items_per_order = df['quantity'].mean()
total_items_sold = df['quantity'].sum()

print("=== 关键业务指标 ===")
print(f"总销售额: ¥{total_revenue:,.2f}")
print(f"总利润: ¥{total_profit:,.2f}")
print(f"整体利润率: {overall_profit_margin:.2f}%")
print(f"总订单数: {total_orders:,}")
print(f"独立客户数: {unique_customers:,}")
print(f"平均订单价值: ¥{avg_order_value:.2f}")
print(f"平均客户价值: ¥{avg_customer_value:.2f}")
print(f"客户平均订单数: {avg_orders_per_customer:.2f}")
print(f"平均每单商品数: {avg_items_per_order:.2f}")
print(f"总销售商品数: {total_items_sold:,}")

# 10. 业务洞察和建议
print("\n\n10. 业务洞察和建议")
print("-" * 30)

insights = [
    "=== 主要业务洞察 ===",
    "",
    "1. 产品表现:",
    f"   - 最佳类别: {category_analysis.index[0]} (销售额: ¥{category_analysis.iloc[0]['总销售额']:,.2f})",
    f"   - 最高利润率: {category_analysis.sort_values('利润率', ascending=False).index[0]} ({category_analysis.sort_values('利润率', ascending=False).iloc[0]['利润率']:.1f}%)",
    "",
    "2. 客户洞察:",
    f"   - 高价值客户占比: {(customer_segments['高价值'] / len(customer_analysis) * 100):.1f}%",
    f"   - 平均客户生命周期: {customer_analysis['客户生命周期'].mean():.0f} 天",
    "",
    "3. 渠道表现:",
    f"   - 线上销售占比: {(df[df['sales_channel']=='线上']['total_amount'].sum() / total_revenue * 100):.1f}%",
    f"   - 线上平均订单: ¥{df[df['sales_channel']=='线上']['total_amount'].mean():.2f}",
    f"   - 线下平均订单: ¥{df[df['sales_channel']=='线下']['total_amount'].mean():.2f}",
    "",
    "4. 时间模式:",
    f"   - 最佳销售月份: {monthly_pattern.idxmax()}月",
    f"   - 周末销售占比: {(df[df['is_weekend']==True]['total_amount'].sum() / total_revenue * 100):.1f}%",
    "",
    "=== 业务建议 ===",
    "",
    "1. 产品策略:",
    "   - 加大高利润率产品的推广力度",
    "   - 优化低表现类别的产品组合",
    "   - 考虑季节性产品策略",
    "",
    "2. 客户策略:",
    "   - 制定高价值客户保留计划",
    "   - 针对不同年龄组制定营销策略",
    "   - 提升客户复购率",
    "",
    "3. 渠道优化:",
    "   - 继续投资线上渠道发展",
    "   - 优化线下门店体验",
    "   - 实现线上线下一体化",
    "",
    "4. 运营优化:",
    "   - 根据时间模式优化库存管理",
    "   - 在高峰时段加强营销活动",
    "   - 提升整体运营效率"
]

for insight in insights:
    print(insight)

# 11. 生成报告摘要
print("\n\n11. 生成报告摘要")
print("-" * 30)

# 创建报告目录
os.makedirs('reports', exist_ok=True)

# 生成 HTML 报告
html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>销售数据分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; text-align: center; }}
        .section {{ margin: 20px 0; }}
        .metric {{ background-color: #e8f4fd; padding: 10px; margin: 5px 0; }}
        .insight {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>销售数据分析报告</h1>
        <p>分析期间: {df['order_date'].min().strftime('%Y-%m-%d')} 至 {df['order_date'].max().strftime('%Y-%m-%d')}</p>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>关键业务指标</h2>
        <div class="metric">总销售额: ¥{total_revenue:,.2f}</div>
        <div class="metric">总利润: ¥{total_profit:,.2f}</div>
        <div class="metric">整体利润率: {overall_profit_margin:.2f}%</div>
        <div class="metric">总订单数: {total_orders:,}</div>
        <div class="metric">独立客户数: {unique_customers:,}</div>
        <div class="metric">平均订单价值: ¥{avg_order_value:.2f}</div>
    </div>
    
    <div class="section">
        <h2>产品类别表现</h2>
        <table>
            <tr><th>类别</th><th>总销售额</th><th>订单数量</th><th>利润率</th></tr>
"""

for idx, row in category_analysis.iterrows():
    html_report += f"<tr><td>{idx}</td><td>¥{row['总销售额']:,.2f}</td><td>{row['订单数量']:,}</td><td>{row['利润率']:.2f}%</td></tr>"

html_report += """
        </table>
    </div>
    
    <div class="section">
        <h2>主要洞察</h2>
        <div class="insight">电子产品是销售额最高的类别，但图书类别利润率最高</div>
        <div class="insight">线上渠道占据主导地位，平均订单价值更高</div>
        <div class="insight">客户价值分布呈现明显的二八法则特征</div>
        <div class="insight">销售存在明显的时间模式，需要优化库存和营销策略</div>
    </div>
</body>
</html>
"""

# 保存 HTML 报告
with open('reports/sales_report.html', 'w', encoding='utf-8') as f:
    f.write(html_report)

print("HTML 报告已生成: reports/sales_report.html")

# 保存数据
df.to_csv('reports/sales_data.csv', index=False, encoding='utf-8')
print("销售数据已保存: reports/sales_data.csv")

print("\n" + "=" * 60)
print("销售数据分析项目完成！")
print("=" * 60)

print("\n项目成果:")
print("1. 生成了 15,000 条虚拟销售数据")
print("2. 完成了全面的数据分析")
print("3. 创建了多个可视化图表")
print("4. 生成了 HTML 格式的分析报告")
print("5. 提供了具体的业务洞察和建议")

print("\n文件输出:")
print("- sales_trends.png: 销售趋势图")
print("- product_analysis.png: 产品分析图")
print("- customer_analysis.png: 客户分析图")
print("- time_patterns.png: 时间模式图")
print("- reports/sales_report.html: HTML 报告")
print("- reports/sales_data.csv: 原始数据")

print("\n学习要点:")
print("1. 完整的数据分析流程")
print("2. 业务指标的计算和解释")
print("3. 多维度的数据分析方法")
print("4. 数据可视化最佳实践")
print("5. 从数据到洞察的转化过程")