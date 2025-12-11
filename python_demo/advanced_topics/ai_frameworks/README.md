# AI 框架学习模块

## 模块简介

本模块专注于现代 AI 应用开发框架的学习，主要涵盖 LangChain 和 LlamaIndex 两个核心框架。这些框架是构建大语言模型应用的重要工具，广泛应用于聊天机器人、知识问答、文档分析等场景。

## 学习目标

完成本模块学习后，你将能够：

- 理解 LangChain 框架的核心概念和组件
- 掌握 LlamaIndex 的数据索引和检索机制
- 构建基于大语言模型的智能应用
- 实现 RAG（检索增强生成）系统
- 处理多种数据源和格式
- 优化模型性能和响应速度

## 前置知识

在开始学习本模块之前，建议你已经掌握：

- Python 基础编程（变量、函数、类、异常处理）
- 基本的 Web 开发知识（HTTP、API）
- 对机器学习和自然语言处理有基本了解
- 熟悉 OpenAI API 或其他大语言模型 API

## 模块结构

```
ai_frameworks/
├── README.md                    # 本文档
├── langchain/                   # LangChain 学习内容
│   ├── 01_basic_concepts.py     # 基础概念和组件
│   ├── 02_chains.py             # 链式调用
│   ├── 03_memory.py             # 记忆机制
│   ├── 04_agents.py             # 智能代理
│   ├── 05_document_loaders.py   # 文档加载器
│   └── 06_vector_stores.py      # 向量存储
├── llamaindex/                  # LlamaIndex 学习内容
│   ├── 01_basic_usage.py        # 基础使用
│   ├── 02_data_ingestion.py     # 数据摄取
│   ├── 03_indexing.py           # 索引构建
│   ├── 04_querying.py           # 查询系统
│   ├── 05_customization.py      # 自定义组件
│   └── 06_advanced_rag.py       # 高级 RAG 技术
├── projects/                    # 实践项目
│   ├── project1_chatbot/        # 智能聊天机器人
│   ├── project2_document_qa/    # 文档问答系统
│   └── project3_knowledge_base/ # 知识库系统
└── resources.md                 # 学习资源和社区链接
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv ai_env
source ai_env/bin/activate  # Linux/Mac
# ai_env\Scripts\activate  # Windows

# 安装基础依赖
pip install langchain langchain-openai
pip install llama-index
pip install openai
pip install chromadb  # 向量数据库
pip install streamlit  # 用于构建 Web 界面
```

### 2. API 密钥配置

在开始之前，你需要获取 OpenAI API 密钥：

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册账户并获取 API 密钥
3. 设置环境变量：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

或在代码中设置：

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

### 3. 第一个示例

```python
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# 创建语言模型实例
llm = OpenAI(temperature=0.7)

# 创建提示模板
prompt = PromptTemplate(
    input_variables=["topic"],
    template="请用简单的语言解释：{topic}"
)

# 创建链
chain = LLMChain(llm=llm, prompt=prompt)

# 运行
result = chain.run("什么是人工智能")
print(result)
```

## 学习路径

### 阶段一：基础概念（1-2 周）
1. 学习 LangChain 基础概念
2. 了解 LlamaIndex 核心功能
3. 完成基础示例练习

### 阶段二：核心功能（2-3 周）
1. 掌握链式调用和记忆机制
2. 学习文档处理和向量存储
3. 实践数据索引和检索

### 阶段三：高级特性（2-3 周）
1. 学习智能代理开发
2. 掌握 RAG 系统构建
3. 优化性能和用户体验

### 阶段四：项目实战（3-4 周）
1. 构建智能聊天机器人
2. 开发文档问答系统
3. 创建知识库应用

## 实践项目介绍

### 项目一：智能聊天机器人
- **技术栈**: LangChain + Streamlit + OpenAI
- **功能**: 多轮对话、上下文记忆、个性化回复
- **难度**: ⭐⭐⭐

### 项目二：文档问答系统
- **技术栈**: LlamaIndex + ChromaDB + FastAPI
- **功能**: 文档上传、智能检索、精准问答
- **难度**: ⭐⭐⭐⭐

### 项目三：企业知识库系统
- **技术栈**: LangChain + LlamaIndex + Vue.js
- **功能**: 多源数据集成、智能搜索、知识图谱
- **难度**: ⭐⭐⭐⭐⭐

## 常见问题

### Q: 需要付费的 API 吗？
A: OpenAI API 需要付费使用，但新用户通常有免费额度。你也可以使用开源模型如 Ollama。

### Q: 这些框架的主要区别是什么？
A: LangChain 更注重链式调用和代理，LlamaIndex 专注于数据索引和检索。两者可以结合使用。

### Q: 如何处理中文数据？
A: 两个框架都支持中文，但需要选择合适的嵌入模型和分词器。

### Q: 性能优化有什么建议？
A: 使用缓存、批处理、异步调用，选择合适的向量数据库和嵌入模型。

## 进阶学习建议

1. **深入理解 RAG**: 学习不同的检索策略和生成技术
2. **模型微调**: 了解如何针对特定领域优化模型
3. **多模态应用**: 探索文本、图像、音频的综合处理
4. **生产部署**: 学习模型服务化和性能监控
5. **安全性考虑**: 了解 AI 应用的安全风险和防护措施

## 社区资源

详细的学习资源和社区链接请参考 [resources.md](./resources.md) 文件。

---

**注意**: 本模块的示例代码需要网络连接和 API 密钥。请确保在合适的网络环境下学习，并注意 API 使用成本。