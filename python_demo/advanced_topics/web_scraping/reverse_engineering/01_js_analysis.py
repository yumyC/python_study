#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JavaScript 分析教程

本教程介绍如何分析网页中的 JavaScript 代码，理解数据加载逻辑，
发现隐藏的 API 接口，为爬虫开发提供技术支持。

作者: Python学习课程
日期: 2024
"""

import requests
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
import base64
import hashlib
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import subprocess
import os


class JSAnalyzer:
    """
    JavaScript 分析器
    用于分析网页中的 JS 代码和网络请求
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_js_files(self, url):
        """
        提取页面中的所有 JavaScript 文件
        """
        print(f"=== 分析页面: {url} ===")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # 使用正则表达式提取 JS 文件链接
            js_patterns = [
                r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']',
                r'<script[^>]+src=([^\s>]+\.js[^\s>]*)',
            ]
            
            js_files = set()
            
            for pattern in js_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    # 处理相对链接
                    full_url = urljoin(url, match)
                    js_files.add(full_url)
            
            print(f"找到 {len(js_files)} 个 JavaScript 文件:")
            for js_file in sorted(js_files):
                print(f"  {js_file}")
            
            return list(js_files)
            
        except Exception as e:
            print(f"提取 JS 文件失败: {e}")
            return []
    
    def analyze_js_content(self, js_url):
        """
        分析 JavaScript 文件内容
        """
        print(f"\n=== 分析 JS 文件: {js_url} ===")
        
        try:
            response = self.session.get(js_url)
            response.raise_for_status()
            
            js_content = response.text
            
            # 分析结果
            analysis = {
                'url': js_url,
                'size': len(js_content),
                'api_endpoints': self.find_api_endpoints(js_content),
                'ajax_calls': self.find_ajax_calls(js_content),
                'encryption_functions': self.find_encryption_patterns(js_content),
                'constants': self.find_constants(js_content),
                'event_handlers': self.find_event_handlers(js_content)
            }
            
            return analysis
            
        except Exception as e:
            print(f"分析 JS 文件失败: {e}")
            return None
    
    def find_api_endpoints(self, js_content):
        """
        查找 API 端点
        """
        patterns = [
            r'["\']([^"\']*(?:api|Api|API)[^"\']*)["\']',
            r'["\']([^"\']*\.(?:json|xml|php|asp|jsp)[^"\']*)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.(?:get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']',
            r'\.ajax\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        endpoints = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if self.is_valid_endpoint(match):
                    endpoints.add(match)
        
        return list(endpoints)
    
    def find_ajax_calls(self, js_content):
        """
        查找 AJAX 调用模式
        """
        patterns = [
            r'\.ajax\s*\(\s*\{([^}]+)\}',
            r'fetch\s*\(\s*["\']([^"\']+)["\'][^)]*\)',
            r'axios\.\w+\s*\([^)]+\)',
            r'XMLHttpRequest\s*\(\s*\)',
        ]
        
        ajax_calls = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, js_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                ajax_calls.append({
                    'pattern': pattern,
                    'match': match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0),
                    'position': match.start()
                })
        
        return ajax_calls
    
    def find_encryption_patterns(self, js_content):
        """
        查找加密相关的模式
        """
        patterns = [
            r'(?:md5|MD5|sha1|SHA1|sha256|SHA256|base64|Base64|encrypt|decrypt|cipher)',
            r'(?:AES|DES|RSA|HMAC)',
            r'(?:btoa|atob)',  # Base64 编码/解码
            r'(?:encodeURIComponent|decodeURIComponent)',
            r'(?:JSON\.stringify|JSON\.parse)',
        ]
        
        encryption_functions = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, js_content, re.IGNORECASE)
            for match in matches:
                # 获取函数调用的上下文
                start = max(0, match.start() - 50)
                end = min(len(js_content), match.end() + 50)
                context = js_content[start:end]
                
                encryption_functions.append({
                    'function': match.group(0),
                    'context': context,
                    'position': match.start()
                })
        
        return encryption_functions
    
    def find_constants(self, js_content):
        """
        查找常量定义
        """
        patterns = [
            r'const\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
            r'var\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
            r'let\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
            r'(\w+)\s*:\s*["\']([^"\']+)["\']',  # 对象属性
        ]
        
        constants = {}
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content)
            for name, value in matches:
                if len(value) > 5 and self.is_interesting_constant(name, value):
                    constants[name] = value
        
        return constants
    
    def find_event_handlers(self, js_content):
        """
        查找事件处理器
        """
        patterns = [
            r'addEventListener\s*\(\s*["\'](\w+)["\']',
            r'on(\w+)\s*=',
            r'\.on\s*\(\s*["\'](\w+)["\']',
            r'\.click\s*\(',
            r'\.submit\s*\(',
        ]
        
        events = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            events.update(matches)
        
        return list(events)
    
    def is_valid_endpoint(self, endpoint):
        """
        判断是否为有效的 API 端点
        """
        if not endpoint or len(endpoint) < 3:
            return False
        
        # 排除一些明显不是 API 的路径
        exclude_patterns = [
            r'^#',  # 锚点
            r'^javascript:',  # JavaScript 代码
            r'^mailto:',  # 邮件链接
            r'^tel:',  # 电话链接
            r'\.(css|js|png|jpg|jpeg|gif|ico|svg)$',  # 静态资源
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, endpoint, re.IGNORECASE):
                return False
        
        return True
    
    def is_interesting_constant(self, name, value):
        """
        判断常量是否有趣（可能包含重要信息）
        """
        interesting_names = [
            'api', 'url', 'endpoint', 'key', 'secret', 'token',
            'host', 'domain', 'path', 'config', 'setting'
        ]
        
        return any(keyword in name.lower() for keyword in interesting_names)


