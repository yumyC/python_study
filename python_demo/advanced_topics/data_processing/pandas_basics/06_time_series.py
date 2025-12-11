#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas 时间序列处理教程

时间序列数据处理是数据分析中的重要技能，包括日期时间操作、重采样、滚动窗口等。
本教程详细介绍 Pandas 中的时间序列处理技术。

作者: Python学习课程
日期: 2024年
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 60)
print("Pandas 时间序列处理教程")
print("=" * 60)

# 1. 日期时间基础
print("\n1. 日期时间基础")
print("-" * 30)

# 创建日期时间对象
print("创建日期时间对象:")
single_date = pd.Timestamp('2024-01-15')
print(f"单个时间戳: {single_date}")

# 从字符串解析
date_from_string = pd.to_datetime('2024-01-15 14:30:00')
print(f"从字符串解析: {date_from_string}")

# 创建日期范围
date_range = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
print(f"日期范围: {date_range}")

# 不同频率的日期范围
hourly_range = pd.date_range(start='2024-01-01', periods=24, freq='H')
print(f"小时频率: {hourly_range[:5]}...")

business_days = pd.date_range(start='2024-01-01', periods=10, freq='B')
print(f"工作日: {business_days}")

# 2. 时间序列索引
print("\n\n2. 时间序列索引")
print("-" * 30)

# 创建时间序列数据
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=100, freq='D')
values = np.random.randn(100).cumsum() + 100

ts = pd.Series(values, index=dates)
print("时间序列数据（前10个）:")
print(ts.head(10))

# 时间序列 DataFrame
ts_df = pd.DataFrame({
    'price': np.random.randn(100).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 100),
    'returns': np.random.randn(100) * 0.02
}, index=dates)

print("\n时间序列 DataFrame（前5行）:")
print(ts_df.head())

# 3. 时间序列索引和选择
print("\n\n3. 时间序列索引和选择")
print("-" * 30)

# 按日期选择
print("2024年1月的数据:")
jan_data = ts_df['2024-01']
print(f"1月数据点数: {len(jan_data)}")

# 按日期范围选择
print("\n前10天的数据:")
first_10_days = ts_df['2024-01-01':'2024-01-10']
print(first_10_days['price'])

# 按条件选择
print("\n价格大于100的日期:")
high_price_dates = ts_df[ts_df['price'] > 100].index[:5]
print(high_price_dates)

# 4. 时间序列重采样
print("\n\n4. 时间序列重采样")
print("-" * 30)

# 降采样（日数据到周数据）
weekly_data = ts_df.resample('W').mean()
print("周平均数据:")
print(weekly_data.head())

# 不同的聚合方法
monthly_agg = ts_df.resample('M').agg({
    'price': ['mean', 'max', 'min'],
    'volume': 'sum',
    'returns': 'std'
})
print("\n月度聚合数据:")
print(monthly_agg.head())

# 升采样（填充缺失值）
hourly_upsampled = ts_df.resample('H').ffill()  # 前向填充
print(f"\n升采样到小时数据点数: {len(hourly_upsampled)}")
print("升采样后的前几个小时:")
print(hourly_upsampled.head())

# 5. 滚动窗口计算
print("\n\n5. 滚动窗口计算")
print("-" * 30)

# 简单移动平均
ts_df['MA_5'] = ts_df['price'].rolling(window=5).mean()
ts_df['MA_20'] = ts_df['price'].rolling(window=20).mean()

print("价格和移动平均:")
print(ts_df[['price', 'MA_5', 'MA_20']].head(25))

# 滚动标准差
ts_df['volatility'] = ts_df['returns'].rolling(window=10).std()
print("\n滚动波动率:")
print(ts_df[['returns', 'volatility']].head(15))

# 滚动相关性
ts_df['price_volume_corr'] = ts_df['price'].rolling(window=20).corr(ts_df['volume'])
print("\n价格和成交量的滚动相关性:")
print(ts_df[['price', 'volume', 'price_volume_corr']].tail(10))

# 6. 扩展窗口计算
print("\n\n6. 扩展窗口计算")
print("-" * 30)

# 累计统计
ts_df['cumulative_return'] = (1 + ts_df['returns']).cumprod() - 1
ts_df['expanding_mean'] = ts_df['price'].expanding().mean()
ts_df['expanding_std'] = ts_df['price'].expanding().std()

