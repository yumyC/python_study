#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密参数解析教程

本教程介绍如何分析和破解网站中的加密参数，包括常见的加密算法识别、
参数生成逻辑分析、签名验证机制等。

作者: Python学习课程
日期: 2024
"""

import hashlib
import hmac
import base64
import json
import time
import random
import string
import re
from urllib.parse import quote, unquote, parse_qs
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import execjs
import subprocess
import os


class EncryptionAnalyzer:
    """
    加密参数分析器
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze_request_parameters(self, url, params):
        """
        分析请求参数的加密模式
        """
        print(f"=== 分析请求参数 ===")
        print(f"URL: {url}")
        print(f"参数: {json.dumps(params, indent=2, ensure_ascii=False)}")
        
        analysis_result = {
            'timestamp_params': [],
            'hash_params': [],
            'encoded_params': [],
            'signature_params': [],
            'encrypted_params': []
        }
        
        for key, value in params.items():
            if isinstance(value, str):
                param_type = self.identify_parameter_type(key, value)
                analysis_result[param_type].append({
                    'key': key,
                    'value': value,
                    'analysis': self.analyze_parameter_value(value)
                })
        
        # 打印分析结果
        for param_type, param_list in analysis_result.items():
            if param_list:
                print(f"\n{param_type}:")
                for param in param_list:
                    print(f"  {param['key']}: {param['value']}")
                    if param['analysis']:
                        print(f"    分析: {param['analysis']}")
        
        return analysis_result
    
    def identify_parameter_type(self, key, value):
        """
        识别参数类型
        """
        key_lower = key.lower()
        
        # 时间戳参数
        if any(keyword in key_lower for keyword in ['time', 'timestamp', 'ts', 't']):
            if self.is_timestamp(value):
                return 'timestamp_params'
        
        # 签名参数
        if any(keyword in key_lower for keyword in ['sign', 'signature', 'sig', 'hash']):
            return 'signature_params'
        
        # 哈希参数
        if self.is_hash_like(value):
            return 'hash_params'
        
        # 编码参数
        if self.is_base64_like(value) or self.is_url_encoded(value):
            return 'encoded_params'
        
        # 加密参数
        if self.is_encrypted_like(value):
            return 'encrypted_params'
        
        return 'other_params'
    
    def analyze_parameter_value(self, value):
        """
        分析参数值
        """
        analysis = []
        
        # 检查是否为时间戳
        if self.is_timestamp(value):
            try:
                timestamp = int(value)
                if len(value) == 10:  # 秒级时间戳
                    analysis.append(f"10位时间戳 (秒): {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}")
                elif len(value) == 13:  # 毫秒级时间戳
                    analysis.append(f"13位时间戳 (毫秒): {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))}")
            except:
                pass
        
        # 检查哈希特征
        if self.is_hash_like(value):
            hash_type = self.identify_hash_type(value)
            if hash_type:
                analysis.append(f"可能的哈希类型: {hash_type}")
        
        # 检查 Base64 编码
        if self.is_base64_like(value):
            try:
                decoded = base64.b64decode(value).decode('utf-8')
                analysis.append(f"Base64 解码: {decoded}")
            except:
                try:
                    decoded = base64.b64decode(value)
                    analysis.append(f"Base64 解码 (二进制): {len(decoded)} 字节")
                except:
                    analysis.append("Base64 解码失败")
        
        # 检查 URL 编码
        if self.is_url_encoded(value):
            decoded = unquote(value)
            analysis.append(f"URL 解码: {decoded}")
        
        return '; '.join(analysis) if analysis else None
    
    def is_timestamp(self, value):
        """
        判断是否为时间戳
        """
        try:
            timestamp = int(value)
            # 检查是否在合理的时间戳范围内
            return 1000000000 <= timestamp <= 9999999999999  # 2001年到2286年
        except:
            return False
    
    def is_hash_like(self, value):
        """
        判断是否像哈希值
        """
        if not isinstance(value, str):
            return False
        
        # 检查长度和字符
        if re.match(r'^[a-fA-F0-9]+$', value):
            return len(value) in [32, 40, 56, 64, 96, 128]  # 常见哈希长度
        
        return False
    
    def identify_hash_type(self, value):
        """
        识别哈希类型
        """
        length = len(value)
        
        hash_types = {
            32: 'MD5',
            40: 'SHA1',
            56: 'SHA224',
            64: 'SHA256',
            96: 'SHA384',
            128: 'SHA512'
        }
        
        return hash_types.get(length)
    
    def is_base64_like(self, value):
        """
        判断是否像 Base64 编码
        """
        if not isinstance(value, str) or len(value) < 4:
            return False
        
        # Base64 字符集检查
        base64_pattern = r'^[A-Za-z0-9+/]*={0,2}$'
        return bool(re.match(base64_pattern, value)) and len(value) % 4 == 0
    
    def is_url_encoded(self, value):
        """
        判断是否为 URL 编码
        """
        return '%' in value and re.search(r'%[0-9A-Fa-f]{2}', value)
    
    def is_encrypted_like(self, value):
        """
        判断是否像加密数据
        """
        # 长度较长且包含随机字符
        if len(value) > 20 and not value.isalnum():
            return True
        
        # 包含特殊字符但不是 URL 编码
        if re.search(r'[+/=]', value) and not self.is_url_encoded(value):
            return True
        
        return False