def analyze_network_requests():
    """
    使用浏览器开发者工具分析网络请求
    """
    print("\n=== 网络请求分析 ===")
    
    # 设置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--enable-network-service-logging')
    
    # 启用性能日志
    chrome_options.add_experimental_option('perfLoggingPrefs', {
        'enableNetwork': True,
        'enablePage': False,
    })
    
    chrome_options.add_experimental_option('loggingPrefs', {
        'performance': 'ALL'
    })
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # 访问测试页面
        test_url = "https://httpbin.org/html"
        driver.get(test_url)
        
        # 等待页面加载
        time.sleep(3)
        
        # 获取性能日志
        logs = driver.get_log('performance')
        
        network_requests = []
        
        for log in logs:
            message = json.loads(log['message'])
            
            if message['message']['method'] == 'Network.responseReceived':
                response = message['message']['params']['response']
                request_info = {
                    'url': response['url'],
                    'status': response['status'],
                    'method': response.get('method', 'GET'),
                    'headers': response.get('headers', {}),
                    'mime_type': response.get('mimeType', ''),
                }
                network_requests.append(request_info)
        
        print(f"捕获到 {len(network_requests)} 个网络请求:")
        for req in network_requests:
            print(f"  {req['method']} {req['url']} - {req['status']}")
        
        driver.quit()
        return network_requests
        
    except Exception as e:
        print(f"网络请求分析失败: {e}")
        return []


