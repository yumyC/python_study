"""
FastAPI Hello World 示例

这是最简单的 FastAPI 应用示例，演示如何创建一个基本的 API 端点。

运行方式:
    uvicorn 01_hello_world:app --reload

访问:
    - API: http://127.0.0.1:8000/
    - 交互式文档: http://127.0.0.1:8000/docs
    - 备用文档: http://127.0.0.1:8000/redoc
"""

from fastapi import FastAPI

# 创建 FastAPI 应用实例
# title: 应用标题，会显示在自动生成的文档中
# description: 应用描述
# version: API 版本号
app = FastAPI(
    title="Hello World API",
    description="这是一个简单的 FastAPI 示例应用",
    version="1.0.0"
)


# 定义根路径的 GET 请求处理函数
# @app.get() 是路径操作装饰器
# "/" 是路径（URL 路径）
# 函数返回的内容会自动转换为 JSON 响应
@app.get("/")
def read_root():
    """
    根路径处理函数
    
    返回一个简单的欢迎消息
    """
    return {"message": "Hello World", "status": "success"}


# 定义一个带路径参数的端点
# {name} 是路径参数，会传递给函数的 name 参数
@app.get("/hello/{name}")
def say_hello(name: str):
    """
    个性化问候
    
    参数:
        name: 用户名称（从 URL 路径中获取）
    
    返回:
        包含个性化问候消息的字典
    """
    return {
        "message": f"Hello, {name}!",
        "name": name
    }


# 定义一个返回应用信息的端点
@app.get("/info")
def get_info():
    """
    获取应用信息
    
    返回应用的基本信息
    """
    return {
        "app_name": "FastAPI Hello World",
        "version": "1.0.0",
        "framework": "FastAPI",
        "python_version": "3.9+"
    }


# 健康检查端点
# 通常用于监控系统检查服务是否正常运行
@app.get("/health")
def health_check():
    """
    健康检查端点
    
    返回服务健康状态
    """
    return {
        "status": "healthy",
        "service": "api"
    }


"""
学习要点:

1. FastAPI 应用创建
   - 使用 FastAPI() 创建应用实例
   - 可以设置标题、描述、版本等元数据

2. 路径操作装饰器
   - @app.get() 用于处理 GET 请求
   - 装饰器参数是 URL 路径
   - 支持其他 HTTP 方法: post, put, delete, patch 等

3. 路径参数
   - 使用 {参数名} 在路径中定义参数
   - 参数会自动传递给处理函数
   - 支持类型提示进行自动验证

4. 返回值
   - 函数返回的 Python 字典会自动转换为 JSON
   - 也可以返回列表、字符串等其他类型

5. 自动文档
   - FastAPI 自动生成交互式 API 文档
   - /docs 提供 Swagger UI 界面
   - /redoc 提供 ReDoc 界面
   - 文档基于函数的类型提示和文档字符串生成

6. 开发服务器
   - uvicorn 是 ASGI 服务器，用于运行 FastAPI 应用
   - --reload 参数启用热重载，代码修改后自动重启
   - 默认运行在 http://127.0.0.1:8000

实践练习:
1. 添加一个新的端点 /goodbye/{name}，返回告别消息
2. 创建一个 /time 端点，返回当前服务器时间
3. 修改 /info 端点，添加更多应用信息
4. 访问 /docs 查看自动生成的文档，尝试在文档中测试 API
"""
