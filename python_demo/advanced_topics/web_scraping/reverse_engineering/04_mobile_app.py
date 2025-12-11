#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动端应用抓包教程

本教程介绍如何对移动端应用进行网络抓包分析，包括 HTTP/HTTPS 请求捕获、
证书绕过、协议分析等技术。

作者: Python学习课程
日期: 2024
"""

import requests
import json
import time
import socket
import ssl
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import os
import base64
import hashlib


class MobileAppAnalyzer:
    """
    移动应用分析器
    """
    
    def __init__(self):
        self.captured_requests = []
        self.proxy_port = 8888
        self.cert_file = "proxy_cert.pem"
        self.key_file = "proxy_key.pem"
    
    def setup_proxy_server(self):
        """
        设置代理服务器
        """
        print("=== 设置代理服务器 ===")
        
        class ProxyHandler(BaseHTTPRequestHandler):
            def __init__(self, analyzer, *args, **kwargs):
                self.analyzer = analyzer
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                self.handle_request('GET')
            
            def do_POST(self):
                self.handle_request('POST')
            
            def do_PUT(self):
                self.handle_request('PUT')
            
            def do_DELETE(self):
                self.handle_request('DELETE')
            
            def handle_request(self, method):
                # 捕获请求信息
                request_info = {
                    'timestamp': time.time(),
                    'method': method,
                    'url': self.path,
                    'headers': dict(self.headers),
                    'client_address': self.client_address[0]
                }
                
                # 读取请求体
                if method in ['POST', 'PUT']:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        request_info['body'] = self.rfile.read(content_length).decode('utf-8', errors='ignore')
                
                # 保存请求
                self.analyzer.captured_requests.append(request_info)
                
                print(f"捕获请求: {method} {self.path}")
                
                # 转发请求到真实服务器
                try:
                    self.forward_request(request_info)
                except Exception as e:
                    print(f"转发请求失败: {e}")
                    self.send_error(500, str(e))
            
            def forward_request(self, request_info):
                # 这里应该实现真实的请求转发
                # 为了演示，我们返回一个模拟响应
                
                response_data = {
                    'status': 'success',
                    'message': '这是代理服务器的模拟响应',
                    'original_request': {
                        'method': request_info['method'],
                        'url': request_info['url']
                    }
                }
                
                response_json = json.dumps(response_data, ensure_ascii=False)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(response_json.encode())))
                self.end_headers()
                self.wfile.write(response_json.encode())
        
        # 创建处理器工厂
        def handler_factory(*args, **kwargs):
            return ProxyHandler(self, *args, **kwargs)
        
        try:
            server = HTTPServer(('0.0.0.0', self.proxy_port), handler_factory)
            print(f"代理服务器启动在端口 {self.proxy_port}")
            print(f"请在移动设备上设置代理: {self.get_local_ip()}:{self.proxy_port}")
            
            # 在新线程中运行服务器
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return server
            
        except Exception as e:
            print(f"启动代理服务器失败: {e}")
            return None
    
    def get_local_ip(self):
        """
        获取本机 IP 地址
        """
        try:
            # 连接到一个远程地址来获取本机 IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def generate_ssl_certificate(self):
        """
        生成 SSL 证书用于 HTTPS 抓包
        """
        print("\n=== 生成 SSL 证书 ===")
        
        try:
            # 使用 openssl 命令生成证书
            cert_commands = [
                # 生成私钥
                f"openssl genrsa -out {self.key_file} 2048",
                
                # 生成证书签名请求
                f"openssl req -new -key {self.key_file} -out proxy_cert.csr -subj '/C=CN/ST=Beijing/L=Beijing/O=Proxy/CN=proxy.local'",
                
                # 生成自签名证书
                f"openssl x509 -req -days 365 -in proxy_cert.csr -signkey {self.key_file} -out {self.cert_file}",
                
                # 清理临时文件
                "rm proxy_cert.csr"
            ]
            
            for cmd in cert_commands:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"命令执行失败: {cmd}")
                    print(f"错误: {result.stderr}")
                    return False
            
            print(f"SSL 证书生成成功: {self.cert_file}")
            print("请将证书安装到移动设备上以支持 HTTPS 抓包")
            
            return True
            
        except Exception as e:
            print(f"生成 SSL 证书失败: {e}")
            print("提示: 需要安装 OpenSSL")
            return False
    
    def analyze_captured_requests(self):
        """
        分析捕获的请求
        """
        print(f"\n=== 分析捕获的请求 ({len(self.captured_requests)} 个) ===")
        
        if not self.captured_requests:
            print("没有捕获到请求")
            return
        
        # 按 URL 分组
        url_groups = {}
        for req in self.captured_requests:
            url = req['url']
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(req)
        
        print(f"发现 {len(url_groups)} 个不同的 URL:")
        
        for url, requests in url_groups.items():
            print(f"\nURL: {url}")
            print(f"请求次数: {len(requests)}")
            
            # 分析第一个请求的详细信息
            first_req = requests[0]
            print(f"方法: {first_req['method']}")
            print(f"客户端: {first_req['client_address']}")
            
            # 分析请求头
            interesting_headers = ['User-Agent', 'Authorization', 'X-Token', 'Content-Type']
            for header in interesting_headers:
                if header in first_req['headers']:
                    value = first_req['headers'][header]
                    print(f"{header}: {value}")
            
            # 分析请求体
            if 'body' in first_req and first_req['body']:
                body = first_req['body']
                print(f"请求体长度: {len(body)} 字符")
                
                # 尝试解析 JSON
                try:
                    json_data = json.loads(body)
                    print("请求体 (JSON):")
                    print(json.dumps(json_data, indent=2, ensure_ascii=False)[:200] + "...")
                except:
                    print(f"请求体 (文本): {body[:100]}...")
    
    def extract_api_patterns(self):
        """
        提取 API 模式
        """
        print(f"\n=== 提取 API 模式 ===")
        
        if not self.captured_requests:
            return
        
        # 提取 API 端点
        api_endpoints = set()
        auth_methods = set()
        content_types = set()
        
        for req in self.captured_requests:
            url = req['url']
            
            # 提取 API 端点模式
            if '/api/' in url or '/v1/' in url or '/v2/' in url:
                api_endpoints.add(url)
            
            # 提取认证方法
            headers = req['headers']
            if 'Authorization' in headers:
                auth_type = headers['Authorization'].split(' ')[0]
                auth_methods.add(auth_type)
            
            if 'X-Token' in headers or 'X-Auth-Token' in headers:
                auth_methods.add('Custom-Token')
            
            # 提取内容类型
            if 'Content-Type' in headers:
                content_types.add(headers['Content-Type'])
        
        print(f"API 端点 ({len(api_endpoints)} 个):")
        for endpoint in sorted(api_endpoints):
            print(f"  {endpoint}")
        
        print(f"\n认证方法 ({len(auth_methods)} 种):")
        for method in auth_methods:
            print(f"  {method}")
        
        print(f"\n内容类型 ({len(content_types)} 种):")
        for content_type in content_types:
            print(f"  {content_type}")
        
        return {
            'api_endpoints': list(api_endpoints),
            'auth_methods': list(auth_methods),
            'content_types': list(content_types)
        }


def simulate_mobile_requests():
    """
    模拟移动端请求
    """
    print("\n=== 模拟移动端请求 ===")
    
    # 模拟移动端的 User-Agent
    mobile_user_agents = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
        'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
        'MyApp/1.0 (iPhone; iOS 14.7.1; Scale/3.00)',
        'MyApp/1.0 (Android 11; Mobile)'
    ]
    
    # 模拟移动端 API 请求
    mobile_requests = [
        {
            'url': 'https://api.example.com/v1/user/profile',
            'method': 'GET',
            'headers': {
                'User-Agent': mobile_user_agents[0],
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                'X-Device-ID': 'iPhone12,1',
                'X-App-Version': '1.2.3',
                'Accept': 'application/json'
            }
        },
        {
            'url': 'https://api.example.com/v1/data/sync',
            'method': 'POST',
            'headers': {
                'User-Agent': mobile_user_agents[1],
                'Content-Type': 'application/json',
                'X-Token': 'mobile_token_12345',
                'X-Timestamp': str(int(time.time())),
                'X-Signature': 'a1b2c3d4e5f6...'
            },
            'data': {
                'device_info': {
                    'platform': 'Android',
                    'version': '11',
                    'model': 'SM-G991B'
                },
                'sync_data': [
                    {'type': 'user_action', 'timestamp': int(time.time()), 'action': 'login'},
                    {'type': 'page_view', 'timestamp': int(time.time()), 'page': 'home'}
                ]
            }
        }
    ]
    
    print("移动端请求特征分析:")
    
    for i, req in enumerate(mobile_requests, 1):
        print(f"\n请求 {i}:")
        print(f"URL: {req['url']}")
        print(f"方法: {req['method']}")
        
        # 分析移动端特征
        headers = req['headers']
        
        # User-Agent 分析
        ua = headers.get('User-Agent', '')
        if 'iPhone' in ua:
            print("设备类型: iOS")
        elif 'Android' in ua:
            print("设备类型: Android")
        
        # 移动端特有头部
        mobile_headers = ['X-Device-ID', 'X-App-Version', 'X-Token']
        for header in mobile_headers:
            if header in headers:
                print(f"{header}: {headers[header]}")
        
        # 数据分析
        if 'data' in req:
            data = req['data']
            print("请求数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
    
    return mobile_requests


def analyze_app_security():
    """
    分析移动应用安全特征
    """
    print("\n=== 移动应用安全分析 ===")
    
    # 模拟从应用中提取的安全特征
    security_features = {
        'certificate_pinning': {
            'enabled': True,
            'certificates': [
                'sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
                'sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB='
            ],
            'bypass_methods': [
                'Frida Hook',
                'Xposed Module',
                'SSL Kill Switch'
            ]
        },
        'root_detection': {
            'enabled': True,
            'detection_methods': [
                'su binary check',
                'root apps detection',
                'build tags check',
                'test keys check'
            ],
            'bypass_methods': [
                'Magisk Hide',
                'RootCloak',
                'Frida Hook'
            ]
        },
        'anti_debugging': {
            'enabled': True,
            'techniques': [
                'ptrace detection',
                'debugger port check',
                'timing checks',
                'exception handling'
            ]
        },
        'obfuscation': {
            'code_obfuscation': True,
            'string_encryption': True,
            'control_flow_obfuscation': True,
            'tools_used': ['ProGuard', 'DexGuard', 'Ollvm']
        },
        'api_security': {
            'request_signing': True,
            'timestamp_validation': True,
            'nonce_usage': True,
            'rate_limiting': True
        }
    }
    
    print("应用安全特征:")
    
    for feature, details in security_features.items():
        print(f"\n{feature.replace('_', ' ').title()}:")
        
        if isinstance(details, dict):
            for key, value in details.items():
                if isinstance(value, list):
                    print(f"  {key}: {', '.join(value)}")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"  {details}")
    
    # 安全建议
    print(f"\n安全分析建议:")
    recommendations = [
        "使用 Frida 进行动态分析",
        "尝试 SSL Pinning 绕过",
        "分析应用的混淆程度",
        "检查 Root 检测机制",
        "分析 API 签名算法",
        "监控网络通信模式",
        "检查数据存储安全性"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    return security_features


def frida_hooking_example():
    """
    Frida Hook 示例代码
    """
    print("\n=== Frida Hook 示例 ===")
    
    # Frida JavaScript 代码示例
    frida_script = """
    // SSL Pinning 绕过
    Java.perform(function() {
        console.log("[+] SSL Pinning 绕过脚本启动");
        
        // Hook OkHttp3 CertificatePinner
        var CertificatePinner = Java.use("okhttp3.CertificatePinner");
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(hostname, peerCertificates) {
            console.log("[+] SSL Pinning 绕过: " + hostname);
            return;
        };
        
        // Hook HttpsURLConnection
        var HttpsURLConnection = Java.use("javax.net.ssl.HttpsURLConnection");
        HttpsURLConnection.setDefaultHostnameVerifier.implementation = function(hostnameVerifier) {
            console.log("[+] 绕过 HostnameVerifier");
            return;
        };
        
        // Hook 网络请求
        var URL = Java.use("java.net.URL");
        URL.openConnection.overload().implementation = function() {
            var connection = this.openConnection();
            console.log("[+] 网络请求: " + this.toString());
            return connection;
        };
        
        // Hook 加密函数
        var MessageDigest = Java.use("java.security.MessageDigest");
        MessageDigest.digest.overload('[B').implementation = function(input) {
            var result = this.digest(input);
            console.log("[+] MessageDigest: " + Java.use("java.util.Arrays").toString(input));
            console.log("[+] 结果: " + Java.use("java.util.Arrays").toString(result));
            return result;
        };
        
        // Hook SharedPreferences (数据存储)
        var SharedPreferences = Java.use("android.content.SharedPreferences");
        var Editor = Java.use("android.content.SharedPreferences$Editor");
        
        Editor.putString.implementation = function(key, value) {
            console.log("[+] SharedPreferences 存储: " + key + " = " + value);
            return this.putString(key, value);
        };
    });
    
    // Root 检测绕过
    Java.perform(function() {
        console.log("[+] Root 检测绕过脚本启动");
        
        // Hook Runtime.exec
        var Runtime = Java.use("java.lang.Runtime");
        Runtime.exec.overload('java.lang.String').implementation = function(command) {
            if (command.indexOf("su") !== -1) {
                console.log("[+] 阻止 su 命令执行: " + command);
                throw new Error("Command not found");
            }
            return this.exec(command);
        };
        
        // Hook File.exists (检测 su 文件)
        var File = Java.use("java.io.File");
        File.exists.implementation = function() {
            var path = this.getAbsolutePath();
            if (path.indexOf("su") !== -1 || path.indexOf("busybox") !== -1) {
                console.log("[+] 隐藏 Root 文件: " + path);
                return false;
            }
            return this.exists();
        };
    });
    """
    
    print("Frida Hook 脚本示例:")
    print(frida_script[:500] + "...")
    
    # Python Frida 使用示例
    python_frida_code = """