def reverse_engineer_api():
    """
    逆向工程 API 调用示例
    """
    print("\n=== API 逆向工程示例 ===")
    
    # 模拟一个需要逆向的 API 调用
    # 通常这些信息是通过分析 JS 代码获得的
    
    api_info = {
        'base_url': 'https://httpbin.org',
        'endpoint': '/post',
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'auth_required': True,
        'timestamp_required': True,
        'signature_required': True,
    }
    
    print(f"目标 API: {api_info['base_url']}{api_info['endpoint']}")
    
    # 生成请求参数
    timestamp = int(time.time())
    
    # 模拟签名生成（通常需要从 JS 代码中分析得出）
    def generate_signature(data, timestamp, secret_key="demo_secret"):
        """
        模拟签名生成算法
        实际情况需要从 JS 代码中分析具体算法
        """
        # 构建签名字符串
        sign_string = f"{json.dumps(data, sort_keys=True)}{timestamp}{secret_key}"
        
        # 生成 MD5 签名
        signature = hashlib.md5(sign_string.encode()).hexdigest()
        
        return signature
    
    # 准备请求数据
    request_data = {
        'action': 'get_data',
        'params': {
            'page': 1,
            'limit': 10,
            'category': 'test'
        }
    }
    
    # 生成签名
    signature = generate_signature(request_data, timestamp)
    
    # 构建完整的请求
    full_data = {
        'data': request_data,
        'timestamp': timestamp,
        'signature': signature
    }
    
    print(f"请求数据: {json.dumps(full_data, indent=2)}")
    
    try:
        # 发送请求
        response = requests.post(
            f"{api_info['base_url']}{api_info['endpoint']}",
            json=full_data,
            headers=api_info['headers']
        )
        
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def decode_obfuscated_js():
    """
    解混淆 JavaScript 代码示例
    """
    print("\n=== JavaScript 解混淆示例 ===")
    
    # 模拟混淆的 JavaScript 代码
    obfuscated_js = """
    var _0x1234 = ['hello', 'world', 'console', 'log'];
    function _0x5678(a, b) {
        return _0x1234[a] + ' ' + _0x1234[b];
    }
    _0x1234[2][_0x1234[3]](_0x5678(0, 1));
    """
    
    print("混淆的代码:")
    print(obfuscated_js)
    
    # 简单的解混淆策略
    def simple_deobfuscate(code):
        """
        简单的解混淆函数
        实际情况可能需要更复杂的分析
        """
        # 提取数组定义
        array_match = re.search(r'var\s+(\w+)\s*=\s*\[(.*?)\]', code)
        if array_match:
            array_name = array_match.group(1)
            array_content = array_match.group(2)
            
            # 解析数组内容
            array_items = []
            for item in array_content.split(','):
                item = item.strip().strip('\'"')
                array_items.append(item)
            
            print(f"\n数组 {array_name}: {array_items}")
            
            # 替换数组访问
            deobfuscated = code
            for i, item in enumerate(array_items):
                pattern = f'{array_name}\\[{i}\\]'
                deobfuscated = re.sub(pattern, f'"{item}"', deobfuscated)
            
            return deobfuscated
        
        return code
    
    deobfuscated = simple_deobfuscate(obfuscated_js)
    print("\n解混淆后的代码:")
    print(deobfuscated)
    
    return deobfuscated


