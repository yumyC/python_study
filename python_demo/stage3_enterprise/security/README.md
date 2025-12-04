# 安全模块 (Security Module)

## 概述

本模块介绍 Python Web 应用中的安全机制，包括身份认证、授权、JWT 令牌和 OAuth2 等核心概念。通过学习本模块，你将掌握如何构建安全的企业级 Web 应用。

## 学习目标

完成本模块学习后，你将能够：

- 理解身份认证和授权的区别
- 实现基于用户名密码的认证系统
- 使用 JWT 令牌进行无状态认证
- 实现基于角色的访问控制 (RBAC)
- 集成 OAuth2 第三方登录
- 理解常见的安全威胁和防护措施

## 前置知识

- 完成第二阶段 Web 框架学习
- 理解 HTTP 协议和状态管理
- 熟悉数据库操作和 ORM
- 了解加密和哈希的基本概念

## 内容结构

### FastAPI 安全示例

1. **01_authentication.py** - 基础认证
   - 用户注册和登录
   - 密码哈希存储
   - 会话管理

2. **02_authorization.py** - 授权控制
   - 基于角色的访问控制 (RBAC)
   - 权限装饰器
   - 资源级别权限

3. **03_jwt_tokens.py** - JWT 令牌
   - JWT 生成和验证
   - Access Token 和 Refresh Token
   - 令牌过期处理

4. **04_oauth2.py** - OAuth2 集成
   - OAuth2 密码流程
   - OAuth2 授权码流程
   - 第三方登录集成

### Flask 安全示例

1. **01_authentication.py** - 基础认证
   - Flask-Login 集成
   - 用户认证流程
   - Remember Me 功能

2. **02_authorization.py** - 授权控制
   - Flask-Principal 权限管理
   - 装饰器实现权限控制
   - 动态权限检查

3. **03_jwt_tokens.py** - JWT 令牌
   - Flask-JWT-Extended 使用
   - 令牌刷新机制
   - 令牌撤销

4. **04_session_management.py** - 会话管理
   - Flask Session 配置
   - Redis 会话存储
   - 会话安全设置

## 核心概念

### 1. 身份认证 (Authentication)

身份认证是验证用户身份的过程，回答"你是谁？"的问题。

**常见认证方式：**
- 用户名密码认证
- JWT 令牌认证
- OAuth2 第三方认证
- API Key 认证
- 多因素认证 (MFA)

### 2. 授权 (Authorization)

授权是确定用户能做什么的过程，回答"你能做什么？"的问题。

**常见授权模型：**
- 基于角色的访问控制 (RBAC)
- 基于属性的访问控制 (ABAC)
- 访问控制列表 (ACL)

### 3. JWT (JSON Web Token)

JWT 是一种无状态的认证方式，包含三部分：
- Header: 令牌类型和加密算法
- Payload: 用户信息和声明
- Signature: 签名验证

**优点：**
- 无需服务器存储会话
- 支持跨域认证
- 易于扩展

**注意事项：**
- 不要在 JWT 中存储敏感信息
- 设置合理的过期时间
- 使用 HTTPS 传输

### 4. OAuth2

OAuth2 是一个授权框架，允许第三方应用访问用户资源而无需获取密码。

**四种授权模式：**
- 授权码模式 (Authorization Code)
- 简化模式 (Implicit)
- 密码模式 (Password)
- 客户端模式 (Client Credentials)

### 5. 密码安全

**最佳实践：**
- 使用强哈希算法 (bcrypt, argon2)
- 加盐 (Salt) 防止彩虹表攻击
- 密码复杂度要求
- 防止暴力破解 (限流)

## 安全最佳实践

### 1. 密码存储
```python
# ❌ 错误：明文存储
password = "user_password"

# ❌ 错误：简单哈希
password = hashlib.md5("user_password".encode()).hexdigest()

# ✅ 正确：使用 bcrypt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("user_password")
```

### 2. 令牌管理
```python
# ✅ 设置合理的过期时间
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ✅ 使用强密钥
SECRET_KEY = os.getenv("SECRET_KEY")  # 从环境变量读取
ALGORITHM = "HS256"
```

### 3. HTTPS
- 生产环境必须使用 HTTPS
- 使用 HSTS 头部
- 配置安全的 Cookie 属性

### 4. CORS 配置
```python
# ✅ 明确指定允许的源
origins = [
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]

# ❌ 避免使用通配符
origins = ["*"]  # 不安全
```

### 5. 输入验证
- 验证所有用户输入
- 使用 Pydantic 进行数据验证
- 防止 SQL 注入（使用 ORM）
- 防止 XSS 攻击

## 常见安全威胁

### 1. SQL 注入
**防护：** 使用 ORM 或参数化查询

### 2. XSS (跨站脚本攻击)
**防护：** 输出转义，CSP 头部

### 3. CSRF (跨站请求伪造)
**防护：** CSRF Token，SameSite Cookie

### 4. 暴力破解
**防护：** 限流，账户锁定，验证码

### 5. 会话劫持
**防护：** HTTPS，Secure Cookie，会话超时

## 依赖包

### FastAPI 项目
```bash
pip install fastapi
pip install python-jose[cryptography]  # JWT
pip install passlib[bcrypt]            # 密码哈希
pip install python-multipart           # 表单数据
```

### Flask 项目
```bash
pip install flask
pip install flask-login                # 用户会话管理
pip install flask-jwt-extended         # JWT 支持
pip install flask-principal            # 权限管理
pip install passlib[bcrypt]            # 密码哈希
```

## 学习资源

### 官方文档
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Flask Security](https://flask.palletsprojects.com/en/latest/security/)
- [OAuth2 RFC](https://oauth.net/2/)
- [JWT.io](https://jwt.io/)

### 推荐阅读
- OWASP Top 10 安全风险
- [The Flask Mega-Tutorial - User Authentication](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins)
- [FastAPI Best Practices - Security](https://github.com/zhanymkanov/fastapi-best-practices#security)

### 视频教程
- [FastAPI 安全认证完整教程](https://www.youtube.com/results?search_query=fastapi+authentication)
- [Flask 用户认证系统](https://www.youtube.com/results?search_query=flask+authentication)

## 实践建议

1. **从简单开始**：先实现基础的用户名密码认证
2. **理解原理**：不要只是复制代码，理解每一步的作用
3. **测试安全性**：尝试攻击自己的应用，发现漏洞
4. **阅读源码**：研究 Flask-Login、FastAPI Security 的实现
5. **关注安全动态**：订阅安全相关的博客和新闻

## 下一步

完成本模块学习后，建议：
- 学习中间件模块，了解请求处理流程
- 学习可观测性模块，监控安全事件
- 在 CRM 项目中实践完整的认证授权系统

## 常见问题

### Q: JWT 和 Session 哪个更好？
A: 各有优劣。JWT 适合分布式系统和移动应用，Session 适合传统 Web 应用。可以根据场景选择或结合使用。

### Q: 如何存储 JWT？
A: 
- Web 应用：HttpOnly Cookie（防止 XSS）
- 移动应用：安全存储（Keychain/Keystore）
- 不要存储在 localStorage（易受 XSS 攻击）

### Q: 密码重置如何实现？
A: 生成临时令牌，发送到用户邮箱，验证令牌后允许重置密码。令牌应设置短期过期时间。

### Q: 如何实现"记住我"功能？
A: 使用长期有效的 Refresh Token，存储在安全的 Cookie 中。

### Q: 多因素认证如何实现？
A: 在密码验证后，要求用户输入第二因素（短信验证码、TOTP、硬件令牌等）。