import frida
import sys

def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
    else:
        print(message)

# 连接到设备
device = frida.get_usb_device()
print(f"连接到设备: {device}")

# 附加到应用
package_name = "com.example.app"
try:
    session = device.attach(package_name)
    print(f"附加到应用: {package_name}")
    
    # 加载脚本
    script = session.create_script(frida_script)
    script.on('message', on_message)
    script.load()
    
    print("脚本已加载，开始监控...")
    sys.stdin.read()
    
except frida.ProcessNotFoundError:
    print(f"应用未运行: {package_name}")
except Exception as e:
    print(f"Frida 操作失败: {e}")
    """
    
    print("\nPython Frida 使用代码:")
    print(python_frida_code)
    
    print("\n使用步骤:")
    steps = [
        "1. 安装 Frida: pip install frida-tools",
        "2. 在设备上安装 frida-server",
        "3. 启动目标应用",
        "4. 运行 Frida 脚本",
        "5. 观察 Hook 输出"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    return {
        'frida_script': frida_script,
        'python_code': python_frida_code
    }


def main():
    """
    主函数，运行移动端分析示例
    """
    print("移动端应用抓包教程")
    print("=" * 50)
    
    try:
        # 创建分析器
        analyzer = MobileAppAnalyzer()
        
        # 1. 设置代理服务器
        print("1. 设置代理服务器...")
        server = analyzer.setup_proxy_server()
        
        if server:
            print("代理服务器已启动，等待 10 秒接收请求...")
            time.sleep(10)
            
            # 分析捕获的请求
            analyzer.analyze_captured_requests()
            patterns = analyzer.extract_api_patterns()
        
        # 2. 生成 SSL 证书
        print("\n2. 生成 SSL 证书...")
        # analyzer.generate_ssl_certificate()
        
        # 3. 模拟移动端请求
        print("\n3. 模拟移动端请求...")
        mobile_requests = simulate_mobile_requests()
        
        # 4. 安全分析
        print("\n4. 安全特征分析...")
        security_analysis = analyze_app_security()
        
        # 5. Frida Hook 示例
        print("\n5. Frida Hook 示例...")
        frida_examples = frida_hooking_example()
        
        print("\n=== 总结 ===")
        print("移动端抓包分析要点:")
        print("1. 设置代理服务器捕获请求")
        print("2. 处理 SSL 证书和 HTTPS")
        print("3. 分析移动端特有的请求特征")
        print("4. 识别和绕过安全防护")
        print("5. 使用 Frida 进行动态分析")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. 移动端抓包基础
   - 代理服务器设置
   - SSL 证书安装
   - HTTPS 流量解密
   - 设备网络配置
   - 抓包工具使用

2. 移动端请求特征
   - 特殊的 User-Agent
   - 设备标识符
   - 应用版本信息
   - 移动端特有头部
   - 二进制协议

3. 安全防护机制
   - SSL Certificate Pinning
   - Root/Jailbreak 检测
   - 反调试技术
   - 代码混淆
   - 运行时保护

4. 绕过技术
   - Frida 动态 Hook
   - Xposed 模块
   - SSL Kill Switch
   - Magisk Hide
   - 静态分析工具

5. 协议分析
   - API 端点发现
   - 认证机制分析
   - 参数加密解析
   - 签名算法逆向
   - 数据格式识别

工具推荐:
- Burp Suite Mobile Assistant
- Charles Proxy
- mitmproxy
- Frida
- Objection
- Xposed Framework
- Magisk

实战流程:
1. 环境准备 (代理、证书)
2. 设备配置 (网络、Root)
3. 应用分析 (静态、动态)
4. 流量捕获 (HTTP、HTTPS)
5. 协议分析 (请求、响应)
6. 安全绕过 (Hook、补丁)
7. 自动化脚本开发

注意事项:
- 仅用于授权测试
- 遵守法律法规
- 保护用户隐私
- 不要恶意攻击
- 合理使用技术
"""