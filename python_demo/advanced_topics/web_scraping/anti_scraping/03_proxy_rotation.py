#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理轮换教程

本教程介绍如何使用代理服务器进行 IP 轮换，绕过基于 IP 的反爬限制。
包括代理池管理、健康检查、智能轮换等技术。

作者: Python学习课程
日期: 2024
"""

import requests
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from urllib.parse import urlparse
import socket
import socks
from collections import defaultdict, deque


class ProxyManager:
    """
    代理管理器
    """
    
    def __init__(self):
        self.proxy_pool = []
        self.working_proxies = []
        self.failed_proxies = set()
        self.proxy_stats = defaultdict(lambda: {'success': 0, 'failed': 0, 'response_time': []})
        self.current_index = 0
        self.lock = threading.Lock()
        
        # 初始化代理池
        self.init_proxy_pool()
    
    def init_proxy_pool(self):
        """
        初始化代理池
        """
        print("=== 初始化代理池 ===")
        
        # 免费代理列表（仅用于演示，实际使用需要有效代理）
        free_proxies = [
            # HTTP 代理
            {'type': 'http', 'host': '127.0.0.1', 'port': 8888, 'auth': None},
            {'type': 'http', 'host': '127.0.0.1', 'port': 8889, 'auth': None},
            
            # SOCKS5 代理
            {'type': 'socks5', 'host': '127.0.0.1', 'port': 1080, 'auth': None},
            
            # 带认证的代理
            {'type': 'http', 'host': 'proxy.example.com', 'port': 8080, 'auth': ('username', 'password')},
        ]
        
        # 公共代理 API（示例，需要替换为真实的代理服务）
        public_proxy_apis = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        ]
        
        # 添加免费代理到池中
        for proxy in free_proxies:
            self.proxy_pool.append(proxy)
        
        # 尝试从公共 API 获取代理
        self.fetch_public_proxies(public_proxy_apis)
        
        print(f"代理池初始化完成，共 {len(self.proxy_pool)} 个代理")
    
    def fetch_public_proxies(self, api_urls):
        """
        从公共 API 获取代理
        """
        print("从公共 API 获取代理...")
        
        for api_url in api_urls:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    # 解析代理列表
                    proxies = self.parse_proxy_response(response.text)
                    self.proxy_pool.extend(proxies)
                    print(f"从 {api_url} 获取到 {len(proxies)} 个代理")
                    
            except Exception as e:
                print(f"获取代理失败 {api_url}: {e}")
    
    def parse_proxy_response(self, response_text):
        """
        解析代理响应
        """
        proxies = []
        
        # 尝试解析不同格式的代理列表
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                # 格式: host:port
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        host, port = parts
                        proxy = {
                            'type': 'http',
                            'host': host.strip(),
                            'port': int(port.strip()),
                            'auth': None
                        }
                        proxies.append(proxy)
                        
            except Exception:
                continue
        
        return proxies[:10]  # 限制数量，避免过多无效代理
    
    def check_proxy_health(self, proxy, test_url="https://httpbin.org/ip", timeout=10):
        """
        检查代理健康状态
        """
        try:
            start_time = time.time()
            
            # 构建代理配置
            proxy_config = self.build_proxy_config(proxy)
            
            # 发送测试请求
            response = requests.get(
                test_url,
                proxies=proxy_config,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # 验证 IP 是否改变
                try:
                    data = response.json()
                    proxy_ip = data.get('origin', '').split(',')[0].strip()
                    
                    return {
                        'success': True,
                        'response_time': response_time,
                        'proxy_ip': proxy_ip,
                        'status_code': response.status_code
                    }
                except:
                    return {
                        'success': True,
                        'response_time': response_time,
                        'proxy_ip': 'unknown',
                        'status_code': response.status_code
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'response_time': response_time
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response_time': timeout
            }
    
    def build_proxy_config(self, proxy):
        """
        构建代理配置
        """
        if proxy['type'] == 'http':
            if proxy['auth']:
                username, password = proxy['auth']
                proxy_url = f"http://{username}:{password}@{proxy['host']}:{proxy['port']}"
            else:
                proxy_url = f"http://{proxy['host']}:{proxy['port']}"
            
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        
        elif proxy['type'] == 'socks5':
            if proxy['auth']:
                username, password = proxy['auth']
                proxy_url = f"socks5://{username}:{password}@{proxy['host']}:{proxy['port']}"
            else:
                proxy_url = f"socks5://{proxy['host']}:{proxy['port']}"
            
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        
        return {}
    
    def test_all_proxies(self, max_workers=10):
        """
        测试所有代理的健康状态
        """
        print(f"\n=== 测试代理健康状态 ({len(self.proxy_pool)} 个) ===")
        
        working_proxies = []
        
        def test_single_proxy(proxy):
            result = self.check_proxy_health(proxy)
            return proxy, result
        
        # 并发测试代理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(test_single_proxy, proxy): proxy 
                             for proxy in self.proxy_pool}
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    proxy, result = future.result()
                    
                    proxy_key = f"{proxy['host']}:{proxy['port']}"
                    
                    if result['success']:
                        working_proxies.append(proxy)
                        self.proxy_stats[proxy_key]['success'] += 1
                        self.proxy_stats[proxy_key]['response_time'].append(result['response_time'])
                        
                        print(f"✓ {proxy_key} - {result['response_time']:.2f}s - IP: {result.get('proxy_ip', 'unknown')}")
                    else:
                        self.failed_proxies.add(proxy_key)
                        self.proxy_stats[proxy_key]['failed'] += 1
                        
                        print(f"✗ {proxy_key} - {result.get('error', 'unknown error')}")
                        
                except Exception as e:
                    print(f"✗ 测试代理出错: {e}")
        
        self.working_proxies = working_proxies
        print(f"\n可用代理: {len(working_proxies)} 个")
        
        return working_proxies
    
    def get_next_proxy(self):
        """
        获取下一个可用代理
        """
        with self.lock:
            if not self.working_proxies:
                return None
            
            proxy = self.working_proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.working_proxies)
            
            return proxy
    
    def get_best_proxy(self):
        """
        获取最佳代理（基于响应时间和成功率）
        """
        if not self.working_proxies:
            return None
        
        best_proxy = None
        best_score = float('inf')
        
        for proxy in self.working_proxies:
            proxy_key = f"{proxy['host']}:{proxy['port']}"
            stats = self.proxy_stats[proxy_key]
            
            if stats['response_time']:
                avg_response_time = sum(stats['response_time']) / len(stats['response_time'])
                success_rate = stats['success'] / (stats['success'] + stats['failed'])
                
                # 综合评分：响应时间越低越好，成功率越高越好
                score = avg_response_time / success_rate
                
                if score < best_score:
                    best_score = score
                    best_proxy = proxy
        
        return best_proxy or self.working_proxies[0]
    
    def remove_failed_proxy(self, proxy):
        """
        移除失败的代理
        """
        with self.lock:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                proxy_key = f"{proxy['host']}:{proxy['port']}"
                self.failed_proxies.add(proxy_key)
                print(f"移除失败代理: {proxy_key}")
    
    def get_proxy_stats(self):
        """
        获取代理统计信息
        """
        return dict(self.proxy_stats)


class ProxyRotationSession:
    """
    代理轮换会话
    """
    
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
        self.current_proxy = None
        self.request_count = 0
        self.rotation_interval = 10  # 每10个请求轮换一次
        
        # 设置默认头部
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def request(self, method, url, **kwargs):
        """
        发送请求，自动处理代理轮换
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 检查是否需要轮换代理
                if self.should_rotate_proxy():
                    self.rotate_proxy()
                
                # 设置代理
                if self.current_proxy:
                    proxy_config = self.proxy_manager.build_proxy_config(self.current_proxy)
                    kwargs['proxies'] = proxy_config
                
                # 发送请求
                response = self.session.request(method, url, **kwargs)
                
                # 更新统计
                self.request_count += 1
                
                if self.current_proxy:
                    proxy_key = f"{self.current_proxy['host']}:{self.current_proxy['port']}"
                    self.proxy_manager.proxy_stats[proxy_key]['success'] += 1
                
                return response
                
            except Exception as e:
                print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                # 如果是代理相关错误，移除当前代理
                if self.current_proxy and self.is_proxy_error(e):
                    self.proxy_manager.remove_failed_proxy(self.current_proxy)
                    self.current_proxy = None
                
                if attempt == max_retries - 1:
                    raise e
                
                time.sleep(1)  # 重试前等待
        
        return None
    
    def should_rotate_proxy(self):
        """
        判断是否应该轮换代理
        """
        # 没有当前代理
        if not self.current_proxy:
            return True
        
        # 达到轮换间隔
        if self.request_count % self.rotation_interval == 0:
            return True
        
        return False
    
    def rotate_proxy(self):
        """
        轮换代理
        """
        new_proxy = self.proxy_manager.get_next_proxy()
        
        if new_proxy:
            self.current_proxy = new_proxy
            proxy_key = f"{new_proxy['host']}:{new_proxy['port']}"
            print(f"轮换到代理: {proxy_key}")
        else:
            print("没有可用代理")
            self.current_proxy = None
    
    def is_proxy_error(self, error):
        """
        判断是否为代理相关错误
        """
        error_str = str(error).lower()
        proxy_error_keywords = [
            'connection error', 'proxy error', 'tunnel connection failed',
            'connection refused', 'timeout', 'unreachable'
        ]
        
        return any(keyword in error_str for keyword in proxy_error_keywords)
    
    def get(self, url, **kwargs):
        """GET 请求"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url, **kwargs):
        """POST 请求"""
        return self.request('POST', url, **kwargs)


def proxy_rotation_demo():
    """
    代理轮换演示
    """
    print("\n=== 代理轮换演示 ===")
    
    # 创建代理管理器
    proxy_mgr = ProxyManager()
    
    # 测试代理健康状态
    working_proxies = proxy_mgr.test_all_proxies()
    
    if not working_proxies:
        print("没有可用代理，使用直连模式演示")
        # 添加一个虚拟的"直连"代理用于演示
        proxy_mgr.working_proxies = [{'type': 'direct', 'host': 'direct', 'port': 0, 'auth': None}]
    
    # 创建轮换会话
    session = ProxyRotationSession(proxy_mgr)
    
    # 模拟多个请求
    test_urls = [
        'https://httpbin.org/ip',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/headers',
        'https://httpbin.org/get',
    ] * 3  # 重复3次，总共12个请求
    
    print(f"\n发送 {len(test_urls)} 个测试请求...")
    
    for i, url in enumerate(test_urls, 1):
        try:
            print(f"\n请求 {i}: {url}")
            
            if session.current_proxy and session.current_proxy['type'] != 'direct':
                response = session.get(url, timeout=10)
                
                if response and response.status_code == 200:
                    try:
                        data = response.json()
                        current_ip = data.get('origin', 'unknown').split(',')[0].strip()
                        print(f"  响应成功 - 当前 IP: {current_ip}")
                    except:
                        print(f"  响应成功 - 状态码: {response.status_code}")
                else:
                    print(f"  响应失败")
            else:
                # 直连模式
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        current_ip = data.get('origin', 'unknown').split(',')[0].strip()
                        print(f"  直连成功 - 当前 IP: {current_ip}")
                    except:
                        print(f"  直连成功 - 状态码: {response.status_code}")
            
            time.sleep(1)  # 请求间隔
            
        except Exception as e:
            print(f"  请求失败: {e}")
    
    # 显示统计信息
    print(f"\n=== 代理使用统计 ===")
    stats = proxy_mgr.get_proxy_stats()
    
    for proxy_key, stat in stats.items():
        if stat['success'] > 0 or stat['failed'] > 0:
            success_rate = stat['success'] / (stat['success'] + stat['failed']) * 100
            avg_time = sum(stat['response_time']) / len(stat['response_time']) if stat['response_time'] else 0
            
            print(f"{proxy_key}:")
            print(f"  成功: {stat['success']}, 失败: {stat['failed']}")
            print(f"  成功率: {success_rate:.1f}%")
            print(f"  平均响应时间: {avg_time:.2f}s")


def advanced_proxy_techniques():
    """
    高级代理技术
    """
    print("\n=== 高级代理技术 ===")
    
    # 技术1: 智能代理选择
    def smart_proxy_selection():
        print("\n技术1: 智能代理选择")
        
        class SmartProxySelector:
            def __init__(self, proxies):
                self.proxies = proxies
                self.performance_history = defaultdict(lambda: deque(maxlen=10))
                self.failure_count = defaultdict(int)
                self.last_used = defaultdict(float)
            
            def select_proxy(self, target_domain=None):
                """基于多个因素选择最佳代理"""
                
                # 过滤掉最近失败过多的代理
                available_proxies = [
                    p for p in self.proxies 
                    if self.failure_count[f"{p['host']}:{p['port']}"] < 3
                ]
                
                if not available_proxies:
                    return None
                
                best_proxy = None
                best_score = float('-inf')
                
                current_time = time.time()
                
                for proxy in available_proxies:
                    proxy_key = f"{proxy['host']}:{proxy['port']}"
                    
                    # 计算评分因子
                    # 1. 性能历史 (响应时间)
                    perf_history = self.performance_history[proxy_key]
                    avg_response_time = sum(perf_history) / len(perf_history) if perf_history else 5.0
                    perf_score = 1.0 / (avg_response_time + 0.1)  # 响应时间越短分数越高
                    
                    # 2. 失败率
                    failure_score = 1.0 / (self.failure_count[proxy_key] + 1)
                    
                    # 3. 使用间隔 (避免频繁使用同一代理)
                    time_since_last_use = current_time - self.last_used[proxy_key]
                    interval_score = min(time_since_last_use / 60.0, 1.0)  # 最多1分钟间隔
                    
                    # 综合评分
                    total_score = perf_score * 0.4 + failure_score * 0.4 + interval_score * 0.2
                    
                    if total_score > best_score:
                        best_score = total_score
                        best_proxy = proxy
                
                if best_proxy:
                    proxy_key = f"{best_proxy['host']}:{best_proxy['port']}"
                    self.last_used[proxy_key] = current_time
                
                return best_proxy
            
            def record_performance(self, proxy, response_time, success):
                """记录代理性能"""
                proxy_key = f"{proxy['host']}:{proxy['port']}"
                
                if success:
                    self.performance_history[proxy_key].append(response_time)
                    # 成功时减少失败计数
                    if self.failure_count[proxy_key] > 0:
                        self.failure_count[proxy_key] -= 1
                else:
                    self.failure_count[proxy_key] += 1
        
        # 演示智能选择
        demo_proxies = [
            {'host': 'proxy1.example.com', 'port': 8080, 'type': 'http', 'auth': None},
            {'host': 'proxy2.example.com', 'port': 8080, 'type': 'http', 'auth': None},
            {'host': 'proxy3.example.com', 'port': 8080, 'type': 'http', 'auth': None},
        ]
        
        selector = SmartProxySelector(demo_proxies)
        
        # 模拟使用历史
        for i in range(5):
            proxy = selector.select_proxy()
            if proxy:
                # 模拟性能数据
                response_time = random.uniform(1.0, 5.0)
                success = random.choice([True, True, True, False])  # 75% 成功率
                
                selector.record_performance(proxy, response_time, success)
                
                proxy_key = f"{proxy['host']}:{proxy['port']}"
                status = "成功" if success else "失败"
                print(f"  选择 {proxy_key} - {response_time:.2f}s - {status}")
    
    # 技术2: 代理池动态管理
    def dynamic_proxy_pool():
        print("\n技术2: 代理池动态管理")
        
        class DynamicProxyPool:
            def __init__(self):
                self.active_proxies = []
                self.backup_proxies = []
                self.blacklisted_proxies = set()
                self.health_check_interval = 300  # 5分钟
                self.last_health_check = 0
            
            def add_proxy_source(self, source_func):
                """添加代理源"""
                try:
                    new_proxies = source_func()
                    self.backup_proxies.extend(new_proxies)
                    print(f"从代理源获取 {len(new_proxies)} 个代理")
                except Exception as e:
                    print(f"获取代理源失败: {e}")
            
            def promote_backup_proxies(self, count=5):
                """提升备用代理到活跃池"""
                promoted = 0
                
                while self.backup_proxies and promoted < count:
                    proxy = self.backup_proxies.pop(0)
                    proxy_key = f"{proxy['host']}:{proxy['port']}"
                    
                    if proxy_key not in self.blacklisted_proxies:
                        self.active_proxies.append(proxy)
                        promoted += 1
                        print(f"提升代理到活跃池: {proxy_key}")
                
                return promoted
            
            def remove_failed_proxy(self, proxy):
                """移除失败代理"""
                proxy_key = f"{proxy['host']}:{proxy['port']}"
                
                if proxy in self.active_proxies:
                    self.active_proxies.remove(proxy)
                
                self.blacklisted_proxies.add(proxy_key)
                print(f"代理已加入黑名单: {proxy_key}")
                
                # 如果活跃代理不足，提升备用代理
                if len(self.active_proxies) < 3:
                    self.promote_backup_proxies(2)
            
            def periodic_health_check(self):
                """定期健康检查"""
                current_time = time.time()
                
                if current_time - self.last_health_check > self.health_check_interval:
                    print("执行定期健康检查...")
                    
                    # 检查活跃代理
                    failed_proxies = []
                    for proxy in self.active_proxies:
                        # 这里应该实际检查代理健康状态
                        # 为演示目的，随机标记一些为失败
                        if random.random() < 0.1:  # 10% 失败率
                            failed_proxies.append(proxy)
                    
                    # 移除失败代理
                    for proxy in failed_proxies:
                        self.remove_failed_proxy(proxy)
                    
                    self.last_health_check = current_time
        
        # 演示动态管理
        pool = DynamicProxyPool()
        
        # 模拟代理源
        def mock_proxy_source():
            return [
                {'host': f'proxy{i}.example.com', 'port': 8080, 'type': 'http', 'auth': None}
                for i in range(1, 6)
            ]
        
        pool.add_proxy_source(mock_proxy_source)
        pool.promote_backup_proxies(3)
        
        print(f"活跃代理数量: {len(pool.active_proxies)}")
        print(f"备用代理数量: {len(pool.backup_proxies)}")
    
    # 技术3: 地理位置代理选择
    def geo_proxy_selection():
        print("\n技术3: 地理位置代理选择")
        
        class GeoProxyManager:
            def __init__(self):
                self.proxies_by_country = defaultdict(list)
                self.country_preferences = {}
            
            def add_proxy(self, proxy, country):
                """添加带地理位置信息的代理"""
                proxy['country'] = country
                self.proxies_by_country[country].append(proxy)
            
            def set_country_preference(self, target_domain, preferred_countries):
                """设置域名的国家偏好"""
                self.country_preferences[target_domain] = preferred_countries
            
            def select_proxy_by_geo(self, target_url):
                """根据地理位置选择代理"""
                domain = urlparse(target_url).netloc
                
                # 检查是否有特定偏好
                if domain in self.country_preferences:
                    preferred_countries = self.country_preferences[domain]
                    
                    for country in preferred_countries:
                        if country in self.proxies_by_country:
                            proxies = self.proxies_by_country[country]
                            if proxies:
                                return random.choice(proxies)
                
                # 没有偏好时随机选择
                all_proxies = []
                for proxies in self.proxies_by_country.values():
                    all_proxies.extend(proxies)
                
                return random.choice(all_proxies) if all_proxies else None
        
        # 演示地理位置选择
        geo_mgr = GeoProxyManager()
        
        # 添加不同国家的代理
        countries = ['US', 'UK', 'DE', 'JP', 'SG']
        for country in countries:
            for i in range(2):
                proxy = {
                    'host': f'{country.lower()}-proxy{i}.example.com',
                    'port': 8080,
                    'type': 'http',
                    'auth': None
                }
                geo_mgr.add_proxy(proxy, country)
        
        # 设置偏好
        geo_mgr.set_country_preference('amazon.com', ['US'])
        geo_mgr.set_country_preference('amazon.co.uk', ['UK'])
        geo_mgr.set_country_preference('rakuten.co.jp', ['JP'])
        
        # 测试选择
        test_urls = [
            'https://amazon.com/products',
            'https://amazon.co.uk/products',
            'https://rakuten.co.jp/products',
            'https://example.com/page'
        ]
        
        for url in test_urls:
            proxy = geo_mgr.select_proxy_by_geo(url)
            if proxy:
                print(f"  {url} -> {proxy['country']} ({proxy['host']})")
    
    # 执行演示
    smart_proxy_selection()
    dynamic_proxy_pool()
    geo_proxy_selection()


def main():
    """
    主函数，运行所有示例
    """
    print("代理轮换教程")
    print("=" * 50)
    
    try:
        # 1. 代理轮换演示
        proxy_rotation_demo()
        
        # 2. 高级代理技术
        advanced_proxy_techniques()
        
        print(f"\n=== 代理使用最佳实践 ===")
        best_practices = [
            "1. 维护多个代理源",
            "2. 实现健康检查机制",
            "3. 智能代理选择算法",
            "4. 地理位置匹配",
            "5. 失败代理自动移除",
            "6. 代理池动态管理",
            "7. 请求频率控制",
            "8. 代理认证管理",
            "9. 监控代理性能",
            "10. 备用代理准备"
        ]
        
        for practice in best_practices:
            print(f"  {practice}")
        
        print(f"\n=== 注意事项 ===")
        warnings = [
            "• 使用合法的代理服务",
            "• 遵守代理服务条款",
            "• 不要滥用免费代理",
            "• 保护代理认证信息",
            "• 监控代理使用成本",
            "• 定期更新代理列表"
        ]
        
        for warning in warnings:
            print(f"  {warning}")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. 代理基础知识
   - HTTP/HTTPS 代理
   - SOCKS4/SOCKS5 代理
   - 代理认证机制
   - 代理链和级联

2. 代理池管理
   - 代理获取和验证
   - 健康状态检查
   - 失效代理移除
   - 动态池维护

3. 轮换策略
   - 随机轮换
   - 顺序轮换
   - 智能选择
   - 基于性能轮换

4. 高级技术
   - 地理位置匹配
   - 性能评分系统
   - 失败重试机制
   - 负载均衡

5. 监控和优化
   - 响应时间统计
   - 成功率监控
   - 代理质量评估
   - 成本效益分析

代理来源:
- 付费代理服务
- 免费代理列表
- 自建代理服务器
- 云服务商代理
- 住宅代理网络

工具和库:
- requests: HTTP 请求
- pysocks: SOCKS 代理支持
- aiohttp: 异步 HTTP
- proxy-checker: 代理验证
- rotating-proxies: Scrapy 代理轮换

实施建议:
1. 选择可靠的代理服务商
2. 实现完整的代理管理系统
3. 监控代理使用情况
4. 建立代理质量评估机制
5. 准备多个备用方案

常见问题:
- 代理连接超时
- 认证失败
- IP 被封禁
- 代理质量差
- 成本控制

注意事项:
- 遵守法律法规
- 尊重网站条款
- 合理使用代理资源
- 保护隐私和安全
- 避免恶意行为
"""