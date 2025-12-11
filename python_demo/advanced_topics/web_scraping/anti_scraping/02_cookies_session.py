#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie 和会话管理教程

本教程介绍如何处理 Cookie 和会话管理来绕过基于会话的反爬机制。
包括 Cookie 持久化、会话保持、登录状态维护等技术。

作者: Python学习课程
日期: 2024
"""

import requests
import json
import time
import pickle
import os
from http.cookiejar import LWPCookieJar, MozillaCookieJar
from urllib.parse import urljoin, urlparse
import base64
import hashlib
import random
import string


class SessionManager:
    """
    会话管理器
    """
    
    def __init__(self, cookie_file=None):
        self.session = requests.Session()
        self.cookie_file = cookie_file or 'cookies.txt'
        self.login_status = False
        self.session_data = {}
        
        # 设置默认头部
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 加载已保存的 Cookie
        self.load_cookies()
    
    def save_cookies(self):
        """
        保存 Cookie 到文件
        """
        try:
            # 方法1: 使用 pickle 保存整个 cookie jar
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(self.session.cookies, f)
            
            # 方法2: 保存为 JSON 格式（可读性更好）
            json_file = self.cookie_file.replace('.txt', '.json')
            cookie_dict = {}
            
            for cookie in self.session.cookies:
                cookie_dict[cookie.name] = {
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure,
                    'rest': cookie.rest
                }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_dict, f, indent=2, ensure_ascii=False)
            
            print(f"Cookie 已保存到 {self.cookie_file} 和 {json_file}")
            
        except Exception as e:
            print(f"保存 Cookie 失败: {e}")
    
    def load_cookies(self):
        """
        从文件加载 Cookie
        """
        try:
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, 'rb') as f:
                    self.session.cookies.update(pickle.load(f))
                print(f"已加载 Cookie: {len(self.session.cookies)} 个")
                return True
        except Exception as e:
            print(f"加载 Cookie 失败: {e}")
        
        return False
    
    def clear_cookies(self):
        """
        清除所有 Cookie
        """
        self.session.cookies.clear()
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)
        print("Cookie 已清除")
    
    def get_cookie_info(self):
        """
        获取 Cookie 信息
        """
        print("=== Cookie 信息 ===")
        
        if not self.session.cookies:
            print("没有 Cookie")
            return
        
        for cookie in self.session.cookies:
            print(f"名称: {cookie.name}")
            print(f"值: {cookie.value}")
            print(f"域名: {cookie.domain}")
            print(f"路径: {cookie.path}")
            print(f"过期时间: {cookie.expires}")
            print(f"安全: {cookie.secure}")
            print("-" * 30)
    
    def simulate_login(self, username, password, login_url="https://httpbin.org/cookies/set"):
        """
        模拟登录过程
        """
        print(f"=== 模拟登录: {username} ===")
        
        try:
            # 第一步: 获取登录页面（获取 CSRF token 等）
            print("1. 获取登录页面...")
            response = self.session.get(login_url)
            
            # 模拟从页面提取 CSRF token
            csrf_token = self.generate_csrf_token()
            
            # 第二步: 提交登录表单
            print("2. 提交登录信息...")
            login_data = {
                'username': username,
                'password': password,
                'csrf_token': csrf_token,
                'remember_me': 'on'
            }
            
            # 模拟登录请求（这里使用 httpbin 的 cookie 设置接口）
            login_response = self.session.post(
                f"{login_url}/session_id/{self.generate_session_id()}",
                data=login_data
            )
            
            # 检查登录结果
            if login_response.status_code == 200:
                self.login_status = True
                self.session_data['username'] = username
                self.session_data['login_time'] = time.time()
                
                print("登录成功!")
                self.save_cookies()
                return True
            else:
                print(f"登录失败: {login_response.status_code}")
                return False
                
        except Exception as e:
            print(f"登录过程出错: {e}")
            return False
    
    def generate_csrf_token(self):
        """
        生成 CSRF token
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def generate_session_id(self):
        """
        生成会话 ID
        """
        timestamp = str(int(time.time()))
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return hashlib.md5((timestamp + random_str).encode()).hexdigest()
    
    def check_login_status(self, check_url="https://httpbin.org/cookies"):
        """
        检查登录状态
        """
        print("=== 检查登录状态 ===")
        
        try:
            response = self.session.get(check_url)
            
            if response.status_code == 200:
                # 检查响应中的 Cookie
                try:
                    data = response.json()
                    cookies = data.get('cookies', {})
                    
                    if cookies:
                        print("当前会话 Cookie:")
                        for name, value in cookies.items():
                            print(f"  {name}: {value}")
                        
                        # 检查是否有会话相关的 Cookie
                        session_indicators = ['session_id', 'sessionid', 'JSESSIONID', 'PHPSESSID']
                        has_session = any(indicator in cookies for indicator in session_indicators)
                        
                        if has_session:
                            print("检测到会话 Cookie，可能已登录")
                            self.login_status = True
                        else:
                            print("未检测到会话 Cookie")
                            self.login_status = False
                    else:
                        print("没有 Cookie")
                        self.login_status = False
                        
                except json.JSONDecodeError:
                    print("无法解析响应为 JSON")
                    
            else:
                print(f"检查失败: {response.status_code}")
                
        except Exception as e:
            print(f"检查登录状态出错: {e}")
        
        return self.login_status
    
    def maintain_session(self, heartbeat_url="https://httpbin.org/get"):
        """
        维持会话活跃
        """
        print("=== 维持会话活跃 ===")
        
        if not self.login_status:
            print("未登录，无需维持会话")
            return
        
        try:
            # 发送心跳请求
            response = self.session.get(heartbeat_url)
            
            if response.status_code == 200:
                print("会话心跳成功")
                
                # 更新最后活跃时间
                self.session_data['last_active'] = time.time()
                
                # 检查是否需要刷新 Cookie
                self.refresh_cookies_if_needed()
                
            else:
                print(f"会话心跳失败: {response.status_code}")
                
        except Exception as e:
            print(f"维持会话出错: {e}")
    
    def refresh_cookies_if_needed(self):
        """
        根据需要刷新 Cookie
        """
        current_time = time.time()
        
        # 检查 Cookie 是否即将过期
        for cookie in self.session.cookies:
            if cookie.expires and cookie.expires < current_time + 3600:  # 1小时内过期
                print(f"Cookie {cookie.name} 即将过期，需要刷新")
                # 这里可以实现 Cookie 刷新逻辑
                break
    
    def handle_session_timeout(self):
        """
        处理会话超时
        """
        print("=== 处理会话超时 ===")
        
        # 清除过期的会话数据
        self.login_status = False
        self.session_data.clear()
        
        # 可以选择重新登录
        print("会话已超时，需要重新登录")


