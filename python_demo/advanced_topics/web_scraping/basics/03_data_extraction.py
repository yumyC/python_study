#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提取与存储教程

本教程介绍如何从网页中提取结构化数据，并将数据存储到不同的格式中。
涵盖数据清理、格式转换、文件存储等实用技能。

作者: Python学习课程
日期: 2024
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import sqlite3
import pandas as pd
import re
from datetime import datetime
import os


class DataExtractor:
    """
    数据提取器类
    封装常用的数据提取和处理方法
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page(self, url, **kwargs):
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=10, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"获取页面失败: {e}")
            return None
    
    def parse_html(self, html_content):
        """解析 HTML 内容"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def clean_text(self, text):
        """清理文本内容"""
        if not text:
            return ""
        
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 去除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()""''—-]', '', text)
        
        return text
    
    def extract_numbers(self, text):
        """从文本中提取数字"""
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        return [float(num) for num in numbers]
    
    def extract_dates(self, text):
        """从文本中提取日期"""
        # 匹配常见的日期格式
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2024-01-01
            r'\d{4}/\d{2}/\d{2}',  # 2024/01/01
            r'\d{2}-\d{2}-\d{4}',  # 01-01-2024
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates


def extract_news_data():
    """
    新闻数据提取示例
    演示如何从新闻网站提取结构化数据
    """
    print("=== 新闻数据提取示例 ===")
    
    # 模拟新闻页面 HTML
    html_content = """
    <div class="news-container">
        <article class="news-item" data-id="1">
            <h2 class="title">
                <a href="/news/1">人工智能技术取得重大突破</a>
            </h2>
            <div class="meta">
                <span class="author">记者: 张三</span>
                <span class="date">2024-01-15 14:30:00</span>
                <span class="category">科技</span>
                <span class="views">阅读量: 1,234</span>
            </div>
            <p class="summary">
                最新研究显示，人工智能在自然语言处理领域取得了重大突破...
            </p>
            <div class="tags">
                <span class="tag">AI</span>
                <span class="tag">机器学习</span>
                <span class="tag">NLP</span>
            </div>
        </article>
        
        <article class="news-item" data-id="2">
            <h2 class="title">
                <a href="/news/2">新能源汽车销量创新高</a>
            </h2>
            <div class="meta">
                <span class="author">记者: 李四</span>
                <span class="date">2024-01-14 16:45:00</span>
                <span class="category">汽车</span>
                <span class="views">阅读量: 2,567</span>
            </div>
            <p class="summary">
                据统计，2024年第一季度新能源汽车销量同比增长45%...
            </p>
            <div class="tags">
                <span class="tag">新能源</span>
                <span class="tag">汽车</span>
                <span class="tag">销量</span>
            </div>
        </article>
    </div>
    """
    
    extractor = DataExtractor()
    soup = extractor.parse_html(html_content)
    
    news_list = []
    
    # 提取每篇新闻的数据
    articles = soup.find_all('article', class_='news-item')
    
    for article in articles:
        news_data = {}
        
        # 提取基本信息
        news_data['id'] = article.get('data-id')
        
        # 提取标题和链接
        title_link = article.find('h2', class_='title').find('a')
        news_data['title'] = extractor.clean_text(title_link.text)
        news_data['url'] = title_link.get('href')
        
        # 提取元数据
        meta_div = article.find('div', class_='meta')
        author_span = meta_div.find('span', class_='author')
        news_data['author'] = author_span.text.replace('记者: ', '') if author_span else ''
        
        date_span = meta_div.find('span', class_='date')
        news_data['publish_date'] = date_span.text if date_span else ''
        
        category_span = meta_div.find('span', class_='category')
        news_data['category'] = category_span.text if category_span else ''
        
        # 提取阅读量
        views_span = meta_div.find('span', class_='views')
        if views_span:
            views_text = views_span.text
            views_numbers = extractor.extract_numbers(views_text)
            news_data['views'] = int(views_numbers[0]) if views_numbers else 0
        
        # 提取摘要
        summary_p = article.find('p', class_='summary')
        news_data['summary'] = extractor.clean_text(summary_p.text) if summary_p else ''
        
        # 提取标签
        tags_div = article.find('div', class_='tags')
        if tags_div:
            tag_spans = tags_div.find_all('span', class_='tag')
            news_data['tags'] = [tag.text for tag in tag_spans]
        else:
            news_data['tags'] = []
        
        news_list.append(news_data)
    
    # 显示提取的数据
    for news in news_list:
        print(f"ID: {news['id']}")
        print(f"标题: {news['title']}")
        print(f"作者: {news['author']}")
        print(f"发布时间: {news['publish_date']}")
        print(f"分类: {news['category']}")
        print(f"阅读量: {news['views']}")
        print(f"标签: {', '.join(news['tags'])}")
        print(f"摘要: {news['summary'][:50]}...")
        print("-" * 50)
    
    return news_list


