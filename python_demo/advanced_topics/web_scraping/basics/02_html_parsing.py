#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 解析教程

本教程介绍如何使用 BeautifulSoup 和 lxml 解析 HTML 内容。
涵盖元素选择、属性提取、文本处理等核心技能。

作者: Python学习课程
日期: 2024
"""

import requests
from bs4 import BeautifulSoup
import lxml.html
import re
from urllib.parse import urljoin


def basic_beautifulsoup():
    """
    BeautifulSoup 基础使用
    演示如何解析 HTML 并提取基本信息
    """
    print("=== BeautifulSoup 基础使用 ===")
    
    # 示例 HTML 内容
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>示例网页</title>
        <meta charset="utf-8">
    </head>
    <body>
        <div class="header">
            <h1 id="main-title">欢迎来到我的网站</h1>
            <nav>
                <ul>
                    <li><a href="/home">首页</a></li>
                    <li><a href="/about">关于我们</a></li>
                    <li><a href="/contact">联系我们</a></li>
                </ul>
            </nav>
        </div>
        <div class="content">
            <article class="post" data-id="1">
                <h2>第一篇文章</h2>
                <p class="meta">作者: 张三 | 日期: 2024-01-01</p>
                <p>这是文章的内容...</p>
                <div class="tags">
                    <span class="tag">Python</span>
                    <span class="tag">爬虫</span>
                </div>
            </article>
            <article class="post" data-id="2">
                <h2>第二篇文章</h2>
                <p class="meta">作者: 李四 | 日期: 2024-01-02</p>
                <p>这是另一篇文章的内容...</p>
                <div class="tags">
                    <span class="tag">Web开发</span>
                    <span class="tag">JavaScript</span>
                </div>
            </article>
        </div>
    </body>
    </html>
    """
    
    # 创建 BeautifulSoup 对象
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取标题
    title = soup.find('title').text
    print(f"网页标题: {title}")
    
    # 提取主标题
    main_title = soup.find('h1', id='main-title').text
    print(f"主标题: {main_title}")
    
    # 提取所有链接
    links = soup.find_all('a')
    print("导航链接:")
    for link in links:
        href = link.get('href')
        text = link.text
        print(f"  {text}: {href}")


def css_selectors():
    """
    CSS 选择器使用
    演示如何使用 CSS 选择器精确定位元素
    """
    print("\n=== CSS 选择器使用 ===")
    
    html_content = """
    <div class="container">
        <div class="sidebar">
            <ul class="menu">
                <li class="menu-item active"><a href="#home">首页</a></li>
                <li class="menu-item"><a href="#news">新闻</a></li>
                <li class="menu-item"><a href="#about">关于</a></li>
            </ul>
        </div>
        <div class="main-content">
            <h1>新闻列表</h1>
            <div class="news-list">
                <div class="news-item" data-category="tech">
                    <h3>技术新闻标题</h3>
                    <p class="summary">技术新闻摘要...</p>
                    <span class="date">2024-01-01</span>
                </div>
                <div class="news-item" data-category="business">
                    <h3>商业新闻标题</h3>
                    <p class="summary">商业新闻摘要...</p>
                    <span class="date">2024-01-02</span>
                </div>
            </div>
        </div>
    </div>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 使用类选择器
    menu_items = soup.select('.menu-item')
    print(f"菜单项数量: {len(menu_items)}")
    
    # 使用属性选择器
    active_item = soup.select('.menu-item.active')[0]
    print(f"当前活跃菜单: {active_item.text}")
    
    # 使用后代选择器
    news_titles = soup.select('.news-list h3')
    print("新闻标题:")
    for title in news_titles:
        print(f"  {title.text}")
    
    # 使用属性选择器
    tech_news = soup.select('.news-item[data-category="tech"]')
    print(f"技术新闻数量: {len(tech_news)}")


def extract_attributes():
    """
    属性提取示例
    演示如何提取元素的各种属性
    """
    print("\n=== 属性提取 ===")
    
    html_content = """
    <div class="product-list">
        <div class="product" data-id="1" data-price="99.99">
            <img src="/images/product1.jpg" alt="产品1" width="200" height="150">
            <h3>产品名称1</h3>
            <p class="price">¥99.99</p>
            <a href="/product/1" class="btn btn-primary">查看详情</a>
        </div>
        <div class="product" data-id="2" data-price="199.99">
            <img src="/images/product2.jpg" alt="产品2" width="200" height="150">
            <h3>产品名称2</h3>
            <p class="price">¥199.99</p>
            <a href="/product/2" class="btn btn-primary">查看详情</a>
        </div>
    </div>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    products = soup.find_all('div', class_='product')
    
    for product in products:
        # 提取数据属性
        product_id = product.get('data-id')
        price = product.get('data-price')
        
        # 提取图片信息
        img = product.find('img')
        img_src = img.get('src')
        img_alt = img.get('alt')
        
        # 提取链接
        link = product.find('a')
        link_href = link.get('href')
        
        # 提取文本内容
        name = product.find('h3').text
        
        print(f"产品 ID: {product_id}")
        print(f"产品名称: {name}")
        print(f"价格: {price}")
        print(f"图片: {img_src} (alt: {img_alt})")
        print(f"详情链接: {link_href}")
        print("-" * 30)