def cookie_analysis_demo():
    """
    Cookie 分析演示
    """
    print("\n=== Cookie 分析演示 ===")
    
    # 创建会话管理器
    session_mgr = SessionManager('demo_cookies.txt')
    
    # 模拟访问需要 Cookie 的网站
    test_url = "https://httpbin.org/cookies/set/test_cookie/test_value"
    
    print("1. 首次访问，设置 Cookie...")
    response = session_mgr.session.get(test_url)
    print(f"响应状态: {response.status_code}")
    
    # 显示 Cookie 信息
    session_mgr.get_cookie_info()
    
    # 保存 Cookie
    session_mgr.save_cookies()
    
    # 测试 Cookie 持久化
    print("\n2. 创建新会话管理器，测试 Cookie 加载...")
    new_session_mgr = SessionManager('demo_cookies.txt')
    
    # 使用加载的 Cookie 访问
    check_url = "https://httpbin.org/cookies"
    response = new_session_mgr.session.get(check_url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("服务器接收到的 Cookie:")
            print(json.dumps(data.get('cookies', {}), indent=2))
        except:
            print("无法解析响应")
    
    return session_mgr


def advanced_cookie_techniques():
    """
    高级 Cookie 技术
    """
    print("\n=== 高级 Cookie 技术 ===")
    
    # 技术1: Cookie 域名和路径管理
    def cookie_domain_path_demo():
        print("\n技术1: Cookie 域名和路径管理")
        
        session = requests.Session()
        
        # 设置不同域名和路径的 Cookie
        cookie_configs = [
            {'name': 'site_cookie', 'value': 'site_value', 'domain': '.example.com', 'path': '/'},
            {'name': 'api_cookie', 'value': 'api_value', 'domain': 'api.example.com', 'path': '/v1/'},
            {'name': 'user_cookie', 'value': 'user_value', 'domain': 'www.example.com', 'path': '/user/'},
        ]
        
        for config in cookie_configs:
            session.cookies.set(
                name=config['name'],
                value=config['value'],
                domain=config['domain'],
                path=config['path']
            )
            print(f"设置 Cookie: {config['name']} for {config['domain']}{config['path']}")
        
        # 显示 Cookie 匹配规则
        test_urls = [
            'https://www.example.com/',
            'https://api.example.com/v1/data',
            'https://www.example.com/user/profile',
            'https://sub.example.com/page'
        ]
        
        for url in test_urls:
            matching_cookies = []
            for cookie in session.cookies:
                # 简化的匹配逻辑
                parsed_url = urlparse(url)
                if (cookie.domain in parsed_url.netloc or parsed_url.netloc.endswith(cookie.domain)) and \
                   parsed_url.path.startswith(cookie.path):
                    matching_cookies.append(cookie.name)
            
            print(f"URL {url} 匹配的 Cookie: {matching_cookies}")
    
    # 技术2: Cookie 加密和签名
    def cookie_security_demo():
        print("\n技术2: Cookie 安全处理")
        
        # 模拟加密 Cookie 值
        def encrypt_cookie_value(value, key="secret_key"):
            # 简单的 Base64 + 时间戳加密
            timestamp = str(int(time.time()))
            data = f"{value}:{timestamp}"
            encoded = base64.b64encode(data.encode()).decode()
            
            # 添加签名
            signature = hashlib.md5((encoded + key).encode()).hexdigest()[:8]
            return f"{encoded}.{signature}"
        
        def decrypt_cookie_value(encrypted_value, key="secret_key"):
            try:
                encoded, signature = encrypted_value.split('.')
                
                # 验证签名
                expected_sig = hashlib.md5((encoded + key).encode()).hexdigest()[:8]
                if signature != expected_sig:
                    return None, "签名验证失败"
                
                # 解密数据
                decoded = base64.b64decode(encoded).decode()
                value, timestamp = decoded.split(':')
                
                # 检查时间戳（例如：24小时有效期）
                if int(time.time()) - int(timestamp) > 86400:
                    return None, "Cookie 已过期"
                
                return value, "成功"
                
            except Exception as e:
                return None, f"解密失败: {e}"
        
        # 演示加密和解密
        original_value = "user_id_12345"
        encrypted = encrypt_cookie_value(original_value)
        decrypted, status = decrypt_cookie_value(encrypted)
        
        print(f"原始值: {original_value}")
        print(f"加密后: {encrypted}")
        print(f"解密后: {decrypted} ({status})")
    
    # 技术3: Cookie 池管理
    def cookie_pool_demo():
        print("\n技术3: Cookie 池管理")
        
        class CookiePool:
            def __init__(self):
                self.cookie_pool = []
                self.current_index = 0
            
            def add_session(self, session_cookies):
                """添加会话 Cookie 到池中"""
                self.cookie_pool.append(session_cookies)
                print(f"添加会话到池中，当前池大小: {len(self.cookie_pool)}")
            
            def get_next_session(self):
                """获取下一个会话 Cookie"""
                if not self.cookie_pool:
                    return None
                
                cookies = self.cookie_pool[self.current_index]
                self.current_index = (self.current_index + 1) % len(self.cookie_pool)
                return cookies
            
            def remove_invalid_session(self, session_cookies):
                """移除无效的会话 Cookie"""
                if session_cookies in self.cookie_pool:
                    self.cookie_pool.remove(session_cookies)
                    print(f"移除无效会话，当前池大小: {len(self.cookie_pool)}")
        
        # 演示 Cookie 池使用
        pool = CookiePool()
        
        # 模拟添加多个会话
        for i in range(3):
            session = requests.Session()
            session.cookies.set('session_id', f'session_{i}')
            session.cookies.set('user_token', f'token_{i}')
            pool.add_session(session.cookies)
        
        # 轮换使用会话
        for i in range(5):
            cookies = pool.get_next_session()
            if cookies:
                session_id = cookies.get('session_id', 'unknown')
                print(f"使用会话: {session_id}")
    
    # 执行演示
    cookie_domain_path_demo()
    cookie_security_demo()
    cookie_pool_demo()


def session_persistence_demo():
    """
    会话持久化演示
    """
    print("\n=== 会话持久化演示 ===")
    
    # 创建会话管理器
    session_mgr = SessionManager('persistent_session.txt')
    
    # 模拟登录
    print("1. 模拟用户登录...")
    login_success = session_mgr.simulate_login('testuser', 'testpass')
    
    if login_success:
        print("2. 检查登录状态...")
        session_mgr.check_login_status()
        
        print("3. 模拟一些业务操作...")
        business_urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers"
        ]
        
        for url in business_urls:
            try:
                response = session_mgr.session.get(url)
                print(f"访问 {url}: {response.status_code}")
                time.sleep(1)  # 模拟操作间隔
            except Exception as e:
                print(f"访问 {url} 失败: {e}")
        
        print("4. 维持会话活跃...")
        session_mgr.maintain_session()
        
        print("5. 保存会话状态...")
        session_mgr.save_cookies()
        
        # 模拟程序重启后恢复会话
        print("\n6. 模拟程序重启，恢复会话...")
        new_session_mgr = SessionManager('persistent_session.txt')
        new_session_mgr.check_login_status()
        
        if new_session_mgr.login_status:
            print("会话恢复成功!")
        else:
            print("会话恢复失败，需要重新登录")


