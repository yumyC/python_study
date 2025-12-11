# 智能聊天机器人项目

## 项目简介

本项目使用 LangChain 和 Streamlit 构建一个智能聊天机器人，具备多轮对话、上下文记忆和个性化回复功能。

## 功能特性

- **多轮对话**: 支持连续的对话交互
- **上下文记忆**: 记住对话历史，提供连贯的回复
- **个性化设置**: 可配置机器人的角色和风格
- **Web界面**: 基于 Streamlit 的友好用户界面
- **对话历史**: 保存和查看历史对话记录
- **多种模式**: 支持不同的对话模式（助手、朋友、专家等）

## 技术栈

- **LangChain**: 对话链和记忆管理
- **Streamlit**: Web 用户界面
- **OpenAI API**: 大语言模型（可选，支持本地模型）
- **Python**: 主要编程语言

## 项目结构

```
project1_chatbot/
├── README.md                 # 项目说明
├── requirements.txt          # 依赖包
├── app.py                   # 主应用程序
├── chatbot.py               # 聊天机器人核心逻辑
├── config.py                # 配置文件
├── utils.py                 # 工具函数
└── data/                    # 数据目录
    ├── conversations/       # 对话历史
    └── personas/           # 角色配置
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

创建 `.env` 文件并设置必要的环境变量：

```bash
# OpenAI API 密钥（可选）
OPENAI_API_KEY=your_openai_api_key_here

# 应用配置
APP_TITLE=智能聊天机器人
DEFAULT_PERSONA=assistant
```

### 3. 运行应用

```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

## 使用说明

### 基本对话

1. 打开应用后，在文本框中输入您的问题
2. 点击"发送"或按回车键
3. 机器人会根据上下文给出回复

### 个性化设置

1. 在侧边栏选择不同的机器人角色：
   - **助手**: 专业、有帮助的助手
   - **朋友**: 友好、随意的朋友
   - **专家**: 专业领域的专家
   - **创意**: 富有创意和想象力

2. 调整对话参数：
   - **温度**: 控制回复的创造性（0-1）
   - **记忆长度**: 记住的对话轮数
   - **最大长度**: 回复的最大字数

### 对话历史

- 查看当前会话的对话历史
- 导出对话记录为文本文件
- 清除当前对话历史

## 核心组件说明

### 1. 聊天机器人核心 (chatbot.py)

```python
class ChatBot:
    def __init__(self, persona="assistant", memory_length=10):
        # 初始化LLM和记忆
        self.llm = self._setup_llm()
        self.memory = self._setup_memory(memory_length)
        self.persona = persona
        
    def chat(self, message: str) -> str:
        # 处理用户消息并生成回复
        pass
```

### 2. Web界面 (app.py)

使用 Streamlit 构建交互式界面：
- 消息输入和显示
- 侧边栏配置
- 对话历史管理

### 3. 配置管理 (config.py)

管理不同的机器人角色和系统配置：
- 角色提示模板
- 默认参数设置
- 环境变量管理

## 扩展功能

### 1. 添加新角色

在 `data/personas/` 目录下创建新的角色配置文件：

```json
{
    "name": "编程助手",
    "description": "专业的编程和技术助手",
    "system_prompt": "你是一个专业的编程助手...",
    "temperature": 0.3,
    "max_tokens": 500
}
```

### 2. 集成外部知识库

```python
# 添加文档检索功能
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

def setup_knowledge_base():
    # 加载文档并创建向量存储
    pass
```

### 3. 多语言支持

```python
# 添加语言检测和翻译
def detect_language(text: str) -> str:
    # 检测输入语言
    pass

def translate_response(text: str, target_lang: str) -> str:
    # 翻译回复
    pass
```

## 性能优化

### 1. 缓存机制

```python
import streamlit as st

@st.cache_data
def load_model():
    # 缓存模型加载
    pass
```

### 2. 异步处理

```python
import asyncio

async def async_chat(message: str) -> str:
    # 异步处理聊天请求
    pass
```

### 3. 流式输出

```python
def stream_response(message: str):
    # 流式生成回复
    for chunk in response_generator:
        yield chunk
```

## 部署选项

### 1. Streamlit Cloud

1. 将代码推送到 GitHub
2. 在 Streamlit Cloud 中连接仓库
3. 配置环境变量
4. 部署应用

### 2. Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### 3. 云服务器部署

```bash
# 使用 PM2 管理进程
pm2 start "streamlit run app.py" --name chatbot
```

## 故障排除

### 常见问题

1. **API 密钥错误**
   - 检查 `.env` 文件中的 API 密钥
   - 确认密钥有效且有足够配额

2. **内存不足**
   - 减少记忆长度设置
   - 定期清理对话历史

3. **响应缓慢**
   - 检查网络连接
   - 考虑使用本地模型
   - 启用缓存机制

### 调试技巧

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

# 在关键位置添加日志
logger = logging.getLogger(__name__)
logger.debug(f"Processing message: {message}")
```

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 创建 GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本项目仅用于学习和演示目的。在生产环境中使用时，请确保遵循相关的安全和隐私规范。