def text_processing():
    """
    文本处理示例
    演示如何清理和处理提取的文本内容
    """
    print("\n=== 文本处理 ===")
    
    html_content = """
    <div class="article">
        <h1>   文章标题   </h1>
        <div class="meta">
            发布时间: <span class="date">2024-01-01 10:30:00</span>
            作者: <span class="author">张三</span>
        </div>
        <div class="content">
            <p>这是第一段内容。</p>
            <p>这是第二段内容，包含<strong>重要信息</strong>。</p>
            <p>联系电话: 138-0000-0000</p>
            <p>邮箱: example@email.com</p>
        </div>
        <div class="footer">
            <span>阅读量: 1,234</span>
            <span>点赞数: 56</span>
        </div>
    </div>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取并清理标题
    title = soup.find('h1').text.strip()
    print(f"标题: '{title}'")
    
    # 提取日期和作者
    date = soup.find('span', class_='date').text
    author = soup.find('span', class_='author').text
    print(f"发布时间: {date}")
    print(f"作者: {author}")
    
    # 提取所有段落文本
    paragraphs = soup.find_all('p')
    content = []
    for p in paragraphs:
        text = p.get_text().strip()
        if text:
            content.append(text)
    
    print("文章内容:")
    for i, paragraph in enumerate(content, 1):
        print(f"  {i}. {paragraph}")
    
    # 使用正则表达式提取特定信息
    full_text = ' '.join(content)
    
    # 提取电话号码
    phone_pattern = r'1[3-9]\d{1}-\d{4}-\d{4}'
    phones = re.findall(phone_pattern, full_text)
    print(f"电话号码: {phones}")
    
    # 提取邮箱
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, full_text)
    print(f"邮箱地址: {emails}")


def lxml_usage():
    """
    lxml 库使用示例
    演示 lxml 的高性能 HTML 解析能力
    """
    print("\n=== lxml 库使用 ===")
    
    html_content = """
    <html>
    <body>
        <div class="container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>姓名</th>
                        <th>年龄</th>
                        <th>城市</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>张三</td>
                        <td>25</td>
                        <td>北京</td>
                    </tr>
                    <tr>
                        <td>李四</td>
                        <td>30</td>
                        <td>上海</td>
                    </tr>
                    <tr>
                        <td>王五</td>
                        <td>28</td>
                        <td>广州</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    # 使用 lxml 解析
    doc = lxml.html.fromstring(html_content)
    
    # 使用 XPath 选择器
    table_rows = doc.xpath('//tbody/tr')
    
    print("表格数据:")
    for row in table_rows:
        cells = row.xpath('.//td/text()')
        name, age, city = cells
        print(f"  姓名: {name}, 年龄: {age}, 城市: {city}")
    
    # XPath 的强大功能
    # 选择第二行的数据
    second_row = doc.xpath('//tbody/tr[2]//td/text()')
    print(f"第二行数据: {second_row}")
    
    # 选择年龄大于 25 的行（需要更复杂的逻辑）
    all_ages = doc.xpath('//tbody/tr/td[2]/text()')
    print(f"所有年龄: {all_ages}")