print("累计和扩展统计:")
print(ts_df[['price', 'cumulative_return', 'expanding_mean', 'expanding_std']].head(10))

# 7. 时间偏移和移位
print("\n\n7. 时间偏移和移位")
print("-" * 30)

# 数据移位
ts_df['price_lag1'] = ts_df['price'].shift(1)  # 滞后1期
ts_df['price_lead1'] = ts_df['price'].shift(-1)  # 超前1期

print("价格移位:")
print(ts_df[['price', 'price_lag1', 'price_lead1']].head(10))

# 计算变化率
ts_df['price_change'] = ts_df['price'].pct_change()
ts_df['price_diff'] = ts_df['price'].diff()

print("\n价格变化:")
print(ts_df[['price', 'price_change', 'price_diff']].head(10))

# 8. 时区处理
print("\n\n8. 时区处理")
print("-" * 30)

# 创建带时区的时间序列
utc_dates = pd.date_range('2024-01-01', periods=5, freq='D', tz='UTC')
print("UTC 时间:")
print(utc_dates)

# 转换时区
beijing_dates = utc_dates.tz_convert('Asia/Shanghai')
print("\n北京时间:")
print(beijing_dates)

# 本地化时区
naive_dates = pd.date_range('2024-01-01', periods=5, freq='D')
localized_dates = naive_dates.tz_localize('Asia/Shanghai')
print("\n本地化时区:")
print(localized_dates)

# 9. 日期时间组件提取
print("\n\n9. 日期时间组件提取")
print("-" * 30)

# 提取日期组件
ts_df['year'] = ts_df.index.year
ts_df['month'] = ts_df.index.month
ts_df['day'] = ts_df.index.day
ts_df['weekday'] = ts_df.index.dayofweek
ts_df['week_name'] = ts_df.index.day_name()

print("日期组件:")
print(ts_df[['year', 'month', 'day', 'weekday', 'week_name']].head(10))

# 按星期几分组分析
weekday_analysis = ts_df.groupby('weekday')['returns'].mean()
print("\n按星期几的平均收益:")
weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
for i, avg_return in weekday_analysis.items():
    print(f"{weekday_names[i]}: {avg_return:.4f}")

# 10. 时间序列可视化
print("\n\n10. 时间序列可视化")
print("-" * 30)

# 创建图表
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 价格时间序列
axes[0, 0].plot(ts_df.index, ts_df['price'])
axes[0, 0].set_title('价格时间序列')
axes[0, 0].set_ylabel('价格')

# 移动平均
axes[0, 1].plot(ts_df.index, ts_df['price'], label='价格', alpha=0.7)
axes[0, 1].plot(ts_df.index, ts_df['MA_5'], label='5日均线')
axes[0, 1].plot(ts_df.index, ts_df['MA_20'], label='20日均线')
axes[0, 1].set_title('价格和移动平均')
axes[0, 1].legend()

# 收益率分布
axes[1, 0].hist(ts_df['returns'].dropna(), bins=20, alpha=0.7)
axes[1, 0].set_title('收益率分布')
axes[1, 0].set_xlabel('收益率')

# 累计收益
axes[1, 1].plot(ts_df.index, ts_df['cumulative_return'])
axes[1, 1].set_title('累计收益')
axes[1, 1].set_ylabel('累计收益率')

plt.tight_layout()
plt.savefig('time_series_analysis.png', dpi=300, bbox_inches='tight')
print("时间序列图表已保存为 'time_series_analysis.png'")

# 11. 季节性分析
print("\n\n11. 季节性分析")
print("-" * 30)

# 创建更长的时间序列用于季节性分析
long_dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
seasonal_trend = np.sin(2 * np.pi * np.arange(len(long_dates)) / 365.25) * 10
noise = np.random.randn(len(long_dates)) * 5
seasonal_data = pd.Series(100 + seasonal_trend + noise, index=long_dates)

# 按月份分组
monthly_pattern = seasonal_data.groupby(seasonal_data.index.month).mean()
print("月度季节性模式:")
months = ['1月', '2月', '3月', '4月', '5月', '6月', 
          '7月', '8月', '9月', '10月', '11月', '12月']