def extract_product_data():
    """
    商品数据提取示例
    演示如何从电商网站提取商品信息
    """
    print("\n=== 商品数据提取示例 ===")
    
    html_content = """
    <div class="product-grid">
        <div class="product-card" data-product-id="P001">
            <div class="product-image">
                <img src="/images/laptop1.jpg" alt="笔记本电脑">
            </div>
            <div class="product-info">
                <h3 class="product-name">高性能游戏笔记本</h3>
                <div class="price-info">
                    <span class="current-price">¥8,999</span>
                    <span class="original-price">¥9,999</span>
                    <span class="discount">9折</span>
                </div>
                <div class="rating">
                    <span class="stars">★★★★☆</span>
                    <span class="rating-count">(128评价)</span>
                </div>
                <div class="specs">
                    <span class="spec">Intel i7</span>
                    <span class="spec">16GB内存</span>
                    <span class="spec">512GB SSD</span>
                </div>
                <div class="seller">
                    <span>商家: 科技数码专营店</span>
                    <span class="location">发货地: 北京</span>
                </div>
            </div>
        </div>
        
        <div class="product-card" data-product-id="P002">
            <div class="product-image">
                <img src="/images/phone1.jpg" alt="智能手机">
            </div>
            <div class="product-info">
                <h3 class="product-name">5G智能手机</h3>
                <div class="price-info">
                    <span class="current-price">¥3,299</span>
                    <span class="original-price">¥3,599</span>
                    <span class="discount">8.5折</span>
                </div>
                <div class="rating">
                    <span class="stars">★★★★★</span>
                    <span class="rating-count">(256评价)</span>
                </div>
                <div class="specs">
                    <span class="spec">6.5英寸屏幕</span>
                    <span class="spec">128GB存储</span>
                    <span class="spec">5000mAh电池</span>
                </div>
                <div class="seller">
                    <span>商家: 手机官方旗舰店</span>
                    <span class="location">发货地: 深圳</span>
                </div>
            </div>
        </div>
    </div>
    """
    
    extractor = DataExtractor()
    soup = extractor.parse_html(html_content)
    
    products = []
    
    # 提取商品信息
    product_cards = soup.find_all('div', class_='product-card')
    
    for card in product_cards:
        product = {}
        
        # 基本信息
        product['id'] = card.get('data-product-id')
        
        # 商品名称
        name_elem = card.find('h3', class_='product-name')
        product['name'] = extractor.clean_text(name_elem.text) if name_elem else ''
        
        # 图片信息
        img_elem = card.find('img')
        if img_elem:
            product['image_url'] = img_elem.get('src')
            product['image_alt'] = img_elem.get('alt')
        
        # 价格信息
        price_info = card.find('div', class_='price-info')
        if price_info:
            current_price_elem = price_info.find('span', class_='current-price')
            if current_price_elem:
                price_text = current_price_elem.text
                price_numbers = extractor.extract_numbers(price_text)
                product['current_price'] = price_numbers[0] if price_numbers else 0
            
            original_price_elem = price_info.find('span', class_='original-price')
            if original_price_elem:
                price_text = original_price_elem.text
                price_numbers = extractor.extract_numbers(price_text)
                product['original_price'] = price_numbers[0] if price_numbers else 0
            
            discount_elem = price_info.find('span', class_='discount')
            product['discount'] = discount_elem.text if discount_elem else ''
        
        # 评分信息
        rating_div = card.find('div', class_='rating')
        if rating_div:
            stars_elem = rating_div.find('span', class_='stars')
            if stars_elem:
                star_count = stars_elem.text.count('★')
                product['rating'] = star_count
            
            rating_count_elem = rating_div.find('span', class_='rating-count')
            if rating_count_elem:
                count_text = rating_count_elem.text
                count_numbers = extractor.extract_numbers(count_text)
                product['rating_count'] = int(count_numbers[0]) if count_numbers else 0
        
        # 规格信息
        specs_div = card.find('div', class_='specs')
        if specs_div:
            spec_spans = specs_div.find_all('span', class_='spec')
            product['specs'] = [spec.text for spec in spec_spans]
        
        # 商家信息
        seller_div = card.find('div', class_='seller')
        if seller_div:
            seller_spans = seller_div.find_all('span')
            for span in seller_spans:
                text = span.text
                if '商家:' in text:
                    product['seller'] = text.replace('商家: ', '')
                elif '发货地:' in text:
                    product['location'] = text.replace('发货地: ', '')
        
        products.append(product)
    
    # 显示提取的数据
    for product in products:
        print(f"商品ID: {product['id']}")
        print(f"商品名称: {product['name']}")
        print(f"当前价格: ¥{product.get('current_price', 0)}")
        print(f"原价: ¥{product.get('original_price', 0)}")
        print(f"评分: {product.get('rating', 0)}星")
        print(f"评价数: {product.get('rating_count', 0)}")
        print(f"规格: {', '.join(product.get('specs', []))}")
        print(f"商家: {product.get('seller', '')}")
        print("-" * 50)
    
    return products