class CommonEncryption:
    """
    常见加密算法实现
    """
    
    @staticmethod
    def md5_hash(text):
        """MD5 哈希"""
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def sha1_hash(text):
        """SHA1 哈希"""
        return hashlib.sha1(text.encode()).hexdigest()
    
    @staticmethod
    def sha256_hash(text):
        """SHA256 哈希"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    @staticmethod
    def hmac_sha256(text, key):
        """HMAC-SHA256"""
        return hmac.new(key.encode(), text.encode(), hashlib.sha256).hexdigest()
    
    @staticmethod
    def base64_encode(text):
        """Base64 编码"""
        return base64.b64encode(text.encode()).decode()
    
    @staticmethod
    def base64_decode(encoded_text):
        """Base64 解码"""
        return base64.b64decode(encoded_text).decode()
    
    @staticmethod
    def aes_encrypt(text, key, iv=None):
        """AES 加密"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            
            if iv is None:
                iv = b'0' * 16  # 简单的 IV
            
            cipher = AES.new(key.encode()[:16].ljust(16, b'0'), AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(pad(text.encode(), AES.block_size))
            return base64.b64encode(encrypted).decode()
        except ImportError:
            return "需要安装 pycryptodome: pip install pycryptodome"
    
    @staticmethod
    def aes_decrypt(encrypted_text, key, iv=None):
        """AES 解密"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            
            if iv is None:
                iv = b'0' * 16
            
            cipher = AES.new(key.encode()[:16].ljust(16, b'0'), AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
            return decrypted.decode()
        except ImportError:
            return "需要安装 pycryptodome: pip install pycryptodome"


def analyze_signature_generation():
    """
    分析签名生成算法
    """
    print("\n=== 签名生成算法分析 ===")
    
    # 模拟一个常见的签名生成场景
    params = {
        'method': 'getUserInfo',
        'userId': '12345',
        'timestamp': str(int(time.time())),
        'nonce': ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    }
    
    secret_key = "demo_secret_key"
    
    print("原始参数:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # 常见的签名生成方法
    
    # 方法1: 参数排序后拼接
    def method1_signature(params, secret):
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_string = param_string + secret
        return hashlib.md5(sign_string.encode()).hexdigest()
    
    # 方法2: 只拼接值
    def method2_signature(params, secret):
        sorted_values = [params[k] for k in sorted(params.keys())]
        value_string = ''.join(sorted_values)
        sign_string = value_string + secret
        return hashlib.sha256(sign_string.encode()).hexdigest()
    
    # 方法3: HMAC 签名
    def method3_signature(params, secret):
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        return hmac.new(secret.encode(), param_string.encode(), hashlib.sha256).hexdigest()
    
    # 方法4: 包含特殊格式
    def method4_signature(params, secret):
        # 模拟某些网站的特殊签名格式
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_string = f"POST&{quote(param_string, safe='')}&{secret}"
        return base64.b64encode(hashlib.sha1(sign_string.encode()).digest()).decode()
    
    print("\n不同签名方法的结果:")
    print(f"方法1 (MD5拼接): {method1_signature(params, secret_key)}")
    print(f"方法2 (SHA256值拼接): {method2_signature(params, secret_key)}")
    print(f"方法3 (HMAC-SHA256): {method3_signature(params, secret_key)}")
    print(f"方法4 (特殊格式): {method4_signature(params, secret_key)}")
    
    return {
        'params': params,
        'signatures': {
            'method1': method1_signature(params, secret_key),
            'method2': method2_signature(params, secret_key),
            'method3': method3_signature(params, secret_key),
            'method4': method4_signature(params, secret_key)
        }
    }


def reverse_js_encryption():
    """
    逆向 JavaScript 加密算法
    """
    print("\n=== 逆向 JavaScript 加密算法 ===")
    
    # 模拟从网页中提取的 JavaScript 加密函数
    js_code = """
    function generateSign(params, timestamp, secretKey) {
        // 参数排序
        var keys = Object.keys(params).sort();
        var paramStr = '';
        
        for (var i = 0; i < keys.length; i++) {
            if (i > 0) paramStr += '&';
            paramStr += keys[i] + '=' + params[keys[i]];
        }
        
        // 添加时间戳和密钥
        var signStr = paramStr + '&timestamp=' + timestamp + '&key=' + secretKey;
        
        // MD5 加密
        return CryptoJS.MD5(signStr).toString();
    }
    
    function encryptData(data, key) {
        var encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), key).toString();
        return encrypted;
    }
    
    // 模拟 CryptoJS.MD5 函数
    var CryptoJS = {
        MD5: function(str) {
            // 这里应该是真实的 MD5 实现
            return {
                toString: function() {
                    // 简化的 MD5 模拟
                    return 'simulated_md5_' + str.length;
                }
            };
        },
        AES: {
            encrypt: function(data, key) {
                return {
                    toString: function() {
                        return 'encrypted_' + data.replace(/[^a-zA-Z0-9]/g, '').substring(0, 10);
                    }
                };
            }
        }
    };
    """
    
    print("JavaScript 加密代码:")
    print(js_code[:300] + "...")
    
    try:
        # 使用 PyExecJS 执行 JavaScript 代码
        ctx = execjs.compile(js_code)
        
        # 测试参数
        test_params = {
            'userId': '12345',
            'action': 'getData'
        }
        timestamp = int(time.time())
        secret_key = 'test_secret'
        
        # 调用 JavaScript 函数
        signature = ctx.call('generateSign', test_params, timestamp, secret_key)
        encrypted_data = ctx.call('encryptData', test_params, secret_key)
        
        print(f"\nJavaScript 执行结果:")
        print(f"签名: {signature}")
        print(f"加密数据: {encrypted_data}")
        
        # Python 实现相同的逻辑
        def python_generate_sign(params, timestamp, secret_key):
            keys = sorted(params.keys())
            param_str = '&'.join([f"{k}={params[k]}" for k in keys])
            sign_str = f"{param_str}&timestamp={timestamp}&key={secret_key}"
            return f"simulated_md5_{len(sign_str)}"  # 模拟 MD5
        
        python_signature = python_generate_sign(test_params, timestamp, secret_key)
        print(f"Python 实现结果: {python_signature}")
        
        return {
            'js_signature': signature,
            'python_signature': python_signature,
            'encrypted_data': encrypted_data
        }
        
    except Exception as e:
        print(f"JavaScript 执行失败: {e}")
        print("提示: 需要安装 PyExecJS: pip install PyExecJS")
        return None


def crack_simple_encryption():
    """
    破解简单加密示例
    """
    print("\n=== 破解简单加密示例 ===")
    
    # 模拟一个简单的加密场景
    original_data = "sensitive_user_data"
    
    # 简单的 XOR 加密
    def simple_xor_encrypt(data, key):
        result = []
        for i, char in enumerate(data):
            result.append(chr(ord(char) ^ ord(key[i % len(key)])))
        return ''.join(result)
    
    # 简单的位移加密
    def simple_shift_encrypt(data, shift):
        result = []
        for char in data:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base + shift) % 26 + base))
            else:
                result.append(char)
        return ''.join(result)
    
    # 加密数据
    xor_key = "key123"
    shift_amount = 3
    
    xor_encrypted = simple_xor_encrypt(original_data, xor_key)
    shift_encrypted = simple_shift_encrypt(original_data, shift_amount)
    
    print(f"原始数据: {original_data}")
    print(f"XOR 加密 (key: {xor_key}): {repr(xor_encrypted)}")
    print(f"位移加密 (shift: {shift_amount}): {shift_encrypted}")
    
    # 破解尝试
    print("\n破解尝试:")
    
    # XOR 破解 (已知密钥)
    xor_decrypted = simple_xor_encrypt(xor_encrypted, xor_key)
    print(f"XOR 解密: {xor_decrypted}")
    
    # 位移破解 (暴力破解)
    print("位移解密尝试:")
    for shift in range(26):
        decrypted = simple_shift_encrypt(shift_encrypted, -shift)
        if 'user' in decrypted.lower():  # 假设我们知道原文包含 'user'
            print(f"  shift {shift}: {decrypted} ← 可能正确")
        else:
            print(f"  shift {shift}: {decrypted}")
    
    return {
        'original': original_data,
        'xor_encrypted': xor_encrypted,
        'shift_encrypted': shift_encrypted,
        'xor_decrypted': xor_decrypted
    }


def analyze_real_world_example():
    """
    真实世界加密分析示例
    """
    print("\n=== 真实世界加密分析示例 ===")
    
    # 模拟从某个网站抓取到的加密请求
    captured_request = {
        'url': 'https://api.example.com/getData',
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json',
            'X-Timestamp': '1640995200',
            'X-Nonce': 'abc123def456',
            'X-Signature': 'a1b2c3d4e5f6789012345678901234567890abcd'
        },
        'data': {
            'encrypted_params': 'U2FsdGVkX1+vupppZksvRf5pq5g5XjFRIipRkwB0K1Y=',
            'timestamp': '1640995200',
            'version': '1.0'
        }
    }
    
    print("捕获的请求:")
    print(json.dumps(captured_request, indent=2, ensure_ascii=False))
    
    # 分析加密参数
    analyzer = EncryptionAnalyzer()
    
    # 分析请求头
    print("\n请求头分析:")
    header_analysis = analyzer.analyze_request_parameters(
        captured_request['url'], 
        captured_request['headers']
    )
    
    # 分析请求体
    print("\n请求体分析:")
    body_analysis = analyzer.analyze_request_parameters(
        captured_request['url'], 
        captured_request['data']
    )
    
    # 尝试解密 encrypted_params
    encrypted_params = captured_request['data']['encrypted_params']
    print(f"\n尝试解密参数: {encrypted_params}")
    
    # 常见的解密尝试
    possible_keys = ['default_key', 'api_secret', '12345678', 'secretkey']
    
    for key in possible_keys:
        try:
            # 尝试 AES 解密
            decrypted = CommonEncryption.aes_decrypt(encrypted_params, key)
            print(f"密钥 '{key}' AES 解密: {decrypted}")
        except Exception as e:
            print(f"密钥 '{key}' AES 解密失败: {str(e)[:50]}...")
        
        try:
            # 尝试 Base64 + 简单解密
            decoded = base64.b64decode(encrypted_params)
            print(f"密钥 '{key}' Base64 解码长度: {len(decoded)} 字节")
        except Exception as e:
            pass
    
    # 签名验证尝试
    print(f"\n签名验证尝试:")
    signature = captured_request['headers']['X-Signature']
    timestamp = captured_request['headers']['X-Timestamp']
    nonce = captured_request['headers']['X-Nonce']
    
    # 构建签名字符串的可能方式
    sign_attempts = [
        f"{timestamp}{nonce}",
        f"{nonce}{timestamp}",
        f"{timestamp}{nonce}{json.dumps(captured_request['data'], sort_keys=True)}",
        f"POST{captured_request['url']}{timestamp}{nonce}"
    ]
    
    for i, sign_string in enumerate(sign_attempts, 1):
        for key in possible_keys:
            md5_sign = CommonEncryption.md5_hash(sign_string + key)
            sha1_sign = CommonEncryption.sha1_hash(sign_string + key)
            hmac_sign = CommonEncryption.hmac_sha256(sign_string, key)
            
            if md5_sign == signature:
                print(f"  方式{i} MD5 匹配! 密钥: {key}, 签名字符串: {sign_string}")
            elif sha1_sign == signature:
                print(f"  方式{i} SHA1 匹配! 密钥: {key}, 签名字符串: {sign_string}")
            elif hmac_sign == signature:
                print(f"  方式{i} HMAC 匹配! 密钥: {key}, 签名字符串: {sign_string}")
    
    return {
        'request': captured_request,
        'header_analysis': header_analysis,
        'body_analysis': body_analysis
    }


def main():
    """
    主函数，运行所有示例
    """
    print("加密参数解析教程")
    print("=" * 50)
    
    try:
        # 1. 分析签名生成
        signature_analysis = analyze_signature_generation()
        
        # 2. 逆向 JavaScript 加密
        js_analysis = reverse_js_encryption()
        
        # 3. 破解简单加密
        crack_analysis = crack_simple_encryption()
        
        # 4. 真实世界示例分析
        real_world_analysis = analyze_real_world_example()
        
        print("\n=== 总结 ===")
        print("1. 学会识别不同类型的加密参数")
        print("2. 掌握常见的签名生成算法")
        print("3. 能够逆向简单的 JavaScript 加密")
        print("4. 了解真实场景的分析方法")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    
    print("\n教程完成！")


if __name__ == "__main__":
    main()


"""
学习要点总结:

