"""
LlamaIndex 基础使用教程

本文件介绍 LlamaIndex 的基本概念和使用方法：
1. LlamaIndex 核心概念
2. 基础索引创建和查询
3. 不同类型的索引
4. 简单的问答系统
5. 配置和自定义

学习目标：
- 理解 LlamaIndex 的核心架构
- 掌握基础的索引和查询操作
- 学会构建简单的问答系统
- 了解不同索引类型的特点
"""

import os
import tempfile
from typing import List, Optional

# LlamaIndex 核心导入
try:
    from llama_index.core import (
        VectorStoreIndex, 
        SimpleDirectoryReader, 
        Document,
        Settings,
        StorageContext,
        load_index_from_storage
    )
    from llama_index.core.llms import MockLLM
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI
    
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    print("LlamaIndex 未安装，请运行: pip install llama-index")
    LLAMAINDEX_AVAILABLE = False

# 模拟嵌入和LLM（用于演示）
class MockEmbedding:
    """模拟嵌入模型"""
    
    def get_text_embedding(self, text: str) -> List[float]:
        """生成模拟嵌入向量"""
        import hashlib
        import numpy as np
        
        # 基于文本内容生成确定性向量
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        np.random.seed(seed)
        
        return np.random.normal(0, 1, 384).tolist()
    
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入向量"""
        return [self.get_text_embedding(text) for text in texts]

def demo_basic_concepts():
    """演示 LlamaIndex 基础概念"""
    print("=== LlamaIndex 基础概念演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    print("LlamaIndex 核心组件:")
    print("1. Document - 文档对象，包含文本内容和元数据")
    print("2. Index - 索引，用于组织和检索文档")
    print("3. Query Engine - 查询引擎，处理用户查询")
    print("4. LLM - 大语言模型，用于生成回答")
    print("5. Embedding Model - 嵌入模型，将文本转换为向量")
    print()
    
    # 创建示例文档
    documents = [
        Document(
            text="Python是一种高级编程语言，由Guido van Rossum创建于1991年。它以简洁的语法和强大的功能而闻名。",
            metadata={"source": "python_intro", "category": "编程语言"}
        ),
        Document(
            text="机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习和改进。",
            metadata={"source": "ml_intro", "category": "人工智能"}
        ),
        Document(
            text="深度学习是机器学习的一个子集，它使用具有多个层的神经网络来模拟人脑的工作方式。",
            metadata={"source": "dl_intro", "category": "人工智能"}
        )
    ]
    
    print("示例文档:")
    for i, doc in enumerate(documents):
        print(f"{i+1}. {doc.text[:50]}...")
        print(f"   元数据: {doc.metadata}")
    print()

def demo_simple_index():
    """演示简单索引创建和查询"""
    print("=== 简单索引演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    if os.getenv("OPENAI_API_KEY"):
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        Settings.embed_model = OpenAIEmbedding()
        print("使用 OpenAI 模型")
    else:
        Settings.llm = MockLLM()
        Settings.embed_model = MockEmbedding()
        print("使用模拟模型（演示用）")
    
    # 创建文档
    documents = [
        Document(text="FastAPI是一个现代、快速的Python Web框架，用于构建API。它基于标准Python类型提示，具有自动API文档生成功能。"),
        Document(text="Flask是一个轻量级的Python Web框架，它简单易用，适合小型到中型的Web应用开发。"),
        Document(text="Django是一个功能完整的Python Web框架，它遵循'约定优于配置'的原则，适合大型Web应用。"),
        Document(text="Streamlit是一个用于创建数据应用的Python库，它可以快速将数据脚本转换为可分享的Web应用。")
    ]
    
    try:
        # 创建向量索引
        index = VectorStoreIndex.from_documents(documents)
        print("向量索引创建成功")
        
        # 创建查询引擎
        query_engine = index.as_query_engine()
        
        # 执行查询
        queries = [
            "什么是FastAPI？",
            "哪个框架适合大型应用？",
            "Python Web框架有哪些？"
        ]
        
        for query in queries:
            print(f"\n查询: {query}")
            try:
                response = query_engine.query(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"查询失败: {e}")
        
    except Exception as e:
        print(f"索引创建失败: {e}")
    
    print()

def demo_directory_reader():
    """演示目录读取器"""
    print("=== 目录读取器演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 创建临时目录和文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建示例文件
        files_content = {
            "python_basics.txt": """