def save_to_json(data, filename):
    """
    保存数据到 JSON 文件
    """
    print(f"\n=== 保存数据到 JSON: {filename} ===")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filename}")
        
        # 显示文件大小
        file_size = os.path.getsize(filename)
        print(f"文件大小: {file_size} 字节")
        
    except Exception as e:
        print(f"保存 JSON 文件失败: {e}")


def save_to_csv(data, filename):
    """
    保存数据到 CSV 文件
    """
    print(f"\n=== 保存数据到 CSV: {filename} ===")
    
    if not data:
        print("没有数据可保存")
        return
    
    try:
        # 获取所有字段名
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in data:
                # 处理列表类型的字段
                row = {}
                for key, value in item.items():
                    if isinstance(value, list):
                        row[key] = ', '.join(map(str, value))
                    else:
                        row[key] = value
                writer.writerow(row)
        
        print(f"数据已保存到 {filename}")
        print(f"字段: {', '.join(fieldnames)}")
        
    except Exception as e:
        print(f"保存 CSV 文件失败: {e}")


def save_to_database(data, db_name, table_name):
    """
    保存数据到 SQLite 数据库
    """
    print(f"\n=== 保存数据到数据库: {db_name} ===")
    
    if not data:
        print("没有数据可保存")
        return
    
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # 创建表（简化版本，实际应用中需要更仔细的字段定义）
        if table_name == 'news':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    publish_date TEXT,
                    category TEXT,
                    views INTEGER,
                    summary TEXT,
                    tags TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入数据
            for item in data:
                cursor.execute('''
                    INSERT OR REPLACE INTO news 
                    (id, title, author, publish_date, category, views, summary, tags, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('id'),
                    item.get('title'),
                    item.get('author'),
                    item.get('publish_date'),
                    item.get('category'),
                    item.get('views', 0),
                    item.get('summary'),
                    ', '.join(item.get('tags', [])),
                    item.get('url')
                ))
        
        elif table_name == 'products':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    current_price REAL,
                    original_price REAL,
                    discount TEXT,
                    rating INTEGER,
                    rating_count INTEGER,
                    specs TEXT,
                    seller TEXT,
                    location TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入数据
            for item in data:
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (id, name, current_price, original_price, discount, rating, 
                     rating_count, specs, seller, location, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('id'),
                    item.get('name'),
                    item.get('current_price', 0),
                    item.get('original_price', 0),
                    item.get('discount'),
                    item.get('rating', 0),
                    item.get('rating_count', 0),
                    ', '.join(item.get('specs', [])),
                    item.get('seller'),
                    item.get('location'),
                    item.get('image_url')
                ))
        
        conn.commit()
        
        # 查询插入的记录数
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f"数据已保存到数据库，表 {table_name} 共有 {count} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"保存到数据库失败: {e}")


def save_to_excel(data, filename):
    """
    保存数据到 Excel 文件
    """
    print(f"\n=== 保存数据到 Excel: {filename} ===")
    
    if not data:
        print("没有数据可保存")
        return
    
    try:
        # 使用 pandas 创建 DataFrame
        df = pd.DataFrame(data)
        
        # 处理列表类型的列
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        # 保存到 Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"数据已保存到 {filename}")
        print(f"数据形状: {df.shape}")
        print(f"列名: {', '.join(df.columns)}")
        
    except ImportError:
        print("需要安装 openpyxl: pip install openpyxl")
    except Exception as e:
        print(f"保存 Excel 文件失败: {e}")


def data_analysis_example(data):
    """
    数据分析示例
    演示如何对提取的数据进行简单分析
    """
    print("\n=== 数据分析示例 ===")
    
    if not data:
        print("没有数据可分析")
        return
    
    try:
        df = pd.DataFrame(data)
        
        print(f"数据总数: {len(df)}")
        print(f"数据列: {', '.join(df.columns)}")
        
        # 如果是商品数据
        if 'current_price' in df.columns:
            print(f"价格统计:")
            print(f"  平均价格: ¥{df['current_price'].mean():.2f}")
            print(f"  最高价格: ¥{df['current_price'].max():.2f}")
            print(f"  最低价格: ¥{df['current_price'].min():.2f}")
            
            if 'rating' in df.columns:
                print(f"评分统计:")
                print(f"  平均评分: {df['rating'].mean():.1f}星")
                print(f"  最高评分: {df['rating'].max()}星")
        
        # 如果是新闻数据
        if 'views' in df.columns:
            print(f"阅读量统计:")
            print(f"  平均阅读量: {df['views'].mean():.0f}")
            print(f"  最高阅读量: {df['views'].max()}")
            
            if 'category' in df.columns:
                print(f"分类统计:")
                category_counts = df['category'].value_counts()
                for category, count in category_counts.items():
                    print(f"  {category}: {count}篇")
        
    except Exception as e:
        print(f"数据分析失败: {e}")


def main():
    """
    主函数，运行所有示例
    """
    print("数据提取与存储教程")
    print("=" * 50)
    
    try:
        # 创建输出目录
        os.makedirs('output', exist_ok=True)
        
        # 提取新闻数据
        news_data = extract_news_data()
        
        # 提取商品数据
        product_data = extract_product_data()
        
        # 保存数据到不同格式
        if news_data:
            save_to_json(news_data, 'output/news_data.json')
            save_to_csv(news_data, 'output/news_data.csv')
            save_to_database(news_data, 'output/scraped_data.db', 'news')
            save_to_excel(news_data, 'output/news_data.xlsx')
            data_analysis_example(news_data)
        
        if product_data:
            save_to_json(product_data, 'output/product_data.json')
            save_to_csv(product_data, 'output/product_data.csv')
            save_to_database(product_data, 'output/scraped_data.db', 'products')
            save_to_excel(product_data, 'output/product_data.xlsx')
            data_analysis_example(product_data)
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. 数据提取策略
   - 识别数据结构和模式
   - 设计提取规则
   - 处理异常情况
   - 数据验证和清理

2. 文本处理技巧
   - 去除多余空白字符
   - 正则表达式应用
   - 编码问题处理
   - 特殊字符处理

3. 数据存储格式
   - JSON: 保持数据结构，适合 API 交互
   - CSV: 表格数据，易于分析
   - SQLite: 关系型数据，支持查询
   - Excel: 可视化友好，支持复杂格式

4. 数据质量保证
   - 数据类型转换
   - 缺失值处理
   - 重复数据去除
   - 数据一致性检查

5. 性能优化
   - 批量处理
   - 内存管理
   - 异常处理
   - 进度监控

练习建议:
1. 尝试提取不同类型的网站数据
2. 实现数据去重和清理功能
3. 设计通用的数据提取框架
4. 练习不同存储格式的转换
5. 实现数据质量检查功能
"""