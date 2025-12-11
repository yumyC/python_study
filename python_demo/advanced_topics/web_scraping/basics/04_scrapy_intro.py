#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapy 框架入门教程

本教程介绍 Scrapy 爬虫框架的基础使用方法。
Scrapy 是一个专业的爬虫框架，提供了完整的爬虫开发解决方案。

作者: Python学习课程
日期: 2024

注意: 本文件主要用于演示 Scrapy 的概念和代码结构
实际运行需要创建完整的 Scrapy 项目
"""

import scrapy
from scrapy import Request, Spider
from scrapy.http import Response
import json
import re
from urllib.parse import urljoin


class BasicSpider(scrapy.Spider):
    """
    基础爬虫示例
    演示 Scrapy Spider 的基本结构和方法
    """
    
    # 爬虫名称，必须唯一
    name = 'basic_spider'
    
    # 允许的域名列表
    allowed_domains = ['example.com']
    
    # 起始 URL 列表
    start_urls = [
        'https://example.com/page1',
        'https://example.com/page2',
    ]
    
    # 自定义设置
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # 下载延迟
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # 随机延迟
        'USER_AGENT': 'BasicSpider 1.0',
    }
    
    def parse(self, response):
        """
        默认的响应处理方法
        处理 start_urls 中 URL 的响应
        """
        # 提取页面标题
        title = response.css('title::text').get()
        
        # 提取所有链接
        links = response.css('a::attr(href)').getall()
        
        # 返回数据项
        yield {
            'url': response.url,
            'title': title,
            'links_count': len(links),
            'timestamp': response.meta.get('download_timestamp')
        }
        
        # 跟进链接
        for link in links:
            if link.startswith('/'):
                # 处理相对链接
                full_url = urljoin(response.url, link)
                yield Request(
                    url=full_url,
                    callback=self.parse_detail,
                    meta={'parent_url': response.url}
                )
    
    def parse_detail(self, response):
        """
        详情页面解析方法
        """
        # 提取详情页面的内容
        content = response.css('div.content::text').getall()
        
        yield {
            'url': response.url,
            'parent_url': response.meta.get('parent_url'),
            'content': ' '.join(content).strip(),
            'word_count': len(' '.join(content).split())
        }


class NewsSpider(scrapy.Spider):
    """
    新闻爬虫示例
    演示如何爬取新闻网站的数据
    """
    
    name = 'news_spider'
    allowed_domains = ['news.example.com']
    
    def start_requests(self):
        """
        生成初始请求
        可以自定义请求参数
        """
        urls = [
            'https://news.example.com/tech',
            'https://news.example.com/business',
            'https://news.example.com/sports',
        ]
        
        for url in urls:
            yield Request(
                url=url,
                callback=self.parse_category,
                meta={'category': url.split('/')[-1]}
            )
    
    def parse_category(self, response):
        """
        解析分类页面
        """
        category = response.meta['category']
        
        # 提取新闻列表
        news_items = response.css('div.news-item')
        
        for item in news_items:
            # 提取新闻链接
            news_url = item.css('a::attr(href)').get()
            if news_url:
                yield Request(
                    url=urljoin(response.url, news_url),
                    callback=self.parse_news,
                    meta={'category': category}
                )
        
        # 处理分页
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield Request(
                url=urljoin(response.url, next_page),
                callback=self.parse_category,
                meta={'category': category}
            )
    
    def parse_news(self, response):
        """
        解析新闻详情页
        """
        # 提取新闻数据
        title = response.css('h1.title::text').get()
        author = response.css('span.author::text').get()
        publish_date = response.css('span.date::text').get()
        content_paragraphs = response.css('div.content p::text').getall()
        tags = response.css('div.tags span.tag::text').getall()
        
        # 清理和处理数据
        content = '\n'.join(content_paragraphs).strip()
        
        # 提取阅读量（如果有）
        views_text = response.css('span.views::text').get()
        views = 0
        if views_text:
            views_match = re.search(r'(\d+)', views_text)
            if views_match:
                views = int(views_match.group(1))
        
        yield {
            'url': response.url,
            'title': title,
            'author': author,
            'publish_date': publish_date,
            'category': response.meta['category'],
            'content': content,
            'tags': tags,
            'views': views,
            'word_count': len(content.split()) if content else 0
        }


class EcommerceSpider(scrapy.Spider):
    """
    电商爬虫示例
    演示如何爬取商品信息
    """
    
    name = 'ecommerce_spider'
    allowed_domains = ['shop.example.com']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,  # 降低并发请求
        'AUTOTHROTTLE_ENABLED': True,  # 启用自动限速
    }
    
    def start_requests(self):
        """
        生成商品分类页面的请求
        """
        categories = [
            'electronics',
            'clothing',
            'books',
            'home-garden'
        ]
        
        for category in categories:
            url = f'https://shop.example.com/category/{category}'
            yield Request(
                url=url,
                callback=self.parse_category,
                meta={'category': category}
            )
    
    def parse_category(self, response):
        """
        解析商品分类页面
        """
        # 提取商品链接
        product_links = response.css('div.product-item a::attr(href)').getall()
        
        for link in product_links:
            yield Request(
                url=urljoin(response.url, link),
                callback=self.parse_product,
                meta={'category': response.meta['category']}
            )
        
        # 处理分页
        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page:
            yield Request(
                url=urljoin(response.url, next_page),
                callback=self.parse_category,
                meta={'category': response.meta['category']}
            )
    
    def parse_product(self, response):
        """
        解析商品详情页
        """
        # 提取商品基本信息
        name = response.css('h1.product-name::text').get()
        price_text = response.css('span.current-price::text').get()
        original_price_text = response.css('span.original-price::text').get()
        
        # 处理价格
        price = self.extract_price(price_text)
        original_price = self.extract_price(original_price_text)
        
        # 提取评分信息
        rating_stars = len(response.css('div.rating span.star.filled'))
        rating_count_text = response.css('span.rating-count::text').get()
        rating_count = self.extract_number(rating_count_text)
        
        # 提取商品描述
        description_parts = response.css('div.description p::text').getall()
        description = '\n'.join(description_parts).strip()
        
        # 提取商品规格
        specs = {}
        spec_rows = response.css('table.specs tr')
        for row in spec_rows:
            key = row.css('td.spec-key::text').get()
            value = row.css('td.spec-value::text').get()
            if key and value:
                specs[key.strip()] = value.strip()
        
        # 提取商品图片
        image_urls = response.css('div.product-images img::attr(src)').getall()
        image_urls = [urljoin(response.url, url) for url in image_urls]
        
        # 提取库存信息
        stock_text = response.css('span.stock-info::text').get()
        in_stock = 'in stock' in stock_text.lower() if stock_text else False
        
        yield {
            'url': response.url,
            'name': name,
            'category': response.meta['category'],
            'price': price,
            'original_price': original_price,
            'discount_percent': self.calculate_discount(price, original_price),
            'rating': rating_stars,
            'rating_count': rating_count,
            'description': description,
            'specs': specs,
            'image_urls': image_urls,
            'in_stock': in_stock,
            'scraped_at': response.meta.get('download_timestamp')
        }
    
    def extract_price(self, price_text):
        """提取价格数字"""
        if not price_text:
            return 0
        
        # 使用正则表达式提取数字
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        return float(price_match.group()) if price_match else 0
    
    def extract_number(self, text):
        """提取文本中的数字"""
        if not text:
            return 0
        
        number_match = re.search(r'\d+', text)
        return int(number_match.group()) if number_match else 0
    
    def calculate_discount(self, current_price, original_price):
        """计算折扣百分比"""
        if not original_price or original_price <= current_price:
            return 0
        
        return round((1 - current_price / original_price) * 100, 1)


class ScrapyPipeline:
    """
    Scrapy 管道示例
    用于处理爬取的数据项
    """
    
    def __init__(self):
        self.items_count = 0
        self.duplicate_urls = set()
    
    def open_spider(self, spider):
        """爬虫开始时调用"""
        spider.logger.info(f"Spider {spider.name} started")
        self.items_count = 0
    
    def close_spider(self, spider):
        """爬虫结束时调用"""
        spider.logger.info(f"Spider {spider.name} finished. Processed {self.items_count} items")
    
    def process_item(self, item, spider):
        """处理每个数据项"""
        # 去重检查
        if item.get('url') in self.duplicate_urls:
            spider.logger.warning(f"Duplicate item found: {item.get('url')}")
            return item
        
        self.duplicate_urls.add(item.get('url'))
        
        # 数据清理
        if 'title' in item:
            item['title'] = item['title'].strip() if item['title'] else ''
        
        if 'content' in item:
            item['content'] = item['content'].strip() if item['content'] else ''
        
        # 数据验证
        if not item.get('url'):
            spider.logger.error("Item missing URL")
            return item
        
        self.items_count += 1
        return item


class JsonWriterPipeline:
    """
    JSON 文件写入管道
    """
    
    def open_spider(self, spider):
        self.file = open(f'{spider.name}_items.json', 'w', encoding='utf-8')
    
    def close_spider(self, spider):
        self.file.close()
    
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item


# Scrapy 设置示例
SCRAPY_SETTINGS = {
    # 基本设置
    'BOT_NAME': 'web_scraping_tutorial',
    'SPIDER_MODULES': ['spiders'],
    'NEWSPIDER_MODULE': 'spiders',
    
    # 下载设置
    'DOWNLOAD_DELAY': 1,
    'RANDOMIZE_DOWNLOAD_DELAY': True,
    'CONCURRENT_REQUESTS': 16,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    
    # 用户代理
    'USER_AGENT': 'web_scraping_tutorial (+http://www.yourdomain.com)',
    
    # 遵守 robots.txt
    'ROBOTSTXT_OBEY': True,
    
    # 管道设置
    'ITEM_PIPELINES': {
        'pipelines.ScrapyPipeline': 300,
        'pipelines.JsonWriterPipeline': 800,
    },
    
    # 自动限速
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 1,
    'AUTOTHROTTLE_MAX_DELAY': 60,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    
    # 缓存设置
    'HTTPCACHE_ENABLED': True,
    'HTTPCACHE_EXPIRATION_SECS': 3600,
    
    # 日志设置
    'LOG_LEVEL': 'INFO',
}


def create_scrapy_project():
    """
    创建 Scrapy 项目的命令示例
    """
    commands = [
        "# 安装 Scrapy",
        "pip install scrapy",
        "",
        "# 创建新项目",
        "scrapy startproject web_scraping_tutorial",
        "",
        "# 进入项目目录",
        "cd web_scraping_tutorial",
        "",
        "# 创建爬虫",
        "scrapy genspider news_spider news.example.com",
        "",
        "# 运行爬虫",
        "scrapy crawl news_spider",
        "",
        "# 保存数据到文件",
        "scrapy crawl news_spider -o output.json",
        "scrapy crawl news_spider -o output.csv",
        "",
        "# 使用自定义设置运行",
        "scrapy crawl news_spider -s DOWNLOAD_DELAY=2",
        "",
        "# 查看爬虫列表",
        "scrapy list",
        "",
        "# 检查爬虫代码",
        "scrapy check news_spider",
    ]
    
    return '\n'.join(commands)


def scrapy_best_practices():
    """
    Scrapy 最佳实践指南
    """
    practices = {
        "项目结构": [
            "合理组织爬虫文件",
            "使用 items.py 定义数据结构",
            "在 pipelines.py 中处理数据",
            "在 middlewares.py 中处理请求/响应",
            "使用 settings.py 管理配置"
        ],
        
        "性能优化": [
            "设置合理的并发数",
            "使用下载延迟避免被封",
            "启用自动限速功能",
            "使用缓存减少重复请求",
            "合理设置超时时间"
        ],
        
        "数据质量": [
            "在 Items 中定义字段验证",
            "使用 Pipeline 清理数据",
            "实现去重机制",
            "处理编码问题",
            "验证数据完整性"
        ],
        
        "错误处理": [
            "处理网络异常",
            "处理解析错误",
            "实现重试机制",
            "记录详细日志",
            "监控爬虫状态"
        ],
        
        "反爬应对": [
            "轮换 User-Agent",
            "使用代理池",
            "控制请求频率",
            "处理验证码",
            "模拟真实用户行为"
        ]
    }
    
    return practices


def main():
    """
    主函数，展示 Scrapy 相关信息
    """
    print("Scrapy 框架入门教程")
    print("=" * 50)
    
    print("\n=== 创建 Scrapy 项目 ===")
    print(create_scrapy_project())
    
    print("\n=== Scrapy 最佳实践 ===")
    practices = scrapy_best_practices()
    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item}")
    
    print("\n=== 重要提示 ===")
    print("1. 本文件仅用于演示 Scrapy 的代码结构")
    print("2. 实际使用需要创建完整的 Scrapy 项目")
    print("3. 运行命令: scrapy startproject your_project_name")
    print("4. 然后将相应的代码放入对应的文件中")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. Scrapy 核心概念
   - Spider: 定义爬取逻辑
   - Item: 定义数据结构
   - Pipeline: 处理数据项
   - Middleware: 处理请求和响应
   - Settings: 配置管理

2. Spider 开发
   - 继承 scrapy.Spider 类
   - 定义 name、allowed_domains、start_urls
   - 实现 parse 方法处理响应
   - 使用 yield 返回数据和请求

3. 数据提取
   - CSS 选择器: response.css()
   - XPath 选择器: response.xpath()
   - 提取文本: ::text
   - 提取属性: ::attr(name)

4. 请求处理
   - 使用 Request 对象发送请求
   - 通过 meta 传递数据
   - 设置回调函数处理响应
   - 处理相对链接和绝对链接

5. 高级功能
   - 自定义设置
   - 数据管道处理
   - 中间件开发
   - 自动限速
   - 缓存机制

实际使用步骤:
1. 安装 Scrapy: pip install scrapy
2. 创建项目: scrapy startproject project_name
3. 创建爬虫: scrapy genspider spider_name domain.com
4. 编写爬虫逻辑
5. 运行爬虫: scrapy crawl spider_name
6. 保存数据: scrapy crawl spider_name -o output.json

注意事项:
- 遵守 robots.txt 协议
- 设置合理的下载延迟
- 处理反爬机制
- 监控爬虫性能
- 确保数据质量
"""