Python基础知识

Python是一种解释型、面向对象的编程语言。它具有以下特点：
1. 语法简洁明了
2. 跨平台兼容
3. 丰富的标准库
4. 活跃的社区支持

Python广泛应用于Web开发、数据科学、人工智能等领域。
            """,
            "web_frameworks.txt": """
Python Web框架

常见的Python Web框架包括：

1. Django - 功能完整的框架
   - 内置ORM
   - 管理后台
   - 用户认证系统

2. Flask - 轻量级框架
   - 简单易学
   - 灵活性高
   - 适合小型项目

3. FastAPI - 现代框架
   - 高性能
   - 自动文档生成
   - 类型提示支持
            """,
            "data_science.txt": """
Python数据科学

Python在数据科学领域的主要库：

1. NumPy - 数值计算
2. Pandas - 数据处理
3. Matplotlib - 数据可视化
4. Scikit-learn - 机器学习
5. TensorFlow/PyTorch - 深度学习

这些库构成了Python数据科学生态系统的基础。
            """
        }
        
        # 写入文件
        for filename, content in files_content.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
        
        try:
            # 使用目录读取器
            reader = SimpleDirectoryReader(temp_dir)
            documents = reader.load_data()
            
            print(f"从目录加载了 {len(documents)} 个文档")
            
            for doc in documents:
                filename = os.path.basename(doc.metadata.get('file_path', '未知'))
                print(f"- {filename}: {len(doc.text)} 字符")
            
            # 创建索引并查询
            if documents:
                Settings.llm = MockLLM()
                Settings.embed_model = MockEmbedding()
                
                index = VectorStoreIndex.from_documents(documents)
                query_engine = index.as_query_engine()
                
                query = "Python有哪些Web框架？"
                print(f"\n查询: {query}")
                
                try:
                    response = query_engine.query(query)
                    print(f"回答: {response}")
                except Exception as e:
                    print(f"查询失败: {e}")
        
        except Exception as e:
            print(f"目录读取失败: {e}")
    
    print()

def demo_index_persistence():
    """演示索引持久化"""
    print("=== 索引持久化演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    documents = [
        Document(text="人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。"),
        Document(text="机器学习是人工智能的一个子集，它使计算机能够从数据中学习而无需明确编程。"),
        Document(text="深度学习是机器学习的一个分支，它使用神经网络来模拟人脑的学习过程。")
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # 创建索引
            index = VectorStoreIndex.from_documents(documents)
            print("索引创建成功")
            
            # 保存索引
            index.storage_context.persist(persist_dir=temp_dir)
            print(f"索引已保存到: {temp_dir}")
            
            # 加载索引
            storage_context = StorageContext.from_defaults(persist_dir=temp_dir)
            loaded_index = load_index_from_storage(storage_context)
            print("索引加载成功")
            
            # 测试加载的索引
            query_engine = loaded_index.as_query_engine()
            query = "什么是人工智能？"
            
            print(f"\n使用加载的索引查询: {query}")
            try:
                response = query_engine.query(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"查询失败: {e}")
        
        except Exception as e:
            print(f"索引持久化演示失败: {e}")
    
    print()

def demo_custom_query_engine():
    """演示自定义查询引擎"""
    print("=== 自定义查询引擎演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    documents = [
        Document(
            text="Python编程语言具有简洁的语法和强大的功能。",
            metadata={"topic": "编程", "difficulty": "初级"}
        ),
        Document(
            text="机器学习算法可以从数据中自动学习模式。",
            metadata={"topic": "AI", "difficulty": "中级"}
        ),
        Document(
            text="深度学习神经网络需要大量的计算资源。",
            metadata={"topic": "AI", "difficulty": "高级"}
        )
    ]
    
    try:
        index = VectorStoreIndex.from_documents(documents)
        
        # 创建不同配置的查询引擎
        
        # 1. 基础查询引擎
        basic_engine = index.as_query_engine()
        
        # 2. 配置相似度阈值的查询引擎
        similarity_engine = index.as_query_engine(
            similarity_top_k=2,  # 返回最相似的2个文档
        )
        
        print("查询引擎配置:")
        print("1. 基础查询引擎 - 默认配置")
        print("2. 相似度查询引擎 - 限制返回文档数量")
        
        query = "编程语言的特点"
        
        print(f"\n测试查询: {query}")
        
        try:
            print("\n基础查询引擎结果:")
            response1 = basic_engine.query(query)
            print(f"回答: {response1}")
            
            print("\n相似度查询引擎结果:")
            response2 = similarity_engine.query(query)
            print(f"回答: {response2}")
            
        except Exception as e:
            print(f"查询执行失败: {e}")
    
    except Exception as e:
        print(f"自定义查询引擎演示失败: {e}")
    
    print()

def demo_metadata_filtering():
    """演示元数据过滤"""
    print("=== 元数据过滤演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    print("元数据过滤概念:")
    print("1. 可以根据文档的元数据进行过滤")
    print("2. 支持多种过滤条件组合")
    print("3. 提高查询的精确性和相关性")
    
    # 示例元数据结构
    metadata_examples = [
        {"source": "tutorial", "level": "beginner", "topic": "python"},
        {"source": "documentation", "level": "advanced", "topic": "ml"},
        {"source": "blog", "level": "intermediate", "topic": "web"}
    ]
    
    print("\n示例元数据结构:")
    for i, meta in enumerate(metadata_examples):
        print(f"{i+1}. {meta}")
    
    print("\n可能的过滤查询:")
    print("- 只查询初学者教程")
    print("- 只查询Python相关内容")
    print("- 排除博客来源的内容")
    print()

def demo_error_handling():
    """演示错误处理"""
    print("=== 错误处理演示 ===")
    
    print("常见错误和处理方法:")
    
    error_scenarios = {
        "API密钥未设置": {
            "错误": "OpenAI API key not found",
            "解决方案": "设置 OPENAI_API_KEY 环境变量"
        },
        "文档为空": {
            "错误": "No documents provided",
            "解决方案": "确保提供有效的文档内容"
        },
        "索引文件损坏": {
            "错误": "Failed to load index",
            "解决方案": "重新创建索引或检查存储路径"
        },
        "查询超时": {
            "错误": "Query timeout",
            "解决方案": "增加超时时间或简化查询"
        }
    }
    
    for scenario, info in error_scenarios.items():
        print(f"\n{scenario}:")
        print(f"  错误: {info['错误']}")
        print(f"  解决方案: {info['解决方案']}")
    
    print("\n最佳实践:")
    print("1. 始终使用 try-except 包装关键操作")
    print("2. 检查必要的环境变量和依赖")
    print("3. 提供有意义的错误信息")
    print("4. 实现重试机制处理临时错误")
    print()

def main():
    """主函数"""
    print("LlamaIndex 基础使用学习")
    print("=" * 50)
    
    # 检查依赖
    if not LLAMAINDEX_AVAILABLE:
        print("⚠️  LlamaIndex 未安装")
        print("请运行: pip install llama-index")
        print()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  注意: 未检测到 OPENAI_API_KEY 环境变量")
        print("将使用模拟模型进行演示")
        print()
    
    # 运行演示
    demo_basic_concepts()
    demo_simple_index()
    demo_directory_reader()
    demo_index_persistence()
    demo_custom_query_engine()
    demo_metadata_filtering()
    demo_error_handling()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. LlamaIndex 专注于数据索引和检索")
    print("2. Document 是基础的数据单元")
    print("3. Index 提供高效的数据组织方式")
    print("4. Query Engine 处理用户查询")
    print("5. 支持多种数据源和格式")
    print("6. 索引可以持久化存储和加载")

if __name__ == "__main__":
    main()