def extract_hidden_apis():
    """
    提取隐藏的 API 接口
    """
    print("\n=== 提取隐藏 API 接口 ===")
    
    # 模拟从 JS 代码中提取的 API 信息
    js_code_sample = """
    const API_CONFIG = {
        baseURL: 'https://api.example.com/v1',
        endpoints: {
            getUserInfo: '/user/info',
            getProductList: '/products',
            submitOrder: '/orders/create',
            uploadFile: '/upload'
        },
        auth: {
            tokenKey: 'X-Auth-Token',
            refreshEndpoint: '/auth/refresh'
        }
    };
    
    function makeRequest(endpoint, data) {
        const url = API_CONFIG.baseURL + API_CONFIG.endpoints[endpoint];
        const headers = {
            'Content-Type': 'application/json',
            [API_CONFIG.auth.tokenKey]: getAuthToken()
        };
        
        return fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });
    }
    """
    
    print("从 JS 代码中提取 API 信息:")
    
    # 提取 API 配置
    config_match = re.search(r'const\s+API_CONFIG\s*=\s*({.*?});', js_code_sample, re.DOTALL)
    if config_match:
        config_str = config_match.group(1)
        print(f"API 配置: {config_str}")
        
        # 提取基础 URL
        base_url_match = re.search(r'baseURL:\s*["\']([^"\']+)["\']', config_str)
        if base_url_match:
            base_url = base_url_match.group(1)
            print(f"基础 URL: {base_url}")
        
        # 提取端点
        endpoints_match = re.search(r'endpoints:\s*{([^}]+)}', config_str)
        if endpoints_match:
            endpoints_str = endpoints_match.group(1)
            endpoint_matches = re.findall(r'(\w+):\s*["\']([^"\']+)["\']', endpoints_str)
            
            print("API 端点:")
            for name, path in endpoint_matches:
                full_url = base_url + path if base_url_match else path
                print(f"  {name}: {full_url}")
        
        # 提取认证信息
        auth_match = re.search(r'auth:\s*{([^}]+)}', config_str)
        if auth_match:
            auth_str = auth_match.group(1)
            print(f"认证配置: {{{auth_str}}}")
    
    # 提取函数调用模式
    function_matches = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*{', js_code_sample)
    print(f"发现函数: {function_matches}")
    
    return {
        'base_url': base_url if 'base_url' in locals() else None,
        'endpoints': dict(endpoint_matches) if 'endpoint_matches' in locals() else {},
        'functions': function_matches
    }


def analyze_websocket_connections():
    """
    分析 WebSocket 连接
    """
    print("\n=== WebSocket 连接分析 ===")
    
    # WebSocket 连接模式
    websocket_patterns = [
        r'new\s+WebSocket\s*\(\s*["\']([^"\']+)["\']',
        r'ws://[^\s"\']+',
        r'wss://[^\s"\']+',
        r'socket\.io',
        r'sockjs',
    ]
    
    sample_js = """
    const socket = new WebSocket('wss://api.example.com/ws');
    
    socket.onopen = function(event) {
        console.log('WebSocket connected');
        socket.send(JSON.stringify({
            type: 'auth',
            token: getAuthToken()
        }));
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
    
    const io = require('socket.io-client');
    const socketIO = io('https://api.example.com:3000');
    """
    
    print("分析 WebSocket 连接:")
    
    for pattern in websocket_patterns:
        matches = re.findall(pattern, sample_js, re.IGNORECASE)
        if matches:
            print(f"模式 '{pattern}' 匹配: {matches}")
    
    # 提取 WebSocket URL
    ws_urls = re.findall(r'wss?://[^\s"\']+', sample_js)
    print(f"WebSocket URLs: {ws_urls}")
    
    # 提取消息处理模式
    message_patterns = [
        r'onmessage\s*=\s*function',
        r'addEventListener\s*\(\s*["\']message["\']',
        r'socket\.on\s*\(\s*["\']([^"\']+)["\']',
    ]
    
    for pattern in message_patterns:
        matches = re.findall(pattern, sample_js, re.IGNORECASE)
        if matches:
            print(f"消息处理模式: {matches}")


def main():
    """
    主函数，运行所有示例
    """
    print("JavaScript 分析教程")
    print("=" * 50)
    
    try:
        # 创建分析器
        analyzer = JSAnalyzer()
        
        # 示例：分析一个网页的 JS 文件
        test_url = "https://httpbin.org/html"
        js_files = analyzer.extract_js_files(test_url)
        
        # 分析第一个 JS 文件（如果存在）
        if js_files:
            analysis = analyzer.analyze_js_content(js_files[0])
            if analysis:
                print(f"\nJS 文件分析结果:")
                print(f"文件大小: {analysis['size']} 字节")
                print(f"API 端点: {len(analysis['api_endpoints'])} 个")
                print(f"AJAX 调用: {len(analysis['ajax_calls'])} 个")
                print(f"加密函数: {len(analysis['encryption_functions'])} 个")
        
        # 网络请求分析（需要 Chrome 驱动）
        # analyze_network_requests()
        
        # API 逆向工程示例
        reverse_engineer_api()
        
        # JavaScript 解混淆示例
        decode_obfuscated_js()
        
        # 提取隐藏 API
        extract_hidden_apis()
        
        # WebSocket 分析
        analyze_websocket_connections()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. JavaScript 分析基础
   - 提取页面中的 JS 文件
   - 分析 JS 代码结构
   - 识别关键函数和变量
   - 理解代码执行流程

2. API 发现技巧
   - 搜索 URL 模式
   - 分析 AJAX 调用
   - 提取 API 配置
   - 识别请求参数

3. 加密算法识别
   - 常见加密函数特征
   - 签名生成逻辑
   - 参数编码方式
   - 时间戳和随机数

4. 代码解混淆
   - 变量名还原
   - 字符串解码
   - 控制流分析
   - 函数调用追踪

5. 网络请求分析
   - 浏览器开发者工具
   - 网络日志捕获
   - 请求头分析
   - 响应数据解析

实用工具:
- Chrome DevTools
- Burp Suite
- Fiddler
- Wireshark
- JSNice (代码美化)
- JS Beautifier

分析步骤:
1. 打开浏览器开发者工具
2. 监控网络请求
3. 分析 JavaScript 源码
4. 识别关键 API 调用
5. 提取请求参数和算法
6. 复现 API 调用逻辑

注意事项:
- 遵守法律法规
- 尊重网站条款
- 不要恶意攻击
- 保护个人隐私
- 合理使用技术
"""