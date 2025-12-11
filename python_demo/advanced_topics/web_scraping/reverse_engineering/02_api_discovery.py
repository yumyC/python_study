#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 接口发现教程

本教程介绍如何通过各种技术手段发现网站的隐藏 API 接口，
包括网络监控、源码分析、目录扫描等方法。

作者: Python学习课程
日期: 2024
"""

import requests
import json
import re
from urllib.parse import urljoin, urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import mitmproxy
from mitmproxy import http
import subprocess
import os


class APIDiscovery:
    """
    API 发现工具类
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.discovered_apis = set()
        self.lock = threading.Lock()
    
    def discover_from_source(self, url):
        """
        从页面源码中发现 API 接口
        """
        print(f"=== 从源码发现 API: {url} ===")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # API 模式匹配
            api_patterns = [
                # 常见的 API 路径模式
                r'["\']([^"\']*(?:/api/|/v\d+/|/rest/)[^"\']*)["\']',
                r'["\']([^"\']*\.(?:json|xml|php|asp|jsp)[^"\']*)["\']',
                
                # AJAX 调用
                r'url\s*:\s*["\']([^"\']+)["\']',
                r'fetch\s*\(\s*["\']([^"\']+)["\']',
                r'axios\.(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']',
                
                # GraphQL
                r'["\']([^"\']*graphql[^"\']*)["\']',
                
                # WebSocket
                r'["\']([^"\']*(?:ws://|wss://)[^"\']*)["\']',
                
                # 移动端 API
                r'["\']([^"\']*(?:/mobile/|/app/)[^"\']*)["\']',
            ]
            
            found_apis = set()
            
            for pattern in api_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if self.is_valid_api_path(match):
                        # 转换为完整 URL
                        full_url = urljoin(url, match)
                        found_apis.add(full_url)
            
            print(f"从源码发现 {len(found_apis)} 个 API:")
            for api in sorted(found_apis):
                print(f"  {api}")
            
            with self.lock:
                self.discovered_apis.update(found_apis)
            
            return found_apis
            
        except Exception as e:
            print(f"源码分析失败: {e}")
            return set()
    
    def discover_from_js_files(self, base_url):
        """
        从 JavaScript 文件中发现 API
        """
        print(f"\n=== 从 JS 文件发现 API: {base_url} ===")
        
        try:
            # 首先获取主页面
            response = self.session.get(base_url)
            response.raise_for_status()
            
            # 提取 JS 文件链接
            js_patterns = [
                r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']',
                r'<script[^>]+src=([^\s>]+\.js[^\s>]*)',
            ]
            
            js_files = set()
            for pattern in js_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    full_url = urljoin(base_url, match)
                    js_files.add(full_url)
            
            print(f"找到 {len(js_files)} 个 JS 文件")
            
            # 并发分析 JS 文件
            found_apis = set()
            
            def analyze_js_file(js_url):
                try:
                    js_response = self.session.get(js_url, timeout=10)
                    js_response.raise_for_status()
                    
                    # 在 JS 内容中查找 API
                    js_apis = self.extract_apis_from_js(js_response.text, base_url)
                    return js_apis
                    
                except Exception as e:
                    print(f"分析 JS 文件失败 {js_url}: {e}")
                    return set()
            
            # 使用线程池并发处理
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {executor.submit(analyze_js_file, js_url): js_url 
                               for js_url in list(js_files)[:10]}  # 限制数量
                
                for future in as_completed(future_to_url):
                    js_url = future_to_url[future]
                    try:
                        apis = future.result()
                        found_apis.update(apis)
                        if apis:
                            print(f"  {js_url}: 发现 {len(apis)} 个 API")
                    except Exception as e:
                        print(f"处理 {js_url} 时出错: {e}")
            
            print(f"从 JS 文件总共发现 {len(found_apis)} 个 API")
            
            with self.lock:
                self.discovered_apis.update(found_apis)
            
            return found_apis
            
        except Exception as e:
            print(f"JS 文件分析失败: {e}")
            return set()
    
    def extract_apis_from_js(self, js_content, base_url):
        """
        从 JS 内容中提取 API
        """
        apis = set()
        
        # 更详细的 API 模式
        patterns = [
            # 直接的 URL 字符串
            r'["\']([^"\']*(?:/api/|/v\d+/|/rest/|/graphql)[^"\']*)["\']',
            
            # 对象属性中的 URL
            r'(?:url|endpoint|path|href)\s*:\s*["\']([^"\']+)["\']',
            
            # 函数调用中的 URL
            r'(?:fetch|axios|ajax|request)\s*\([^)]*["\']([^"\']+)["\']',
            
            # 模板字符串
            r'`([^`]*(?:/api/|/v\d+/)[^`]*)`',
            
            # 字符串拼接
            r'["\']([^"\']*)["\'][\s]*\+[\s]*["\']([^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 处理字符串拼接的情况
                    url = ''.join(match)
                else:
                    url = match
                
                if self.is_valid_api_path(url):
                    full_url = urljoin(base_url, url)
                    apis.add(full_url)
        
        return apis
    
    def directory_scan(self, base_url, wordlist=None):
        """
        目录扫描发现 API
        """
        print(f"\n=== 目录扫描发现 API: {base_url} ===")
        
        if wordlist is None:
            # 常见的 API 路径
            wordlist = [
                'api', 'v1', 'v2', 'v3', 'rest', 'graphql',
                'api/v1', 'api/v2', 'api/users', 'api/auth',
                'api/login', 'api/data', 'api/search', 'api/config',
                'admin/api', 'mobile/api', 'app/api',
                'json', 'xml', 'rpc', 'soap',
                'users.json', 'config.json', 'data.json',
                'status', 'health', 'ping', 'version',
            ]
        
        found_endpoints = []
        
        def check_endpoint(path):
            try:
                url = urljoin(base_url, path)
                response = self.session.get(url, timeout=5)
                
                # 检查响应
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # 判断是否为 API 响应
                    if any(ct in content_type for ct in ['json', 'xml', 'api']):
                        return {
                            'url': url,
                            'status': response.status_code,
                            'content_type': content_type,
                            'size': len(response.content)
                        }
                    
                    # 检查响应内容是否像 API
                    if self.looks_like_api_response(response.text):
                        return {
                            'url': url,
                            'status': response.status_code,
                            'content_type': content_type,
                            'size': len(response.content),
                            'note': 'Possible API response'
                        }
                
                elif response.status_code in [401, 403]:
                    # 需要认证的端点也可能是 API
                    return {
                        'url': url,
                        'status': response.status_code,
                        'note': 'Authentication required'
                    }
                
            except Exception:
                pass
            
            return None
        
        print(f"扫描 {len(wordlist)} 个路径...")
        
        # 并发扫描
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_path = {executor.submit(check_endpoint, path): path 
                            for path in wordlist}
            
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    if result:
                        found_endpoints.append(result)
                        print(f"  发现: {result['url']} ({result['status']})")
                except Exception as e:
                    pass
        
        print(f"目录扫描发现 {len(found_endpoints)} 个端点")
        
        # 添加到发现的 API 列表
        with self.lock:
            for endpoint in found_endpoints:
                self.discovered_apis.add(endpoint['url'])
        
        return found_endpoints
    
    def network_monitoring(self, target_url, duration=30):
        """
        网络监控发现 API（需要手动交互）
        """
        print(f"\n=== 网络监控发现 API: {target_url} ===")
        print(f"监控时长: {duration} 秒")
        
        # 设置 Chrome 选项
        chrome_options = Options()
        chrome_options.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': False,
        })
        chrome_options.add_experimental_option('loggingPrefs', {
            'performance': 'ALL'
        })
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            print("浏览器已启动，请在页面上进行操作...")
            driver.get(target_url)
            
            # 等待用户操作
            time.sleep(duration)
            
            # 获取网络日志
            logs = driver.get_log('performance')
            
            api_requests = []
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    
                    if message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        url = response['url']
                        
                        # 过滤出可能的 API 请求
                        if self.is_likely_api_url(url):
                            api_requests.append({
                                'url': url,
                                'method': response.get('method', 'GET'),
                                'status': response['status'],
                                'content_type': response.get('mimeType', ''),
                                'timestamp': log['timestamp']
                            })
                
                except Exception:
                    continue
            
            driver.quit()
            
            # 去重并排序
            unique_apis = {}
            for req in api_requests:
                url = req['url']
                if url not in unique_apis:
                    unique_apis[url] = req
            
            api_requests = sorted(unique_apis.values(), key=lambda x: x['timestamp'])
            
            print(f"网络监控发现 {len(api_requests)} 个 API 请求:")
            for req in api_requests:
                print(f"  {req['method']} {req['url']} - {req['status']}")
            
            # 添加到发现的 API 列表
            with self.lock:
                for req in api_requests:
                    self.discovered_apis.add(req['url'])
            
            return api_requests
            
        except Exception as e:
            print(f"网络监控失败: {e}")
            return []
    
    def robots_txt_analysis(self, base_url):
        """
        分析 robots.txt 文件发现隐藏路径
        """
        print(f"\n=== 分析 robots.txt: {base_url} ===")
        
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url)
            
            if response.status_code == 200:
                print("robots.txt 内容:")
                print(response.text)
                
                # 提取 Disallow 路径
                disallow_paths = re.findall(r'Disallow:\s*([^\s]+)', response.text)
                
                potential_apis = []
                for path in disallow_paths:
                    if self.is_potential_api_path(path):
                        full_url = urljoin(base_url, path)
                        potential_apis.append(full_url)
                
                print(f"发现 {len(potential_apis)} 个潜在的 API 路径:")
                for api in potential_apis:
                    print(f"  {api}")
                
                return potential_apis
            
            else:
                print("未找到 robots.txt 文件")
                return []
                
        except Exception as e:
            print(f"robots.txt 分析失败: {e}")
            return []
    
    def sitemap_analysis(self, base_url):
        """
        分析 sitemap.xml 发现 API 端点
        """
        print(f"\n=== 分析 sitemap.xml: {base_url} ===")
        
        sitemap_urls = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemaps.xml',
            '/sitemap/sitemap.xml'
        ]
        
        found_apis = []
        
        for sitemap_path in sitemap_urls:
            try:
                sitemap_url = urljoin(base_url, sitemap_path)
                response = self.session.get(sitemap_url)
                
                if response.status_code == 200:
                    print(f"找到 sitemap: {sitemap_url}")
                    
                    # 提取 URL
                    url_pattern = r'<loc>([^<]+)</loc>'
                    urls = re.findall(url_pattern, response.text)
                    
                    for url in urls:
                        if self.is_likely_api_url(url):
                            found_apis.append(url)
                    
                    break
                    
            except Exception:
                continue
        
        if found_apis:
            print(f"从 sitemap 发现 {len(found_apis)} 个潜在 API:")
            for api in found_apis:
                print(f"  {api}")
        else:
            print("未从 sitemap 发现 API")
        
        return found_apis
    
    def is_valid_api_path(self, path):
        """
        判断路径是否为有效的 API 路径
        """
        if not path or len(path) < 2:
            return False
        
        # 排除明显不是 API 的路径
        exclude_patterns = [
            r'^#', r'^javascript:', r'^mailto:', r'^tel:',
            r'\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|ttf)$',
            r'^data:', r'^blob:'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False
        
        # API 路径特征
        api_indicators = [
            '/api/', '/v1/', '/v2/', '/v3/', '/rest/', '/graphql',
            '.json', '.xml', '/mobile/', '/app/', '/admin/api'
        ]
        
        return any(indicator in path.lower() for indicator in api_indicators)
    
    def is_likely_api_url(self, url):
        """
        判断 URL 是否可能是 API
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # API 特征
        api_indicators = [
            'api', 'rest', 'graphql', 'json', 'xml',
            'v1', 'v2', 'v3', 'mobile', 'app'
        ]
        
        return any(indicator in path for indicator in api_indicators)
    
    def is_potential_api_path(self, path):
        """
        判断是否为潜在的 API 路径
        """
        api_keywords = [
            'api', 'admin', 'mobile', 'app', 'json',
            'xml', 'rest', 'graphql', 'v1', 'v2'
        ]
        
        return any(keyword in path.lower() for keyword in api_keywords)
    
    def looks_like_api_response(self, content):
        """
        判断内容是否像 API 响应
        """
        try:
            # 尝试解析为 JSON
            json.loads(content)
            return True
        except:
            pass
        
        # 检查 XML
        if content.strip().startswith('<?xml') or content.strip().startswith('<'):
            return True
        
        # 检查其他 API 响应特征
        api_patterns = [
            r'"status":', r'"code":', r'"message":', r'"data":',
            r'"error":', r'"success":', r'"result":'
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in api_patterns)
    
    def generate_report(self):
        """
        生成发现报告
        """
        print(f"\n=== API 发现报告 ===")
        print(f"总共发现 {len(self.discovered_apis)} 个 API 端点:")
        
        # 按域名分组
        by_domain = {}
        for api in self.discovered_apis:
            domain = urlparse(api).netloc
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(api)
        
        for domain, apis in by_domain.items():
            print(f"\n{domain} ({len(apis)} 个):")
            for api in sorted(apis):
                print(f"  {api}")
        
        return list(self.discovered_apis)


def comprehensive_api_discovery(target_url):
    """
    综合 API 发现示例
    """
    print("=== 综合 API 发现 ===")
    
    discovery = APIDiscovery()
    
    try:
        # 1. 源码分析
        discovery.discover_from_source(target_url)
        
        # 2. JS 文件分析
        discovery.discover_from_js_files(target_url)
        
        # 3. 目录扫描
        discovery.directory_scan(target_url)
        
        # 4. robots.txt 分析
        discovery.robots_txt_analysis(target_url)
        
        # 5. sitemap 分析
        discovery.sitemap_analysis(target_url)
        
        # 6. 网络监控（可选，需要手动交互）
        # discovery.network_monitoring(target_url, duration=10)
        
        # 生成报告
        all_apis = discovery.generate_report()
        
        return all_apis
        
    except Exception as e:
        print(f"API 发现过程出错: {e}")
        return []


def main():
    """
    主函数，运行 API 发现示例
    """
    print("API 接口发现教程")
    print("=" * 50)
    
    try:
        # 测试目标
        target_url = "https://httpbin.org/"
        
        print(f"目标网站: {target_url}")
        
        # 执行综合发现
        discovered_apis = comprehensive_api_discovery(target_url)
        
        print(f"\n=== 最终结果 ===")
        print(f"总共发现 {len(discovered_apis)} 个 API 端点")
        
        # 保存结果
        if discovered_apis:
            with open('discovered_apis.json', 'w', encoding='utf-8') as f:
                json.dump(discovered_apis, f, indent=2, ensure_ascii=False)
            print("结果已保存到 discovered_apis.json")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. API 发现方法
   - 源码分析: 从 HTML/JS 中提取 API 路径
   - 目录扫描: 暴力枚举常见 API 路径
   - 网络监控: 实时捕获 API 请求
   - 文件分析: robots.txt, sitemap.xml
   - 错误页面: 从错误信息中获取线索

2. 源码分析技巧
   - 正则表达式匹配 URL 模式
   - JavaScript 代码分析
   - AJAX 调用识别
   - 配置文件提取
   - 字符串拼接还原

3. 目录扫描策略
   - 常见 API 路径字典
   - 响应状态码分析
   - 内容类型判断
   - 并发扫描优化
   - 智能过滤机制

4. 网络监控技术
   - 浏览器开发者工具
   - 代理工具 (Burp Suite, mitmproxy)
   - Selenium 网络日志
   - WebSocket 连接监控
   - 移动端抓包

5. 高级发现技巧
   - GraphQL 端点发现
   - WebSocket API 识别
   - 移动端 API 分析
   - 微服务架构探测
   - API 版本枚举

工具推荐:
- Burp Suite: 专业 Web 安全测试
- OWASP ZAP: 开源安全扫描
- Postman: API 测试和文档
- Insomnia: REST 客户端
- mitmproxy: Python 代理工具

实战建议:
1. 多种方法结合使用
2. 关注错误页面信息
3. 分析移动端应用
4. 监控 WebSocket 连接
5. 注意 API 版本差异
6. 记录发现过程
7. 验证 API 可用性

注意事项:
- 遵守法律法规
- 尊重 robots.txt
- 控制扫描频率
- 避免对服务器造成压力
- 不要尝试未授权访问
"""