def main():
    """
    主函数，运行所有示例
    """
    print("Cookie 和会话管理教程")
    print("=" * 50)
    
    try:
        # 1. Cookie 分析演示
        session_mgr = cookie_analysis_demo()
        
        # 2. 高级 Cookie 技术
        advanced_cookie_techniques()
        
        # 3. 会话持久化演示
        session_persistence_demo()
        
        print(f"\n=== 最佳实践总结 ===")
        best_practices = [
            "1. 正确保存和加载 Cookie",
            "2. 处理 Cookie 的域名和路径",
            "3. 实现会话超时检测",
            "4. 维持会话活跃状态",
            "5. 处理登录状态验证",
            "6. 实现 Cookie 池轮换",
            "7. 加密敏感 Cookie 数据",
            "8. 监控会话有效性"
        ]
        
        for practice in best_practices:
            print(f"  {practice}")
        
        # 清理演示文件
        cleanup_files = ['demo_cookies.txt', 'demo_cookies.json', 'persistent_session.txt']
        for file in cleanup_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"清理文件: {file}")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. Cookie 基础知识
   - Cookie 的作用和机制
   - 域名和路径匹配规则
   - 过期时间和安全属性
   - HttpOnly 和 Secure 标志

2. 会话管理
   - 会话 ID 的生成和维护
   - 登录状态的保持
   - 会话超时处理
   - 心跳机制实现

3. Cookie 持久化
   - 文件存储格式选择
   - 加载和保存机制
   - 跨程序会话恢复
   - 数据完整性验证

4. 高级技术
   - Cookie 加密和签名
   - 多会话池管理
   - 智能轮换策略
   - 失效检测和恢复

5. 安全考虑
   - 敏感信息加密
   - 时间戳验证
   - 签名防篡改
   - 安全存储实践

常见问题解决:
- 会话过期自动重登录
- Cookie 冲突处理
- 跨域 Cookie 管理
- 移动端会话适配
- 分布式会话同步

工具和库:
- requests.Session: 会话管理
- http.cookiejar: Cookie 存储
- pickle/json: 数据序列化
- cryptography: 加密处理

实施建议:
1. 设计完整的会话生命周期
2. 实现自动登录和重试机制
3. 监控会话状态和有效性
4. 建立 Cookie 池管理系统
5. 加强安全防护措施

注意事项:
- 遵守网站的会话策略
- 不要过度频繁地请求
- 保护用户隐私和数据安全
- 合理处理异常情况
- 定期清理过期数据
"""