for i, avg_value in monthly_pattern.items():
    print(f"{months[i-1]}: {avg_value:.2f}")

# 12. 时间序列分解
print("\n\n12. 时间序列分解")
print("-" * 30)

# 简单的趋势分解
def simple_decompose(series, window=30):
    """简单的时间序列分解"""
    # 趋势（移动平均）
    trend = series.rolling(window=window, center=True).mean()
    
    # 去趋势
    detrended = series - trend
    
    # 季节性（简化版，按月计算）
    seasonal = detrended.groupby(detrended.index.month).transform('mean')
    
    # 残差
    residual = detrended - seasonal
    
    return trend, seasonal, residual

trend, seasonal, residual = simple_decompose(seasonal_data)

print("时间序列分解结果（前10个值）:")
decomp_df = pd.DataFrame({
    'original': seasonal_data,
    'trend': trend,
    'seasonal': seasonal,
    'residual': residual
})
print(decomp_df.head(10))

# 13. 时间序列异常检测
print("\n\n13. 时间序列异常检测")
print("-" * 30)

def detect_outliers_ts(series, window=20, threshold=3):
    """基于滚动统计的异常检测"""
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    
    # 计算 Z-score
    z_scores = (series - rolling_mean) / rolling_std
    
    # 标记异常值
    outliers = np.abs(z_scores) > threshold
    
    return outliers, z_scores

outliers, z_scores = detect_outliers_ts(ts_df['price'])
outlier_dates = ts_df.index[outliers]

print(f"检测到 {outliers.sum()} 个异常值")
if len(outlier_dates) > 0:
    print("异常值日期（前5个）:")
    for date in outlier_dates[:5]:
        print(f"  {date.strftime('%Y-%m-%d')}: {ts_df.loc[date, 'price']:.2f}")

# 14. 实际应用场景
print("\n\n14. 实际应用场景")
print("-" * 30)

# 场景1: 股票技术分析
def technical_analysis(price_series):
    """股票技术分析指标"""
    df = pd.DataFrame({'price': price_series})
    
    # 移动平均
    df['MA5'] = df['price'].rolling(5).mean()
    df['MA20'] = df['price'].rolling(20).mean()
    
    # 布林带
    df['BB_middle'] = df['price'].rolling(20).mean()
    bb_std = df['price'].rolling(20).std()
    df['BB_upper'] = df['BB_middle'] + 2 * bb_std
    df['BB_lower'] = df['BB_middle'] - 2 * bb_std
    
    # RSI（简化版）
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD（简化版）
    ema12 = df['price'].ewm(span=12).mean()
    ema26 = df['price'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
    
    return df

tech_indicators = technical_analysis(ts_df['price'])
print("技术分析指标（最后5天）:")
print(tech_indicators[['price', 'MA5', 'MA20', 'RSI', 'MACD']].tail())

# 场景2: 销售预测
def sales_forecast_simple(sales_series, periods=7):
    """简单的销售预测"""
    # 使用指数平滑
    alpha = 0.3
    forecast = [sales_series.iloc[-1]]
    
    for i in range(periods):
        if i == 0:
            next_value = alpha * sales_series.iloc[-1] + (1 - alpha) * sales_series.rolling(7).mean().iloc[-1]
        else:
            next_value = alpha * forecast[-1] + (1 - alpha) * forecast[-1]
        forecast.append(next_value)
    
    return forecast[1:]  # 排除第一个值

# 模拟销售数据
sales_data = ts_df['volume'].rolling(7).mean().dropna()
forecast = sales_forecast_simple(sales_data)

print(f"\n未来7天销售预测:")
future_dates = pd.date_range(start=sales_data.index[-1] + timedelta(days=1), periods=7, freq='D')
for date, pred in zip(future_dates, forecast):
    print(f"{date.strftime('%Y-%m-%d')}: {pred:.0f}")

print("\n" + "=" * 60)
print("时间序列处理教程完成！")
print("=" * 60)

# 练习建议
print("\n练习建议:")
print("1. 尝试更复杂的时间序列分解方法")
print("2. 实现更多的技术分析指标")
print("3. 练习不同频率的时间序列重采样")
print("4. 学习时间序列预测模型（ARIMA等）")
print("5. 处理真实的金融或业务时间序列数据")