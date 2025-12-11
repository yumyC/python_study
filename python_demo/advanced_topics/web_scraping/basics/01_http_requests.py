#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 请求基础教程

本教程介绍如何使用 Python 进行 HTTP 请求，这是爬虫开发的基础。
涵盖 GET、POST 请求，请求头设置，参数传递等核心概念。

作者: Python学习课程
日期: 2024
"""

import requests
import json
from urllib.parse import urljoin, urlparse
import time


def basic_get_request():
    """
    基础 GET 请求示例
    演示如何发送简单的 GET 请求并处理响应
    """
    print("=== 基础 GET 请求 ===")
    
    # 发送 GET 请求
    url = "https://httpbin.org/get"
    response = requests.get(url)
    
    # 检查响应状态
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text[:200]}...")
    
    # JSON 响应处理
    if response.headers.get('content-type', '').startswith('application/json'):
        data = response.json()
        print(f"JSON 数据: {json.dumps(data, indent=2, ensure_ascii=False)}")


def get_with_parameters():
    """
    带参数的 GET 请求
    演示如何传递查询参数
    """
    print("\n=== 带参数的 GET 请求 ===")
    
    url = "https://httpbin.org/get"
    params = {
        'name': '张三',
        'age': 25,
        'city': '北京'
    }
    
    response = requests.get(url, params=params)
    print(f"请求 URL: {response.url}")
    print(f"响应内容: {response.json()}")


def custom_headers():
    """
    自定义请求头
    演示如何设置 User-Agent 和其他请求头
    """
    print("\n=== 自定义请求头 ===")
    
    url = "https://httpbin.org/headers"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    response = requests.get(url, headers=headers)
    data = response.json()
    print(f"服务器接收到的请求头: {json.dumps(data['headers'], indent=2, ensure_ascii=False)}")


def post_request():
    """
    POST 请求示例
    演示如何发送 POST 请求和表单数据
    """
    print("\n=== POST 请求 ===")
    
    # 发送表单数据
    url = "https://httpbin.org/post"
    data = {
        'username': 'testuser',
        'password': 'testpass',
        'email': 'test@example.com'
    }
    
    response = requests.post(url, data=data)
    result = response.json()
    print(f"表单数据: {result['form']}")
    
    # 发送 JSON 数据
    json_data = {
        'name': '李四',
        'age': 30,
        'skills': ['Python', 'JavaScript', 'SQL']
    }
    
    response = requests.post(url, json=json_data)
    result = response.json()
    print(f"JSON 数据: {result['json']}")


def session_usage():
    """
    Session 使用示例
    演示如何使用 Session 保持连接和 Cookie
    """
    print("\n=== Session 使用 ===")
    
    # 创建 Session 对象
    session = requests.Session()
    
    # 设置 Session 级别的请求头
    session.headers.update({
        'User-Agent': 'Python-Spider/1.0'
    })
    
    # 使用 Session 发送请求
    response1 = session.get("https://httpbin.org/cookies/set/session_id/12345")
    print(f"设置 Cookie 后的响应: {response1.status_code}")
    
    # Cookie 会自动保持
    response2 = session.get("https://httpbin.org/cookies")
    cookies = response2.json()
    print(f"当前 Cookies: {cookies}")
    
    # 关闭 Session
    session.close()


def handle_errors():
    """
    错误处理示例
    演示如何处理网络错误和 HTTP 错误
    """
    print("\n=== 错误处理 ===")
    
    # 处理网络错误
    try:
        response = requests.get("https://nonexistent-domain-12345.com", timeout=5)
    except requests.exceptions.ConnectionError:
        print("连接错误: 无法连接到服务器")
    except requests.exceptions.Timeout:
        print("超时错误: 请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    
    # 处理 HTTP 错误状态码
    try:
        response = requests.get("https://httpbin.org/status/404")
        response.raise_for_status()  # 如果状态码不是 2xx，会抛出异常
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}")
        print(f"状态码: {response.status_code}")


def advanced_features():
    """
    高级特性示例
    演示超时、重试、代理等高级功能
    """
    print("\n=== 高级特性 ===")
    
    # 设置超时
    try:
        response = requests.get("https://httpbin.org/delay/2", timeout=3)
        print(f"请求成功: {response.status_code}")
    except requests.exceptions.Timeout:
        print("请求超时")
    
    # 禁用 SSL 验证（仅用于测试）
    try:
        response = requests.get("https://httpbin.org/get", verify=False)
        print(f"禁用 SSL 验证的请求: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 使用代理（示例，需要有效的代理服务器）
    proxies = {
        'http': 'http://proxy.example.com:8080',
        'https': 'https://proxy.example.com:8080'
    }
    # response = requests.get("https://httpbin.org/ip", proxies=proxies)


def url_operations():
    """
    URL 操作示例
    演示如何处理和构建 URL
    """
    print("\n=== URL 操作 ===")
    
    # 解析 URL
    url = "https://example.com/path/to/page?param1=value1&param2=value2#section"
    parsed = urlparse(url)
    print(f"协议: {parsed.scheme}")
    print(f"域名: {parsed.netloc}")
    print(f"路径: {parsed.path}")
    print(f"查询参数: {parsed.query}")
    print(f"锚点: {parsed.fragment}")
    
    # 构建 URL
    base_url = "https://example.com/api/"
    endpoint = "users/123"
    full_url = urljoin(base_url, endpoint)
    print(f"完整 URL: {full_url}")


def rate_limiting():
    """
    请求频率控制示例
    演示如何控制请求频率，避免被服务器封禁
    """
    print("\n=== 请求频率控制 ===")
    
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers"
    ]
    
    for i, url in enumerate(urls, 1):
        print(f"发送第 {i} 个请求: {url}")
        response = requests.get(url)
        print(f"响应状态: {response.status_code}")
        
        # 请求间隔，避免频率过高
        if i < len(urls):
            print("等待 1 秒...")
            time.sleep(1)


def main():
    """
    主函数，运行所有示例
    """
    print("HTTP 请求基础教程")
    print("=" * 50)
    
    try:
        basic_get_request()
        get_with_parameters()
        custom_headers()
        post_request()
        session_usage()
        handle_errors()
        advanced_features()
        url_operations()
        rate_limiting()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. HTTP 请求基础
   - GET 和 POST 请求的区别和使用场景
   - 请求参数的传递方式
   - 响应状态码的含义

2. 请求头的重要性
   - User-Agent 用于标识客户端
   - Accept 系列头部用于内容协商
   - 自定义请求头可以模拟真实浏览器

3. Session 的优势
   - 自动处理 Cookie
   - 连接复用提高效率
   - 统一的配置管理

4. 错误处理
   - 网络异常处理
   - HTTP 状态码检查
   - 超时设置的重要性

5. 最佳实践
   - 设置合理的超时时间
   - 控制请求频率
   - 使用 Session 提高效率
   - 正确处理异常情况

练习建议:
1. 尝试访问不同的网站，观察响应内容
2. 修改 User-Agent，看看服务器的不同响应
3. 实现一个简单的 API 客户端
4. 练习处理各种错误情况
"""