1. 加密参数识别
   - 时间戳参数: timestamp, ts, t
   - 签名参数: sign, signature, sig
   - 哈希参数: 固定长度的十六进制字符串
   - 编码参数: Base64, URL编码
   - 加密参数: 随机字符串, 二进制数据

2. 常见加密算法
   - MD5: 32位十六进制
   - SHA1: 40位十六进制
   - SHA256: 64位十六进制
   - HMAC: 带密钥的哈希
   - AES: 对称加密
   - Base64: 编码算法

3. 签名生成模式
   - 参数排序拼接
   - 添加时间戳和随机数
   - 包含密钥或盐值
   - 特殊格式化规则
   - 多层嵌套加密

4. 逆向分析技巧
   - JavaScript 代码分析
   - 网络请求监控
   - 参数模式识别
   - 暴力破解尝试
   - 已知明文攻击

5. 破解方法
   - 字典攻击
   - 暴力破解
   - 模式分析
   - 时序攻击
   - 侧信道攻击

工具推荐:
- CyberChef: 在线编码解码
- Burp Suite: 请求分析
- PyExecJS: JavaScript 执行
- Hashcat: 哈希破解
- John the Ripper: 密码破解

实战步骤:
1. 捕获加密请求
2. 识别参数类型
3. 分析 JavaScript 代码
4. 提取加密逻辑
5. Python 复现算法
6. 验证破解结果

注意事项:
- 仅用于学习研究
- 遵守法律法规
- 不要用于恶意攻击
- 保护他人隐私
- 合理使用技术
"""