def real_website_example():
    """
    真实网站解析示例
    演示如何解析真实网站的内容
    """
    print("\n=== 真实网站解析示例 ===")
    
    try:
        # 获取网页内容
        url = "https://httpbin.org/html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 提取标题
        title = soup.find('title')
        if title:
            print(f"网页标题: {title.text}")
        
        # 提取所有链接
        links = soup.find_all('a', href=True)
        print(f"找到 {len(links)} 个链接:")
        for link in links[:5]:  # 只显示前5个
            href = link['href']
            text = link.text.strip()
            # 处理相对链接
            full_url = urljoin(url, href)
            print(f"  {text}: {full_url}")
        
        # 提取所有图片
        images = soup.find_all('img', src=True)
        print(f"找到 {len(images)} 个图片:")
        for img in images[:3]:  # 只显示前3个
            src = img['src']
            alt = img.get('alt', '无描述')
            full_url = urljoin(url, src)
            print(f"  {alt}: {full_url}")
            
    except requests.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"解析失败: {e}")


def advanced_parsing():
    """
    高级解析技巧
    演示一些高级的 HTML 解析技巧
    """
    print("\n=== 高级解析技巧 ===")
    
    html_content = """
    <div class="complex-structure">
        <div class="item" data-type="news">
            <h3>新闻标题1</h3>
            <div class="nested">
                <span class="category">科技</span>
                <span class="views">1000</span>
            </div>
        </div>
        <div class="item" data-type="blog">
            <h3>博客标题1</h3>
            <div class="nested">
                <span class="category">技术</span>
                <span class="views">500</span>
            </div>
        </div>
        <!-- 注释内容 -->
        <script>
            var data = {
                "items": [
                    {"id": 1, "name": "item1"},
                    {"id": 2, "name": "item2"}
                ]
            };
        </script>
    </div>
    """
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. 使用 lambda 函数进行复杂筛选
    news_items = soup.find_all(lambda tag: tag.name == 'div' and 
                              tag.get('class') == ['item'] and 
                              tag.get('data-type') == 'news')
    print(f"新闻类型的项目: {len(news_items)}")
    
    # 2. 提取 JavaScript 中的数据
    script_tag = soup.find('script')
    if script_tag:
        script_content = script_tag.string
        # 使用正则表达式提取 JSON 数据
        json_pattern = r'var data = ({.*?});'
        match = re.search(json_pattern, script_content, re.DOTALL)
        if match:
            print(f"脚本中的数据: {match.group(1)}")
    
    # 3. 处理嵌套结构
    items = soup.find_all('div', class_='item')
    for item in items:
        title = item.find('h3').text
        category = item.find('span', class_='category').text
        views = item.find('span', class_='views').text
        item_type = item.get('data-type')
        
        print(f"类型: {item_type}, 标题: {title}, 分类: {category}, 浏览量: {views}")
    
    # 4. 使用 CSS 选择器的高级功能
    # 选择第一个 item
    first_item = soup.select('.item:first-child')[0]
    print(f"第一个项目的标题: {first_item.find('h3').text}")
    
    # 选择包含特定文本的元素
    tech_items = soup.find_all(text=re.compile('技术'))
    print(f"包含'技术'的文本: {[text.strip() for text in tech_items]}")


def main():
    """
    主函数，运行所有示例
    """
    print("HTML 解析教程")
    print("=" * 50)
    
    try:
        basic_beautifulsoup()
        css_selectors()
        extract_attributes()
        text_processing()
        lxml_usage()
        real_website_example()
        advanced_parsing()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. BeautifulSoup 基础
   - 创建解析器对象
   - 使用 find() 和 find_all() 方法
   - CSS 选择器的使用

2. 元素定位方法
   - 按标签名定位
   - 按类名和 ID 定位
   - 按属性定位
   - 使用 CSS 选择器

3. 数据提取技巧
   - 提取文本内容
   - 提取属性值
   - 处理嵌套结构
   - 清理和格式化文本

4. 高级功能
   - 正则表达式结合使用
   - XPath 选择器（lxml）
   - 处理 JavaScript 内容
   - 复杂条件筛选

5. 最佳实践
   - 选择合适的解析器
   - 处理编码问题
   - 异常处理
   - 性能优化

练习建议:
1. 尝试解析不同结构的网页
2. 练习各种 CSS 选择器
3. 实现一个通用的数据提取函数
4. 处理包含 JavaScript 的页面
"""